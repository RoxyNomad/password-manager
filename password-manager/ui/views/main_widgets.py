import customtkinter as ctk
from tkinter import ttk
from ui.theme import UI_FONT

def build_header(parent, app):
    header_frame = ctk.CTkFrame(parent, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(15, 10))

    title = ctk.CTkLabel(
        header_frame, 
        text="Password Vault", 
        font=ctk.CTkFont(family=UI_FONT, size=22, weight="bold"),
        text_color="#F3F4F6"
    )
    title.pack(side="left")

    ctk.CTkButton(
        header_frame, 
        text="Lock Vault", 
        command=app.auth.lock_vault, 
        width=90, 
        height=32, 
        fg_color="#DC2626", 
        hover_color="#B91C1C"
    ).pack(side="right", padx=(5, 0))

    ctk.CTkButton(
        header_frame, 
        text="Change Master Key", 
        command=app.dialogs.open_change_master_dialog, 
        width=140, 
        height=32, 
        fg_color="#D97706", 
        hover_color="#B45309"
    ).pack(side="right", padx=5)

    ctk.CTkButton(
        header_frame, 
        text="Audit", 
        command=app.dialogs.open_audit_dialog, 
        width=80, 
        height=32, 
        fg_color="#374151", 
        hover_color="#4B5563"
    ).pack(side="right", padx=5)

    ctk.CTkButton(
        header_frame, 
        text="Export CSV", 
        command=app.io_handler.export_vault_to_csv, 
        width=100, 
        height=32,
        fg_color="#374151", 
        hover_color="#4B5563"
    ).pack(side="right", padx=5)

    ctk.CTkButton(
        header_frame, 
        text="Import CSV", 
        command=app.io_handler.import_vault_from_csv, 
        width=100, 
        height=32,
        fg_color="#374151", 
        hover_color="#4B5563"
    ).pack(side="right", padx=5)

def build_search_and_filter(parent, app):
    filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
    filter_frame.pack(fill="x", padx=20, pady=5)

    entry_search = ctk.CTkEntry(
        filter_frame, 
        placeholder_text="Search target or identity...", 
        width=280,
        height=36
    )
    entry_search.pack(side="left", padx=(0, 10))
    entry_search.bind("<KeyRelease>", lambda e: app.entry_handler.load_entries())

    filter_category = ctk.CTkOptionMenu(
        filter_frame, 
        values=["ALL", "Work", "Personal", "Finance", "Social", "Other"],
        command=lambda v: app.entry_handler.load_entries(),
        height=36
    )
    filter_category.set("ALL")
    filter_category.pack(side="left", padx=5)

    fav_only_var = ctk.BooleanVar(value=False)
    chk_fav_only = ctk.CTkCheckBox(
        filter_frame, 
        text="Favorites Only", 
        variable=fav_only_var,
        command=app.entry_handler.load_entries
    )
    chk_fav_only.pack(side="left", padx=15)

    chk_show_pass = ctk.CTkCheckBox(
        filter_frame, 
        text="Show Passwords", 
        command=app.toggle_password_visibility
    )
    chk_show_pass.pack(side="right")

    return entry_search, filter_category, fav_only_var

def build_treeview(parent, on_double_click, on_copy_pw, on_copy_user):
    tree_frame = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=10, border_color="#1F2937", border_width=1)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("ID", "FAV", "CATEGORY", "TARGET_URI", "IDENTITY", "DECRYPTED_SECRET", "TOTP_CODE")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("ID", text="ID")
    tree.heading("FAV", text="★")
    tree.heading("CATEGORY", text="Category")
    tree.heading("TARGET_URI", text="Target / URI")
    tree.heading("IDENTITY", text="Identity / User")
    tree.heading("DECRYPTED_SECRET", text="Secret")
    tree.heading("TOTP_CODE", text="2FA Code")

    tree.column("ID", width=40, anchor="center")
    tree.column("FAV", width=40, anchor="center")
    tree.column("CATEGORY", width=110, anchor="center")
    tree.column("TARGET_URI", width=200, anchor="w")
    tree.column("IDENTITY", width=180, anchor="w")
    tree.column("DECRYPTED_SECRET", width=180, anchor="w")
    tree.column("TOTP_CODE", width=100, anchor="center")

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
    scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)

    tree.bind("<Double-1>", on_double_click)
    tree.bind("<Control-c>", lambda e: on_copy_pw())
    tree.bind("<Control-u>", lambda e: on_copy_user())

    return tree

def build_form(parent, app):
    form_frame = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=10, border_color="#1F2937", border_width=1)
    form_frame.pack(fill="x", padx=20, pady=(5, 10), ipady=5)

    form_frame.grid_columnconfigure(0, weight=2)
    form_frame.grid_columnconfigure(1, weight=2)
    form_frame.grid_columnconfigure(2, weight=2)
    form_frame.grid_columnconfigure(3, weight=1)
    form_frame.grid_columnconfigure(4, weight=1)

    # Row 0
    entry_link = ctk.CTkEntry(form_frame, placeholder_text="Target URI (e.g. github.com)", height=36)
    entry_link.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

    entry_user = ctk.CTkEntry(form_frame, placeholder_text="Identity / Username", height=36)
    entry_user.grid(row=0, column=1, sticky="ew", padx=5, pady=10)

    entry_pass = ctk.CTkEntry(form_frame, placeholder_text="Password", show="•", height=36)
    entry_pass.grid(row=0, column=2, sticky="ew", padx=5, pady=10)

    opt_category = ctk.CTkOptionMenu(form_frame, values=["Work", "Personal", "Finance", "Social", "Other"], height=36)
    opt_category.set("Other")
    opt_category.grid(row=0, column=3, columnspan=2, sticky="ew", padx=10, pady=10)

    # Row 1
    entry_totp = ctk.CTkEntry(form_frame, placeholder_text="TOTP Secret (Optional)", height=36)
    entry_totp.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

    ctk.CTkButton(
        form_frame, 
        text="Scan QR", 
        command=app.io_handler.scan_and_fill_qr_code, 
        height=36,
        fg_color="#374151",
        hover_color="#4B5563"
    ).grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 10))

    ctk.CTkButton(
        form_frame, 
        text="Generate", 
        command=app.entry_handler.generate_and_set_password, 
        height=36,
        fg_color="#374151",
        hover_color="#4B5563"
    ).grid(row=1, column=2, sticky="ew", padx=5, pady=(0, 10))

    chk_favorite = ctk.CTkCheckBox(form_frame, text="Favorite")
    chk_favorite.grid(row=1, column=3, sticky="w", padx=10, pady=(0, 10))

    btn_save = ctk.CTkButton(
        form_frame, 
        text="Save Entry", 
        command=app.entry_handler.save_entry, 
        height=36,
        font=ctk.CTkFont(family=UI_FONT, size=13, weight="bold")
    )
    btn_save.grid(row=1, column=4, sticky="ew", padx=10, pady=(0, 10))

    return {
        "link": entry_link,
        "user": entry_user,
        "pass": entry_pass,
        "totp": entry_totp,
        "category": opt_category,
        "favorite": chk_favorite,
        "btn_save": btn_save
    }

def build_status_bar(parent):
    status_bar = ctk.CTkLabel(
        parent, 
        text="System Ready • Vault Decrypted", 
        font=ctk.CTkFont(family=UI_FONT, size=11), 
        text_color="#9CA3AF",
        anchor="w"
    )
    status_bar.pack(fill="x", padx=20, pady=(0, 10))
    return status_bar