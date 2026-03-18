from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"
DB = "data.db"

# ======= DB connection =======
def db():
    try:
        return sqlite3.connect(DB)
    except Exception as e:
        print("DB ERROR:", e)
        return None

# ======= DB init =======
def init():
    con = db()
    if con is None:
        return

    cur = con.cursor()
    # סיסמה
    cur.execute("""
    CREATE TABLE IF NOT EXISTS password(
        pass TEXT
    )
    """)
    cur.execute("SELECT * FROM password")
    if not cur.fetchone():
        cur.execute("INSERT INTO password VALUES ('1234')")

    # תלמידים
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        tz TEXT PRIMARY KEY,
        name TEXT
    )
    """)
    con.commit()
    con.close()

init()

# ======= LOGIN =======
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        p = request.form["password"]
        con = db()
        cur = con.cursor()
        cur.execute("SELECT pass FROM password")
        real = cur.fetchone()[0]
        con.close()
        if p == real:
            session["login"] = True
            return redirect("/system")
    return render_template("login.html")

# ======= SYSTEM =======
@app.route("/system")
def system():
    if not session.get("login"):
        return redirect("/")
    con = db()
    cur = con.cursor()
    students = cur.execute("SELECT * FROM students").fetchall()
    con.close()

    # ימים חודש עברי לדוגמה
    days = ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "ז'"]

    return render_template("index.html", students=students, days=days)

# ======= SAVE =======
@app.route("/save", methods=["POST"])
def save():
    data = request.json
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM students")
    for r in data:
        cur.execute("INSERT INTO students VALUES (?,?)", (r["tz"], r["name"]))
    con.commit()
    con.close()
    return {"ok": True}

# ======= CHANGE PASSWORD =======
@app.route("/change_password", methods=["POST"])
def change():
    if not session.get("login"):
        return ""
    p = request.form["newpass"]
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM password")
    cur.execute("INSERT INTO password VALUES (?)", (p,))
    con.commit()
    con.close()
    return redirect("/system")

# ======= EXCEL =======
@app.route("/excel")
def excel():
    con = db()
    cur = con.cursor()
    students = cur.execute("SELECT * FROM students").fetchall()
    con.close()
    if not students:
        return "No students in database", 400

    # ימים חודש עברי
    days = ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "ז'"]
    records = []
    for s in students:
        tz, name = s
        day_data = {}
        for day in days:
            day_data[f"{day}_לפנה\"ת"] = ""
            day_data[f"{day}_תפילה"] = ""
            day_data[f"{day}_סדר"] = ""
        records.append({"ת.ז.": tz, "שם": name, **day_data})

    df = pd.DataFrame(records)
    now = datetime.now().strftime("%d-%m-%Y %H-%M")
    file = f"report-{now}.xlsx"
    with pd.ExcelWriter(file) as writer:
        for day in days:
            cols = ["ת.ז.", "שם",
                    f"{day}_לפנה\"ת", f"{day}_תפילה", f"{day}_סדר"]
            df[cols].to_excel(writer, sheet_name=day, index=False)
    return send_file(file, as_attachment=True)

# ======= RUN APP =======
if __name__ == "__main__":
    app.run()