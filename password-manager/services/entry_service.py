from .security_service import SecurityService

class EntryService:
    def __init__(self, fernet):
        self.fernet = fernet

    def decrypt_entry_data(self, db_entry):
        if not db_entry:
            return None

        enc_pw = db_entry[3] if len(db_entry) > 3 else ""
        enc_totp = db_entry[4] if len(db_entry) > 4 else ""

        try:
            plain_pw = SecurityService.decrypt_text(self.fernet, enc_pw) if enc_pw else ""
        except Exception:
            plain_pw = ""

        try:
            plain_totp = SecurityService.decrypt_text(self.fernet, enc_totp) if enc_totp else ""
        except Exception:
            plain_totp = ""

        return {
            "id": db_entry[0],
            "link": db_entry[1] if len(db_entry) > 1 else "",
            "user": db_entry[2] if len(db_entry) > 2 else "",
            "pw": plain_pw,
            "totp": plain_totp,
            "category": db_entry[5] if len(db_entry) > 5 else "Other",
            "is_fav": db_entry[6] if len(db_entry) > 6 else 0
        }

    @staticmethod
    def extract_entry_data(entry_id, link, user, pw, totp, category, is_fav_value) -> dict:
        return {
            "id": entry_id,
            "link": link.strip() if link else "",
            "user": user.strip() if user else "",
            "pw": pw.strip() if pw else "",
            "totp": totp.strip() if totp else "",
            "category": category,
            "is_fav": 1 if is_fav_value else 0
        }

    @staticmethod
    def handle_delete_fallback(parent_window, entry_id):
        app = getattr(parent_window, "app", None) or getattr(parent_window, "master", None)

        if hasattr(app, "entry_handler") and hasattr(app.entry_handler, "delete_entry"):
            app.entry_handler.delete_entry(entry_id)
        elif hasattr(parent_window, "delete_entry"):
            parent_window.delete_entry(entry_id)