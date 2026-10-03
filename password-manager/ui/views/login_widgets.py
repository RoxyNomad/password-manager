import customtkinter as ctk
from ui.theme import UI_FONT

def create_login_card(parent):
    card = ctk.CTkFrame(
        parent, 
        corner_radius=12, 
        fg_color="#111827", 
        border_color="#1F2937", 
        border_width=1, 
        width=420, 
        height=320
    )
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)
    return card


def build_login_header(card):
    ctk.CTkLabel(
        card, 
        text="Vault Locked",
        font=ctk.CTkFont(family=UI_FONT, size=24, weight="bold"),
        text_color="#F3F4F6"
    ).pack(pady=(40, 8))

    ctk.CTkLabel(
        card, 
        text="Enter your master password to unlock:",
        font=ctk.CTkFont(family=UI_FONT, size=13),
        text_color="#9CA3AF"
    ).pack(pady=(0, 15))


def create_password_input(card, on_return_trigger):
    entry = ctk.CTkEntry(
        card, 
        show="*", 
        width=320,
        height=40,
        placeholder_text="Master password...",
        font=ctk.CTkFont(family=UI_FONT, size=14)
    )
    entry.pack(pady=15)
    entry.focus()
    entry.bind("<Return>", lambda event: on_return_trigger())
    return entry


def create_unlock_button(card, on_click_trigger):
    ctk.CTkButton(
        card, 
        text="Unlock Vault", 
        command=on_click_trigger,
        width=320, 
        height=42, 
        font=ctk.CTkFont(family=UI_FONT, size=14, weight="bold")
    ).pack(pady=10)