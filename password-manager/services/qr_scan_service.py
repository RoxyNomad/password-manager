import urllib.parse
from typing import Optional
from PIL import Image
from pyzbar.pyzbar import decode

class QRScanService:
    @staticmethod
    def extract_secret_from_qr_data(qr_data: str) -> str:
        if qr_data.startswith("otpauth://"):
            parsed = urllib.parse.urlparse(qr_data)
            params = urllib.parse.parse_qs(parsed.query)
            
            for key, values in params.items():
                if key.lower() == "secret" and values:
                    return values[0]
                    
        return qr_data

    @classmethod
    def scan_qr_from_file(cls, file_path: str) -> str:
        try:
            img = Image.open(file_path)
        except Exception as e:
            raise FileNotFoundError(f"Bild konnte nicht geladen werden: {e}")

        decoded_objects = decode(img)

        if not decoded_objects:
            raise ValueError("Kein gültiger QR-Code im Bild gefunden.")

        qr_data = decoded_objects[0].data.decode("utf-8")

        return cls.extract_secret_from_qr_data(qr_data)