
import os
from flask import Flask,render_template,request,redirect,jsonify,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user
from datetime import datetime
from openpyxl import Workbook

app=Flask(__name__)
app.secret_key="secret"

app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("DATABASE_URL","sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db=SQLAlchemy(app)
login_manager=LoginManager(app)

class User(UserMixin,db.Model):
 id=db.Column(db.Integer,primary_key=True)
 username=db.Column(db.String(50),unique=True)
 password=db.Column(db.String(200))

class Student(db.Model):
 id=db.Column(db.Integer,primary_key=True)
 tz=db.Column(db.String(20),unique=True)
 name=db.Column(db.String(100))

class Day(db.Model):
 id=db.Column(db.Integer,primary_key=True)
 name=db.Column(db.String(50))
 active=db.Column(db.Boolean)

class Seder(db.Model):
 id=db.Column(db.Integer,primary_key=True)
 name=db.Column(db.String(50))
 start=db.Column(db.String(5))
 amount=db.Column(db.Float)
 late=db.Column(db.Float)

class Attendance(db.Model):
 id=db.Column(db.Integer,primary_key=True)
 student_id=db.Column(db.Integer)
 day_id=db.Column(db.Integer)
 s1=db.Column(db.String(5))
 s2=db.Column(db.String(5))
 s3=db.Column(db.String(5))
 total=db.Column(db.Float)

@login_manager.user_loader
def load_user(id):
 return User.query.get(int(id))

def minutes_late(start,arrival):

 h1,m1=map(int,start.split(":"))
 h2,m2=map(int,arrival.split(":"))

 s=h1*60+m1
 a=h2*60+m2

 return max(0,a-s)

def calc_payment(start,arrival,amount,late):

 late_min=minutes_late(start,arrival)

 steps=late_min//10

 deduction=steps*late

 return max(0,amount-deduction)

with app.app_context():

 db.create_all()

 if not User.query.first():
  db.session.add(User(username="admin",password="1234"))

 if not Seder.query.first():
  db.session.add(Seder(name="סדר א",start="08:00",amount=10,late=2))
  db.session.add(Seder(name="סדר ב",start="14:00",amount=10,late=2))
  db.session.add(Seder(name="סדר ג",start="20:00",amount=10,late=2))

 db.session.commit()

@app.route("/")
def home():
 return redirect("/login")

@app.route("/login",methods=["GET","POST"])
def login():

 if request.method=="POST":

  u=User.query.filter_by(username=request.form["username"]).first()

  if u and u.password==request.form["password"]:
   login_user(u)
   return redirect("/dashboard")

 return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():

 students=Student.query.all()
 days=Day.query.filter_by(active=True).all()

 return render_template("dashboard.html",students=students,days=days)

@app.route("/logout")
def logout():
 logout_user()
 return redirect("/login")

@app.route("/api/students")
def students():

 s=Student.query.all()

 return jsonify([{"tz":x.tz,"name":x.name} for x in s])

@app.route("/download")
def download():

 wb=Workbook()
 ws=wb.active

 ws.append(["תז","שם","סהכ"])

 for s in Student.query.all():

  rows=Attendance.query.filter_by(student_id=s.id).all()

  total=sum([r.total or 0 for r in rows])

  ws.append([s.tz,s.name,total])

 name="עדכון_ישיבת_בין_הזמנים_"+datetime.now().strftime("%Y_%m_%d_%H_%M")+".xlsx"

 path="/tmp/"+name

 wb.save(path)

 return send_file(path,as_attachment=True,download_name=name)

@app.route("/api/phone")
def phone():

 action=request.args.get("action")

 if action=="students":

  s=Student.query.all()

  return jsonify([{"tz":x.tz,"name":x.name} for x in s])

 return jsonify({"ok":1})

if __name__=="__main__":
 app.run()
