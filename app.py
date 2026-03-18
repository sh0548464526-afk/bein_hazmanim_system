from flask import Flask, render_template, request, redirect, session, send_file
import psycopg2
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE_URL = os.environ.get("DATABASE_URL")
MASTER_PASSWORD = "9999"

# --- חיבור למסד ---
def db():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("DB ERROR:", e)
        return None

# --- יצירת טבלאות אם אין ---
def init():
    con = db()
    if con is None:
        print("Database not connected")
        return
    cur = con.cursor()

    # טבלת סיסמה
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password(
            pass TEXT
        )
    """)
    cur.execute("SELECT pass FROM password")
    if not cur.fetchone():
        cur.execute("INSERT INTO password VALUES ('1234')")

    # טבלת תלמידים
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students(
            tz TEXT PRIMARY KEY,
            name TEXT
        )
    """)

    # טבלת נוכחות לפי ימים
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance(
            tz TEXT,
            day TEXT,
            before_prayer TEXT,
            prayer TEXT,
            seder TEXT
        )
    """)

    con.commit()
    con.close()

init()

# --- כניסה ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        p = request.form["password"]
        con = db()
        if con is None:
            return "Database error", 500
        cur = con.cursor()
        cur.execute("SELECT pass FROM password LIMIT 1")
        row = cur.fetchone()
        con.close()
        if (row and p == row[0]) or p == MASTER_PASSWORD:
            session["login"] = True
            return redirect("/system")
    return render_template("login.html")

# --- דף המערכת ---
@app.route("/system")
def system():
    if not session.get("login"):
        return redirect("/")

    con = db()
    if con is None:
        return "Database error", 500
    cur = con.cursor()

    # תלמידים
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    # נוכחות
    cur.execute("SELECT * FROM attendance")
    att = cur.fetchall()
    con.close()

    # רשימת ימים קיימים
    days = sorted(list(set([r[1] for r in att])))

    # מבנה נתונים לטבלה
    data = {}
    for tz, name in students:
        data[tz] = {"name": name, "days": {}}

    for tz, day, b, p, s in att:
        if tz in data:
            data[tz]["days"][day] = {"before": b, "prayer": p, "seder": s}

    return render_template("index.html", data=data, days=days, students=students)

# --- שמירה ---
@app.route("/save", methods=["POST"])
def save():
    data = request.json
    con = db()
    if con is None:
        return {"ok": False}, 500
    cur = con.cursor()

    # מחיקה קודם
    cur.execute("DELETE FROM students")
    cur.execute("DELETE FROM attendance")

    for r in data:
        tz = r.get("tz")
        name = r.get("name")
        if not tz:
            continue
        cur.execute("INSERT INTO students VALUES (%s, %s)", (tz, name))
        for day, vals in r.get("days", {}).items():
            cur.execute("""
                INSERT INTO attendance VALUES (%s, %s, %s, %s, %s)
            """, (tz, day, vals.get("before", ""), vals.get("prayer", ""), vals.get("seder", "")))

    con.commit()
    con.close()
    return {"ok": True}

# --- שינוי סיסמה ---
@app.route("/change_password", methods=["POST"])
def change():
    if not session.get("login"):
        return ""
    p = request.form["newpass"]
    con = db()
    if con is None:
        return "Database error", 500
    cur = con.cursor()
    cur.execute("DELETE FROM password")
    cur.execute("INSERT INTO password VALUES (%s)", (p,))
    con.commit()
    con.close()
    return redirect("/system")

# --- יצוא Excel ---
@app.route("/excel")
def excel():
    con = db()
    if con is None:
        return "Database error", 500

    df = pd.read_sql("SELECT * FROM attendance", con)
    now = datetime.now().strftime("%d-%m-%Y %H-%M")
    file = f"עדכון ישיבת בין הזמנים נכון ל-{now}.xlsx"

    with pd.ExcelWriter(file) as writer:
        for day in df["day"].unique():
            df[df["day"]==day].to_excel(writer, sheet_name=day, index=False)

    con.close()
    return send_file(file, as_attachment=True)

if __name__ == "__main__":
    app.run()
