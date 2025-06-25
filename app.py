from config import setting
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
import xml.etree.ElementTree as ET
import sqlite3
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'

API_KEY = setting.DATABASE_CONFIG["api_decoded_key"]

# 공공 데이터 포탈 api 조회 함수
def get_station_arrivals(ars_id):
    url = "http://ws.bus.go.kr/api/rest/arrive/getLowArrInfoByStId"
    params = {
        "serviceKey": API_KEY,
        "arsId": ars_id
    }
    resp = requests.get(url, params=params)
    root = ET.fromstring(resp.content)

    result = []
    for item in root.iter("itemList"):
        bus_number = item.findtext("rtNm")
        traTime1 = item.findtext("traTime1")
        traTime2 = item.findtext("traTime2")

        arrival1 = int(traTime1) // 60 if traTime1 and traTime1.isdigit() else None
        arrival2 = int(traTime2) // 60 if traTime2 and traTime2.isdigit() else None

        result.append({
            "busNumber": bus_number,
            "arrival1": arrival1,
            "arrival2": arrival2
        })

    return result

def get_stations_by_name(st_name):
    url = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByName"
    params = {
        "serviceKey": API_KEY,  # 주의: 'ServiceKey' → 'serviceKey'
        "stSrch": st_name
    }
    resp = requests.get(url, params=params)
    root = ET.fromstring(resp.content)

    results = []
    for item in root.iter("itemList"):
        ars_id = item.findtext("arsId")
        station_name = item.findtext("stNm")

        # 도착정보 추가
        arrivals = get_station_arrivals(ars_id)

        results.append({
            "stationName": station_name,
            "arsId": ars_id,
            "arrivals": arrivals
        })

    return results

# db 관리 함수
def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ars_id TEXT NOT NULL,
            station_name TEXT NOT NULL,
            UNIQUE(user_id, ars_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

def add_favorite(user_id, ars_id, station_name):
    conn = get_db_connection()
    try:
        conn.execute('INSERT OR IGNORE INTO favorites (user_id, ars_id, station_name) VALUES (?, ?, ?)',
                     (user_id, ars_id, station_name))
        conn.commit()
    finally:
        conn.close()

def remove_favorite(user_id, ars_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM favorites WHERE user_id = ? AND ars_id = ?', (user_id, ars_id))
        conn.commit()
    finally:
        conn.close()

def get_user_favorites(user_id):
    conn = get_db_connection()
    try:
        rows = conn.execute('SELECT ars_id, station_name FROM favorites WHERE user_id = ?', (user_id,)).fetchall()
        return [{"arsId": row["ars_id"], "stationName": row["station_name"]} for row in rows]
    finally:
        conn.close()

def get_user_id(username):
    conn = get_db_connection()
    try:
        row = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        return row['id'] if row else None
    finally:
        conn.close()

# 버스 도착 정보 관련 함수

def get_bus_arrival_info(bus_stop_id):
    url = 'http://apis.data.go.kr/1613000/BusArrivalService/getBusArrivalList'
    params = {
        'serviceKey': API_KEY,
        'stationId': bus_stop_id,
        'numOfRows': '5',
        'pageNo': '1',
        '_type': 'json'
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        return items
    except Exception as e:
        print('버스 도착 정보 조회 실패:', e)
        return []

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login_form'))

@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash("아이디와 비밀번호를 모두 입력해주세요.", "danger")
        return redirect(url_for('signup_form'))

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        flash("이미 존재하는 아이디입니다.", "danger")
        return redirect(url_for('signup_form'))
    finally:
        conn.close()
    flash("회원가입 성공! 로그인 해주세요.", "success")
    return redirect(url_for('login_form'))

@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash("아이디와 비밀번호를 모두 입력해주세요.", "danger")
        return redirect(url_for('login_form'))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    conn.close()

    if user:
        session['username'] = user['username']
        flash(f"{user['username']}님 환영합니다!", "success")
        return redirect(url_for('home'))
    else:
        flash("아이디 또는 비밀번호가 올바르지 않습니다.", "danger")
        return redirect(url_for('login_form'))

@app.route('/logout')
def logout():
    session.clear()
    flash("로그아웃 되었습니다.", "info")
    return redirect(url_for('login_form'))

@app.route('/home')
def home():
    if 'username' not in session:
        flash("로그인이 필요합니다.", "warning")    
        return redirect(url_for('login_form'))

    user_id = get_user_id(session['username'])
    favorites = get_user_favorites(user_id)
    # 즐겨찾기 정류장별 도착정보 수집
    favorite_arrivals = []
    for fav in favorites:
        arrivals = get_station_arrivals(fav['arsId'])
        favorite_arrivals.append({
            "stationName": fav['stationName'],
            "arsId": fav['arsId'],
            "arrivals": arrivals
        })

    return render_template('home.html', username=session['username'], favorite_arrivals=favorite_arrivals)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['station']
        result = get_stations_by_name(query)
        return render_template('search.html', results=result, query=query)
    return render_template('search.html')

@app.route('/favorite', methods=['POST'])
def toggle_favorite():
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    user_id = get_user_id(session['username'])
    data = request.json
    ars_id = data.get('arsId')
    station_name = data.get('stationName')
    action = data.get('action')  # 'add' or 'remove'

    if not all([ars_id, station_name, action]):
        return jsonify({"error": "잘못된 요청입니다."}), 400

    if action == 'add':
        add_favorite(user_id, ars_id, station_name)
    elif action == 'remove':
        remove_favorite(user_id, ars_id)
    else:
        return jsonify({"error": "알 수 없는 action"}), 400

    return jsonify({"success": True})

if __name__ == '__main__':
    app.secret_key = app.config['SECRET_KEY']
    create_tables()
    app.run(debug=True)