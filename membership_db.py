import sqlite3

# Nama database
DB_NAME = "members.db"

# Fungsi untuk membuat database dan tabel
def create_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Fungsi untuk menambahkan anggota
def add_member(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO members (user_id, username) 
        VALUES (?, ?)
    ''', (user_id, username))
    conn.commit()
    conn.close()

# Fungsi untuk memeriksa apakah pengguna sudah terdaftar
def is_member(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM members WHERE user_id = ?', (user_id,))
    member = c.fetchone()
    conn.close()
    return member is not None

# Fungsi untuk menghapus anggota
def remove_member(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM members WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
