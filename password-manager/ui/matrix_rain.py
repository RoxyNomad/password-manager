import random
import customtkinter as ctk
from ui.theme import MATRIX_FONT

MATRIX_CHARS = ['ｱ', 'ｲ', 'ｳ', 'ｴ', 'ｵ', 'ｶ', 'ｷ', 'ｸ', 'ｹ', 'ｺ', '0', '1', '2', '3', 'X', 'Y', 'Z', '@', '#', '$']

class MatrixRainCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#050505", highlightthickness=0, **kwargs)
        self.rain_running = False
        self.drops = []

    def start_rain(self):
        self.master.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 100 or height < 100:
            width, height = 1200, 800

        font_size = 14
        columns = int(width / font_size)
        self.drops = [random.randint(-50, 0) for _ in range(columns)]
        self.rain_running = True
        self.animate_rain(font_size, height)

    def animate_rain(self, font_size, height):
        if not self.rain_running:
            return

        self.delete("all")
        for i in range(len(self.drops)):
            char = random.choice(MATRIX_CHARS)
            x = i * font_size
            y = self.drops[i] * font_size

            self.create_text(x, y, text=char, fill="#88FF88", font=(MATRIX_FONT, font_size, "bold"), anchor="nw")
            if self.drops[i] > 1:
                self.create_text(x, y - font_size, text=random.choice(MATRIX_CHARS), fill="#005511", font=(MATRIX_FONT, font_size), anchor="nw")

            if y > height and random.random() > 0.975:
                self.drops[i] = 0
            else:
                self.drops[i] += 1

        self.after(40, lambda: self.animate_rain(font_size, height))

    def stop_rain(self):
        self.rain_running = False