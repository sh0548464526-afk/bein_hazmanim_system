from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

DB = "data.db"

def db():
    return sqlite3.connect(DB)

def init():
    con = db()
    cur = con.cursor()

    # טבלת סיסמה
    cur.execute("""
    CREATE TABLE IF NOT EXISTS password(
        pass TEXT
    )
    """)

    cur.execute("SELECT pass FROM password")
    row = cur.fetchone()

    if not row:
        cur.execute("INSERT INTO password VALUES ('1234')")

    # טבלת תלמידים
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        tz TEXT,
        name TEXT
    )
    """)

    con.commit()
    con.close()

# 🔥 חשוב מאוד – זה פותר את הבעיה שלך
init()

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        p = request.form["password"]

        con = db()
        cur = con.cursor()

        cur.execute("SELECT pass FROM password")
        row = cur.fetchone()
        con.close()

        if row and p == row[0]:
            session["login"] = True
            return redirect("/system")

    return render_template("login.html")

@app.route("/system")
def system():

    if not session.get("login"):
        return redirect("/")

    con = db()
    cur = con.cursor()

    rows = cur.execute(
        "SELECT * FROM students"
    ).fetchall()

    con.close()

    return render_template(
        "index.html",
        students=rows
    )

@app.route("/save", methods=["POST"])
def save():

    data = request.json

    con = db()
    cur = con.cursor()

    cur.execute("DELETE FROM students")

    for r in data:
        if r["tz"] or r["name"]:
            cur.execute(
                "INSERT INTO students VALUES (?,?)",
                (r["tz"], r["name"])
            )

    con.commit()
    con.close()

    return {"ok": True}

@app.route("/change_password", methods=["POST"])
def change():

    if not session.get("login"):
        return ""

    p = request.form["newpass"]

    con = db()
    cur = con.cursor()

    cur.execute("DELETE FROM password")

    cur.execute(
        "INSERT INTO password VALUES (?)",
        (p,)
    )

    con.commit()
    con.close()

    return redirect("/system")

@app.route("/excel")
def excel():

    con = db()

    df = pd.read_sql_query(
        "SELECT * FROM students",
        con
    )

    file = "report.xlsx"

    df.to_excel(file, index=False)

    con.close()

    return send_file(
        file,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
