import customtkinter as ctk
from ui.theme import UI_FONT
from services import SecurityService
from ui.dialogs.audit_widgets import create_score_card, create_stat_box, setup_audit_treeview

class SecurityAuditDialog(ctk.CTkToplevel):
    def __init__(self, parent, audit_data, fernet=None):
        super().__init__(parent, fg_color="#0B0F17")
        self.title("Security Audit Report")
        self.geometry("640x540")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        service = SecurityService(fernet)
        score = audit_data.get("overall_score", 100)
        score_color = service.get_score_color(score)

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_header(main_container)
        create_score_card(main_container, score, score_color)

        self._build_stats(main_container, audit_data, service)

        ctk.CTkLabel(
            main_container,
            text="Attention Required Entries",
            font=ctk.CTkFont(family=UI_FONT, size=12, weight="bold"),
            text_color="#9CA3AF"
        ).pack(anchor="w", pady=(0, 6))

        table_frame = ctk.CTkFrame(
            main_container, corner_radius=10, fg_color="#111827", border_width=1, border_color="#1F2937"
        )
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        tree = setup_audit_treeview(table_frame)
        for issue in audit_data.get("issues", []):
            tree.insert("", "end", values=(issue["id"], issue["target"], issue["user"], issue["reason"]))

        # 4. Close Button
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

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            header,
            text="Security Audit Report",
            font=ctk.CTkFont(family=UI_FONT, size=20, weight="bold"),
            text_color="#F3F4F6"
        ).pack(side="left")

    def _build_stats(self, parent, audit_data, service):
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 15))
        stats_frame.columnconfigure((0, 1, 2), weight=1)

        weak_cnt = audit_data.get("weak_count", 0)
        reused_cnt = audit_data.get("reused_count", 0)

        create_stat_box(stats_frame, 0, "Total Passwords", str(audit_data.get("total", 0)), "#F3F4F6")
        create_stat_box(stats_frame, 1, "Weak Passwords", str(weak_cnt), service.get_stat_color(weak_cnt))
        create_stat_box(stats_frame, 2, "Reused Passwords", str(reused_cnt), service.get_stat_color(reused_cnt))