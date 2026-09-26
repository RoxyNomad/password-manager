from PIL import Image
from pyzbar.pyzbar import decode
import urllib.parse

def scan_qr_from_file(file_path: str) -> str:
    """
    Liest ein Bild ein, dekodiert den enthaltenen QR-Code
    und extrahiert den TOTP-Secret-Key.
    """
    img = Image.open(file_path)
    decoded_objects = decode(img)

    if not decoded_objects:
        raise ValueError("Kein gültiger QR-Code im Bild gefunden.")

    qr_data = decoded_objects[0].data.decode('utf-8')

    # Falls es ein otpauth:// Link ist (z.B. otpauth://totp/Service:User?secret=JBSWY3DPEHPK3PXP)
    if qr_data.startswith("otpauth://"):
        parsed = urllib.parse.urlparse(qr_data)
        params = urllib.parse.parse_qs(parsed.query)
        if "secret" in params:
            return params["secret"][0]

    return qr_data