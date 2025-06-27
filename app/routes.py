# Import module
import flask
import werkzeug.security
import app.database as database
from app.services import bus_api

# Init
main = flask.Blueprint("main", __name__)

# Home route
@main.route("/")
def index():
    if "username" in flask.session:
        return flask.redirect(flask.url_for("main.home"))
    else:
        return flask.redirect(flask.url_for("main.login"))
    return flask.render_template("index.html")

@main.route("/home")
def home():
    user_id = flask.session.get("user_id")
    if not user_id:
        return flask.redirect(flask.url_for("main.login"))
    
    user_id = flask.session["user_id"]
    favorites = database.get_favorite_buses(user_id)
    return flask.render_template("home/home.html", favorites=favorites, username=flask.session["username"])

# Auth route
@main.route("/login", methods=["GET", "POST"])
def login():
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

@main.route("/logout")
def logout():
    flask.session.pop("username", None)
    flask.flash("로그아웃 되었습니다.", "info")
    return flask.redirect(flask.url_for("main.login"))

@main.route("/signup", methods=["GET", "POST"])
def signup():
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        if database.add_user(username, password):
            flask.flash("회원가입 성공! 로그인 해주세요.", "success")
            return flask.redirect(flask.url_for("main.login"))
        else:
            flask.flash("이미 존재하는 사용자명입니다.", "danger")
    return flask.render_template("auth/signup.html")

# Bus route

@main.route("/search", methods=["GET"])
def search_station():
    keyword = flask.request.args.get("keyword", "")
    if not keyword:
        flask.flash("검색어를 입력해주세요.", "warning")
        return flask.redirect(flask.url_for("main.home"))

    stations = bus_api.get_station_by_name(keyword)
    return flask.render_template("bus/search.html", stations=stations, keyword=keyword)

@main.route("/search/station/<ars_id>")
def station_detail(ars_id):
    buses = bus_api.get_station_by_uid(ars_id)
    return flask.render_template("bus/detail.html", ars_id=ars_id, buses=buses)

@main.route("/favorite/add", methods=["POST"])
def add_favorite():
    if "user_id" not in flask.session:
        flask.flash("로그인이 필요합니다.", "warning")
        return flask.redirect(flask.url_for("main.login"))

    user_id = flask.session["user_id"]
    route_id = flask.request.form.get("route_id")
    station_name = flask.request.form.get("station_name")
    ars_id = flask.request.form.get("ars_id")

    if not (route_id and station_name and ars_id):
        flask.flash("필수 정보가 누락되었습니다.", "danger")
        return flask.redirect(flask.request.referrer or flask.url_for("main.home"))

    database.add_favorite_bus(user_id, route_id, station_name, ars_id)
    flask.flash("즐겨찾기에 추가되었습니다.", "success")
    return flask.redirect(flask.request.referrer or flask.url_for("main.home"))