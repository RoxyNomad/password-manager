# crypto.py
import base64
import os
import json
import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import SALT_FILE

def get_or_create_salt() -> bytes:
    if not os.path.exists(SALT_FILE):
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
        return salt
    with open(SALT_FILE, "rb") as f:
        return f.read()

def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=400_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

def encrypt_text(fernet: Fernet, plain_text: str) -> str:
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_text(fernet: Fernet, encrypted_text: str) -> str:
    try:
        return fernet.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return "[Entschlüsselung fehlgeschlagen]"

def create_encrypted_backup(all_db_rows, fernet: Fernet, export_file_path: str):
    backup_data = []
    for row in all_db_rows:
        entry_id, link, user, enc_pw = row
        decrypted_pw = decrypt_text(fernet, enc_pw)
        backup_data.append({
            "target": link,
            "identity": user,
            "secret": decrypted_pw
        })
    raw_json = json.dumps(backup_data, indent=2)
    encrypted_payload = encrypt_text(fernet, raw_json)
    
    with open(export_file_path, "w", encoding="utf-8") as f:
        f.write(encrypted_payload)

# NEUE FUNKTION: Passwort-Generator
def generate_secure_password(length: int = 16) -> str:
    """Generiert ein kryptografisch sicheres Zufallspasswort."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))