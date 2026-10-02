# database.py
import sqlite3
import shutil
import csv

DB_NAME = "vault.db"

def get_connection():
    """Erstellt eine Verbindung zur SQLite-Datenbank."""
    conn = sqlite3.connect(DB_NAME)
    # Ermöglicht den Zugriff auf Spalten per Name (z.B. row['id'])
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """Initialisiert die Datenbank-Tabelle, falls sie nicht existiert."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT NOT NULL,
            user TEXT,
            pw TEXT NOT NULL,
            totp TEXT,
            category TEXT DEFAULT 'Other',
            is_fav INTEGER DEFAULT 0
        )
    """)
    
    # Spalten für ältere DB-Versionen sicherstellen
    for col_def in [
        ("totp", "TEXT DEFAULT ''"),
        ("category", "TEXT DEFAULT 'Other'"),
        ("is_fav", "INTEGER DEFAULT 0")
    ]:
        try:
            cursor.execute(f"ALTER TABLE entries ADD COLUMN {col_def[0]} {col_def[1]}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

def add_entry(link, user, pw, totp="", category="Other", is_fav=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entries (link, user, pw, totp, category, is_fav) VALUES (?, ?, ?, ?, ?, ?)",
        (link, user, pw, totp, category, is_fav)
    )
    conn.commit()
    conn.close()

def update_entry(entry_id, link, user, pw, totp="", category="Other", is_fav=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE entries SET link = ?, user = ?, pw = ?, totp = ?, category = ?, is_fav = ? WHERE id = ?",
        (link, user, pw, totp, category, is_fav, int(entry_id))
    )
    conn.commit()
    conn.close()

def toggle_favorite(entry_id):
    """Schaltet den Favoriten-Status eines Eintrags um (0 -> 1 oder 1 -> 0)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE entries SET is_fav = CASE WHEN is_fav = 1 THEN 0 ELSE 1 END WHERE id = ?", (int(entry_id),))
    conn.commit()
    conn.close()

def get_entry_by_id(entry_id: int):
    """Ruft einen einzelnen Eintrag anhand seiner ID ab."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, link, user, pw, totp, category, is_fav FROM entries WHERE id = ?", (int(entry_id),))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return (row["id"], row["link"], row["user"], row["pw"], row["totp"], row["category"], row["is_fav"])
    return None

def get_all_entries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, link, user, pw, totp, category, is_fav FROM entries ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_entry(entry_id: int):
    """Löscht einen Eintrag anhand seiner ID."""
    conn = get_connection()
    cursor = conn.cursor()
    clean_id = int(entry_id)
    cursor.execute("DELETE FROM entries WHERE id = ?", (clean_id,))
    conn.commit()
    conn.close()

def export_to_csv(file_path, entries_decrypted):
    """
    Exportiert eine Liste von bereits entschlüsselten Einträgen in eine CSV-Datei.
    Format der Spalten: Target, Identity, Password, TOTP, Category, Favorite
    """
    with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["TARGET_URI", "IDENTITY", "PASSWORD", "2FA_SECRET", "CATEGORY", "IS_FAVORITE"])
        
        for entry in entries_decrypted:
            writer.writerow([
                entry.get("link", ""),
                entry.get("user", ""),
                entry.get("pw", ""),
                entry.get("totp", ""),
                entry.get("category", "Other"),
                entry.get("is_fav", 0)
            ])

def import_from_csv(file_path):
    """
    Liest eine CSV-Datei ein und ordnet die Spalten anhand der Header-Namen dynamisch zu.
    """
    imported_data = []
    with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            if not row:
                continue

            clean_row = {str(k).strip().lower(): str(v).strip() for k, v in row.items() if k}

            link = clean_row.get("target_uri") or clean_row.get("url") or clean_row.get("link") or clean_row.get("name") or ""
            user = clean_row.get("identity") or clean_row.get("username") or clean_row.get("user") or clean_row.get("email") or ""
            pw = clean_row.get("password") or clean_row.get("pw") or clean_row.get("secret") or ""
            totp = clean_row.get("2fa_secret") or clean_row.get("totp_secret") or clean_row.get("totp") or clean_row.get("note") or ""
            category = clean_row.get("category") or "Other"
            
            try:
                is_fav = int(clean_row.get("is_favorite") or clean_row.get("is_fav") or 0)
            except ValueError:
                is_fav = 0

            if not link and user:
                link = user
                user = ""

            if link or pw:
                imported_data.append({
                    "link": link,
                    "user": user,
                    "pw": pw,
                    "totp": totp,
                    "category": category,
                    "is_fav": is_fav
                })
            
    return imported_data