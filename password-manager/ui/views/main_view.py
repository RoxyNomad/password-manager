import customtkinter as ctk
from services import MainViewService
from ui.dialogs.edit_dialog import EditEntryDialog
from ui.views.main_widgets import (
    build_header,
    build_search_and_filter,
    build_treeview,
    build_form,
    build_status_bar
)

class MainView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_controller

        MainViewService.configure_treeview_style()

        build_header(self, self.app)
        self.entry_search, self.filter_category, self.fav_only_var = build_search_and_filter(self, self.app)
        self.tree = build_treeview(
            self, 
            on_double_click=self.edit_selected_entry,
            on_copy_pw=self.app.clipboard_mgr.copy_password,
            on_copy_user=self.app.clipboard_mgr.copy_username
        )
        self.form_elements = build_form(self, self.app)
        self.status_bar = build_status_bar(self)

        self.entry_link = self.form_elements["link"]
        self.entry_user = self.form_elements["user"]
        self.entry_pass = self.form_elements["pass"]
        self.entry_totp = self.form_elements["totp"]
        self.opt_category = self.form_elements["category"]
        self.chk_favorite = self.form_elements["favorite"]
        self.btn_save = self.form_elements["btn_save"]

    def show_clipboard_timer(self, label, remaining, total):
        self.status_bar.configure(
            text=f"• {label} copied to clipboard (clears in {remaining}s)",
            text_color="#10B981"
        )

    def hide_clipboard_timer(self):
        self.status_bar.configure(
            text="System Ready • Vault Decrypted",
            text_color="#9CA3AF"
        )

    def edit_selected_entry(self, event=None):
        entry_data = MainViewService.extract_entry_from_tree(self.tree, event)
        if not entry_data:
            return

        EditEntryDialog(
            parent=self.winfo_toplevel(), 
            entry_data=entry_data, 
            on_save=self._update_entry_in_db,
            on_delete=self.app.entry_handler.delete_entry
        )

    def _update_entry_in_db(self, updated_data):
        MainViewService.process_entry_update(self.app, updated_data)