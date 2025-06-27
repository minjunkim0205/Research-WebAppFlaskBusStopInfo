# Import module
import flask

# Init
main = flask.Blueprint("main", __name__)

# Route
@main.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "POST":
        message = "Hello (POST)"
    else:
        message = "Hello (GET)"

    return flask.render_template("index.html", message=message)
