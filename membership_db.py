import sqlite3

DB_NAME = "members.db"

# Membuat database dan tabel jika belum ada
def create_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            is_paid BOOLEAN DEFAULT 0,
            payment_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Fungsi untuk memeriksa apakah user sudah membayar
def is_member(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM members WHERE user_id = ? AND is_paid = 1', (user_id,))
    member = c.fetchone()
    conn.close()
    return member is not None
