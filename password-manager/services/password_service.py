import math
import re
import secrets
import string
from typing import Tuple

COMMON_WEAK_PATTERNS = [
    "123456", "password", "123456789", "qwerty", "12345678", "111111", 
    "1234567", "dragon", "pussy", "baseball", "football", "shadow", "mustang",
    "master", "admin", "welcome", "matrix", "letmein", "iloveyou"
]

class PasswordService:
    @staticmethod
    def calculate_entropy(password: str) -> float:
        if not password:
            return 0.0

        pool_size = 0
        if re.search(r"[a-z]", password):
            pool_size += 26
        if re.search(r"[A-Z]", password):
            pool_size += 26
        if re.search(r"[0-9]", password):
            pool_size += 10
        if re.search(r"[^a-zA-Z0-9]", password):
            pool_size += 32

        if pool_size == 0:
            return 0.0

        entropy = len(password) * math.log2(pool_size)
        return round(entropy, 1)

    @classmethod
    def check_password_strength(cls, password: str) -> Tuple[float, str, str, float]:
        if not password:
            return 0.0, "EMPTY", "#555555", 0.0

        pw_lower = password.lower()

        for pattern in COMMON_WEAK_PATTERNS:
            if pattern in pw_lower:
                return 0.15, "EXPOSED_PATTERN", "#FF3333", cls.calculate_entropy(password)

        if len(set(password)) < 3 and len(password) > 4:
            return 0.2, "REPETITIVE", "#FF3333", cls.calculate_entropy(password)

        entropy = cls.calculate_entropy(password)

        if entropy < 28:
            return 0.2, f"VERY_WEAK ({entropy} bits)", "#FF3333", entropy
        elif entropy < 36:
            return 0.4, f"WEAK ({entropy} bits)", "#FFAA00", entropy
        elif entropy < 60:
            return 0.65, f"MODERATE ({entropy} bits)", "#FFFF00", entropy
        elif entropy < 80:
            return 0.85, f"STRONG ({entropy} bits)", "#00FF66", entropy
        else:
            return 1.0, f"EXCELLENT ({entropy} bits)", "#00FFFF", entropy

    @staticmethod
    def generate_password(
        length: int = 16, 
        use_upper: bool = True, 
        use_digits: bool = True, 
        use_symbols: bool = True
    ) -> str:
        chars = string.ascii_lowercase
        if use_upper:
            chars += string.ascii_uppercase
        if use_digits:
            chars += string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not chars:
            chars = string.ascii_lowercase

        return "".join(secrets.choice(chars) for _ in range(length))