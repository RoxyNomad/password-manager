# ui/dialogs/edit_dialog.py
import customtkinter as ctk
from ui.theme import UI_FONT

class EditEntryDialog(ctk.CTkToplevel):
    def __init__(self, parent, entry_data, on_save_callback, on_delete_callback=None, **kwargs):
        super().__init__(parent, fg_color="#0B0F17")
        self.entry_data = entry_data  # Dict: {'id': ..., 'link': ..., 'user': ..., 'pw': ..., 'totp': ..., 'category': ..., 'is_fav': ...}
        self.on_save = on_save_callback
        self.on_delete = on_delete_callback

        self.title("Edit Vault Entry")
        self.geometry("450x480")
        self.resizable(False, False)

        # 1. UI bauen & Daten laden
        self._build_ui()
        self._load_entry_data()

        # 2. Modal-Einstellungen aktivieren (erst NACH dem UI-Aufbau)
        self.transient(parent)  # An Elternfenster binden
        self.update()           # Rendert das Fenster sofort im Window Manager
        self.grab_set()         # Sperrt Eingaben für das Hauptfenster

    def _build_ui(self):
        """Erstellt alle Widgets im Dark-Theme Design."""
        # Hauptcontainer Card
        self.container = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            fg_color="#111827", 
            border_width=1, 
            border_color="#1F2937"
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            self.container, 
            text=f"Edit Entry (ID: {self.entry_data.get('id')})", 
            font=ctk.CTkFont(family=UI_FONT, size=18, weight="bold"), 
            text_color="#F3F4F6"
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Target / URI
        ctk.CTkLabel(
            self.container, 
            text="Target URI / Website", 
            font=ctk.CTkFont(family=UI_FONT, size=11, weight="bold"), 
            text_color="#9CA3AF"
        ).pack(anchor="w", padx=15, pady=(2, 2))
        
        self.entry_link = ctk.CTkEntry(self.container, height=36, fg_color="#1F2937", border_color="#374151")
        self.entry_link.pack(fill="x", padx=15, pady=(0, 6))

        # Username / Identity
        ctk.CTkLabel(
            self.container, 
            text="Identity / Username", 
            font=ctk.CTkFont(family=UI_FONT, size=11, weight="bold"), 
            text_color="#9CA3AF"
        ).pack(anchor="w", padx=15, pady=(2, 2))
        
        self.entry_user = ctk.CTkEntry(self.container, height=36, fg_color="#1F2937", border_color="#374151")
        self.entry_user.pack(fill="x", padx=15, pady=(0, 6))

        # Password
        ctk.CTkLabel(
            self.container, 
            text="Password / Secret", 
            font=ctk.CTkFont(family=UI_FONT, size=11, weight="bold"), 
            text_color="#9CA3AF"
        ).pack(anchor="w", padx=15, pady=(2, 2))
        
        self.entry_pass = ctk.CTkEntry(self.container, height=36, fg_color="#1F2937", border_color="#374151")
        self.entry_pass.pack(fill="x", padx=15, pady=(0, 6))

        # TOTP Secret
        ctk.CTkLabel(
            self.container, 
            text="TOTP Secret (Optional)", 
            font=ctk.CTkFont(family=UI_FONT, size=11, weight="bold"), 
            text_color="#9CA3AF"
        ).pack(anchor="w", padx=15, pady=(2, 2))
        
        self.entry_totp = ctk.CTkEntry(self.container, height=36, fg_color="#1F2937", border_color="#374151")
        self.entry_totp.pack(fill="x", padx=15, pady=(0, 8))

        # Category Dropdown & Favorite Checkbox
        row_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        row_frame.pack(fill="x", padx=15, pady=(2, 8))

        self.opt_category = ctk.CTkOptionMenu(
            row_frame, 
            values=["Work", "Personal", "Finance", "Social", "Other"],
            height=36,
            width=150
        )
        self.opt_category.pack(side="left")

        self.chk_fav = ctk.CTkCheckBox(row_frame, text="Favorite", font=ctk.CTkFont(family=UI_FONT, size=12))
        self.chk_fav.pack(side="right", padx=10)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(15, 10))

        # Roten Löschen-Button auf der linken Seite hinzufügen
        ctk.CTkButton(
            btn_frame, 
            text="Delete", 
            command=self._on_delete,
            font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
            fg_color="#DC2626",
            hover_color="#991B1B",
            width=90,
            height=36
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            command=self.destroy,
            font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
            fg_color="#374151",
            hover_color="#4B5563",
            width=90,
            height=36
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame, 
            text="Save Changes", 
            command=self._on_save,
            font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
            width=120,
            height=36
        ).pack(side="right")

    def _load_entry_data(self):
        """Befüllt die Eingabefelder mit den übergebenen Werten."""
        if not self.entry_data:
            return

        self.entry_link.insert(0, self.entry_data.get("link", ""))
        self.entry_user.insert(0, self.entry_data.get("user", ""))
        self.entry_pass.insert(0, self.entry_data.get("pw", ""))
        self.entry_totp.insert(0, self.entry_data.get("totp", ""))

        category = self.entry_data.get("category", "Other")
        if category in ["Work", "Personal", "Finance", "Social", "Other"]:
            self.opt_category.set(category)

        if self.entry_data.get("is_fav"):
            self.chk_fav.select()

    def _on_save(self):
        """Liest die Formularwerte aus und übergibt sie an das Callback."""
        updated_entry = {
            "id": self.entry_data.get("id"),
            "link": self.entry_link.get().strip(),
            "user": self.entry_user.get().strip(),
            "pw": self.entry_pass.get().strip(),
            "totp": self.entry_totp.get().strip(),
            "category": self.opt_category.get(),
            "is_fav": 1 if self.chk_fav.get() else 0
        }
        if self.on_save:
            self.on_save(updated_entry)
        self.destroy()

    def _on_delete(self):
        entry_id = self.entry_data.get("id")
        self.destroy()  # Dialog schließen
        if self.on_delete:
            self.on_delete(entry_id)  # Löschen ausführen