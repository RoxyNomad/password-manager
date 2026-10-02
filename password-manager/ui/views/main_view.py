# ui/views/main_view.py
import customtkinter as ctk
from tkinter import ttk
from ui.theme import UI_FONT
from ui.controllers.entry_handler import EditEntryDialog

class MainView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_controller

        self._configure_treeview_style()
        self._build_header()
        self._build_search_and_filter()
        self._build_treeview()
        self._build_form()
        self._build_status_bar()

    def _configure_treeview_style(self):
        """Customizes the standard Tkinter Treeview to match dark theme styling."""
        style = ttk.Style()
        
        # 'clamp' ensures color overrides apply consistently across Linux and macOS
        if "clamp" in style.theme_names():
            style.theme_use("clamp")

        style.configure(
            "Treeview",
            background="#111827",
            foreground="#F3F4F6",
            fieldbackground="#111827",
            borderwidth=0,
            font=(UI_FONT, 10),
            rowheight=32
        )
        style.configure(
            "Treeview.Heading",
            background="#1F2937",
            foreground="#9CA3AF",
            borderwidth=1,
            relief="flat",
            font=(UI_FONT, 10, "bold")
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

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(
            header_frame, 
            text="Password Vault", 
            font=ctk.CTkFont(family=UI_FONT, size=22, weight="bold"),
            text_color="#F3F4F6"
        )
        title.pack(side="left")

        # System Actions (Right)
        ctk.CTkButton(
            header_frame, 
            text="Lock Vault", 
            command=self.app.auth.lock_vault, 
            width=90, 
            height=32, 
            fg_color="#DC2626", 
            hover_color="#B91C1C"
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            header_frame, 
            text="Change Master Key", 
            command=self.app.dialogs.open_change_master_dialog, 
            width=140, 
            height=32, 
            fg_color="#D97706", 
            hover_color="#B45309"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            header_frame, 
            text="Audit", 
            command=self.app.dialogs.open_audit_dialog, 
            width=80, 
            height=32, 
            fg_color="#374151", 
            hover_color="#4B5563"
        ).pack(side="right", padx=5)

        # CSV Actions
        ctk.CTkButton(
            header_frame, 
            text="Export CSV", 
            command=self.app.io_handler.export_vault_to_csv, 
            width=100, 
            height=32,
            fg_color="#374151", 
            hover_color="#4B5563"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            header_frame, 
            text="Import CSV", 
            command=self.app.io_handler.import_vault_from_csv, 
            width=100, 
            height=32,
            fg_color="#374151", 
            hover_color="#4B5563"
        ).pack(side="right", padx=5)

    def _build_search_and_filter(self):
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=5)

        self.entry_search = ctk.CTkEntry(
            filter_frame, 
            placeholder_text="Search target or identity...", 
            width=280,
            height=36
        )
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda e: self.app.entry_handler.load_entries())

        self.filter_category = ctk.CTkOptionMenu(
            filter_frame, 
            values=["ALL", "Work", "Personal", "Finance", "Social", "Other"],
            command=lambda v: self.app.entry_handler.load_entries(),
            height=36
        )
        self.filter_category.set("ALL")
        self.filter_category.pack(side="left", padx=5)

        self.fav_only_var = ctk.BooleanVar(value=False)
        self.chk_fav_only = ctk.CTkCheckBox(
            filter_frame, 
            text="Favorites Only", 
            variable=self.fav_only_var,
            command=self.app.entry_handler.load_entries
        )
        self.chk_fav_only.pack(side="left", padx=15)

        self.chk_show_pass = ctk.CTkCheckBox(
            filter_frame, 
            text="Show Passwords", 
            command=self.app.toggle_password_visibility
        )
        self.chk_show_pass.pack(side="right")

    def _build_treeview(self):
        tree_frame = ctk.CTkFrame(self, fg_color="#111827", corner_radius=10, border_color="#1F2937", border_width=1)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "FAV", "CATEGORY", "TARGET_URI", "IDENTITY", "DECRYPTED_SECRET", "TOTP_CODE")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("ID", text="ID")
        self.tree.heading("FAV", text="★")
        self.tree.heading("CATEGORY", text="Category")
        self.tree.heading("TARGET_URI", text="Target / URI")
        self.tree.heading("IDENTITY", text="Identity / User")
        self.tree.heading("DECRYPTED_SECRET", text="Secret")
        self.tree.heading("TOTP_CODE", text="2FA Code")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("FAV", width=40, anchor="center")
        self.tree.column("CATEGORY", width=110, anchor="center")
        self.tree.column("TARGET_URI", width=200, anchor="w")
        self.tree.column("IDENTITY", width=180, anchor="w")
        self.tree.column("DECRYPTED_SECRET", width=180, anchor="w")
        self.tree.column("TOTP_CODE", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)

        self.tree.bind("<Double-1>", self.edit_selected_entry)
        self.tree.bind("<Control-c>", lambda e: self.app.clipboard_mgr.copy_password())
        self.tree.bind("<Control-u>", lambda e: self.app.clipboard_mgr.copy_username())

    def _build_form(self):
        form_frame = ctk.CTkFrame(self, fg_color="#111827", corner_radius=10, border_color="#1F2937", border_width=1)
        form_frame.pack(fill="x", padx=20, pady=(5, 10), ipady=5)

        # Responsive column expansion
        form_frame.grid_columnconfigure(0, weight=2)
        form_frame.grid_columnconfigure(1, weight=2)
        form_frame.grid_columnconfigure(2, weight=2)
        form_frame.grid_columnconfigure(3, weight=1)
        form_frame.grid_columnconfigure(4, weight=1)

        # Row 0: Target, User, Pass, Category
        self.entry_link = ctk.CTkEntry(form_frame, placeholder_text="Target URI (e.g. github.com)", height=36)
        self.entry_link.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.entry_user = ctk.CTkEntry(form_frame, placeholder_text="Identity / Username", height=36)
        self.entry_user.grid(row=0, column=1, sticky="ew", padx=5, pady=10)

        self.entry_pass = ctk.CTkEntry(form_frame, placeholder_text="Password", show="•", height=36)
        self.entry_pass.grid(row=0, column=2, sticky="ew", padx=5, pady=10)

        self.opt_category = ctk.CTkOptionMenu(form_frame, values=["Work", "Personal", "Finance", "Social", "Other"], height=36)
        self.opt_category.set("Other")
        self.opt_category.grid(row=0, column=3, columnspan=2, sticky="ew", padx=10, pady=10)

        # Row 1: TOTP, Scan QR, Generate, Favorite, Save
        self.entry_totp = ctk.CTkEntry(form_frame, placeholder_text="TOTP Secret (Optional)", height=36)
        self.entry_totp.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        ctk.CTkButton(
            form_frame, 
            text="Scan QR", 
            command=self.app.io_handler.scan_and_fill_qr_code, 
            height=36,
            fg_color="#374151",
            hover_color="#4B5563"
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 10))

        ctk.CTkButton(
            form_frame, 
            text="Generate", 
            command=self.app.entry_handler.generate_and_set_password, 
            height=36,
            fg_color="#374151",
            hover_color="#4B5563"
        ).grid(row=1, column=2, sticky="ew", padx=5, pady=(0, 10))

        self.chk_favorite = ctk.CTkCheckBox(form_frame, text="Favorite")
        self.chk_favorite.grid(row=1, column=3, sticky="w", padx=10, pady=(0, 10))

        self.btn_save = ctk.CTkButton(
            form_frame, 
            text="Save Entry", 
            command=self.app.entry_handler.save_entry, 
            height=36,
            font=ctk.CTkFont(family=UI_FONT, size=13, weight="bold")
        )
        self.btn_save.grid(row=1, column=4, sticky="ew", padx=10, pady=(0, 10))

    def _build_status_bar(self):
        self.status_bar = ctk.CTkLabel(
            self, 
            text="System Ready • Vault Decrypted", 
            font=ctk.CTkFont(family=UI_FONT, size=11), 
            text_color="#9CA3AF",
            anchor="w"
        )
        self.status_bar.pack(fill="x", padx=20, pady=(0, 10))

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
        item_id = None
        if event:
            # Check row under cursor directly
            region = self.tree.identify("region", event.x, event.y)
            if region == "cell" or region == "tree":
                item_id = self.tree.identify_row(event.y)
        
        if not item_id:
            selection = self.tree.selection()
            item_id = selection[0] if selection else None

        if not item_id:
            return

        values = self.tree.item(item_id, "values")
        if not values:
            return

        entry_data = {
            "id": values[0],
            "is_fav": 1 if values[1] == "★" else 0,
            "category": values[2],
            "link": values[3],
            "user": values[4],
            "pw": values[5],
            "totp": values[6] if len(values) > 6 else ""
        }

        EditEntryDialog(
            parent=self.winfo_toplevel(), 
            entry_data=entry_data, 
            on_save_callback=self._update_entry_in_db
        )

    def _update_entry_in_db(self, updated_data):
        if hasattr(self.app, 'entry_handler'):
            if hasattr(self.app.entry_handler, 'update_entry'):
                self.app.entry_handler.update_entry(updated_data)
            else:
                self.app.entry_handler.save_entry(updated_data)
                self.app.entry_handler.load_entries()