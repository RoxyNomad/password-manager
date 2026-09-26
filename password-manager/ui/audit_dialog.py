import customtkinter as ctk
from tkinter import ttk
from ui.theme import MATRIX_FONT

class SecurityAuditDialog(ctk.CTkToplevel):
    def __init__(self, parent, audit_data):
        super().__init__(parent, fg_color="#050505")
        self.title("SECURITY_AUDIT // SYSTEM_HEALTH")
        self.geometry("620x520")
        self.resizable(False, False)

        # Modales Fenster-Setup
        self.transient(parent)
        self.grab_set()

        # Dunklen Matrix-Hintergrund erzwingen
        self.configure(fg_color="#050505")

        score = audit_data.get("overall_score", 100)
        score_color = "#00FF66" if score >= 80 else ("#FFAA00" if score >= 50 else "#FF3333")

        # Container Frame als Basis für alle Widgets
        main_container = ctk.CTkFrame(self, fg_color="#050505", corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # 1. Header
        header = ctk.CTkFrame(main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        lbl_title = ctk.CTkLabel(
            header, 
            text=">_ SECURITY_AUDIT_REPORT", 
            font=ctk.CTkFont(family=MATRIX_FONT, size=18, weight="bold"), 
            text_color="#00FF66"
        )
        lbl_title.pack(side="left")

        # 2. Score Card
        score_frame = ctk.CTkFrame(main_container, corner_radius=8, fg_color="#0A0A0A", border_width=1, border_color="#00FF66")
        score_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            score_frame, 
            text="VAULT_HEALTH_SCORE:", 
            font=ctk.CTkFont(family=MATRIX_FONT, size=13, weight="bold"), 
            text_color="#00FF66"
        ).pack(side="left", padx=15, pady=12)
        
        ctk.CTkLabel(
            score_frame, 
            text=f"{score}%", 
            font=ctk.CTkFont(family=MATRIX_FONT, size=26, weight="bold"), 
            text_color=score_color
        ).pack(side="right", padx=15, pady=8)

        # 3. Quick Stats Grid
        stats_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)
        stats_frame.columnconfigure((0, 1, 2), weight=1)

        self._create_stat_box(stats_frame, 0, "TOTAL_KEYS", str(audit_data.get("total", 0)), "#00FF66")
        self._create_stat_box(stats_frame, 1, "WEAK_KEYS", str(audit_data.get("weak_count", 0)), "#FF3333" if audit_data.get("weak_count", 0) > 0 else "#00FF66")
        self._create_stat_box(stats_frame, 2, "REUSED_KEYS", str(audit_data.get("reused_count", 0)), "#FF9900" if audit_data.get("reused_count", 0) > 0 else "#00FF66")

        # 4. Table Header Label
        ctk.CTkLabel(
            main_container, 
            text="ATTENTION_REQUIRED_ENTRIES:", 
            font=ctk.CTkFont(family=MATRIX_FONT, size=11, weight="bold"), 
            text_color="#00FF66"
        ).pack(anchor="w", pady=(10, 2))

        # 5. Issues Treeview Table
        table_frame = ctk.CTkFrame(main_container, corner_radius=8, fg_color="#0A0A0A", border_width=1, border_color="#330000")
        table_frame.pack(fill="both", expand=True, pady=(0, 5))

        tree = ttk.Treeview(table_frame, columns=("ID", "Target", "User", "Issue"), show="headings", height=6)
        tree.heading("ID", text="ID")
        tree.heading("Target", text="TARGET_URI")
        tree.heading("User", text="IDENTITY")
        tree.heading("Issue", text="VULNERABILITY")

        tree.column("ID", width=35, anchor="center")
        tree.column("Target", width=130)
        tree.column("User", width=140)
        tree.column("Issue", width=190)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Audit.Treeview", 
            background="#0A0A0A", 
            foreground="#FF5555", 
            fieldbackground="#0A0A0A", 
            rowheight=24, 
            font=(MATRIX_FONT, 9)
        )
        style.configure(
            "Audit.Treeview.Heading", 
            background="#150000", 
            foreground="#FF5555", 
            font=(MATRIX_FONT, 9, "bold")
        )
        tree.configure(style="Audit.Treeview")

        for issue in audit_data.get("issues", []):
            tree.insert("", "end", values=(issue["id"], issue["target"], issue["user"], issue["reason"]))

        tree.pack(fill="both", expand=True, padx=5, pady=5)

        # WICHTIG: Erzwingt sofortiges Rendering aller Widgets im Toplevel
        self.update_idletasks()

    def _create_stat_box(self, parent, col, title, val, color):
        box = ctk.CTkFrame(parent, corner_radius=6, fg_color="#0A0A0A", border_width=1, border_color="#003300")
        box.grid(row=0, column=col, padx=4, sticky="ew")
        
        ctk.CTkLabel(
            box, 
            text=title, 
            font=ctk.CTkFont(family=MATRIX_FONT, size=9, weight="bold"), 
            text_color="#00FF66"
        ).pack(pady=(6, 2))
        
        ctk.CTkLabel(
            box, 
            text=val, 
            font=ctk.CTkFont(family=MATRIX_FONT, size=18, weight="bold"), 
            text_color=color
        ).pack(pady=(0, 6))