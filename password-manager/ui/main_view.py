import customtkinter as ctk
from tkinter import ttk
from ui.theme import MATRIX_FONT
import generator

CATEGORIES = ["ALL", "Social Media", "Work", "Banking", "Streaming", "Personal", "Other"]

class MainView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_controller
        self.fav_only_var = ctk.BooleanVar(value=False)

        self._build_header()
        self._build_search_bar()
        self._build_input_form()
        self._build_action_buttons()
        self._build_treeview()
        self._build_clipboard_indicator()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(15, 5))

        ctk.CTkLabel(header_frame, text=">_ MATRIX // DATA_VAULT", font=ctk.CTkFont(family=MATRIX_FONT, size=26, weight="bold")).pack(side="left")
        
        ctk.CTkButton(header_frame, text="[ AUDIT ]", command=self.app.open_audit_dialog, width=80, height=28, fg_color="#003300", hover_color="#005500").pack(side="right", padx=5) # Neu!
        ctk.CTkButton(header_frame, text="[ MASTER_KEY ]", command=self.app.open_change_master_dialog, width=110, height=28).pack(side="right", padx=5)
        ctk.CTkButton(header_frame, text="[ IMPORT_CSV ]", command=self.app.import_vault_from_csv, width=100, height=28).pack(side="right", padx=5)
        ctk.CTkButton(header_frame, text="[ EXPORT_CSV ]", command=self.app.export_vault_to_csv, width=90, height=28).pack(side="right", padx=5)

    def _build_search_bar(self):
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(pady=5, padx=40, fill="x")

        ctk.CTkLabel(search_frame, text="SEARCH_FILTER:", font=ctk.CTkFont(family=MATRIX_FONT, size=13, weight="bold")).pack(side="left", padx=(0, 10))

        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Filter target or identity...", font=ctk.CTkFont(family=MATRIX_FONT, size=13))
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda event: self.app.load_entries())

        # Kategorie-Filter Dropdown
        ctk.CTkLabel(search_frame, text="CATEGORY:", font=ctk.CTkFont(family=MATRIX_FONT, size=12, weight="bold")).pack(side="left", padx=(0, 5))
        self.filter_category = ctk.CTkOptionMenu(
            search_frame, 
            values=CATEGORIES, 
            command=lambda selected: self.app.load_entries(),
            width=130,
            font=ctk.CTkFont(family=MATRIX_FONT, size=11, weight="bold")
        )
        self.filter_category.set("ALL")
        self.filter_category.pack(side="left", padx=(0, 10))

        # Quick Access: Only Favorites Switch/Button
        self.btn_fav_filter = ctk.CTkCheckBox(
            search_frame, 
            text="★ FAVS", 
            variable=self.fav_only_var,
            font=ctk.CTkFont(family=MATRIX_FONT, size=11, weight="bold"),
            command=self.app.load_entries
        )
        self.btn_fav_filter.pack(side="left", padx=(0, 15))

        self.chk_show_pass = ctk.CTkCheckBox(search_frame, text="SHOW_SECRETS", font=ctk.CTkFont(family=MATRIX_FONT, size=11, weight="bold"), command=self.app.toggle_password_visibility)
        self.chk_show_pass.pack(side="right")

    def _build_input_form(self):
        input_frame = ctk.CTkFrame(self, corner_radius=8)
        input_frame.pack(pady=10, padx=40, fill="x")
        input_frame.grid_columnconfigure(1, weight=1)

        # Target
        ctk.CTkLabel(input_frame, text="TARGET_URI:", font=ctk.CTkFont(family=MATRIX_FONT, size=13, weight="bold")).grid(row=0, column=0, padx=20, pady=6, sticky="w")
        self.entry_link = ctk.CTkEntry(input_frame, placeholder_text="e.g. matrix.net", font=ctk.CTkFont(family=MATRIX_FONT, size=13))
        self.entry_link.grid(row=0, column=1, padx=20, pady=6, sticky="ew")

        # Identity
        ctk.CTkLabel(input_frame, text="IDENTITY/MAIL:", font=ctk.CTkFont(family=MATRIX_FONT, size=13, weight="bold")).grid(row=1, column=0, padx=20, pady=6, sticky="w")
        self.entry_user = ctk.CTkEntry(input_frame, placeholder_text="e.g. neo@construct.io", font=ctk.CTkFont(family=MATRIX_FONT, size=13))
        self.entry_user.grid(row=1, column=1, padx=20, pady=6, sticky="ew")

        # Secret Hash
        ctk.CTkLabel(input_frame, text="SECRET_HASH:", font=ctk.CTkFont(family=MATRIX_FONT, size=13, weight="bold")).grid(row=2, column=0, padx=20, pady=6, sticky="w")
        self.entry_pass = ctk.CTkEntry(input_frame, placeholder_text="passcode...", show="*", font=ctk.CTkFont(family=MATRIX_FONT, size=13))
        self.entry_pass.grid(row=2, column=1, padx=20, pady=6, sticky="ew")
        self.entry_pass.bind("<KeyRelease>", lambda event: self.update_strength_indicator())

        # 2FA / TOTP
        ctk.CTkLabel(input_frame, text="2FA_SECRET_KEY:", font=ctk.CTkFont(family=MATRIX_FONT, size=13, weight="bold")).grid(row=3, column=0, padx=20, pady=6, sticky="w")
        self.entry_totp = ctk.CTkEntry(input_frame, placeholder_text="e.g. JBSWY3DPEHPK3PXP (optional)", font=ctk.CTkFont(family=MATRIX_FONT, size=13))
        self.entry_totp.grid(row=3, column=1, padx=20, pady=6, sticky="ew")

        # Category & Favorite (in eine Zeile)
        ctk.CTkLabel(input_frame, text="CATEGORY / FAV:", font=ctk.CTkFont(family=MATRIX_FONT, size=13, weight="bold")).grid(row=4, column=0, padx=20, pady=6, sticky="w")
        
        cat_fav_box = ctk.CTkFrame(input_frame, fg_color="transparent")
        cat_fav_box.grid(row=4, column=1, padx=20, pady=6, sticky="w")

        self.opt_category = ctk.CTkOptionMenu(
            cat_fav_box, 
            values=[c for c in CATEGORIES if c != "ALL"],
            font=ctk.CTkFont(family=MATRIX_FONT, size=12, weight="bold"),
            width=130
        )
        self.opt_category.set("Other")
        self.opt_category.pack(side="left", padx=(0, 15))

        self.chk_favorite = ctk.CTkCheckBox(
            cat_fav_box, 
            text="ADD_TO_FAVORITES (★)", 
            font=ctk.CTkFont(family=MATRIX_FONT, size=12, weight="bold")
        )
        self.chk_favorite.pack(side="left")

        # Strength Bar
        ctk.CTkLabel(input_frame, text="STRENGTH:", font=ctk.CTkFont(family=MATRIX_FONT, size=11, weight="bold")).grid(row=5, column=0, padx=20, pady=(0, 10), sticky="w")
        strength_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        strength_frame.grid(row=5, column=1, padx=20, pady=(0, 10), sticky="ew")

        self.strength_bar = ctk.CTkProgressBar(strength_frame, height=8)
        self.strength_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.strength_bar.set(0)

        self.strength_label = ctk.CTkLabel(strength_frame, text="EMPTY", font=ctk.CTkFont(family=MATRIX_FONT, size=10, weight="bold"), text_color="#555555")
        self.strength_label.pack(side="right")

    def _build_action_buttons(self):
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=5, padx=40, fill="x")

        ctk.CTkButton(
            btn_frame, text="[ GENERATE_HASH ]", command=self.app.generate_and_set_password, height=38, font=ctk.CTkFont(
                family=MATRIX_FONT, size=13, weight="bold"
            )).pack(side="left", padx=(0, 5), expand=True, fill="x")
        
        self.btn_save = ctk.CTkButton(
            btn_frame, text="[ STORE_DATA ]", command=self.app.save_entry, height=38, font=ctk.CTkFont(
                family=MATRIX_FONT, size=13, weight="bold"
            ))
        self.btn_save.pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            btn_frame, text="[ CHECK_LEAKS ]", command=self.app.check_selected_breached, height=38, font=ctk.CTkFont(
                family=MATRIX_FONT, size=13, weight="bold"
            )).pack(side="left", padx=5, expand=True, fill="x")
        
        ctk.CTkButton(
            btn_frame, text="[ EDIT_SELECTED ]", command=self.app.edit_selected_entry, height=38, font=ctk.CTkFont(
                family=MATRIX_FONT, size=13, weight="bold"
            )).pack(side="left", padx=5, expand=True, fill="x")

        self.btn_toggle_fav = ctk.CTkButton(
            btn_frame, text="[ ★ TOGGLE_FAV ]", command=self.app.toggle_selected_favorite, font=ctk.CTkFont(
                family=MATRIX_FONT, size=12, weight="bold"
            ))
        self.btn_toggle_fav.pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, 
            text="[ DELETE_SELECTED ]", 
            command=self.app.delete_selected_entry, 
            height=38, fg_color=["#3B0000", "#3B0000"], 
            hover_color=["#FF0000", "#FF0000"], 
            border_color=["#FF0000", "#FF0000"], 
            text_color=["#FF0000", "#000000"], 
            font=ctk.CTkFont(
                family=MATRIX_FONT, size=13, weight="bold"
            )).pack(side="left", padx=(5, 0), expand=True, fill="x")

    def _build_treeview(self):
        self.setup_treeview_matrix_style()
        table_frame = ctk.CTkFrame(self, corner_radius=8)
        table_frame.pack(pady=10, padx=40, fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "FAV", "Category", "Link", "User", "Pass", "TOTP"), show="headings", selectmode="browse")
        self.tree.heading("ID", text="ID")
        self.tree.heading("FAV", text="FAV")
        self.tree.heading("Category", text="CATEGORY")
        self.tree.heading("Link", text="TARGET_URI")
        self.tree.heading("User", text="IDENTITY")
        self.tree.heading("Pass", text="DECRYPTED_SECRET")
        self.tree.heading("TOTP", text="2FA_CODE (30s)")

        self.tree.column("ID", width=35, anchor="center")
        self.tree.column("FAV", width=35, anchor="center")
        self.tree.column("Category", width=110, anchor="center")
        self.tree.column("Link", width=180)
        self.tree.column("User", width=200)
        self.tree.column("Pass", width=180)
        self.tree.column("TOTP", width=110, anchor="center")

        self.tree.bind("<Double-1>", self.app.copy_password_to_clipboard)
        self.tree.bind("<Control-c>", lambda e: self.app.copy_password_to_clipboard(None))
        self.tree.bind("<Control-u>", lambda e: self.app.copy_username_to_clipboard(None))
        self.tree.bind("<Control-t>", lambda e: self.app.copy_totp_to_clipboard(None))

        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

    def setup_treeview_matrix_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#050505", foreground="#00FF66", fieldbackground="#050505", rowheight=30, borderwidth=1, relief="solid", font=(MATRIX_FONT, 10))
        style.map("Treeview", background=[("selected", "#003300")], foreground=[("selected", "#00FF66")])
        style.configure("Treeview.Heading", background="#001100", foreground="#00FF66", relief="flat", font=(MATRIX_FONT, 11, "bold"))
        style.map("Treeview.Heading", background=[("active", "#002200")])

    def update_strength_indicator(self):
        pw = self.entry_pass.get()
        score, status, color, entropy = generator.check_password_strength(pw)
        
        self.strength_bar.set(score)
        self.strength_bar.configure(progress_color=color)
        
        if not pw:
            self.strength_label.configure(text="EMPTY", text_color="#555555")
        else:
            self.strength_label.configure(text=f"{status}", text_color=color)

    def _build_clipboard_indicator(self):
        """Erstellt die untere Statusleiste für den Zwischenablage-Timer."""
        self.clipboard_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.clipboard_frame.pack(fill="x", padx=40, pady=(0, 15))

        self.lbl_clipboard_status = ctk.CTkLabel(
            self.clipboard_frame,
            text="",
            font=ctk.CTkFont(family=MATRIX_FONT, size=11, weight="bold"),
            text_color="#00FF66"
        )
        self.lbl_clipboard_status.pack(side="left", padx=(0, 10))

        self.progress_clipboard = ctk.CTkProgressBar(self.clipboard_frame, height=6)
        self.progress_clipboard.pack(side="left", fill="x", expand=True)
        self.progress_clipboard.set(0)

        # Standardmäßig ausblenden, bis etwas kopiert wird
        self.clipboard_frame.pack_forget()

    def show_clipboard_timer(self, item_name: str, seconds_remaining: int, total_seconds: int = 15):
        """Aktiviert die Statusanzeige und aktualisiert den Fortschritt."""
        if not self.clipboard_frame.winfo_ismapped():
            self.clipboard_frame.pack(fill="x", padx=40, pady=(0, 15))

        progress = seconds_remaining / total_seconds
        self.progress_clipboard.set(progress)
        self.lbl_clipboard_status.configure(
            text=f">_ {item_name.upper()} COPIED // AUTO_CLEAR IN: {seconds_remaining:02d}s"
        )

    def hide_clipboard_timer(self):
        """Versteckt die Statusanzeige, wenn der Timer abgelaufen ist."""
        self.clipboard_frame.pack_forget()
        self.progress_clipboard.set(0)