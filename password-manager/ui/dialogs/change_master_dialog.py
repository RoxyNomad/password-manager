import customtkinter as ctk
from ui.theme import UI_FONT

class ChangeMasterKeyDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent, fg_color="#0B0F17")
        self.on_success = on_success_callback
        
        self.title("Change Master Key")
        self.geometry("420x260")
        self.resizable(False, False)

        # Modal Window Setup
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

        ctk.CTkLabel(
            container, 
            text="Change Master Key", 
            font=ctk.CTkFont(family=UI_FONT, size=18, weight="bold"), 
            text_color="#F3F4F6"
        ).pack(anchor="w", padx=15, pady=(15, 2))

        ctk.CTkLabel(
            container, 
            text="Re-encrypts the vault with a new password.", 
            font=ctk.CTkFont(family=UI_FONT, size=12), 
            text_color="#9CA3AF"
        ).pack(anchor="w", padx=15, pady=(0, 15))

        self.entry_new = ctk.CTkEntry(
            container, 
            show="*", 
            placeholder_text="Enter new master password...",
            font=ctk.CTkFont(family=UI_FONT, size=13),
            height=38,
            fg_color="#1F2937",
            border_color="#374151",
            text_color="#F9FAFB"
        )
        self.entry_new.pack(fill="x", padx=15, pady=(0, 15))
        self.entry_new.bind("<Return>", lambda e: self._on_submit())

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            command=self.destroy,
            font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
            fg_color="#374151",
            hover_color="#4B5563",
            width=100,
            height=36
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame, 
            text="Re-encrypt Vault", 
            command=self._on_submit,
            font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
            width=140,
            height=36
        ).pack(side="right")

        self.update_idletasks()
        self.after(10, self.focus_force)
        self.entry_new.focus()

    def _on_submit(self):
        new_pw = self.entry_new.get().strip()
        if new_pw and len(new_pw) >= 4:
            self.on_success(new_pw)
            self.destroy()
        else:
            self.entry_new.configure(border_color="#EF4444")