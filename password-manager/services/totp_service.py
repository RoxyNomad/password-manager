import pyotp
from .security_service import SecurityService

class TotpService:
    @staticmethod
    def generate(fernet, enc_totp_secret: str) -> str:
        if not enc_totp_secret or not fernet:
            return "---"
        try:
            secret = SecurityService.decrypt_text(fernet, enc_totp_secret).strip()
            return pyotp.TOTP(secret).now() if secret else "---"
        except Exception:
            return "INVALID"