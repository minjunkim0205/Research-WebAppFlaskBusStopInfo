# Import module
from config import secret
from modules import userDatabase as database
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Init flask
app = Flask(__name__)
app.secret_key = secret.KEY["flask"]

# Init db
database.init_db()

# Flask route
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

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

if __name__ == '__main__':
    app.run(debug=True)
