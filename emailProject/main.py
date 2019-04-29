from flask import Flask, request, redirect, g, render_template, Response, session, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import json
import hashlib
import jsonpickle
import datetime
import smtplib, ssl
from email.mime.text import MIMEText

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "test.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)
PORT = 5555

class User(db.Model):
    #__tablename__ = 'users'
    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, primary_key=False)
    password = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)


class Email(db.Model):
    #__tablename__ = 'emails'
    emailID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, unique=False, nullable=False,primary_key=False)
    recipient = subject = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    subject = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    body = db.Column(db.String(1000), unique=False, nullable=False, primary_key=False)
    sent_time = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)

def sendEmail(emailTo, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "cset3200project@gmail.com"
    FROM = "cset3200project@gmail.com"
    msg['To'] = emailTo

    server = smtplib.SMTP('smtp.gmail.com:587')
    password = "BK8DTYx8UnrgyM2"

    server.starttls()
    server.login(FROM,password)
    server.sendmail(FROM, emailTo, msg.as_string())
    server.quit()

@app.route("/",methods = ['GET','POST'])
def index():
    return render_template("index.html")

@app.route("/signup_auth", methods = ['POST'])
def handle():
        if request.form:
            try:
                render = True
                password = request.form.get("psw")
                password = hashlib.sha256(password.encode()).hexdigest()
                user = User(username=request.form.get("uname"), password=password)
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                errorMessage = "Username already exists"
                render = False
                return render_template("index.html", error=errorMessage)
            if(render):
                users = User.query.all()
                return render_template("created.html", users=users)

@app.route("/login_auth", methods = ['POST'])
def login():
    if request.form:
        password = request.form.get("psw")
        password = hashlib.sha256(password.encode()).hexdigest()
        username = request.form.get("uname")

        user = User.query.filter_by(username=username).first()
        if(user.password == password):
            user = jsonpickle.encode(user)
            session["user"] = user
            return redirect(url_for('.emailViewer', user=user))
        else:
            error = "Incorrect password"
            return render_template("index.html",error=error)


@app.route("/email", methods= ['GET','POST'])
def emailViewer():
    user = jsonpickle.decode(session["user"])
    emails = Email.query.filter(Email.userID == user.userID)
    return render_template("email.html",emails=emails)

@app.route("/email_handler", methods = ['GET','POST'])
def emailHandler():
    if request.form:
        user = jsonpickle.decode(session["user"])
        emailTo = request.form.get("emailTo")
        subject = request.form.get("subject")
        body = request.form.get("body")
        time = datetime.datetime.now().strftime("%B %d, %Y %I:%M%p")
        email = Email(userID=user.userID,recipient=emailTo,subject=subject,body=body,sent_time=time)
        db.session.add(email)
        db.session.commit()

        sendEmail(email.recipient,email.subject,email.body)

        return redirect("/email")

@app.route("/delete", methods=["POST"])
def delete():
    emailID = request.form.get("emailID")
    email = Email.query.filter_by(emailID=emailID).first()
    db.session.delete(email)
    db.session.commit()
    return redirect("/email")

@app.route("/print", methods=['GET','POST'])
def print():
    emailID = request.form.get("emailID")
    email = email = Email.query.filter_by(emailID=emailID).first()
    
    recipient = email.recipient
    subject = email.subject
    body = email.body
    return render_template("print.html",recipient=recipient, subject=subject, body=body)

@app.route("/viewEmail", methods=['GET','POST'])
def viewEmail():
    emailID = request.form.get("emailID")
    email = email = Email.query.filter_by(emailID=emailID).first()
    
    recipient = email.recipient
    subject = email.subject
    body = email.body
    return render_template("view.html",recipient=recipient, subject=subject, body=body)

@app.route("/createAccount", methods=['GET','POST'])
def createAccount():
    return render_template("create.html")

@app.route("/logout")
def logout():
    return redirect("/")



if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True,port=PORT)
