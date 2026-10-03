import sqlite3

DB_NAME = "vault.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
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

def add_entry(link, user, pw, totp="", category="Other", is_fav=0) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entries (link, user, pw, totp, category, is_fav) VALUES (?, ?, ?, ?, ?, ?)",
        (link, user, pw, totp, category, is_fav)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE entries SET is_fav = CASE WHEN is_fav = 1 THEN 0 ELSE 1 END WHERE id = ?", (int(entry_id),))
    conn.commit()
    conn.close()

def get_entry_by_id(entry_id: int):
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

def delete_entry(entry_id) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = ?", (int(entry_id),))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()
    return deleted_rows