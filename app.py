import os
from flask import Flask, render_template, request, redirect, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from datetime import datetime
from openpyxl import Workbook

app = Flask(__name__)
app.secret_key = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL","sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# ---------------- models ----------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tz = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    active = db.Column(db.Boolean)

class Seder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    start = db.Column(db.String(10))
    amount = db.Column(db.Float)
    late = db.Column(db.Float)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tz = db.Column(db.String(20))
    name = db.Column(db.String(100))
    day = db.Column(db.String(50))
    seder1 = db.Column(db.String(10))
    seder2 = db.Column(db.String(10))
    seder3 = db.Column(db.String(10))
    total = db.Column(db.Float)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# ---------------- routes ----------------

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        user = User.query.filter_by(username=request.form["username"]).first()

        if user and user.password == request.form["password"]:
            login_user(user)
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():

    students = Student.query.all()

    return render_template("dashboard.html",students=students)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

# -------- students management --------

@app.route("/students")
@login_required
def students():

    students = Student.query.all()

    return jsonify([
        {"tz":s.tz,"name":s.name}
        for s in students
    ])

@app.route("/add_student",methods=["POST"])
@login_required
def add_student():

    tz = request.form["tz"]
    name = request.form["name"]

    db.session.add(Student(tz=tz,name=name))
    db.session.commit()

    return "ok"

# -------- excel export --------

@app.route("/download")
@login_required
def download():

    wb = Workbook()
    ws = wb.active

    ws.append(["תז","שם","סהכ"])

    students = Student.query.all()

    for s in students:

        total = 0

        rows = Attendance.query.filter_by(tz=s.tz).all()

        for r in rows:
            total += r.total or 0

        ws.append([s.tz,s.name,total])

    filename = "עדכון_ישיבת_בין_הזמנים_" + datetime.now().strftime("%Y_%m_%d_%H_%M") + ".xlsx"

    path = "/tmp/" + filename

    wb.save(path)

    return send_file(path,as_attachment=True,download_name=filename)

# -------- phone api --------

@app.route("/phone_api")
def phone_api():

    action = request.args.get("action")

    if action == "students":

        data = Student.query.all()

        return jsonify([
            {"tz":s.tz,"name":s.name}
            for s in data
        ])

    return jsonify({"status":"ok"})

# -------- init database --------

@app.cli.command("initdb")
def initdb():

    db.create_all()

    if not User.query.first():

        db.session.add(User(username="admin",password="1234"))

        db.session.commit()

    print("database ready")

if __name__ == "__main__":
    app.run()