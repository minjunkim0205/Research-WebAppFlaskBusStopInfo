# Import module
import os

class Config:
    # Database
    DATABASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    DATABASE = os.path.join(DATABASE_DIR, "bus_stop.db")
    # API key
    BUS_API_KEY = os.getenv("BUS_API_DECODE_KEY")
    # Secret key
    FLASK_KEY = os.getenv("FLASK_SECRET_KEY")
    # Debug
    DEBUG = True