# Import module
from config import secret
from modules import userDatabase as database
from modules import seoulBusStopInformationApi as busapi
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Init flask
app = Flask(__name__)
app.secret_key = secret.KEY["flask"]

# Init db
database.init_db()

@app.before_request
def load_favorites():
    if 'username' in session:
        raw_favorites = database.get_favorites(session['username'])
        favorites = []
        for fav in raw_favorites:
            ars_id = fav[1]
            route = fav[2]
            arrival_info = busapi.get_station_by_uid(ars_id)
            target = next((i for i in arrival_info if i['rtNm'] == route), None)
            favorites.append((fav[0], ars_id, route, target['arrmsg1'] if target else '정보 없음'))
        session['favorites'] = favorites

# Flask route
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    station_list = []
    if request.method == 'POST':
        query = request.form.get('station_name')
        station_list = busapi.get_station_by_name(query)
        if not station_list:
            flash("해당 이름의 정류장을 찾을 수 없습니다.", "warning")

    return render_template('index.html', username=session['username'], station_list=station_list, favorites=session.get('favorites', []))

@app.route('/view')
def view_station():
    if 'username' not in session:
        return redirect(url_for('login'))

    ars_id = request.args.get('arsId')
    arrival_info = busapi.get_station_by_uid(ars_id) if ars_id else []
    return render_template('view.html', username=session['username'], arrival_info=arrival_info)

@app.route('/favorite', methods=['POST'])
def favorite():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    station_name = request.form['station_name']
    ars_id = request.form['ars_id']
    route_name = request.form['route_name']

    if database.add_favorite(username, station_name, ars_id, route_name):
        flash(f'{route_name}번 버스가 즐겨찾기에 추가되었습니다.', 'success')
    else:
        flash('이미 즐겨찾기에 등록된 버스입니다.', 'info')

    return redirect(url_for('view_station', arsId=ars_id))

@app.route("/favorite_info")
def favorite_info():
    if "username" not in session:
        return redirect(url_for("login"))
    
    ars_id = request.args.get("arsId")
    route = request.args.get("route")

    info = []
    for item in busapi.get_station_by_uid(ars_id):
        if item["rtNm"] == route:
            station_info = busapi.get_station_by_name(item["stationName"])
            if station_info:
                item["tmX"] = station_info[0]["tmX"]
                item["tmY"] = station_info[0]["tmY"]
            info.append(item)
    
    return render_template("favorite_info.html", info=info)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if database.add_user(username, password):
            flash('회원가입 성공! 로그인 해주세요.', 'success')
            return redirect(url_for('login'))
        else:
            flash('이미 존재하는 사용자명입니다.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if database.verify_user(username, password):
            session['username'] = username
            flash('로그인 성공!', 'success')
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('login'))

# Main
if __name__ == '__main__':
    app.run(debug=True)