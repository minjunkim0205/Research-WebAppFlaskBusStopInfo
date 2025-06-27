# Import module
from app import create_app

# Flask 
app = create_app()

# Main
if __name__ == '__main__':
    app.run(debug=True)