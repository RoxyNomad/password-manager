import customtkinter as ctk
from services import SecurityService
from ui.dialogs.master_key_widgets import (
    build_dialog_header, 
    create_password_entry, 
    create_button_bar
)

class ChangeMasterKeyDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent, fg_color="#0B0F17")
        self.on_success = on_success_callback
        self.service = SecurityService()

        self.title("Change Master Key")
        self.geometry("420x260")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        container = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            fg_color="#111827", 
            border_width=1, 
            border_color="#1F2937"
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # UI Komponenten aufbauen
        build_dialog_header(container)
        self.entry_new = create_password_entry(container)
        self.entry_new.bind("<Return>", lambda e: self._on_submit())

        create_button_bar(container, on_cancel=self.destroy, on_submit=self._on_submit)

        self.update_idletasks()
        self.after(10, self.focus_force)
        self.entry_new.focus()

    def _on_submit(self):
        new_pw = self.entry_new.get().strip()
        if self.service.validate_master_password(new_pw):
            self.on_success(new_pw)
            self.destroy()
        else:
            self.entry_new.configure(border_color="#EF4444")