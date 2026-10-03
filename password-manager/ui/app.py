import time
import customtkinter as ctk
import database
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services import TotpService, WindowService, SecurityService

from ui.views import LoginView
from ui.controllers import (
    DialogHandler,
    AuthHandler,
    ClipboardManager,
    EntryHandler,
    ImportExportHandler,
)

class PasswordManagerApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("PASSWORD_VAULT_v1.0")
        
        self.fernet = None
        self.salt = SecurityService.get_or_create_salt()
        self.current_view = None
        self.editing_id = None
        self.hide_passwords = True
        
        self.totp_timer = None
        self.inactivity_timer = None
        self.clipboard_timer = None
        self.clipboard_seconds_left = 0
        self._last_activity_time = time.time()
        
        self.auth = AuthHandler(self)
        self.clipboard_mgr = ClipboardManager(self)
        self.entry_handler = EntryHandler(self)
        self.io_handler = ImportExportHandler(self)
        self.dialogs = DialogHandler(self)

        database.init_db()

        self.is_fullscreen = True
        self.root.after(0, lambda: WindowService.maximize(self.root))
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())

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
            is_checked = bool(self.current_view.chk_show_pass.get())
            self.hide_passwords = not is_checked
            
            if hasattr(self.current_view, 'entry_pass'):
                show_char = "" if is_checked else "•"
                self.current_view.entry_pass.configure(show=show_char)
            
            self.entry_handler.load_entries()

    def generate_totp(self, enc_totp_secret: str) -> str:
        return TotpService.generate(self.fernet, enc_totp_secret)

    def totp_loop(self):
        if self.fernet:
            self.entry_handler.load_entries()
            self.totp_timer = self.root.after(1000, self.totp_loop)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        self.root.wm_state('normal')