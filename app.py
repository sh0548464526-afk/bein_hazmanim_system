
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import io
import os
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)

# ------------------ MODELS ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tz = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_name = db.Column(db.String(50), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(5))
    amount = db.Column(db.Float)
    late_deduction = db.Column(db.Float)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_tz = db.Column(db.String(20), db.ForeignKey('student.tz'))
    student_name = db.Column(db.String(100))
    # עמודות דינמיות לכל יום
    # לדוגמה: day_1_shift1, day_1_shift2, day_1_shift3, day_1_total

# ------------------ ROUTES ------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('dashboard'))
        return 'שם משתמש או סיסמה שגויים', 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    students = Student.query.all()
    days = Day.query.filter_by(active=True).all()
    shifts = Shift.query.all()
    return render_template('dashboard.html', students=students, days=days, shifts=shifts)

@app.route('/download_excel')
def download_excel():
    students = Student.query.all()
    days = Day.query.filter_by(active=True).all()
    # יצירת DataFrame לדוגמה
    data = []
    for s in students:
        row = {'תז': s.tz, 'שם': s.name}
        for d in days:
            row[d.date_name] = '08:00'  # Placeholder
        data.append(row)
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    filename = f"עדכון ישיבת בין הזמנים נכון ל {datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# ------------------ API Example ------------------
@app.route('/api/phone', methods=['POST'])
def api_phone():
    # כאן ייכנסו פרמטרים מהקו טלפון
    data = request.json
    # לדוגמה - החזר אותו דבר
    return jsonify(data)

if __name__ == '__main__':
    db.create_all()
    # יצירת משתמש admin לדוגמה
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('admin', method='sha256')))
        db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=True)
