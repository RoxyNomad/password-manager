import customtkinter as ctk
from ui.theme import UI_FONT

CATEGORIES = ["Work", "Personal", "Finance", "Social", "Other"]


def build_dialog_header(container, entry_id):
    ctk.CTkLabel(
        container, 
        text=f"Edit Entry (ID: {entry_id})", 
        font=ctk.CTkFont(family=UI_FONT, size=18, weight="bold"), 
        text_color="#F3F4F6"
    ).pack(anchor="w", padx=15, pady=(15, 10))


def create_form_field(container, label_text):
    ctk.CTkLabel(
        container, 
        text=label_text, 
        font=ctk.CTkFont(family=UI_FONT, size=11, weight="bold"), 
        text_color="#9CA3AF"
    ).pack(anchor="w", padx=15, pady=(2, 2))

    entry = ctk.CTkEntry(
        container, 
        height=36, 
        fg_color="#1F2937", 
        border_color="#374151"
    )
    return entry


def create_category_and_fav_row(container):
    row_frame = ctk.CTkFrame(container, fg_color="transparent")
    row_frame.pack(fill="x", padx=15, pady=(2, 8))

    opt_category = ctk.CTkOptionMenu(
        row_frame, 
        values=CATEGORIES,
        height=36,
        width=150
    )
    opt_category.pack(side="left")

    chk_fav = ctk.CTkCheckBox(
        row_frame, 
        text="Favorite", 
        font=ctk.CTkFont(family=UI_FONT, size=12)
    )
    chk_fav.pack(side="right", padx=10)

    return opt_category, chk_fav


def create_dialog_buttons(container, on_delete, on_cancel, on_save):
    btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    btn_frame.pack(fill="x", padx=15, pady=(15, 10))

    ctk.CTkButton(
        btn_frame, 
        text="Delete", 
        command=on_delete,
        font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
        fg_color="#DC2626",
        hover_color="#991B1B",
        width=90,
        height=36
    ).pack(side="left", padx=(0, 10))

    ctk.CTkButton(
        btn_frame, 
        text="Cancel", 
        command=on_cancel,
        font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
        fg_color="#374151",
        hover_color="#4B5563",
        width=90,
        height=36
    ).pack(side="left")

    ctk.CTkButton(
        btn_frame, 
        text="Save Changes", 
        command=on_save,
        font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
        width=120,
        height=36
    ).pack(side="right")