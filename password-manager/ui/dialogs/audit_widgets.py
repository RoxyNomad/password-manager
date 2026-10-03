import customtkinter as ctk
from tkinter import ttk
from ui.theme import UI_FONT

def create_score_card(parent, score: int, score_color: str):
    score_frame = ctk.CTkFrame(
        parent, corner_radius=10, fg_color="#111827", border_width=1, border_color="#1F2937"
    )
    score_frame.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(
        score_frame,
        text="Vault Health Score",
        font=ctk.CTkFont(family=UI_FONT, size=14, weight="bold"),
        text_color="#9CA3AF"
    ).pack(side="left", padx=20, pady=16)

    ctk.CTkLabel(
        score_frame,
        text=f"{score}%",
        font=ctk.CTkFont(family=UI_FONT, size=28, weight="bold"),
        text_color=score_color
    ).pack(side="right", padx=20, pady=10)


def create_stat_box(parent, col: int, title: str, val: str, color: str):
    box = ctk.CTkFrame(
        parent, corner_radius=8, fg_color="#111827", border_width=1, border_color="#1F2937"
    )
    box.grid(row=0, column=col, padx=4, sticky="ew")

    ctk.CTkLabel(
        box, text=title,
        font=ctk.CTkFont(family=UI_FONT, size=11, weight="bold"),
        text_color="#9CA3AF"
    ).pack(pady=(10, 2))

    ctk.CTkLabel(
        box, text=val,
        font=ctk.CTkFont(family=UI_FONT, size=20, weight="bold"),
        text_color=color
    ).pack(pady=(0, 10))


def setup_audit_treeview(table_frame) -> ttk.Treeview:
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Audit.Treeview",
        background="#111827",
        foreground="#F9FAFB",
        fieldbackground="#111827",
        rowheight=30,
        borderwidth=0,
        font=(UI_FONT, 10)
    )
    style.configure(
        "Audit.Treeview.Heading",
        background="#1F2937",
        foreground="#9CA3AF",
        relief="flat",
        font=(UI_FONT, 10, "bold")
    )
    style.map(
        "Audit.Treeview",
        background=[("selected", "#374151")],
        foreground=[("selected", "#FFFFFF")]
    )

    tree = ttk.Treeview(
        table_frame,
        columns=("ID", "Target", "User", "Issue"),
        show="headings",
        style="Audit.Treeview"
    )
    tree.heading("ID", text="ID")
    tree.heading("Target", text="Target / URI")
    tree.heading("User", text="Identity")
    tree.heading("Issue", text="Vulnerability")

    tree.column("ID", width=40, anchor="center")
    tree.column("Target", width=140, anchor="w")
    tree.column("User", width=150, anchor="w")
    tree.column("Issue", width=210, anchor="w")

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
    scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)

    return tree