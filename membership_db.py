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
            username TEXT NOT NULL,
            is_paid BOOLEAN DEFAULT 0,
            payment_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

    print("Database and table members are ready.")  # Log tambahan

# Fungsi untuk menambahkan anggota
def add_member(user_id, username, payment_id=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO members (user_id, username, payment_id, is_paid) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, payment_id, 0))  # Status pembayaran awal adalah 0 (belum membayar)
    conn.commit()
    conn.close()

# Fungsi untuk memeriksa apakah pengguna sudah terdaftar
def is_member(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM members WHERE user_id = ? AND is_paid = 1', (user_id,))
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

# Fungsi untuk memperbarui status pembayaran
def update_payment_status(user_id, payment_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE members
        SET is_paid = 1, payment_id = ?
        WHERE user_id = ?
    ''', (payment_id, user_id))
    conn.commit()
    conn.close()
