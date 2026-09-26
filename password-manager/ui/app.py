from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet
import customtkinter as ctk
import pyotp
import time
import sys

# Lokale Module
import crypto
import security
import database
import generator
import qr_scanner
from ui.theme import apply_matrix_theme
from ui.login_view import LoginView
from ui.main_view import MainView
from ui.audit_dialog import SecurityAuditDialog
from ui.change_master_dialog import ChangeMasterKeyDialog

# Sicherheits-Timer Konfiguration (in Sekunden / Millisekunden)
INACTIVITY_TIMEOUT_SEC = 60    # Auto-Lock nach 60 Sekunden Inaktivität
CLIPBOARD_TIMEOUT_SEC = 15     # Zwischenablage nach 15 Sekunden leeren

class PasswordManagerApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("MATRIX // PASSWORD_VAULT_v1.0")
        
        # State Variables & Timers
        self.fernet = None
        self.salt = crypto.get_or_create_salt()
        self.current_view = None
        self.editing_id = None
        self.hide_passwords = True
        
        self.totp_timer = None
        self.inactivity_timer = None
        self.clipboard_timer = None
        self.clipboard_seconds_left = 0
        self._last_activity_time = time.time()
        
        apply_matrix_theme()
        database.init_db()

        # Window State / Fullscreen Management (Cross-Platform für Linux & Windows)
        self.is_fullscreen = True
        self.root.after(0, self.maximize_window)

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Global Inactivity Tracking Events
        self.root.bind_all("<Any-KeyPress>", self.reset_inactivity_timer)
        self.root.bind_all("<Any-ButtonPress>", self.reset_inactivity_timer)
        self.root.bind_all("<Motion>", self.reset_inactivity_timer)

        self.show_login_view()

    # --- VAULT AUTH & LOCK LOGIC ---

    def unlock_vault(self, master_pw: str):
        key = crypto.derive_key(master_pw, self.salt)
        self.fernet = Fernet(key)
        self.switch_view(MainView, app_controller=self)
        self.load_entries()
        self.reset_inactivity_timer()
        self.start_totp_loop()
        self.start_inactivity_checker()

    def lock_vault(self):
        """Sperrt den Vault, verwirft Keys und setzt die UI auf Login zurück."""
        self.fernet = None
        
        if self.totp_timer:
            self.root.after_cancel(self.totp_timer)
            self.totp_timer = None
            
        if self.inactivity_timer:
            self.root.after_cancel(self.inactivity_timer)
            self.inactivity_timer = None

        if self.clipboard_timer:
            self.root.after_cancel(self.clipboard_timer)
            self.clipboard_timer = None

        try:
            self.root.clipboard_clear()
        except Exception:
            pass

        self.show_login_view()
        messagebox.showinfo("SECURITY_LOCK", f"Vault locked automatically due to {INACTIVITY_TIMEOUT_SEC}s of inactivity.")

    def reset_inactivity_timer(self, event=None):
        self._last_activity_time = time.time()

    def start_inactivity_checker(self):
        self._check_inactivity()

    def _check_inactivity(self):
        if self.fernet is not None:
            elapsed = time.time() - self._last_activity_time
            if elapsed >= INACTIVITY_TIMEOUT_SEC:
                self.lock_vault()
                return
            self.inactivity_timer = self.root.after(1000, self._check_inactivity)

    def show_login_view(self):
        self.switch_view(LoginView, on_unlock_callback=self.unlock_vault)

    def switch_view(self, new_view_class, **kwargs):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = new_view_class(self.root, **kwargs)
        self.current_view.pack(fill="both", expand=True)

    # --- QR CODE SCANNER INTEGRATION ---

    def scan_and_fill_qr_code(self):
        if not isinstance(self.current_view, MainView):
            return

        file_path = filedialog.askopenfilename(
            title="SELECT_QR_CODE_IMAGE",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            secret = qr_scanner.scan_qr_from_file(file_path)
            
            self.current_view.entry_totp.delete(0, "end")
            self.current_view.entry_totp.insert(0, secret)
            
            messagebox.showinfo("QR_SCAN_SUCCESS", f"TOTP Secret extracted successfully:\n\nKey: {secret}")
        except Exception as e:
            messagebox.showerror("QR_SCAN_ERROR", f"Failed to decode QR code:\n{str(e)}")

    # --- SAFE CLIPBOARD AUTO-CLEAR LOGIC ---

    def copy_username_to_clipboard(self, event=None):
        if not isinstance(self.current_view, MainView):
            return
        selected = self.current_view.tree.selection()
        if not selected:
            return
        user = self.current_view.tree.item(selected[0], "values")[4]
        self._set_clipboard(user, "IDENTITY")

    def copy_password_to_clipboard(self, event=None):
        if not isinstance(self.current_view, MainView):
            return
        selected = self.current_view.tree.selection()
        if not selected:
            return
        entry_id = self.current_view.tree.item(selected[0], "values")[0]

        for row in database.get_all_entries():
            if str(row[0]) == str(entry_id):
                pw = crypto.decrypt_text(self.fernet, row[3])
                self._set_clipboard(pw, "PASSWORD")
                break

    def copy_totp_to_clipboard(self, event=None):
        if not isinstance(self.current_view, MainView):
            return
        selected = self.current_view.tree.selection()
        if not selected:
            return
        totp_code = self.current_view.tree.item(selected[0], "values")[6]
        if totp_code in ["---", "INVALID"]:
            return

        self._set_clipboard(totp_code, "2FA CODE")

    def _set_clipboard(self, text: str, item_type_name: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.start_clipboard_autoclear(item_type_name)

    def start_clipboard_autoclear(self, item_type_name: str):
        if self.clipboard_timer:
            self.root.after_cancel(self.clipboard_timer)
            self.clipboard_timer = None

        self.clipboard_seconds_left = CLIPBOARD_TIMEOUT_SEC
        self._tick_clipboard_autoclear(item_type_name)

    def _tick_clipboard_autoclear(self, item_type_name: str):
        if not isinstance(self.current_view, MainView):
            return

        v = self.current_view

        if self.clipboard_seconds_left > 0:
            if hasattr(v, 'show_clipboard_timer'):
                v.show_clipboard_timer(item_type_name, self.clipboard_seconds_left, CLIPBOARD_TIMEOUT_SEC)
            elif hasattr(v, 'show_clipboard_status'):
                v.show_clipboard_status(f"[!] {item_type_name} COPIED (Clears in {self.clipboard_seconds_left}s)")
            
            self.clipboard_seconds_left -= 1
            self.clipboard_timer = self.root.after(1000, lambda: self._tick_clipboard_autoclear(item_type_name))
        else:
            self.root.clipboard_clear()
            if hasattr(v, 'hide_clipboard_timer'):
                v.hide_clipboard_timer()
            elif hasattr(v, 'show_clipboard_status'):
                v.show_clipboard_status("[!] CLIPBOARD_CLEARED_FOR_SECURITY")
            self.clipboard_timer = None

    # --- TOTP ENGINE ---

    def start_totp_loop(self):
        if isinstance(self.current_view, MainView) and self.fernet:
            self.update_totp_codes()
            self.totp_timer = self.root.after(1000, self.start_totp_loop)

    def generate_totp(self, enc_totp_secret):
        if not enc_totp_secret:
            return "---"
        try:
            secret = crypto.decrypt_text(self.fernet, enc_totp_secret).strip()
            if not secret:
                return "---"
            totp = pyotp.TOTP(secret)
            return totp.now()
        except Exception:
            return "INVALID"

    def update_totp_codes(self):
        if not isinstance(self.current_view, MainView):
            return
        v = self.current_view

        for item in v.tree.get_children():
            values = list(v.tree.item(item, "values"))
            entry_id = values[0]

            for row in database.get_all_entries():
                if str(row[0]) == str(entry_id):
                    enc_totp = row[4] if len(row) > 4 else ""
                    new_totp = self.generate_totp(enc_totp)
                    if len(values) > 6 and values[6] != new_totp:
                        values[6] = new_totp
                        v.tree.item(item, values=values)
                    break

    # --- CRUD OPERATIONS & VAULT DATA ---

    def load_entries(self):
        if not isinstance(self.current_view, MainView):
            return
        v = self.current_view
        for item in v.tree.get_children():
            v.tree.delete(item)

        query_text = v.entry_search.get().strip().lower()
        selected_category = v.filter_category.get()
        only_favs = v.fav_only_var.get()

        for row in database.get_all_entries():
            entry_id = row[0]
            link = row[1]
            user = row[2]
            enc_pw = row[3]
            enc_totp = row[4] if len(row) > 4 else ""
            category = row[5] if len(row) > 5 else "Other"
            is_fav = row[6] if len(row) > 6 else 0

            if only_favs and is_fav != 1:
                continue

            if query_text and (query_text not in link.lower() and query_text not in user.lower()):
                continue

            if selected_category != "ALL" and category != selected_category:
                continue

            decrypted_pw = crypto.decrypt_text(self.fernet, enc_pw)
            display_pw = decrypted_pw if not self.hide_passwords else "••••••••••••"
            totp_code = self.generate_totp(enc_totp)
            fav_icon = "★" if is_fav == 1 else "☆"

            v.tree.insert("", "end", values=(entry_id, fav_icon, category, link, user, display_pw, totp_code))

    def save_entry(self):
        if not isinstance(self.current_view, MainView):
            return
        v = self.current_view
        link = v.entry_link.get().strip()
        user = v.entry_user.get().strip()
        pw = v.entry_pass.get().strip()
        totp_secret = v.entry_totp.get().strip()
        category = v.opt_category.get()
        is_fav = 1 if v.chk_favorite.get() else 0

        if not link or not user or not pw:
            messagebox.showwarning("INPUT_ERROR", "Target, Identity, and Password required!")
            return

        encrypted_pw = crypto.encrypt_text(self.fernet, pw)
        encrypted_totp = crypto.encrypt_text(self.fernet, totp_secret) if totp_secret else ""

        if self.editing_id is not None:
            database.update_entry(self.editing_id, link, user, encrypted_pw, encrypted_totp, category, is_fav)
            self.editing_id = None
            v.btn_save.configure(text="[ STORE_DATA ]")
        else:
            database.add_entry(link, user, encrypted_pw, encrypted_totp, category, is_fav)

        v.entry_link.delete(0, "end")
        v.entry_user.delete(0, "end")
        v.entry_pass.delete(0, "end")
        v.entry_totp.delete(0, "end")
        v.opt_category.set("Other")
        v.chk_favorite.deselect()
        v.strength_bar.set(0)
        self.load_entries()

    def edit_selected_entry(self):
        if not isinstance(self.current_view, MainView):
            return
        v = self.current_view
        selected = v.tree.selection()
        if not selected:
            messagebox.showwarning("SELECTION_ERROR", "Select an entry to edit!")
            return
        vals = v.tree.item(selected[0], "values")
        self.editing_id = vals[0]

        v.entry_link.delete(0, "end")
        v.entry_link.insert(0, vals[3])
        v.entry_user.delete(0, "end")
        v.entry_user.insert(0, vals[4])

        is_fav = 0
        cat = "Other"
        pw = ""
        totp = ""

        for row in database.get_all_entries():
            if str(row[0]) == str(self.editing_id):
                pw = crypto.decrypt_text(self.fernet, row[3])
                totp = crypto.decrypt_text(self.fernet, row[4]) if len(row) > 4 and row[4] else ""
                cat = row[5] if len(row) > 5 else "Other"
                is_fav = row[6] if len(row) > 6 else 0
                break

        v.entry_pass.delete(0, "end")
        v.entry_pass.insert(0, pw)
        v.entry_totp.delete(0, "end")
        v.entry_totp.insert(0, totp)
        v.opt_category.set(cat)

        if is_fav == 1:
            v.chk_favorite.select()
        else:
            v.chk_favorite.deselect()

        v.btn_save.configure(text="[ UPDATE_DATA ]")

    def delete_selected_entry(self):
        if not isinstance(self.current_view, MainView):
            return
        selected = self.current_view.tree.selection()
        if not selected:
            messagebox.showwarning("SELECTION_ERROR", "Select an entry to delete!")
            return
        entry_id = self.current_view.tree.item(selected[0], "values")[0]
        if messagebox.askyesno("CONFIRM_DELETE", f"Delete entry ID #{entry_id}?"):
            database.delete_entry(entry_id)
            self.load_entries()

    def toggle_selected_favorite(self):
        if not isinstance(self.current_view, MainView):
            return
        v = self.current_view
        selected = v.tree.selection()
        if not selected:
            messagebox.showwarning("SELECTION_ERROR", "Select an entry to toggle favorite status!")
            return
        entry_id = v.tree.item(selected[0], "values")[0]
        database.toggle_favorite(entry_id)
        self.load_entries()

    def toggle_password_visibility(self):
        if isinstance(self.current_view, MainView):
            self.hide_passwords = not self.current_view.chk_show_pass.get()
            self.load_entries()
            
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="Verbergen")
        else:
            self.password_entry.configure(show="*")
            self.toggle_btn.configure(text="Anzeigen")

    def generate_and_set_password(self):
        if isinstance(self.current_view, MainView):
            pw = generator.generate_password()
            self.current_view.entry_pass.delete(0, "end")
            self.current_view.entry_pass.insert(0, pw)
            self.current_view.update_strength_indicator()

    def maximize_window(self):
        """Maximiert das Fenster plattformunabhängig ohne TclError unter Linux."""
        try:
            if sys.platform.startswith("win"):
                self.root.wm_state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except Exception:
            self.root.attributes('-fullscreen', True)

    # --- CSV IMPORT & EXPORT ---

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
                enc_pw = row[3]
                enc_totp = row[4] if len(row) > 4 else ""

                plain_pw = crypto.decrypt_text(self.fernet, enc_pw)
                plain_totp = crypto.decrypt_text(self.fernet, enc_totp) if enc_totp else ""

                decrypted_list.append({
                    "link": row[1],
                    "user": row[2],
                    "pw": plain_pw,
                    "totp": plain_totp,
                    "category": row[5] if len(row) > 5 else "Other",
                    "is_fav": row[6] if len(row) > 6 else 0
                })

            database.export_to_csv(file_path, decrypted_list)
            messagebox.showinfo("SUCCESS", f"Successfully exported {len(decrypted_list)} records to CSV!")
        except Exception as e:
            messagebox.showerror("ERROR", f"Export failed: {str(e)}")

    def import_vault_from_csv(self):
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
                if not item["link"] or not item["pw"]:
                    continue

                enc_pw = crypto.encrypt_text(self.fernet, item["pw"])
                enc_totp = crypto.encrypt_text(self.fernet, item["totp"]) if item["totp"] else ""

                database.add_entry(
                    item["link"],
                    item["user"],
                    enc_pw,
                    enc_totp,
                    item["category"],
                    item["is_fav"]
                )
                imported_count += 1

            self.load_entries()
            messagebox.showinfo("SUCCESS", f"Successfully imported {imported_count} records into vault!")
        except Exception as e:
            messagebox.showerror("ERROR", f"Import failed: {str(e)}")

    # --- DIALOGS & SECURITY TOOLS ---

    def check_selected_breached(self):
        if not isinstance(self.current_view, MainView):
            return
        selected = self.current_view.tree.selection()
        if not selected:
            messagebox.showwarning("SELECTION_ERROR", "Select an entry first!")
            return
        entry_id = self.current_view.tree.item(selected[0], "values")[0]

        pw = ""
        for row in database.get_all_entries():
            if str(row[0]) == str(entry_id):
                pw = crypto.decrypt_text(self.fernet, row[3])
                break

        count = security.check_password_breached(pw)
        if count > 0:
            messagebox.showerror("BREACH_DETECTED", f"WARNING: Password breached {count} times in leaks!")
        elif count == 0:
            messagebox.showinfo("CLEAN", "No leaks detected for this passcode.")
        else:
            messagebox.showwarning("OFFLINE", "Could not connect to HIBP service.")

    def open_change_master_dialog(self):
        def apply_new_master_key(new_pw):
            try:
                new_key = crypto.derive_key(new_pw, self.salt)
                new_fernet = Fernet(new_key)

                for row in database.get_all_entries():
                    entry_id = row[0]
                    link = row[1]
                    user = row[2]
                    enc_pw = row[3]
                    enc_totp = row[4] if len(row) > 4 else ""
                    cat = row[5] if len(row) > 5 else "Other"
                    is_fav = row[6] if len(row) > 6 else 0

                    plain_pw = crypto.decrypt_text(self.fernet, enc_pw)
                    plain_totp = crypto.decrypt_text(self.fernet, enc_totp) if plain_totp else ""

                    re_enc_pw = crypto.encrypt_text(new_fernet, plain_pw)
                    re_enc_totp = crypto.encrypt_text(new_fernet, plain_totp) if plain_totp else ""

                    database.update_entry(entry_id, link, user, re_enc_pw, re_enc_totp, cat, is_fav)

                self.fernet = new_fernet
                messagebox.showinfo("SUCCESS", "Vault successfully re-encrypted with new master key!")
            except Exception as e:
                messagebox.showerror("ERROR", f"Failed to re-encrypt vault: {str(e)}")

        ChangeMasterKeyDialog(self.root, on_success_callback=apply_new_master_key)

    def open_audit_dialog(self):
        entries = database.get_all_entries()
        audit_data = security.run_security_audit(entries, self.fernet)
        SecurityAuditDialog(self.root, audit_data)

    # --- WINDOW / DISPLAY CONTROLS ---

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        self.root.wm_state('normal')