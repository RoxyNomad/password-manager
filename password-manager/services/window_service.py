import sys

class WindowService:
    @staticmethod
    def maximize(root):
        try:
            if sys.platform.startswith("win"):
                root.wm_state('zoomed')
            else:
                root.attributes('-zoomed', True)
        except Exception:
            root.attributes('-fullscreen', True)