import customtkinter as ctk
from tkinter import messagebox
from services import AuthService
from ui.views.login_widgets import (
    build_login_header,
    create_password_input,
    create_unlock_button,
    create_login_card
)

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_unlock_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_unlock_callback = on_unlock_callback

        login_card = create_login_card(self)
        build_login_header(login_card)
        self.master_entry = create_password_input(login_card, self._trigger_unlock)
        create_unlock_button(login_card, self._trigger_unlock)

    def _trigger_unlock(self):
        raw_password = self.master_entry.get()
        is_valid, error_msg = AuthService.validate_login_input(raw_password)

        if not is_valid:
            messagebox.showwarning("Access Denied", error_msg)
            return

        self.on_unlock_callback(raw_password.strip())