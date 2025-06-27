# Import module
import sqlite3
import pathlib
from config import Config

# Load DB path
DB_PATH = pathlib.Path(Config.DATABASE)

# DB connection
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict
    return conn

# Init DB
def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        # User Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """)

        # Favorite bus table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_favorite_bus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bus_stop_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (bus_stop_id) REFERENCES bus_stop(id) ON DELETE CASCADE,
                UNIQUE(user_id, bus_stop_id)
            );
        """)
        conn.commit()
