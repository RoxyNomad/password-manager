import csv
from typing import Any, Dict, List, Optional, Tuple, Union
from cryptography.fernet import Fernet
from .security_service import SecurityService

class VaultIOService:
    def __init__(self, fernet: Optional[Fernet] = None):
        self.fernet = fernet

    def prepare_export_data(self, db_entries: List[Union[dict, tuple]]) -> List[Dict[str, Any]]:
        if not self.fernet:
            raise ValueError("Fernet-Session ist nicht gesetzt!")

        decrypted_list = []
        for row in db_entries:
            if isinstance(row, dict) or hasattr(row, 'keys'):
                enc_pw = row.get("pw") or row.get("password") or ""
                enc_totp = row.get("totp") or row.get("note") or ""
                link = row.get("link") or row.get("url") or ""
                user = row.get("user") or row.get("username") or ""
                category = row.get("category") or "Other"
                is_fav = row.get("is_fav", 0)
            else:
                link = row[1] if len(row) > 1 else ""
                user = row[2] if len(row) > 2 else ""
                enc_pw = row[3] if len(row) > 3 else ""
                enc_totp = row[4] if len(row) > 4 else ""
                category = row[5] if len(row) > 5 else "Other"
                is_fav = row[6] if len(row) > 6 else 0

            plain_pw = SecurityService.decrypt_text(self.fernet, enc_pw) if enc_pw else ""
            plain_totp = SecurityService.decrypt_text(self.fernet, enc_totp) if enc_totp else ""

            decrypted_list.append({
                "link": link,
                "user": user,
                "pw": plain_pw,
                "totp": plain_totp,
                "category": category,
                "is_fav": is_fav
            })
        return decrypted_list

    def prepare_import_entry(self, item: Dict[str, Any]) -> Optional[Tuple[str, str, str, str, str, int]]:
        if not self.fernet:
            raise ValueError("Fernet-Session ist nicht gesetzt!")

        pw = item.get("pw") or item.get("password") or ""
        if not pw:
            return None

        link = item.get("link") or item.get("url") or item.get("name") or "Unkategorisiert"
        user = item.get("user") or item.get("username") or ""
        totp = item.get("totp") or item.get("note") or ""
        category = item.get("category") or "Other"
        is_fav = int(item.get("is_fav", 0))

        enc_pw = SecurityService.encrypt_text(self.fernet, pw)
        enc_totp = SecurityService.encrypt_text(self.fernet, totp) if totp else ""

        return (link, user, enc_pw, enc_totp, category, is_fav)

    def export_to_csv(self, file_path: str, db_entries: List[Union[dict, tuple]]) -> None:
        decrypted_entries = self.prepare_export_data(db_entries)
        
        with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["TARGET_URI", "IDENTITY", "PASSWORD", "2FA_SECRET", "CATEGORY", "IS_FAVORITE"])
            
            for entry in decrypted_entries:
                writer.writerow([
                    entry["link"],
                    entry["user"],
                    entry["pw"],
                    entry["totp"],
                    entry["category"],
                    entry["is_fav"]
                ])