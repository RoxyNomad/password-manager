import json
import tempfile
import os
import customtkinter as ctk

UI_FONT = "Segoe UI" if os.name == "nt" else "Helvetica Neue"

DARK_THEME = {
    "CTkFont": {
        "family": UI_FONT,
        "size": 13,
        "weight": "normal"
    },
    "CTk": {
        "fg_color": ["#0B0F17", "#0B0F17"]
    },
    "CTkFrame": {
        "corner_radius": 10,
        "border_width": 1,
        "fg_color": ["#111827", "#111827"],
        "top_fg_color": ["#1F2937", "#1F2937"],
        "border_color": ["#1F2937", "#1F2937"]
    },
    "CTkButton": {
        "corner_radius": 8,
        "border_width": 0,
        "fg_color": ["#059669", "#059669"],
        "hover_color": ["#10B981", "#10B981"],
        "border_color": ["#10B981", "#10B981"],
        "text_color": ["#FFFFFF", "#FFFFFF"],
        "text_color_disabled": ["#4B5563", "#4B5563"]
    },
    "CTkLabel": {
        "corner_radius": 0,
        "fg_color": "transparent",
        "text_color": ["#F3F4F6", "#F3F4F6"]
    },
    "CTkEntry": {
        "corner_radius": 8,
        "border_width": 1,
        "fg_color": ["#1F2937", "#1F2937"],
        "border_color": ["#374151", "#374151"],
        "text_color": ["#F9FAFB", "#F9FAFB"],
        "placeholder_text_color": ["#6B7280", "#6B7280"]
    },
    "CTkProgressBar": {
        "corner_radius": 6,
        "border_width": 0,
        "fg_color": ["#1F2937", "#1F2937"],
        "progress_color": ["#10B981", "#10B981"],
        "border_color": ["#1F2937", "#1F2937"]
    },
    "CTkCheckBox": {
        "corner_radius": 6,
        "border_width": 2,
        "fg_color": ["#10B981", "#10B981"],
        "border_color": ["#4B5563", "#4B5563"],
        "hover_color": ["#059669", "#059669"],
        "checkmark_color": ["#FFFFFF", "#FFFFFF"],
        "text_color": ["#E5E7EB", "#E5E7EB"],
        "text_color_disabled": ["#4B5563", "#4B5563"]
    },
    "DropdownMenu": {
        "fg_color": ["#1F2937", "#1F2937"],
        "hover_color": ["#374151", "#374151"],
        "text_color": ["#F9FAFB", "#F9FAFB"]
    },
    "CTkOptionMenu": {
        "corner_radius": 8,
        "fg_color": ["#1F2937", "#1F2937"],
        "button_color": ["#10B981", "#10B981"],
        "button_hover_color": ["#059669", "#059669"],
        "text_color": ["#F9FAFB", "#F9FAFB"],
        "text_color_disabled": ["#4B5563", "#4B5563"]
    },
    "CTkScrollbar": {
        "corner_radius": 6,
        "border_spacing": 2,
        "fg_color": "transparent",
        "button_color": ["#374151", "#374151"],
        "button_hover_color": ["#4B5563", "#4B5563"]
    }
}

def apply_dark_theme():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(DARK_THEME, f)
        temp_path = f.name
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme(temp_path)
    try:
        os.remove(temp_path)
    except OSError:
        pass