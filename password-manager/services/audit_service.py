import hashlib
import urllib.request
from collections import Counter
from typing import Any, Dict, List, Tuple
from cryptography.fernet import Fernet

from .security_service import SecurityService
from .password_service import PasswordService


class AuditService:
    @staticmethod
    def check_password_breached(password: str) -> int:
        if not password:
            return 0

        sha1_pw = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix = sha1_pw[:5]
        suffix = sha1_pw[5:]

        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Matrix-Vault-App"}
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                hashes_list = response.read().decode("utf-8").splitlines()
                for line in hashes_list:
                    h, count = line.split(":")
                    if h == suffix:
                        return int(count)
        except Exception:
            return -1

        return 0

    @classmethod
    def run_security_audit(
        cls, entries: List[Any], fernet: Fernet
    ) -> Dict[str, Any]:
        total_count = len(entries)
        if total_count == 0:
            return {
                "total": 0,
                "weak_count": 0,
                "reused_count": 0,
                "no_2fa_count": 0,
                "overall_score": 100,
                "issues": [],
            }

        decrypted_list: List[Tuple[Any, str, str, str]] = []
        weak_entries: List[Dict[str, Any]] = []
        totp_missing_count = 0
        total_entropy_sum = 0.0

        for row in entries:
            if hasattr(row, "keys"):
                entry_id = row["id"] if "id" in row.keys() else row[0]
                link = row["link"] if "link" in row.keys() else (row["url"] if "url" in row.keys() else "Unknown")
                user = row["user"] if "user" in row.keys() else (row["username"] if "username" in row.keys() else "Unknown")
                enc_pw = row["pw"] if "pw" in row.keys() else (row["password"] if "password" in row.keys() else "")
                enc_totp = row["totp"] if "totp" in row.keys() else ""
            else:
                entry_id = row[0]
                link = row[1] if len(row) > 1 else "Unknown"
                user = row[2] if len(row) > 2 else "Unknown"
                enc_pw = row[3] if len(row) > 3 else ""
                enc_totp = row[4] if len(row) > 4 else ""

            pw = ""
            if enc_pw:
                try:
                    pw = SecurityService.decrypt_text(fernet, enc_pw)
                except Exception:
                    pw = ""

            decrypted_list.append((entry_id, link, user, pw))

            score, status, _, entropy = PasswordService.check_password_strength(pw)
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

        pw_counts = Counter([item[3] for item in decrypted_list if item[3]])
        reused_passwords = {
            pw for pw, count in pw_counts.items() if count > 1
        }

        reused_entries: List[Dict[str, Any]] = []
        for entry_id, link, user, pw in decrypted_list:
            if pw in reused_passwords:
                reused_entries.append(
                    {
                        "id": entry_id,
                        "target": link,
                        "user": user,
                        "reason": "REUSED_PASSWORD",
                    }
                )

        avg_entropy = (
            total_entropy_sum / total_count if total_count > 0 else 0.0
        )
        base_score = min(100, int((avg_entropy / 60.0) * 100))

        weak_penalty = (len(weak_entries) / total_count) * 40
        duplicate_penalty = (len(reused_entries) / total_count) * 40

        overall_score = max(
            0, min(100, int(base_score - weak_penalty - duplicate_penalty))
        )

        issues_dict: Dict[Any, Dict[str, Any]] = {}
        for item in weak_entries + reused_entries:
            eid = item["id"]
            if eid not in issues_dict:
                issues_dict[eid] = item.copy()
            else:
                issues_dict[eid]["reason"] += " + " + item["reason"]

        return {
            "total": total_count,
            "weak_count": len(weak_entries),
            "reused_count": len(reused_entries),
            "no_2fa_count": totp_missing_count,
            "overall_score": overall_score,
            "issues": list(issues_dict.values()),
        }