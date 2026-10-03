import time
from tkinter import messagebox
from ui.views import LoginView, MainView
from services import AuthService, INACTIVITY_TIMEOUT_SEC

class AuthHandler:
    def __init__(self, app):
        self.app = app
        self.auth_service = AuthService()

    def unlock_vault(self, master_pw: str):
        self.app.fernet = self.auth_service.create_fernet_session(master_pw, self.app.salt)
        self.app.switch_view(MainView, app_controller=self.app)
        self.app.entry_handler.load_entries()
        self.reset_inactivity_timer()
        self.app.totp_loop()
        self.start_inactivity_checker()

    def lock_vault(self):
        self.app.fernet = None

        if self.app.totp_timer:
            self.app.root.after_cancel(self.app.totp_timer)
            self.app.totp_timer = None

        if self.app.inactivity_timer:
            self.app.root.after_cancel(self.app.inactivity_timer)
            self.app.inactivity_timer = None

        self.app.clipboard_mgr.clear_clipboard()
        self.app.switch_view(LoginView, on_unlock_callback=self.unlock_vault)
        messagebox.showinfo("SECURITY_LOCK", f"Vault locked automatically due to {INACTIVITY_TIMEOUT_SEC}s inactivity.")

    def reset_inactivity_timer(self, event=None):
        self.app._last_activity_time = time.time()

    def start_inactivity_checker(self):
        self._check_inactivity()

    def _check_inactivity(self):
        if self.app.fernet is not None:
            if self.auth_service.is_session_expired(self.app._last_activity_time):
                self.lock_vault()
                return
            self.app.inactivity_timer = self.app.root.after(1000, self._check_inactivity)