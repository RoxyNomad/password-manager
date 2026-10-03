import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import customtkinter as ctk
from ui.theme import apply_dark_theme
from ui.app import PasswordManagerApp

def main():
    apply_dark_theme()
    root = ctk.CTk()
    app = PasswordManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()