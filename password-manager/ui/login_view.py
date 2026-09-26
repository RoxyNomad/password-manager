import customtkinter as ctk
from tkinter import messagebox
from ui.theme import MATRIX_FONT
from ui.matrix_rain import MatrixRainCanvas

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_unlock_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_unlock_callback = on_unlock_callback

        # Regen-Background
        self.rain_canvas = MatrixRainCanvas(self)
        self.rain_canvas.pack(fill="both", expand=True)

        # Centered Card
        login_card = ctk.CTkFrame(
            self, corner_radius=10, fg_color="#0A0A0A",
            border_color="#00FF66", border_width=2, width=450, height=350
        )
        login_card.place(relx=0.5, rely=0.5, anchor="center")
        login_card.pack_propagate(False)
        login_card.lift()

        ctk.CTkLabel(
            login_card, text="[ SYSTEM_LOCKED ]",
            font=ctk.CTkFont(family=MATRIX_FONT, size=26, weight="bold")
        ).pack(pady=(40, 15))

        ctk.CTkLabel(
            login_card, text="ENTER MASTER_KEY TO ACCESS MAINFRAME:",
            font=ctk.CTkFont(family=MATRIX_FONT, size=12)
        ).pack(pady=5)

        self.master_entry = ctk.CTkEntry(
            login_card, show="*", width=320,
            placeholder_text="> master_password...",
            font=ctk.CTkFont(family=MATRIX_FONT, size=14)
        )
        self.master_entry.pack(pady=20)
        self.master_entry.focus()
        self.master_entry.bind("<Return>", lambda event: self._trigger_unlock())

        ctk.CTkButton(
            login_card, text="[ ACCESS_VAULT ]", command=self._trigger_unlock,
            width=200, height=40, font=ctk.CTkFont(family=MATRIX_FONT, size=13, weight="bold")
        ).pack(pady=10)

        self.after(100, self.rain_canvas.start_rain)

    def _trigger_unlock(self):
        pw = self.master_entry.get().strip()
        if not pw:
            messagebox.showwarning("ACCESS_DENIED", "Master key required!")
            return
        self.on_unlock_callback(pw)

    def destroy(self):
        if hasattr(self, 'rain_canvas') and self.rain_canvas:
            self.rain_canvas.stop_rain()
        super().destroy()