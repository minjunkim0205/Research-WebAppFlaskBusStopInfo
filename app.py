from flask import Flask, request, render_template, redirect, url_for, flash, session
import sqlite3
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'

API_KEY = '발급받은_API_키_여기에_넣기'  # data.go.kr에서 받은 키로 변경하세요

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
    conn.commit()
    conn.close()

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

    # TODO: 사용자별 정류장 DB 연동 후 실제 정류장 ID 받아오기
    bus_stop_id = '123456'  # 임시 고정값, 실제로는 사용자별 DB 정보 필요
    arrivals = get_bus_arrival_info(bus_stop_id)

    return render_template('home.html', username=session['username'], arrivals=arrivals)

if __name__ == '__main__':
    app.secret_key = app.config['SECRET_KEY']
    create_tables()
    app.run(debug=True)
