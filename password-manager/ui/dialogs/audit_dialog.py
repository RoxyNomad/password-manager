# ui/dialogs/audit_dialog.py
import customtkinter as ctk
from tkinter import ttk
from ui.theme import UI_FONT  # Verwendet die neue Standard-Schriftart

class SecurityAuditDialog(ctk.CTkToplevel):
    def __init__(self, parent, audit_data):
        super().__init__(parent, fg_color="#0B0F17")
        self.title("Security Audit Report")
        self.geometry("640x540")
        self.resizable(False, False)

        # Modales Fenster-Setup
        self.transient(parent)
        self.grab_set()

        # Score-Farbe dynamisch ermitteln (Emerald / Amber / Red)
        score = audit_data.get("overall_score", 100)
        if score >= 80:
            score_color = "#10B981"
        elif score >= 50:
            score_color = "#F59E0B"
        else:
            score_color = "#EF4444"

        # Hauptcontainer mit modernem Padding
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Header
        header = ctk.CTkFrame(main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        lbl_title = ctk.CTkLabel(
            header, 
            text="Security Audit Report", 
            font=ctk.CTkFont(family=UI_FONT, size=20, weight="bold"), 
            text_color="#F3F4F6"
        )
        lbl_title.pack(side="left")

        # 2. Score Card
        score_frame = ctk.CTkFrame(
            main_container, 
            corner_radius=10, 
            fg_color="#111827", 
            border_width=1, 
            border_color="#1F2937"
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

        # 3. Quick Stats Grid
        stats_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 15))
        stats_frame.columnconfigure((0, 1, 2), weight=1)

        weak_cnt = audit_data.get("weak_count", 0)
        reused_cnt = audit_data.get("reused_count", 0)

        self._create_stat_box(stats_frame, 0, "Total Passwords", str(audit_data.get("total", 0)), "#F3F4F6")
        self._create_stat_box(stats_frame, 1, "Weak Passwords", str(weak_cnt), "#EF4444" if weak_cnt > 0 else "#10B981")
        self._create_stat_box(stats_frame, 2, "Reused Passwords", str(reused_cnt), "#F59E0B" if reused_cnt > 0 else "#10B981")

        # 4. Table Header Label
        ctk.CTkLabel(
            main_container, 
            text="Attention Required Entries", 
            font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"), 
            text_color="#9CA3AF"
        ).pack(anchor="w", pady=(0, 6))

        # 5. Issues Treeview Table Container
        table_frame = ctk.CTkFrame(
            main_container, 
            corner_radius=10, 
            fg_color="#111827", 
            border_width=1, 
            border_color="#1F2937"
        )
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Treeview Style lokal überschreiben
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

        for issue in audit_data.get("issues", []):
            tree.insert("", "end", values=(issue["id"], issue["target"], issue["user"], issue["reason"]))

        # Schließen Button
        ctk.CTkButton(
            main_container,
            text="Close Report",
            command=self.destroy,
            width=120,
            height=34,
            fg_color="#374151",
            hover_color="#4B5563",
            font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold")
        ).pack(anchor="e")

        self.update_idletasks()

    def _create_stat_box(self, parent, col, title, val, color):
        box = ctk.CTkFrame(
            parent, 
            corner_radius=8, 
            fg_color="#111827", 
            border_width=1, 
            border_color="#1F2937"
        )
        box.grid(row=0, column=col, padx=4, sticky="ew")
        
        ctk.CTkLabel(
            box, 
            text=title, 
            font=ctk.CTkFont(family=UI_FONT, size=11, weight="bold"), 
            text_color="#9CA3AF"
        ).pack(pady=(10, 2))
        
        ctk.CTkLabel(
            box, 
            text=val, 
            font=ctk.CTkFont(family=UI_FONT, size=20, weight="bold"), 
            text_color=color
        ).pack(pady=(0, 10))