from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --------- Models ---------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    tz = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Day(db.Model):
    __tablename__ = "days"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)

class Shift(db.Model):
    __tablename__ = "shifts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(10))
    amount = db.Column(db.Float)
    late_deduction = db.Column(db.Float)

class Content(db.Model):
    __tablename__ = "content"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    student = db.relationship("Student")
    day_id = db.Column(db.Integer, db.ForeignKey("days.id"))
    day = db.relationship("Day")
    shift_id = db.Column(db.Integer, db.ForeignKey("shifts.id"))
    shift = db.relationship("Shift")
    arrival_time = db.Column(db.String(10))
    amount_due = db.Column(db.Float)
    total = db.Column(db.Float)

# --------- Routes ---------
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/download_excel")
def download_excel():
    # Placeholder file generation
    filename = f"עדכון ישיבת בין הזמנים נכון ל {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.xlsx"
    path = os.path.join("static", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("TZ,Name,Day1,Day2,Day3,Total\n")
    return send_file(path, as_attachment=True)

# --------- API Placeholder for Phone Line ---------
@app.route("/api/phone_line", methods=["POST"])
def phone_line_api():
    data = request.json
    # Placeholder response
    return jsonify({"status": "ok", "received": data})

if __name__ == "__main__":
    app.run(debug=True)
