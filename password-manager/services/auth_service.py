import time
from cryptography.fernet import Fernet
from .security_service import SecurityService

INACTIVITY_TIMEOUT_SEC = 60

class AuthService:
    def create_fernet_session(self, master_pw: str, salt: bytes) -> Fernet:
        key = SecurityService.derive_key(master_pw, salt)
        return Fernet(key)

    def is_session_expired(self, last_activity_time: float) -> bool:
        return (time.time() - last_activity_time) >= INACTIVITY_TIMEOUT_SEC

    @staticmethod
    def validate_login_input(password: str) -> tuple[bool, str]:
        cleaned_pw = password.strip() if password else ""
        
        if not cleaned_pw:
            return False, "Master password is required!"
            
        return True, ""