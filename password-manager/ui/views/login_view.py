# ui/views/login_view.py
import customtkinter as ctk
from tkinter import messagebox
from ui.theme import UI_FONT  # Verwendet die neue Theme-Schriftart

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_unlock_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_unlock_callback = on_unlock_callback

        # Zentrierte Login-Karte mit modernem Styling
        login_card = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            fg_color="#111827", 
            border_color="#1F2937", 
            border_width=1, 
            width=420, 
            height=320
        )
        login_card.place(relx=0.5, rely=0.5, anchor="center")
        login_card.pack_propagate(False)

        # Titel & Subtitel
        ctk.CTkLabel(
            login_card, 
            text="Vault Locked",
            font=ctk.CTkFont(family=UI_FONT, size=24, weight="bold"),
            text_color="#F3F4F6"
        ).pack(pady=(40, 8))

        ctk.CTkLabel(
            login_card, 
            text="Enter your master password to unlock:",
            font=ctk.CTkFont(family=UI_FONT, size=13),
            text_color="#9CA3AF"
        ).pack(pady=(0, 15))

        # Passworteingabe
        self.master_entry = ctk.CTkEntry(
            login_card, 
            show="*", 
            width=320,
            height=40,
            placeholder_text="Master password...",
            font=ctk.CTkFont(family=UI_FONT, size=14)
        )
        self.master_entry.pack(pady=15)
        self.master_entry.focus()
        self.master_entry.bind("<Return>", lambda event: self._trigger_unlock())

        # Unlock-Button
        ctk.CTkButton(
            login_card, 
            text="Unlock Vault", 
            command=self._trigger_unlock,
            width=320, 
            height=42, 
            font=ctk.CTkFont(family=UI_FONT, size=14, weight="bold")
        ).pack(pady=10)

    def _trigger_unlock(self):
        pw = self.master_entry.get().strip()
        if not pw:
            messagebox.showwarning("Access Denied", "Master password is required!")
            return
        self.on_unlock_callback(pw)