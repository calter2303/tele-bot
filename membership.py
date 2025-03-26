import sqlite3

# Fungsi untuk membuat dan menghubungkan ke database SQLite
def create_db():
    conn = sqlite3.connect("membership.db")
    cursor = conn.cursor()
    # Membuat tabel untuk menyimpan data anggota jika belum ada
    cursor.execute('''CREATE TABLE IF NOT EXISTS members
                      (user_id INTEGER PRIMARY KEY, username TEXT)''')
    conn.commit()
    conn.close()

# Fungsi untuk menambahkan anggota ke database
def add_member(user_id, username):
    conn = sqlite3.connect("membership.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:  # Jika pengguna belum ada
        cursor.execute("INSERT INTO members (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        print(f"{username} has been added as a member.")
    else:
        print(f"{username} is already a member.")
    conn.close()

# Fungsi untuk memeriksa apakah pengguna sudah menjadi anggota
def is_member(user_id):
    conn = sqlite3.connect("membership.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE user_id = ?", (user_id,))
    member = cursor.fetchone()
    conn.close()
    return member is not None

# Fungsi untuk menghapus anggota dari database
def remove_member(user_id):
    conn = sqlite3.connect("membership.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is not None:
        cursor.execute("DELETE FROM members WHERE user_id = ?", (user_id,))
        conn.commit()
        print(f"User with ID {user_id} has been removed from membership.")
    else:
        print(f"User with ID {user_id} is not a member.")
    conn.close()

# Panggil create_db() untuk membuat database dan tabel
create_db()
