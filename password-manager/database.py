import sqlite3
import shutil
import csv

DB_NAME = "vault.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            totp_secret TEXT DEFAULT '',
            category TEXT DEFAULT 'Other',
            is_favorite INTEGER DEFAULT 0
        )
    """)
    
    # Spalten für ältere DB-Versionen schrittweise nachrüsten
    for col_def in [
        ("totp_secret", "TEXT DEFAULT ''"),
        ("category", "TEXT DEFAULT 'Other'"),
        ("is_favorite", "INTEGER DEFAULT 0")
    ]:
        try:
            cursor.execute(f"ALTER TABLE entries ADD COLUMN {col_def[0]} {col_def[1]}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

def add_entry(link, username, password, totp_secret="", category="Other", is_favorite=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entries (link, username, password, totp_secret, category, is_favorite) VALUES (?, ?, ?, ?, ?, ?)",
        (link, username, password, totp_secret, category, is_favorite)
    )
    conn.commit()
    conn.close()

def update_entry(entry_id, link, username, password, totp_secret="", category="Other", is_favorite=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE entries SET link = ?, username = ?, password = ?, totp_secret = ?, category = ?, is_favorite = ? WHERE id = ?",
        (link, username, password, totp_secret, category, is_favorite, entry_id)
    )
    conn.commit()
    conn.close()

def toggle_favorite(entry_id):
    """Schaltet den Favoriten-Status eines Eintrags um (0 -> 1 oder 1 -> 0)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE entries SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def get_all_entries():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, link, username, password, totp_secret, category, is_favorite FROM entries")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_entry(entry_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def export_to_csv(file_path, entries_decrypted):
    """
    Exportiert eine Liste von bereits entschlüsselten Einträgen in eine CSV-Datei.
    Format der Spalten: Target, Identity, Password, TOTP, Category, Favorite
    """
    with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        # Header-Zeile schreiben
        writer.writerow(["TARGET_URI", "IDENTITY", "PASSWORD", "2FA_SECRET", "CATEGORY", "IS_FAVORITE"])
        
        for entry in entries_decrypted:
            writer.writerow([
                entry["link"],
                entry["user"],
                entry["pw"],
                entry["totp"],
                entry["category"],
                entry["is_fav"]
            ])

def import_from_csv(file_path):
    """
    Liest eine CSV-Datei ein und gibt eine Liste von Wörterbüchern zurück.
    Gibt leere Listen zurück, wenn das Format ungültig ist.
    """
    imported_data = []
    with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, None)  # Header überspringen
        
        for row in reader:
            if not row or len(row) < 3:
                continue  # Ungültige Zeilen überspringen
                
            link = row[0].strip()
            user = row[1].strip()
            pw = row[2].strip()
            totp = row[3].strip() if len(row) > 3 else ""
            category = row[4].strip() if len(row) > 4 else "Other"
            try:
                is_fav = int(row[5].strip()) if len(row) > 5 else 0
            except ValueError:
                is_fav = 0
                
            imported_data.append({
                "link": link,
                "user": user,
                "pw": pw,
                "totp": totp,
                "category": category,
                "is_fav": is_fav
            })
            
    return imported_data