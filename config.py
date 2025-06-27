# Import module
import os

# Database dir
DATABASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
DATABASE = os.path.join(DATABASE_DIR, "bus_stop.db")
