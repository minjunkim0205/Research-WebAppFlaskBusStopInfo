# Import module
import sqlite3
import pathlib
import werkzeug.security
from config import Config

# Load DB path
DATABASE = pathlib.Path(Config.DATABASE)

# DB connection
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # dict
    return conn

# Init DB
def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        # User Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """)
        # Favorite bus table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_favorites_bus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                route_id TEXT NOT NULL,
                station_name TEXT NOT NULL,
                ars_id TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        conn.commit()

# User Table
def add_user(username, password):
    hashed_pw = werkzeug.security.generate_password_hash(password)
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 유저명 증복
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    # sqlite3.Row, dict-like 반환 
    return user

def verify_user(username, password):
    user = get_user_by_username(username)
    if user and werkzeug.security.check_password_hash(user["password"], password):
        # 로그인 성공, 사용자 정보 반환
        return user
    else:
        # 로그인 실패, None 반환
        return None

# Bus Table
def add_favorite_bus(user_id, route_id, station_name, ars_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users_favorites_bus (user_id, route_id, station_name, ars_id)
        VALUES (?, ?, ?, ?)
    """, (user_id, route_id, station_name, ars_id))
    conn.commit()
    conn.close()

def get_favorite_buses(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM users_favorites_bus WHERE user_id = ?
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows