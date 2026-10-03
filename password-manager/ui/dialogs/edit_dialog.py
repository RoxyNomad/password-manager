import customtkinter as ctk
from services import EntryService
from ui.dialogs.edit_entry_widgets import (
    build_dialog_header,
    create_form_field,
    create_category_and_fav_row,
    create_dialog_buttons,
    CATEGORIES
)

class EditEntryDialog(ctk.CTkToplevel):
    def __init__(self, parent, entry_data, on_save, on_delete=None, **kwargs):
        super().__init__(parent, fg_color="#0B0F17")
        self.entry_data = entry_data or {}
        self.on_save = on_save
        self.on_delete = on_delete

        self.title("Edit Vault Entry")
        self.geometry("450x480")
        self.resizable(False, False)

        self._build_ui()
        self._load_entry_data()

        self.transient(parent)
        self.update()
        self.grab_set()

    def _build_ui(self):
        container = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            fg_color="#111827", 
            border_width=1, 
            border_color="#1F2937"
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        entry_id = self.entry_data.get("id", "N/A")
        build_dialog_header(container, entry_id)

        self.entry_link = create_form_field(container, "Target URI / Website")
        self.entry_link.pack(fill="x", padx=15, pady=(0, 6))

        self.entry_user = create_form_field(container, "Identity / Username")
        self.entry_user.pack(fill="x", padx=15, pady=(0, 6))

        self.entry_pass = create_form_field(container, "Password / Secret")
        self.entry_pass.pack(fill="x", padx=15, pady=(0, 6))

        self.entry_totp = create_form_field(container, "TOTP Secret (Optional)")
        self.entry_totp.pack(fill="x", padx=15, pady=(0, 8))

        self.opt_category, self.chk_fav = create_category_and_fav_row(container)

        create_dialog_buttons(
            container, 
            on_delete=self._on_delete, 
            on_cancel=self._close_dialog, 
            on_save=self._on_save
        )

    def _load_entry_data(self):
        if not self.entry_data:
            return

        self.entry_link.insert(0, self.entry_data.get("link", ""))
        self.entry_user.insert(0, self.entry_data.get("user", ""))
        self.entry_pass.insert(0, self.entry_data.get("pw", ""))
        self.entry_totp.insert(0, self.entry_data.get("totp", ""))

        category = self.entry_data.get("category", "Other")
        if category in CATEGORIES:
            self.opt_category.set(category)

        if self.entry_data.get("is_fav"):
            self.chk_fav.select()

    def _close_dialog(self):
        self.grab_release()
        self.destroy()

    def _on_save(self):
        updated_entry = EntryService.extract_entry_data(
            entry_id=self.entry_data.get("id"),
            link=self.entry_link.get(),
            user=self.entry_user.get(),
            pw=self.entry_pass.get(),
            totp=self.entry_totp.get(),
            category=self.opt_category.get(),
            is_fav_value=self.chk_fav.get()
        )
        self._close_dialog()
        if self.on_save:
            self.on_save(updated_entry)

    def _on_delete(self):
        entry_id = self.entry_data.get("id")
        self._close_dialog()
        
        if self.on_delete:
            self.on_delete(entry_id)
        else:
            EntryService.handle_delete_fallback(self.master, entry_id)