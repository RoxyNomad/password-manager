import database
from .security_service import SecurityService

CLIPBOARD_TIMEOUT_SEC = 15

class ClipboardService:
    def __init__(self, fernet):
        self.fernet = fernet

    def get_decrypted_password(self, entry_id) -> str:
        if hasattr(database, 'get_entry_by_id'):
            row = database.get_entry_by_id(entry_id)
            if row and len(row) > 3 and row[3]:
                return SecurityService.decrypt_text(self.fernet, row[3])
        else:
            for row in database.get_all_entries():
                if str(row[0]) == str(entry_id):
                    return SecurityService.decrypt_text(self.fernet, row[3])
        return ""