# Import module
import flask
import werkzeug.security
import app.database as database
from app.services import bus_api

# Init
main = flask.Blueprint("main", __name__)

# Index route
@main.route("/", methods=["GET", "POST"])
def index():
    # GET
    if flask.request.method == "GET":
        if "username" in flask.session:
            return flask.redirect(flask.url_for("main.home"))
        else:
            return flask.redirect(flask.url_for("main.login"))
    # POST
    if flask.request.method == "POST":
        pass

# Auth route
@main.route("/login", methods=["GET", "POST"])
def login():
    # GET
    if flask.request.method == "GET":
        return flask.render_template("auth/login.html")
    # POST
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]   
        user = database.verify_user(username, password)
        if user and werkzeug.security.check_password_hash(user["password"], password):
            flask.session["user_id"] = user["id"]
            flask.session["username"] = user["username"]
            flask.flash("로그인 성공!", "success")
            return flask.redirect(flask.url_for("main.home"))
        else:
            flask.flash("아이디 또는 비밀번호가 틀렸습니다.", "danger")
            return flask.render_template("auth/login.html")

@main.route("/logout", methods=["GET", "POST"])
def logout():
    # GET
    if flask.request.method == "GET":
        flask.session.pop("username", None)
        flask.flash("로그아웃 되었습니다.", "info")
        return flask.redirect(flask.url_for("main.login"))
    # POST
    if flask.request.method == "POST":
        pass

@main.route("/signup", methods=["GET", "POST"])
def signup():
    # GET
    if flask.request.method == "GET":
        return flask.render_template("auth/signup.html")
    # POST
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        if database.add_user(username, password):
            flask.flash("회원가입 성공! 로그인 해주세요.", "success")
            return flask.redirect(flask.url_for("main.login"))
        else:
            flask.flash("이미 존재하는 사용자명입니다.", "danger")
            return flask.render_template("auth/signup.html")

# Home route
@main.route("/home", methods=["GET", "POST"])
def home():
    # GET
    if flask.request.method == "GET":
        user_id = flask.session.get("user_id")
        if not user_id:
            return flask.redirect(flask.url_for("main.login"))
        if user_id:
            user_id = flask.session["user_id"]
            return flask.render_template("home/home.html", username=flask.session["username"])
    # POST
    if flask.request.method == "POST":
        pass

# Bus route
@main.route("/search", methods=["GET", "POST"])
def search_station():
    # GET
    if flask.request.method == "GET":
        keyword = flask.request.args.get("keyword", "")
        if not keyword:
            flask.flash("검색어를 입력해주세요.", "warning")
            return flask.redirect(flask.url_for("main.home"))
        if keyword:
            stations = bus_api.get_station_by_name(keyword)
            return flask.render_template("bus/search.html", stations=stations, keyword=keyword)
    # POST
    if flask.request.method == "POST":
        pass
