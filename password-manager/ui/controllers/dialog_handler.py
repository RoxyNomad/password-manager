from tkinter import messagebox
import database
from ui.dialogs import SecurityAuditDialog, ChangeMasterKeyDialog
from services import SecurityService, AuditService

class DialogHandler:
    def __init__(self, app):
        self.app = app

    @property
    def service(self):
        fernet = getattr(self.app, "fernet", None)
        salt = getattr(self.app, "salt", None)
        if not fernet or not salt:
            raise ValueError("Keine aktive Session oder Salt gefunden.")
        return SecurityService(fernet, salt)

    def open_audit_dialog(self):
        try:
            # 1. Sicherstellen, dass Fernet vorhanden ist
            fernet = getattr(self.app, "fernet", None)
            if not fernet:
                messagebox.showerror("ERROR", "Keine aktive Sitzung gefunden. Bitte erneut anmelden.")
                return

            entries = database.get_all_entries()

            audit_data = AuditService.run_security_audit(entries, fernet)

            SecurityAuditDialog(self.app.root, audit_data)

        except Exception as e:
            messagebox.showerror("ERROR", f"Failed to run security audit: {str(e)}")

    def open_change_master_dialog(self):
        def apply_new_master_key(new_pw):
            try:
                new_fernet = self.service.reencrypt_vault(new_pw)
                self.app.fernet = new_fernet
                messagebox.showinfo("SUCCESS", "Vault successfully re-encrypted with new master key!")
            except Exception as e:
                messagebox.showerror("ERROR", f"Failed to re-encrypt vault: {str(e)}")

        ChangeMasterKeyDialog(self.app.root, on_success_callback=apply_new_master_key)