
import os
from flask import Flask,render_template,request,redirect,jsonify,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
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
 username=db.Column(db.String(50))
 password=db.Column(db.String(50))

class Student(db.Model):
 id=db.Column(db.Integer,primary_key=True)
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
 day=db.Column(db.String(10))
 s1=db.Column(db.String(5))
 s2=db.Column(db.String(5))
 s3=db.Column(db.String(5))
 total=db.Column(db.Float)

@login_manager.user_loader
def load_user(id):
 return User.query.get(int(id))

def calc(start,arr,amount,late):
 if not arr: return 0
 h1,m1=map(int,start.split(":"))
 h2,m2=map(int,arr.split(":"))
 late_min=max(0,(h2*60+m2)-(h1*60+m1))
 return max(0,amount-(late_min//10)*late)

with app.app_context():
 db.create_all()

 if not User.query.first():
  db.session.add(User(username="admin",password="1234"))

 if not Seder.query.first():
  db.session.add(Seder(name="א",start="08:00",amount=10,late=2))
  db.session.add(Seder(name="ב",start="14:00",amount=10,late=2))
  db.session.add(Seder(name="ג",start="20:00",amount=10,late=2))

 if not Day.query.first():
  for d in ["א","ב","ג","ד","ה"]:
   db.session.add(Day(name=d,active=True))

 db.session.commit()

@app.route("/",methods=["GET","POST"])
def login():
 if request.method=="POST":
  u=User.query.filter_by(username=request.form["u"]).first()
  if u and u.password==request.form["p"]:
   login_user(u)
   return redirect("/dash")
 return render_template("login.html")

@app.route("/dash")
@login_required
def dash():
 students=Student.query.all()
 days=[d.name for d in Day.query.filter_by(active=True)]
 return render_template("dash.html",students=students,days=days)

@app.route("/save",methods=["POST"])
def save():
 data=request.json
 s=Seder.query.all()

 total=0
 total+=calc(s[0].start,data["s1"],s[0].amount,s[0].late)
 total+=calc(s[1].start,data["s2"],s[1].amount,s[1].late)
 total+=calc(s[2].start,data["s3"],s[2].amount,s[2].late)

 a=Attendance.query.filter_by(student_id=data["id"],day=data["day"]).first()

 if not a:
  a=Attendance(student_id=data["id"],day=data["day"])

 a.s1=data["s1"]
 a.s2=data["s2"]
 a.s3=data["s3"]
 a.total=total

 db.session.add(a)
 db.session.commit()

 return {"total":total}

@app.route("/students",methods=["POST"])
def students():
 db.session.add(Student(name=request.form["name"]))
 db.session.commit()
 return "ok"

@app.route("/download")
def download():
 wb=Workbook()
 ws=wb.active
 ws.append(["שם","סהכ"])

 for s in Student.query.all():
  rows=Attendance.query.filter_by(student_id=s.id).all()
  total=sum([r.total or 0 for r in rows])
  ws.append([s.name,total])

 name="report_"+datetime.now().strftime("%Y%m%d%H%M")+".xlsx"
 path="/tmp/"+name
 wb.save(path)

 return send_file(path,as_attachment=True,download_name=name)

@app.route("/api/phone/get")
def phone_get():
 return jsonify({"students":[s.name for s in Student.query.all()]})

@app.route("/api/phone/update",methods=["POST"])
def phone_update():
 return {"ok":1}

if __name__=="__main__":
 app.run()
