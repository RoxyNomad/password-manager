from services import ClipboardService, CLIPBOARD_TIMEOUT_SEC

class ClipboardManager:
    def __init__(self, app):
        self.app = app

    @property
    def service(self):
        return ClipboardService(self.app.fernet)

    def copy_username(self):
        v = self.app.current_view
        if not hasattr(v, 'tree'):
            return
        selected = v.tree.selection()
        if selected:
            user = v.tree.item(selected[0], "values")[4]
            self.set_clipboard(user, "IDENTITY")

    def copy_password(self):
        v = self.app.current_view
        if not hasattr(v, 'tree'):
            return
        selected = v.tree.selection()
        if selected:
            entry_id = v.tree.item(selected[0], "values")[0]
            pw = self.service.get_decrypted_password(entry_id)
            if pw:
                self.set_clipboard(pw, "PASSWORD")

    def copy_totp(self):
        v = self.app.current_view
        if not hasattr(v, 'tree'):
            return
        selected = v.tree.selection()
        if selected:
            code = v.tree.item(selected[0], "values")[6]
            if code not in ["---", "INVALID"]:
                self.set_clipboard(code, "2FA CODE")

    def copy_to_clipboard(self, text: str, label: str):
        self.set_clipboard(text, label)

    def set_clipboard(self, text: str, label: str):
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
        self.app.root.update()
        self.start_autoclear(label)

    def start_autoclear(self, label: str):
        if getattr(self.app, 'clipboard_timer', None):
            self.app.root.after_cancel(self.app.clipboard_timer)
        self.app.clipboard_seconds_left = CLIPBOARD_TIMEOUT_SEC
        self._tick(label)

    def _tick(self, label: str):
        v = getattr(self.app, 'current_view', None)
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

        v = getattr(self.app, 'current_view', None)
        if hasattr(v, 'hide_clipboard_timer'):
            v.hide_clipboard_timer()

        self.app.clipboard_timer = None