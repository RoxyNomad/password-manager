# main.py
import customtkinter as ctk
from ui.app import PasswordManagerApp

if __name__ == "__main__":
    root = ctk.CTk()
    app = PasswordManagerApp(root)
    root.mainloop()