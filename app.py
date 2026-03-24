from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os, datetime

app = Flask(__name__)
# DATABASE_URL מוגדר ב-Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# מודלים בסיסיים
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tz = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(10))
    amount = db.Column(db.Float)
    deduction_per_10_min = db.Column(db.Float)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tz = db.Column(db.String(20))
    name = db.Column(db.String(100))
    # כאן יהיו עמודות עבור כל יום/סדר, נבנה בהמשך
    total = db.Column(db.Float, default=0)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return redirect(url_for('dashboard'))
    return "שם משתמש או סיסמה שגויים"

@app.route('/dashboard')
def dashboard():
    students = Student.query.all()
    days = Day.query.all()
    shifts = Shift.query.all()
    return render_template('dashboard.html', students=students, days=days, shifts=shifts)

if __name__ == '__main__':
    if not os.path.exists('test.db'):
        db.create_all()
    app.run(debug=True)
