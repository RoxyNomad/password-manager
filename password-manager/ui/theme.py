import json
import tempfile
import os
import customtkinter as ctk

MATRIX_FONT = "Courier New"

MATRIX_THEME = {
    "CTkFont": {"family": "Courier New", "size": 13, "weight": "normal"},
    "CTk": {"fg_color": ["#050505", "#050505"]},
    "CTkFrame": {
        "corner_radius": 6, "border_width": 1,
        "fg_color": ["#0A0A0A", "#0A0A0A"], "top_fg_color": ["#111111", "#111111"],
        "border_color": ["#00FF41", "#00FF41"]
    },
    "CTkButton": {
        "corner_radius": 4, "border_width": 1,
        "fg_color": ["#003B00", "#003B00"], "hover_color": ["#00FF41", "#00FF41"],
        "border_color": ["#00FF41", "#00FF41"], "text_color": ["#00FF41", "#000000"],
        "text_color_disabled": ["#005511", "#005511"]
    },
    "CTkLabel": {"corner_radius": 0, "fg_color": "transparent", "text_color": ["#00FF41", "#00FF41"]},
    "CTkEntry": {
        "corner_radius": 4, "border_width": 1,
        "fg_color": ["#050505", "#050505"], "border_color": ["#00FF41", "#00FF41"],
        "text_color": ["#00FF41", "#00FF41"], "placeholder_text_color": ["#005511", "#005511"]
    },
    "CTkProgressBar": {
        "corner_radius": 4, "border_width": 1,
        "fg_color": ["#0A0A0A", "#0A0A0A"], "progress_color": ["#00FF41", "#00FF41"],
        "border_color": ["#00FF41", "#00FF41"]
    },
    "CTkCheckBox": {
        "corner_radius": 4, "border_width": 2,
        "fg_color": ["#00FF41", "#00FF41"], "border_color": ["#00FF41", "#00FF41"],
        "hover_color": ["#003B00", "#003B00"], "checkmark_color": ["#000000", "#000000"],
        "text_color": ["#00FF41", "#00FF41"], "text_color_disabled": ["#005511", "#005511"]
    },
    "DropdownMenu": {
        "fg_color": ["#0A0A0A", "#0A0A0A"], "hover_color": ["#003B00", "#003B00"],
        "text_color": ["#00FF41", "#00FF41"]
    },
    "CTkOptionMenu": {
        "corner_radius": 4, "fg_color": ["#003B00", "#003B00"],
        "button_color": ["#00FF41", "#00FF41"], "button_hover_color": ["#009922", "#009922"],
        "text_color": ["#00FF41", "#00FF41"], "text_color_disabled": ["#005511", "#005511"]
    },
    "CTkScrollbar": {
        "corner_radius": 4, "border_spacing": 2,
        "fg_color": "transparent", "button_color": ["#003B00", "#003B00"],
        "button_hover_color": ["#00FF41", "#00FF41"]
    }
}

def apply_matrix_theme():
    """Erstellt temporär die JSON-Themedatei und lädt sie in CustomTkinter."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(MATRIX_THEME, f)
        temp_path = f.name
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme(temp_path)
    try:
        os.remove(temp_path)
    except OSError:
        pass