from tkinter import ttk

class MainViewService:
    @staticmethod
    def configure_treeview_style(ui_font: str = "Helvetica Neue"):
        style = ttk.Style()
        
        if "clamp" in style.theme_names():
            style.theme_use("clamp")

        style.configure(
            "Treeview",
            background="#111827",
            foreground="#F3F4F6",
            fieldbackground="#111827",
            borderwidth=0,
            font=(ui_font, 10),
            rowheight=32
        )
        style.configure(
            "Treeview.Heading",
            background="#1F2937",
            foreground="#9CA3AF",
            borderwidth=1,
            relief="flat",
            font=(ui_font, 10, "bold")
        )
        style.map(
            "Treeview",
            background=[("selected", "#059669")],
            foreground=[("selected", "#FFFFFF")]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#374151")]
        )

    @staticmethod
    def extract_entry_from_tree(tree, event=None) -> dict | None:
        item_id = None
        if event:
            region = tree.identify("region", event.x, event.y)
            if region in ("cell", "tree"):
                item_id = tree.identify_row(event.y)
        
        if not item_id:
            selection = tree.selection()
            item_id = selection[0] if selection else None

        if not item_id:
            return None

        values = tree.item(item_id, "values")
        if not values:
            return None

        return {
            "id": values[0],
            "is_fav": 1 if values[1] == "★" else 0,
            "category": values[2],
            "link": values[3],
            "user": values[4],
            "pw": values[5],
            "totp": values[6] if len(values) > 6 else ""
        }

    @staticmethod
    def process_entry_update(app_controller, updated_data):
        if hasattr(app_controller, 'entry_handler'):
            if hasattr(app_controller.entry_handler, 'update_entry'):
                app_controller.entry_handler.update_entry(updated_data)
            else:
                app_controller.entry_handler.save_entry(updated_data)
                app_controller.entry_handler.load_entries()