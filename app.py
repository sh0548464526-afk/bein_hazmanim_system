from flask import Flask, render_template, request, redirect, session, send_file
import psycopg2
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE_URL = os.environ.get("DATABASE_URL")
MASTER_PASSWORD = "9999"

def db():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("DB ERROR:", e)
        return None

def init():
    con = db()
    if con is None:
        return

    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        tz TEXT PRIMARY KEY,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        tz TEXT,
        day TEXT,
        before_prayer TEXT,
        prayer TEXT,
        seder TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS password(
        pass TEXT
    )
    """)

    cur.execute("SELECT pass FROM password")
    if not cur.fetchone():
        cur.execute("INSERT INTO password VALUES ('1234')")

    con.commit()
    con.close()

init()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
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

@app.route("/system")
def system():

    if not session.get("login"):
        return redirect("/")

    con = db()
    if con is None:
        return "Database error", 500

    cur = con.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    cur.execute("SELECT * FROM attendance")
    att = cur.fetchall()

    con.close()

    days = sorted(list(set([r[1] for r in att])))

    data = {}

    for tz, name in students:
        data[tz] = {"name": name, "days": {}}

    for tz, day, b, p, s in att:
        if tz in data:
            data[tz]["days"][day] = {
                "before": b,
                "prayer": p,
                "seder": s
            }

    return render_template("index.html", data=data, days=days)

@app.route("/save", methods=["POST"])
def save():

    data = request.json

    con = db()
    if con is None:
        return {"ok": False}, 500

    cur = con.cursor()

    cur.execute("DELETE FROM students")
    cur.execute("DELETE FROM attendance")

    for r in data:

        tz = r["tz"]
        name = r["name"]

        if not tz:
            continue

        cur.execute("INSERT INTO students VALUES (%s,%s)", (tz, name))

        for d in r["days"]:
            cur.execute("""
            INSERT INTO attendance VALUES (%s,%s,%s,%s,%s)
            """, (
                tz,
                d["day"],
                d["before"],
                d["prayer"],
                d["seder"]
            ))

    con.commit()
    con.close()

    return {"ok": True}

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
            df[df["day"] == day].to_excel(writer, sheet_name=day, index=False)

    con.close()

    return send_file(file, as_attachment=True)

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

if __name__ == "__main__":
    app.run()
