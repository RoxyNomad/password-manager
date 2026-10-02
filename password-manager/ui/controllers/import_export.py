# ui/controllers/import_export.py
from tkinter import filedialog, messagebox
import database
import crypto
import qr_scanner

class ImportExportHandler:
    def __init__(self, app):
        self.app = app

    def export_vault_to_csv(self):
        entries = database.get_all_entries()
        if not entries:
            messagebox.showinfo("INFO", "Vault is empty. Nothing to export.")
            return

        if not messagebox.askyesno("SECURITY_WARNING", "Exporting will write plain-text secrets to file!\nDo you want to proceed?"):
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="EXPORT_VAULT_BACKUP"
        )
        if not file_path:
            return

        try:
            decrypted_list = []
            for row in entries:
                # Prüfen, ob `row` ein Dictionary/Row-Objekt oder ein Tuple ist
                if isinstance(row, dict) or hasattr(row, 'keys'):
                    enc_pw = row.get("pw") or row.get("password") or ""
                    enc_totp = row.get("totp") or row.get("note") or ""
                    link = row.get("link") or row.get("url") or ""
                    user = row.get("user") or row.get("username") or ""
                    category = row.get("category") or row.get("name") or "Other"
                    is_fav = row.get("is_fav", 0)
                else:
                    # Zugriff über Indizes (Tupel-Format)
                    link = row[1] if len(row) > 1 else ""
                    user = row[2] if len(row) > 2 else ""
                    enc_pw = row[3] if len(row) > 3 else ""
                    enc_totp = row[4] if len(row) > 4 else ""
                    category = row[5] if len(row) > 5 else "Other"
                    is_fav = row[6] if len(row) > 6 else 0

                # Entschlüsselung
                plain_pw = crypto.decrypt_text(self.app.fernet, enc_pw) if enc_pw else ""
                plain_totp = crypto.decrypt_text(self.app.fernet, enc_totp) if enc_totp else ""

                # Beide gängigen Schlüssel-Formate mappen (link & url, user & username, pw & password)
                decrypted_list.append({
                    "link": link,
                    "url": link,
                    "user": user,
                    "username": user,
                    "pw": plain_pw,
                    "password": plain_pw,
                    "totp": plain_totp,
                    "note": plain_totp,
                    "category": category,
                    "name": category,
                    "is_fav": is_fav
                })

            database.export_to_csv(file_path, decrypted_list)
            messagebox.showinfo("SUCCESS", f"Successfully exported {len(decrypted_list)} records to CSV!")
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
            imported_entries = database.import_from_csv(file_path)
            if not imported_entries:
                messagebox.showwarning("WARNING", "No valid entries found in file.")
                return

            imported_count = 0
            for item in imported_entries:
                link = item.get("link") or item.get("url") or item.get("name") or "Unkategorisiert"
                pw = item.get("pw") or item.get("password") or ""
                user = item.get("user") or item.get("username") or ""
                totp = item.get("totp") or item.get("note") or ""
                category = item.get("category") or item.get("name") or "Other"
                is_fav = item.get("is_fav", 0)

                if not pw:
                    continue

                enc_pw = crypto.encrypt_text(self.app.fernet, pw)
                enc_totp = crypto.encrypt_text(self.app.fernet, totp) if totp else ""

                database.add_entry(
                    link,
                    user,
                    enc_pw,
                    enc_totp,
                    category,
                    is_fav
                )
                imported_count += 1

            self.app.entry_handler.load_entries()
            messagebox.showinfo("SUCCESS", f"Successfully imported {imported_count} records into vault!")
        except Exception as e:
            messagebox.showerror("ERROR", f"Import failed: {str(e)}")

    def scan_and_fill_qr_code(self):
        v = self.app.current_view
        if not hasattr(v, 'entry_totp'):
            return

        file_path = filedialog.askopenfilename(
            title="SELECT_QR_CODE_IMAGE",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            secret = qr_scanner.scan_qr_from_file(file_path)
            v.entry_totp.delete(0, "end")
            v.entry_totp.insert(0, secret)
            messagebox.showinfo("QR_SCAN_SUCCESS", f"TOTP Secret extracted successfully:\n\nKey: {secret}")
        except Exception as e:
            messagebox.showerror("QR_SCAN_ERROR", f"Failed to decode QR code:\n{str(e)}")