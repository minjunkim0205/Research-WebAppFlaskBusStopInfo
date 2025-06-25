from config import setting
from flask import Flask, request, render_template, redirect, url_for, flash, session
import xml.etree.ElementTree as ET
import sqlite3
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'

API_KEY = setting.DATABASE_CONFIG["api_decoded_key"]

# DB 연결 함수
def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    # 유저 테이블
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # 즐겨찾기 테이블 (username - stId - stationName)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            stId TEXT NOT NULL,
            stationName TEXT NOT NULL,
            UNIQUE(username, stId)
        )
    ''')
    conn.commit()
    conn.close()

# API 호출: 특정 정류장 도착 버스정보
def get_station_arrivals(ars_id):
    url = "http://ws.bus.go.kr/api/rest/arrive/getLowArrInfoByStId"
    params = {
        "serviceKey": API_KEY,
        "arsId": ars_id
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print(f"[ERROR] API 호출 실패: {resp.status_code}")
        return []

    root = ET.fromstring(resp.content)
    headerCd = root.findtext('msgHeader/headerCd')
    if headerCd == '4':  # 결과 없음
        return []

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

# API 호출: 정류장 이름으로 검색
def get_stations_by_name(st_name):
    url = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByName"
    params = {
        "serviceKey": API_KEY,
        "stSrch": st_name
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print(f"[ERROR] API 호출 실패: {resp.status_code}")
        return []

    root = ET.fromstring(resp.content)
    headerCd = root.findtext('msgHeader/headerCd')
    if headerCd == '4':
        return []

    results = []
    for item in root.iter("itemList"):
        ars_id = item.findtext("arsId")
        station_name = item.findtext("stNm")
        arrivals = get_station_arrivals(ars_id)
        results.append({
            "stationName": station_name,
            "arsId": ars_id,
            "arrivals": arrivals
        })
    return results

# 사용자 즐겨찾기 불러오기
def get_user_favorites(username):
    conn = get_db_connection()
    rows = conn.execute("SELECT stId, stationName FROM favorites WHERE username = ?", (username,)).fetchall()
    conn.close()

    results = []
    for row in rows:
        arrivals = get_station_arrivals(row["stId"])
        results.append({
            "arsId": row["stId"],
            "stationName": row["stationName"],
            "arrivals": arrivals
        })
    return results

# 즐겨찾기 추가
def add_favorite(username, stId, stationName):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO favorites (username, stId, stationName) VALUES (?, ?, ?)",
            (username, stId, stationName)
        )
        conn.commit()
    except Exception as e:
        print(f"[ERROR] 즐겨찾기 추가 실패: {e}")
    finally:
        conn.close()

# 즐겨찾기 삭제
def remove_favorite(username, stId):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM favorites WHERE username = ? AND stId = ?", (username, stId))
        conn.commit()
    except Exception as e:
        print(f"[ERROR] 즐겨찾기 삭제 실패: {e}")
    finally:
        conn.close()

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

    username = session['username']
    favorites = get_user_favorites(username)
    return render_template('home.html', username=username, favorites=favorites)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['station']
        results = get_stations_by_name(query)
        return render_template('search.html', results=results, query=query)
    return render_template('search.html')

# 즐겨찾기 추가 API (POST)
@app.route('/favorite/add', methods=['POST'])
def favorite_add():
    if 'username' not in session:
        return {"result": "error", "message": "로그인 필요"}, 401

    username = session['username']
    stId = request.form.get('stId')
    stationName = request.form.get('stationName')
    if not stId or not stationName:
        return {"result": "error", "message": "필요한 정보 부족"}, 400

    add_favorite(username, stId, stationName)
    return redirect(url_for('home'))

# 즐겨찾기 삭제 API (POST)
@app.route('/favorite/remove', methods=['POST'])
def favorite_remove():
    if 'username' not in session:
        return {"result": "error", "message": "로그인 필요"}, 401

    username = session['username']
    stId = request.form.get('stId')
    if not stId:
        return {"result": "error", "message": "필요한 정보 부족"}, 400

    remove_favorite(username, stId)
    return redirect(url_for('home'))


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
