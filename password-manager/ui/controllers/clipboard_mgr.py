import database
import crypto

CLIPBOARD_TIMEOUT_SEC = 15

class ClipboardManager:
    def __init__(self, app):
        self.app = app

    def copy_username(self):
        v = self.app.current_view
        selected = v.tree.selection()
        if selected:
            user = v.tree.item(selected[0], "values")[4]
            self.set_clipboard(user, "IDENTITY")

    def copy_password(self):
        v = self.app.current_view
        selected = v.tree.selection()
        if selected:
            entry_id = v.tree.item(selected[0], "values")[0]
            for row in database.get_all_entries():
                if str(row[0]) == str(entry_id):
                    pw = crypto.decrypt_text(self.app.fernet, row[3])
                    self.set_clipboard(pw, "PASSWORD")
                    break

    def copy_totp(self):
        v = self.app.current_view
        selected = v.tree.selection()
        if selected:
            code = v.tree.item(selected[0], "values")[6]
            if code not in ["---", "INVALID"]:
                self.set_clipboard(code, "2FA CODE")

    # Weiterleitung für den EntryHandler
    def copy_to_clipboard(self, text: str, label: str):
        self.set_clipboard(text, label)

    def set_clipboard(self, text: str, label: str):
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
        self.app.root.update()
        self.start_autoclear(label)

    def start_autoclear(self, label: str):
        if hasattr(self.app, 'clipboard_timer') and self.app.clipboard_timer:
            self.app.root.after_cancel(self.app.clipboard_timer)
        self.app.clipboard_seconds_left = CLIPBOARD_TIMEOUT_SEC
        self._tick(label)

    def _tick(self, label: str):
        v = self.app.current_view
        if self.app.clipboard_seconds_left > 0:
            if hasattr(v, 'show_clipboard_timer'):
                v.show_clipboard_timer(label, self.app.clipboard_seconds_left, CLIPBOARD_TIMEOUT_SEC)
            self.app.clipboard_seconds_left -= 1
            self.app.clipboard_timer = self.app.root.after(1000, lambda: self._tick(label))
        else:
            self.clear_clipboard()

    def clear_clipboard(self):
        try:
            self.app.root.clipboard_clear()
        except Exception:
            pass
        if hasattr(self.app, 'current_view') and hasattr(self.app.current_view, 'hide_clipboard_timer'):
            self.app.current_view.hide_clipboard_timer()
        self.app.clipboard_timer = None