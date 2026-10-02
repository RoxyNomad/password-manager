# ui/app.py
import sys
import time
import pyotp
import customtkinter as ctk
import crypto
import database
from ui.theme import apply_matrix_theme
from ui.views.login_view import LoginView
from ui.views.main_view import MainView
from ui.controllers.dialog_handler import DialogHandler
from ui.controllers.auth_handler import AuthHandler
from ui.controllers.clipboard_mgr import ClipboardManager
from ui.controllers.entry_handler import EntryHandler
from ui.controllers.import_export import ImportExportHandler

class PasswordManagerApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("PASSWORD_VAULT_v1.0")
        
        # State Variables
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
        
        # Module-Handler initialisieren
        self.auth = AuthHandler(self)
        self.clipboard_mgr = ClipboardManager(self)
        self.entry_handler = EntryHandler(self)
        self.io_handler = ImportExportHandler(self)
        self.dialogs = DialogHandler(self)

        apply_matrix_theme()
        database.init_db()

        # Window State
        self.is_fullscreen = True
        self.root.after(0, self.maximize_window)
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())

        # Inaktivitäts-Events
        for event in ["<Any-KeyPress>", "<Any-ButtonPress>", "<Motion>"]:
            self.root.bind_all(event, self.auth.reset_inactivity_timer)

        self.switch_view(LoginView, on_unlock_callback=self.auth.unlock_vault)

    def switch_view(self, new_view_class, **kwargs):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = new_view_class(self.root, **kwargs)
        self.current_view.pack(fill="both", expand=True)

    def toggle_password_visibility(self):
        if hasattr(self.current_view, 'chk_show_pass'):
            # CustomTkinter Checkboxen geben standardmäßig 1 oder 0 als Int zurück
            is_checked = bool(self.current_view.chk_show_pass.get())
            
            # Invertieren für hide_passwords (wenn gecheckt -> Passwörter ZEIGEN -> hide_passwords = False)
            self.hide_passwords = not is_checked
            
            # Maskierung für das Eingabefeld unten im Formular anpassen
            if hasattr(self.current_view, 'entry_pass'):
                show_char = "" if is_checked else "•"
                self.current_view.entry_pass.configure(show=show_char)
            
            # Tabelle neu laden
            self.entry_handler.load_entries()

    def generate_totp(self, enc_totp_secret):
        if not enc_totp_secret or not self.fernet:
            return "---"
        try:
            secret = crypto.decrypt_text(self.fernet, enc_totp_secret).strip()
            return pyotp.TOTP(secret).now() if secret else "---"
        except Exception:
            return "INVALID"

    def totp_loop(self):
        if self.fernet:
            self.entry_handler.load_entries()
            self.totp_timer = self.root.after(1000, self.totp_loop)

    def maximize_window(self):
        try:
            if sys.platform.startswith("win"):
                self.root.wm_state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except Exception:
            self.root.attributes('-fullscreen', True)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        self.root.wm_state('normal')