from tkinter import filedialog, messagebox
import database
from services import VaultIOService, QRScanService

class ImportExportHandler:
    def __init__(self, app):
        self.app = app

    @property
    def io_service(self) -> VaultIOService:
        fernet = getattr(self.app, "fernet", None)
        if not fernet:
            raise ValueError("Keine aktive Verschlüsselungssitzung gefunden. Bitte erneut anmelden.")
        return VaultIOService(fernet)

    def export_vault_to_csv(self):
        entries = database.get_all_entries()
        if not entries:
            messagebox.showinfo("INFO", "Vault is empty. Nothing to export.")
            return

        if not messagebox.askyesno(
            "SECURITY_WARNING", 
            "Exporting will write plain-text secrets to file!\nDo you want to proceed?"
        ):
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="EXPORT_VAULT_BACKUP"
        )
        if not file_path:
            return

        try:
            self.io_service.export_to_csv(file_path, entries)
            
            messagebox.showinfo("SUCCESS", f"Successfully exported {len(entries)} records to CSV!")
        except Exception as e:
            messagebox.showerror("ERROR", f"Export failed: {str(e)}")

    def import_vault_from_csv(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="IMPORT_VAULT_BACKUP"
            )
        if not file_path:
            return

        try:
            service = self.io_service
            
            imported_entries = service.import_from_csv(file_path)
            if not imported_entries:
                messagebox.showwarning("WARNING", "No valid entries found in file.")
                return

            imported_count = 0
            for item in imported_entries:
                entry_tuple = service.prepare_import_entry(item)
                if entry_tuple:
                    database.add_entry(*entry_tuple)
                    imported_count += 1

            if hasattr(self.app, "entry_handler"):
                self.app.entry_handler.load_entries()

            messagebox.showinfo("SUCCESS", f"Successfully imported {imported_count} records into vault!")
        except Exception as e:
            messagebox.showerror("ERROR", f"Import failed: {str(e)}")

    def scan_and_fill_qr_code(self):
        v = getattr(self.app, "current_view", None)
        if not v or not hasattr(v, 'entry_totp'):
            return

        file_path = filedialog.askopenfilename(
            title="SELECT_QR_CODE_IMAGE",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            secret = self.qr_scan_service.scan_qr_from_file(file_path)
            v.entry_totp.delete(0, "end")
            v.entry_totp.insert(0, secret)
            messagebox.showinfo("QR_SCAN_SUCCESS", f"TOTP Secret extracted successfully:\n\nKey: {secret}")
        except Exception as e:
            messagebox.showerror("QR_SCAN_ERROR", f"Failed to decode QR code:\n{str(e)}")