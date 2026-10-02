from tkinter import messagebox
from cryptography.fernet import Fernet
import crypto
import database
import security

from ui.dialogs.audit_dialog import SecurityAuditDialog
from ui.dialogs.change_master_dialog import ChangeMasterKeyDialog

class DialogHandler:
    def __init__(self, app):
        self.app = app

    def open_audit_dialog(self):
        entries = database.get_all_entries()
        audit_data = security.run_security_audit(entries, self.app.fernet)
        SecurityAuditDialog(self.app.root, audit_data)

    def open_change_master_dialog(self):
        def apply_new_master_key(new_pw):
            try:
                new_key = crypto.derive_key(new_pw, self.app.salt)
                new_fernet = Fernet(new_key)

                raw_entries = database.get_all_entries()
                rebound_entries = []

                # Step 1: Decrypt and prepare all data in memory before writing to DB
                for row in raw_entries:
                    entry_id, link, user, enc_pw = row[0], row[1], row[2], row[3]
                    enc_totp = row[4] if len(row) > 4 else ""
                    cat = row[5] if len(row) > 5 else "Other"
                    is_fav = row[6] if len(row) > 6 else 0

                    plain_pw = crypto.decrypt_text(self.app.fernet, enc_pw)
                    plain_totp = crypto.decrypt_text(self.app.fernet, enc_totp) if enc_totp else ""

                    rebound_entries.append({
                        "id": entry_id,
                        "link": link,
                        "user": user,
                        "pw": crypto.encrypt_text(new_fernet, plain_pw),
                        "totp": crypto.encrypt_text(new_fernet, plain_totp) if plain_totp else "",
                        "cat": cat,
                        "is_fav": is_fav
                    })

                # Step 2: Apply database updates
                for item in rebound_entries:
                    database.update_entry(
                        item["id"], item["link"], item["user"], 
                        item["pw"], item["totp"], item["cat"], item["is_fav"]
                    )

                self.app.fernet = new_fernet
                messagebox.showinfo("SUCCESS", "Vault successfully re-encrypted with new master key!")
            except Exception as e:
                messagebox.showerror("ERROR", f"Failed to re-encrypt vault: {str(e)}")

        ChangeMasterKeyDialog(self.app.root, on_success_callback=apply_new_master_key)