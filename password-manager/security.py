import hashlib
import urllib.request

from collections import Counter
import generator
import crypto

def check_password_breached(password: str) -> int:
    """
    Prüft anonym über die HaveIBeenPwned k-Anonymity API,
    ob ein Passwort in bekannten Datendiebstählen auftaucht.
    """
    sha1_pw = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1_pw[:5]
    suffix = sha1_pw[5:]
    
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Matrix-Vault-App'})
    
    try:
        with urllib.request.urlopen(req) as response:
            hashes_list = response.read().decode('utf-8').splitlines()
            for line in hashes_list:
                h, count = line.split(':')
                if h == suffix:
                    return int(count)
    except Exception:
        return -1  # Offline oder Verbindungsfehler
    return 0

def validate_master_password_policy(password: str) -> tuple[bool, str]:
    """Prüft Mindestanforderungen an das Master-Passwort."""
    if len(password) < 8:
        return False, "Master key must be at least 8 characters long!"
    return True, "OK"

def run_security_audit(entries, fernet):
    total_count = len(entries)
    if total_count == 0:
        return {
            "total": 0, "weak_count": 0, "reused_count": 0, 
            "no_2fa_count": 0, "overall_score": 100, "issues": []
        }

    decrypted_list = []
    weak_entries = []
    totp_missing_count = 0
    total_entropy_sum = 0

    for row in entries:
        entry_id = row[0]
        link = row[1] if len(row) > 1 else "Unknown"
        user = row[2] if len(row) > 2 else "Unknown"
        enc_pw = row[3] if len(row) > 3 else ""
        enc_totp = row[4] if len(row) > 4 else ""

        pw = ""
        if enc_pw:
            try:
                pw = crypto.decrypt_text(fernet, enc_pw)
            except Exception:
                pw = ""

        decrypted_list.append((entry_id, link, user, pw))

        # Passwörter auf Bit-Entropie und Schwachstellen prüfen
        score, status, _, entropy = generator.check_password_strength(pw)
        total_entropy_sum += entropy

        if score < 0.6 and pw:
            weak_entries.append({
                "id": entry_id, 
                "target": link, 
                "user": user, 
                "reason": f"{status}"
            })

        if not enc_totp:
            totp_missing_count += 1

    # Doppelte Passwörter ermitteln
    pw_counts = Counter([item[3] for item in decrypted_list if item[3]])
    reused_passwords = {pw for pw, count in pw_counts.items() if count > 1}

    reused_entries = []
    for entry_id, link, user, pw in decrypted_list:
        if pw in reused_passwords:
            reused_entries.append({
                "id": entry_id, 
                "target": link, 
                "user": user, 
                "reason": "REUSED_PASSWORD"
            })

    # Errechnung des Vault Health Scores (0 - 100%)
    avg_entropy = total_entropy_sum / total_count if total_count > 0 else 0
    # ~60 bits Entropie gilt als Zielwert für 100% Basis-Score
    base_score = min(100, int((avg_entropy / 60.0) * 100))
    
    # Abzüge für doppelte & schwache Passwörter
    weak_penalty = (len(weak_entries) / total_count) * 40
    duplicate_penalty = (len(reused_entries) / total_count) * 40
    
    overall_score = max(0, min(100, int(base_score - weak_penalty - duplicate_penalty)))

    # Issues zusammenführen
    issues_dict = {}
    for item in weak_entries + reused_entries:
        eid = item["id"]
        if eid not in issues_dict:
            issues_dict[eid] = item
        else:
            issues_dict[eid]["reason"] += " + " + item["reason"]

    return {
        "total": total_count,
        "weak_count": len(weak_entries),
        "reused_count": len(reused_entries),
        "no_2fa_count": totp_missing_count,
        "overall_score": overall_score,
        "issues": list(issues_dict.values())
    }