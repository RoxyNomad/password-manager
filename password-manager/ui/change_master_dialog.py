import customtkinter as ctk
from ui.theme import MATRIX_FONT

class ChangeMasterKeyDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent, fg_color="#050505")
        self.on_success = on_success_callback
        
        self.title("MASTER_KEY_CHANGE")
        self.geometry("400x230")
        self.resizable(False, False)

        # Modales Fenster-Setup
        self.transient(parent)
        self.grab_set()

        # Dunklen Matrix-Hintergrund erzwingen
        self.configure(fg_color="#050505")

        # Hauptcontainer
        container = ctk.CTkFrame(self, fg_color="#050505", corner_radius=0)
        container.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            container, 
            text=">_ REKEY_MASTER_DATABASE", 
            font=ctk.CTkFont(family=MATRIX_FONT, size=15, weight="bold"), 
            text_color="#00FF66"
        ).pack(pady=(5, 15))

        ctk.CTkLabel(
            container, 
            text="ENTER_NEW_MASTER_KEY:", 
            font=ctk.CTkFont(family=MATRIX_FONT, size=10, weight="bold"), 
            text_color="#00FF66"
        ).pack(anchor="w", padx=10)

        self.entry_new = ctk.CTkEntry(
            container, 
            show="*", 
            font=ctk.CTkFont(family=MATRIX_FONT, size=12),
            border_color="#00FF66",
            fg_color="#0A0A0A",
            text_color="#00FF66"
        )
        self.entry_new.pack(fill="x", padx=10, pady=(4, 15))

        ctk.CTkButton(
            container, 
            text="[ RE-ENCRYPT_VAULT ]", 
            command=self._on_submit,
            font=ctk.CTkFont(family=MATRIX_FONT, size=11, weight="bold"),
            fg_color="#003300",
            hover_color="#005500",
            text_color="#00FF66",
            border_width=1,
            border_color="#00FF66"
        ).pack(fill="x", padx=10, pady=5)

        # WICHTIG: Erzwingt sofortiges Rendering
        self.update_idletasks()

    def _on_submit(self):
        new_pw = self.entry_new.get()
        if new_pw and len(new_pw) >= 4:
            self.on_success(new_pw)
            self.destroy()
        else:
            self.entry_new.configure(border_color="#FF3333")