from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ================= DATABASE CONFIG =================
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'users.db')

db = SQLAlchemy(app)

# ================= LOGIN =================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ================= MODEL =================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ================= INIT DATABASE (FIX UTAMA) =================
with app.app_context():
    db.create_all()

# ================= ROUTES =================

@app.route('/')
def index():
    return redirect(url_for('login'))

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login gagal!')

    return render_template('login.html')

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            flash('Username sudah ada!')
            return redirect('/register')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Register berhasil!')
        return redirect('/login')

    return render_template('register.html')

# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/games')
@login_required
def games():
    return render_template('games.html')


@app.route('/sudoku')
@login_required
def sudoku():
    return render_template('sudoku.html')

@app.route('/minesweeper')
@login_required
def minesweeper():
    return render_template('minesweeper.html')

# ================= RUN =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
