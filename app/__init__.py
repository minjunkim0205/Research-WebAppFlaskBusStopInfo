# Import module
import os
import config
import flask
import dotenv
import app.database as database
import app.routes as routes

def create_app():
    # Load environment variables
    dotenv.load_dotenv()

    # Flask app init
    app = flask.Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    app.config.from_object(config.Config)

    # Init DB within app context
    with app.app_context():
        database.init_db()

    # Register Blueprints
    app.register_blueprint(routes.main)

    return app
