# In generator.py
import math
import random
import string
import re

# Liste der häufigsten schwachen Passwörter / Muster
COMMON_WEAK_PATTERNS = [
    "123456", "password", "123456789", "qwerty", "12345678", "111111", 
    "1234567", "dragon", "pussy", "baseball", "football", "shadow", "mustang",
    "master", "admin", "welcome", "matrix", "letmein", "iloveyou"
]

def calculate_entropy(password: str) -> float:
    """Berechnet die Shannon-Entropie des Passworts in Bits."""
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

    # Bit-Entropie Formula: E = L * log2(R)
    entropy = len(password) * math.log2(pool_size)
    return round(entropy, 1)

def check_password_strength(password: str):
    """
    Überprüft die Passwortstärke basierend auf Entropie und bekannten Schwachstellen.
    Rückgabe: (score_normalized [0.0 - 1.0], status_text, color_code, entropy_bits)
    """
    if not password:
        return 0.0, "EMPTY", "#555555", 0.0

    pw_lower = password.lower()

    # 1. Prüfe auf extrem häufige schwache Passwörter / Muster
    for pattern in COMMON_WEAK_PATTERNS:
        if pattern in pw_lower:
            return 0.15, "EXPOSED_PATTERN", "#FF3333", calculate_entropy(password)

    # 2. Prüfe auf wiederholende Zeichen (z.B. "aaaaa")
    if len(set(password)) < 3 and len(password) > 4:
        return 0.2, "REPETITIVE", "#FF3333", calculate_entropy(password)

    entropy = calculate_entropy(password)

    # Entropie-Klassifizierung nach NIST:
    # < 28 bits  = Sehr schwach (Very Weak)
    # 28-35 bits = Schwach (Weak)
    # 36-59 bits = Mittel (Moderate)
    # 60-79 bits = Strak (Strong)
    # 80+ bits   = Unknackbar (Excellent)

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

def generate_password(length=16, use_upper=True, use_digits=True, use_symbols=True) -> str:
    """Generiert ein zufälliges, hoch-entropisches Passwort."""
    chars = string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if not chars:
        chars = string.ascii_lowercase

    return "".join(random.choice(chars) for _ in range(length))