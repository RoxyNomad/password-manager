import base64
import json
import secrets
import string
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config import SALT_FILE


class SecurityService:
    def __init__(self, fernet: Optional[Fernet] = None, salt: Optional[bytes] = None):
        self.fernet = fernet
        self.salt = salt or self.get_or_create_salt()

    # -------------------------------------------------------------------------
    # KRYPTOGRAFISCHE KERNFUNKTIONEN & KEY DERIVATION
    # -------------------------------------------------------------------------

    @staticmethod
    def get_or_create_salt() -> bytes:
        salt_path = Path(SALT_FILE)
        if not salt_path.exists():
            salt = secrets.token_bytes(16)
            salt_path.write_bytes(salt)
            return salt
        return salt_path.read_bytes()

    @staticmethod
    def derive_key(master_password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=400_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

    @staticmethod
    def encrypt_text(fernet: Fernet, plain_text: str) -> str:
        if not plain_text:
            return ""
        return fernet.encrypt(plain_text.encode()).decode()

    @staticmethod
    def decrypt_text(fernet: Fernet, encrypted_text: str) -> str:
        if not encrypted_text:
            return ""
        try:
            return fernet.decrypt(encrypted_text.encode()).decode()
        except InvalidToken:
            return "[Entschlüsselung fehlgeschlagen: Ungültiger Schlüssel]"
        except Exception:
            return "[Entschlüsselung fehlgeschlagen]"

    # -------------------------------------------------------------------------
    # PASSWORT-GENERATION & VALIDIERUNG
    # -------------------------------------------------------------------------

    @staticmethod
    def validate_master_password(password: str) -> bool:
        if not password:
            return False
        return len(password.strip()) >= 4

    @staticmethod
    def validate_master_password_policy(password: str) -> tuple[bool, str]:
        """Prüft, ob das gewählte Master-Passwort den Richtlinien entspricht."""
        if len(password) < 8:
            return False, "Master key must be at least 8 characters long!"
        return True, "OK"

    @staticmethod
    def generate_secure_password(
        length: int = 16,
        use_symbols: bool = True,
        use_numbers: bool = True
    ) -> str:
        if length < 8:
            length = 8

        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits if use_numbers else ""
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if use_symbols else ""

        alphabet = lowercase + uppercase + digits + symbols

        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase)
        ]
        if use_numbers:
            password.append(secrets.choice(digits))
        if use_symbols:
            password.append(secrets.choice(symbols))

        while len(password) < length:
            password.append(secrets.choice(alphabet))

        secrets.SystemRandom().shuffle(password)
        return "".join(password)

    # -------------------------------------------------------------------------
    # VAULT RE-ENCRYPTION & BACKUP
    # -------------------------------------------------------------------------

    def reencrypt_vault(self, new_master_pw: str, db_module) -> Fernet:
        if not self.fernet:
            raise ValueError("Kein aktiver Fernet-Schlüssel im SecurityService vorhanden.")

        new_key = self.derive_key(new_master_pw, self.salt)
        new_fernet = Fernet(new_key)

        raw_entries = db_module.get_all_entries()
        rebound_entries = []

        for row in raw_entries:
            entry_id, link, user, enc_pw = row[0], row[1], row[2], row[3]
            enc_totp = row[4] if len(row) > 4 else ""
            cat = row[5] if len(row) > 5 else "Other"
            is_fav = row[6] if len(row) > 6 else 0

            plain_pw = self.decrypt_text(self.fernet, enc_pw)
            plain_totp = self.decrypt_text(self.fernet, enc_totp) if enc_totp else ""

            rebound_entries.append({
                "id": entry_id,
                "link": link,
                "user": user,
                "pw": self.encrypt_text(new_fernet, plain_pw),
                "totp": self.encrypt_text(new_fernet, plain_totp) if plain_totp else "",
                "cat": cat,
                "is_fav": is_fav
            })

        for item in rebound_entries:
            db_module.update_entry(
                item["id"], item["link"], item["user"],
                item["pw"], item["totp"], item["cat"], item["is_fav"]
            )

        self.fernet = new_fernet
        return new_fernet

    @classmethod
    def create_encrypted_backup(cls, all_db_rows: list, fernet: Fernet, export_file_path: str) -> None:
        backup_data = []
        for row in all_db_rows:
            entry_id, link, user, enc_pw = row[:4]
            decrypted_pw = cls.decrypt_text(fernet, enc_pw)
            backup_data.append({
                "target": link,
                "identity": user,
                "secret": decrypted_pw
            })

        raw_json = json.dumps(backup_data, indent=2)
        encrypted_payload = cls.encrypt_text(fernet, raw_json)
        Path(export_file_path).write_text(encrypted_payload, encoding="utf-8")

    # -------------------------------------------------------------------------
    # AUDIT & FARB-MAPPING
    # -------------------------------------------------------------------------

    def run_audit(self, db_module) -> Dict[str, Any]:
        entries = db_module.get_all_entries()
        
        total_entries = len(entries)
        weak_count = 0
        reused_count = 0
        passwords_seen = set()

        if self.fernet:
            for row in entries:
                enc_pw = row[3]
                plain_pw = self.decrypt_text(self.fernet, enc_pw)
                
                if len(plain_pw) < 8:
                    weak_count += 1
                if plain_pw in passwords_seen:
                    reused_count += 1
                passwords_seen.add(plain_pw)

        score = 100
        if total_entries > 0:
            score -= (weak_count * 15) + (reused_count * 20)
            score = max(0, score)

        return {
            "score": score,
            "total": total_entries,
            "weak": weak_count,
            "reused": reused_count,
        }

    @staticmethod
    def get_score_color(score: int) -> str:
        if score >= 80:
            return "#10B981"  # Grün
        if score >= 50:
            return "#F59E0B"  # Orange
        return "#EF4444"      # Rot

    @staticmethod
    def get_stat_color(count: int) -> str:
        return "#10B981" if count == 0 else "#EF4444"