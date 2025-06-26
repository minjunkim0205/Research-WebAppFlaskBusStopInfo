# Import module
from config import db
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# DB path load
DB_PATH = db.PATH["dev"]

if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

# DB init
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# DB add user
def add_user(username, password):
    hashed_pw = generate_password_hash(password)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username duplication
    finally:
        conn.close()

# DB verify user
def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        return True
    return False
