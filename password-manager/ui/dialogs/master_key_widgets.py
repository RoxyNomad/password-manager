import customtkinter as ctk
from ui.theme import UI_FONT

def build_dialog_header(container):
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


def create_password_entry(container):
    entry = ctk.CTkEntry(
        container, 
        show="*", 
        placeholder_text="Enter new master password...",
        font=ctk.CTkFont(family=UI_FONT, size=13),
        height=38,
        fg_color="#1F2937",
        border_color="#374151",
        text_color="#F9FAFB"
    )
    entry.pack(fill="x", padx=15, pady=(0, 15))
    return entry


def create_button_bar(container, on_cancel, on_submit):
    btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    btn_frame.pack(fill="x", padx=15, pady=(0, 15))

    ctk.CTkButton(
        btn_frame, 
        text="Cancel", 
        command=on_cancel,
        font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
        fg_color="#374151",
        hover_color="#4B5563",
        width=100,
        height=36
    ).pack(side="left")

    ctk.CTkButton(
        btn_frame, 
        text="Re-encrypt Vault", 
        command=on_submit,
        font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
        width=140,
        height=36
    ).pack(side="right")