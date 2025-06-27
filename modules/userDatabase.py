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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            station_name TEXT,
            ars_id TEXT,
            route_name TEXT
        );
    """)
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

# Add favorite
def add_favorite(username, station_name, ars_id, route_name):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM favorites
            WHERE username=? AND ars_id=? AND route_name=?
        """, (username, ars_id, route_name))
        if cursor.fetchone():
            return False
        cursor.execute("""
            INSERT INTO favorites (username, station_name, ars_id, route_name)
            VALUES (?, ?, ?, ?)
        """, (username, station_name, ars_id, route_name))
        return True

# Get favorite
def get_favorites(username):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT station_name, ars_id, route_name
            FROM favorites
            WHERE username=?
        """, (username,))
        return cursor.fetchall()