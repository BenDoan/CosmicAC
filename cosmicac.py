from flask import *
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
    logging.critical("Couldn't import zbarimg")

from model import Model

import json
import logging
import os
import platform

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
    email = StringField('email', validators=[validators.DataRequired()])
    password = PasswordField('password', validators=[validators.DataRequired()])

class SignupForm(Form):
    name = StringField('name', validators=[validators.DataRequired()])
    email = StringField('email', validators=[validators.DataRequired()])
    password = PasswordField('password', validators=[validators.DataRequired()])
    repeatpassword = PasswordField('repeatpassword', validators=[validators.DataRequired()])

class EditRoomForm(Form):
    title = TextField('title', validators=[validators.Required()])
    number = TextField('number', validators=[validators.Required()])
    short_description = TextField('short_description')
    long_description = TextAreaField('long_description')
    image = TextField('image')

class EditUserForm(Form):
    name = TextField('name')
    email = TextField('email')
    password = PasswordField('password', [
       validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat password')

def create_user(name, email, password, is_admin=False):
    newuser = model.User(name, email, is_admin)
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

def create_userHistory(name, roomName):
    users = model.User.query.filter_by(name=name)
    user = users.first()
    rooms = model.Room.query.filter_by(title=roomName)
    room = rooms.first()
    newhistory = model.UserHistory(user, room)
    db.session.add(newhistory)
    db.session.commit()
    return newhistory

@loginmanager.user_loader
def load_user(email):
    users = model.User.query.filter_by(email=email)
    return users.first()

@app.route('/authenticate', methods=['GET','POST'])
def authenticate():
    print "Authenticating"
    form = LoginForm()
    if form.validate_on_submit():
        users = model.User.query.filter_by(email=form.email.data)
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
        user = model.User.query.filter_by(email=request.form["email"]).first()
        if user != None :
            if pbkdf2_sha256.verify(request.form["password"],user.password) :
                user.authenticated = True
                db.session.commit()
                login_user(user)
                return redirect("/")
        error = "incorrect email or password"
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

        current_user.name = form.name.data
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
        users = model.User.query.all()
        rooms = model.Room.query.all()
        return render_template('admin.html', users=users, rooms=rooms)
    # If the user isn't an admin, return them to /
    return abort(403)

@app.route('/add/user', methods=['GET', 'POST'])
@login_required
def user_add():
    form = EditUserForm()
    if current_user.is_admin:
        if request.method == "POST":
            if not form.validate_on_submit():
                for error in form.errors:
                    flash("Error for {}".format(error), "danger")
                return render_template("add/user.html", form=form)

            user = model.User(form.name.data, form.email.data)
            user.password = pbkdf2_sha256.encrypt(form.password.data)

            db.session.add(user)
            db.session.commit()
            flash("User added", "success")
            return redirect("/admin")
        return render_template("add/user.html", form=EditUserForm())
    abort(403)

@app.route('/edit/user/<user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    form = EditUserForm()
    if current_user.is_admin:
        user = model.User.query.filter_by(id=user_id).first()
        if request.method == "POST":
            if not form.validate_on_submit():
                for error in form.errors:
                    flash("Error for {}".format(error), "danger")
                return render_template("add/user.html", form=form)

            user.name = form.name.data
            user.email = form.email.data
            user.password = pbkdf2_sha256.encrypt(form.password.data)

            db.session.commit()
            flash("User edited", "success")
            return redirect("/admin")
        return render_template("edit/user.html", form=EditUserForm(), user=user)
    abort(403)

@app.route('/delete/user/<user_id>', methods=['GET'])
@login_required
def user_delete(user_id):
    if current_user.is_admin:
        user = model.User.query.filter_by(id=user_id)
        flash("User {} deleted".format(user.first().name), "success")
        user.delete()
        db.session.commit()
        return redirect("/admin")
    abort(403)

@app.route('/add/room', methods=['GET', 'POST'])
@login_required
def room_add():
    form = EditRoomForm()
    if current_user.is_admin:
        if request.method == "POST":
            if not form.validate_on_submit():
                for error in form.errors:
                    flash("Error for {}".format(error), "danger")
                return render_template("add/room.html", form=form)

            room = model.Room(form.title.data,
                              form.number.data,
                              form.short_description.data,
                              form.long_description.data,
                              form.image.data)

            db.session.add(room)
            db.session.commit()
            flash("Room added", "success")
            return redirect("/admin")
        return render_template("add/room.html", form=EditRoomForm())
    abort(403)

@app.route('/edit/room/<room_id>', methods=['GET', 'POST'])
@login_required
def room_edit(room_id):
    form = EditRoomForm()
    if current_user.is_admin:
        room = model.Room.query.filter_by(id=room_id).first()
        if request.method == "POST":
            if not form.validate_on_submit():
                for error in form.errors:
                    flash("Error for {}".format(error), "danger")
                return render_template("add/room.html", form=form)

            room.title = form.title.data
            room.number = form.number.data
            room.short_description = form.short_description.data
            room.long_description = form.long_description.data
            room.image = form.image.data

            db.session.commit()
            flash("Room edited", "success")
            return redirect('/admin')
        new_edit_form = EditRoomForm()
        new_edit_form.long_description.data = room.long_description
        return render_template("edit/room.html", form=new_edit_form, room=room)
    abort(403)

@app.route('/delete/room/<room_id>', methods=['GET'])
@login_required
def room_delete(room_id):
    if current_user.is_admin:
        room = model.Room.query.filter_by(id=room_id)
        flash("Room {} deleted".format(room.first().title), "success")
        room.delete()
        db.session.commit()
        return redirect("/admin")
    abort(403)

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
    result.extend([['number of visits over time (day hour)']])
    listOfTimes = list()
    listOfHours = list()
    for i in range(0, len(histories)):
       listOfTimes.append(histories[i].get_local_time())
    listOfTimes.sort()
    minTime = listOfTimes[0]
    maxTime = listOfTimes[-1]
    delta = maxTime - minTime
    numHoursBetween = delta.days * 24
    numHoursBetween += delta.seconds / 3600
    if delta.seconds % 3600 != 0:
        numHoursBetween += 1
    currentDay = minTime.day
    currentHour = minTime.hour

    for i in range (0, numHoursBetween + 1):
        if (str(currentDay) +" " + str(currentHour)) not in result[0]:
            result[0].extend([str(currentDay) +" " + str(currentHour)])
            result[1].extend([0])
        currentHour +=1
        if currentHour > 23:
            currentDay += 1
            currentHour = 0
    for i in range(0, len(histories)):
        index = -1
        for j in range(0, len(result[0])):
            if str(result[0][j][:2]) == str(histories[i].get_local_time().day) and str(result[0][j][-2:]) == str(histories[i].get_local_time().hour):
                index = j
                break
        if index != -1:
            result[1][index] = int(result[1][index]) + 1
    return Response(json.dumps(result), mimetype="application/json")

@app.route('/room/<room_id>', methods=['GET'])
@login_required
def room(room_id):
    room = model.Room.query.filter_by(id=room_id).first()
    if not room:
        abort(403)
    return render_template('room.html', room=room)

@app.route('/takepicture', methods=['GET'])
@login_required
def takepicture():
    return render_template('takepicture.html')

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
        text = verify_qr(path)
        if text:
            room_id = text.split("Room")[-1]
            room = model.Room.query.filter_by(id=room_id).first()

            ci = model.UserHistory(current_user, room)
            db.session.add(ci)
            db.session.commit()
            flash("Checked in to {}!".format(room.title), "success")
            return redirect('/room/{}'.format(room.id))
        else:
            flash("Invalid QR code", "danger")
            return redirect('/')

##Misc
def verify_qr(path):
    contents = zbarimg(path)
    print "QR code contents are {}".format(contents)
    if "Room" not in contents:
        return None
    return contents.strip()

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
