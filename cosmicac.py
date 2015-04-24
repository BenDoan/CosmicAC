from flask import *
import logging
from logging.handlers import RotatingFileHandler

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from htmlmin import minify
from flask.ext.login import LoginManager,login_user,logout_user, current_user, login_required
from flask_wtf import Form
from wtforms import StringField, PasswordField, TextField, TextAreaField
from wtforms import validators
from passlib.hash import pbkdf2_sha256

try:
    from perform import zbarimg
except:
    pass

from model import Model

import platform
import json
import os

app = Flask(__name__)
loginmanager = LoginManager()
loginmanager.init_app(app)
# https://flask-login.readthedocs.org/en/latest/
loginmanager.login_view = '/signin'

if platform.system().startswith('Win'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\temp\\cosmicac.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/cosmicac.db'

app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

UPLOAD_FOLDER = "/tmp/cosmicac-pics"
if platform.system().startswith('Win'):
    UPLOAD_FOLDER = "C:\\temp\\cosmicac-pics"

assets = Environment(app)
assets.url_expire = False

css = Bundle('css/bootstrap.css', 'css/main.css', filters="cssmin", output='css/gen/packed.css')
assets.register('css_all', css)

model = Model(app)
db = model.db

## Authentication
class LoginForm(Form):
    name = StringField('name', validators=[validators.DataRequired()])
    password = PasswordField('password', validators=[validators.DataRequired()])

class SignupForm(Form):
    name = StringField('name', validators=[validators.DataRequired()])
    email = StringField('email', validators=[validators.DataRequired()])
    password = PasswordField('password', validators=[validators.DataRequired()])
    repeatpassword = PasswordField('repeatpassword', validators=[validators.DataRequired()])

class AddRoomForm(Form):
    title = TextField('title', validators=[validators.Required()])
    number = TextField('number', validators=[validators.Required()])
    short_description = TextAreaField('short_description')
    long_description = TextAreaField('long_description')
    image = TextField('image')

class EditUserForm(Form):
    name = TextField('name')
    email = TextField('email')
    password = PasswordField('password', [
       validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat password')

def create_user(username, email, password, is_admin=False):
    newuser = model.User(username, email, is_admin)
    newuser.password = pbkdf2_sha256.encrypt(password)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def create_room(name, number, shortDesc, longDesc, img):
    #Image will not be working yet
    newRoom = model.Room(name, number, shortDesc, longDesc, img)
    db.session.add(newRoom)
    db.session.commit()
    return newRoom

def create_userHistory(userName, roomName):
    users = model.User.query.filter_by(username=userName)
    user = users.first()
    rooms = model.Room.query.filter_by(title=roomName)
    room = rooms.first()
    newhistory = model.UserHistory(user, room)
    db.session.add(newhistory)
    db.session.commit()
    return newhistory

@loginmanager.user_loader
def load_user(userid):
    users = model.User.query.filter_by(username=userid)
    return users.first()

@app.route('/authenticate', methods=['GET','POST'])
def authenticate():
    print "Authenticating"
    form = LoginForm()
    if form.validate_on_submit():
        users = model.User.query.filter_by(username=request.form["name"])
        user = users.first()
        if user != None :
            if pbkdf2_sha256.verify(request.form["password"], user.password) :
                user.authenticated = True
                db.session.commit()
                login_user(user)
    return redirect(request.form["redirect"])

@app.route('/signin', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'GET' :
        return render_template("signin.html",form = form,error = "")
    error = "some fields were empty"
    if form.validate_on_submit():
        users = model.User.query.filter_by(username = request.form["name"])
        user = users.first()
        if user != None :
            if pbkdf2_sha256.verify(request.form["password"],user.password) :
                user.authenticated = True
                db.session.commit()
                login_user(user)
                return redirect("/")
        error = "incorrect username or password"
    return render_template("signin.html",form = form,error = error);

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = SignupForm()
    if request.method == 'GET' :
        return render_template("signup.html",form = form,error="")
    error = "some fields were empty"
    if form.validate_on_submit():
        error = "some fields were empty"
        if request.form["password"] == request.form["repeatpassword"]:
            user = create_user(request.form["name"], request.form["email"], request.form["password"])
            user.authenticated = True
            db.session.commit()
            login_user(user)
            return redirect("/")
        else:
            error = "passwords did not match"
    return render_template("signup.html",form = form,error=error)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(request.args.get("redirect"))

@app.route('/getuser', methods=['GET'])
def getuser():
    admin = model.User.query.filter_by(username='admin').first()
    return admin.username

@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect('/signin')

##Content
# I think we shouldn't have @login_required here?
@app.route('/', methods=['GET'])
def index():
    if current_user.is_anonymous():
        return redirect("/signin")
    return render_template('index.html', rooms=model.Room.query.all())

@app.route('/rooms', methods=['GET'])
@login_required
def rooms():
    all_rooms = model.Room.query.all()
    return render_template('rooms.html', rooms=all_rooms)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == "POST":
        form = EditUserForm()
        if not form.validate_on_submit():
            for error in form.errors:
                flash("Error for {}".format(error), "danger")
            return render_template("profile.html", form=form)

        current_user.username = form.name.data
        current_user.email = form.email.data
        if form.password.data.strip() != "":
            current_user.password = pbkdf2_sha256.encrypt(form.password.data)
        db.session.commit()
        flash("User updated", "success")
    return render_template('profile.html', form=EditUserForm())

@app.route('/admin', methods=['GET'])
@login_required
def admin():
    if current_user.is_admin:
        return render_template('admin.html', form=AddRoomForm())
    # If the user isn't an admin, return them to /
    return redirect("/")

@app.route('/stats', methods=['GET'])
@login_required
def stats():
    users = model.UserHistory.query.all()
    list1 = [{"text": "Java", "count": "236"},{"text": ".Net", "count": "382"}]
    user = users[0]
    if current_user.is_admin:
        return render_template('stats.html')

@app.route('/_get_stats')
def get_stats():
    histories = model.UserHistory.query.all()
    result = list()
    indexes = list()
    for i in range(0, len(histories)):
        indexOfRoom = -1
        for k, j in enumerate(indexes):
            if j == histories[i].room.title:
               indexOfRoom = k
        if(indexOfRoom >= 0):
           result[indexOfRoom]["count"] = str(int(result[indexOfRoom]["count"]) + 1)
        else:
           indexes.extend([histories[i].room.title])
           result.extend([{"text": histories[i].room.title, "count": "1"}])
    return Response(json.dumps(result), mimetype='application/json')

@app.route('/_get_time_stats')
def get_time_stats():
    histories = model.UserHistory.query.all()
    result = list()
    indexes = list()
    firstTimeDay = 32
    firstTimeHour = 25
    LastTimeDay = 0
    LastTimeHour = 0
    result.extend([['x']])
    result.extend([['number of visits over time']])
    result[0].extend(['05 05'])
    result[1].extend([30])
    result[0].extend(['05 06'])
    result[1].extend([20])
    listOfTimes = list()
    
    for i in range(0, len(histories)):
       listOfTimes.append(histories[i].get_local_time())
       """ day, hour = histories[i].time.split()
        month, day = day.split('/')
        hour, minute = hour.split(':')
        if int(day) < firstTimeDay and int(hour) < firstTimeHour:
            firstTimeDay = int(day)
            firstTimeHour = int(hour)
        if int(day) > LastTimeDay and int(hour) < LastTimeHour:
            LastTimeDay = int(day)
            LastTimeHour = int(hour)"""
    listOfTimes.sort()
    listOfHours = list()
    for i in range(0, len(listOfTimes)):
        listOfHours.append(str(listOfTimes[i]))
    return Response(json.dumps(listOfHours), mimetype="application/json")

@app.route('/room/<room_id>', methods=['GET'])
@login_required
def room(room_id):
    room = model.Room.query.filter_by(id=room_id).first()
    if not room:
        abort(404)
    return render_template('room.html', room=room)

@app.route('/takepicture', methods=['GET'])
@login_required
def takepicture():
    return render_template('takepicture.html')

##Actions
@app.route('/user/add', methods=['POST'])
@login_required
def add_user():
    if current_user.is_admin:
        print request.form
        admin()
    #return render_template('admin.html', form=AddRoomForm())

@app.route('/add/room', methods=['POST'])
@login_required
def add_room():
    if current_user.is_admin:
        form = AddRoomForm()
        if not form.validate_on_submit():
            for error in form.errors:
                flash("Missing room {}".format(error), "danger")
            return render_template("admin.html", form=form)

        flash("Room added", "success")
        room = model.Room(form.title.data, form.number.data, form.short_description.data, form.long_description.data)
        db.session.add(room)
        db.session.commit()

        return redirect("/admin")
    else:
        abort("418")

# Hybrid QR-codes could go to this view. A QR code might contain:
# flainted.com:3000/checkin?id=1
# A user could scan this with their QR code reader, or with our app (which could parse for the id parameter).
@app.route('/checkin', methods=['GET'])
def checkin():
    # If the user is anonymous (meaning not logged-in), then this is probably a first-time user.
    # Display a helpful message about our web application and how they can get started. 
    if current_user.is_anonymous():
        flash("Howdy, and welcome to CosmicAC! You can use this web app to scan the " +
              "QR codes lying around and get cool information about each room! " +
              "First, log in or make an account.", "info")
        return redirect("/signin")

    roomId = request.args.get('id')

    # Redirect to / if no id parameter was specified
    if roomId is None:
        return redirect("/")

    room = model.Room.query.filter_by(id=roomId).first()

    ci = model.UserHistory(current_user, room)
    db.session.add(ci)
    db.session.commit()
    flash("Checked in to {}!".format(room.title), "success")

    return redirect("/room/" + roomId)

@app.route('/receivepicture', methods=['POST'])
@login_required
def recievepicture():
    f = request.files['picture']
    if f:
        path = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(path)
        if verify_qr(path):
            flash("Checked in!", "success")
            return redirect('/')
        else:
            flash("Invalid QR code", "danger")
            return redirect('/')

##Misc
def verify_qr(path):
    contents = zbarimg(path)
    return "password" in contents

@app.route('/js/<remainder>', methods=['GET'])
@app.route('/img/<remainder>', methods=['GET'])
@login_required
def get_static(remainder):
    return send_from_directory(app.static_folder,request.path[1:])

app.secret_key = "Secret"


## Example Logging
## app.logger.error("added: " + str(histories[i].room.title))
if __name__ == "__main__":
    handler = RotatingFileHandler('log.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    app.run(host="0.0.0.0")
