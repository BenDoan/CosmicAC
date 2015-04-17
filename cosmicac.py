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

from model import Model
import platform
import json

app = Flask(__name__)
loginmanager = LoginManager()
loginmanager.init_app(app)

if platform.system().startswith('Win'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\temp\\cosmicac.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/cosmicac.db'

app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

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
    users =  model.User.query.filter_by(username=userid)
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

@login_required
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(request.args.get("redirect"))

@app.route('/getuser', methods=['GET'])
def getuser():
    admin = model.User.query.filter_by(username='admin').first()
    return admin.username

@login_required
@app.route('/signout')
def signout():
    logout_user()
    return redirect('/signin')

##Content
@login_required
@app.route('/', methods=['GET'])
def index():
    if current_user.is_anonymous():
        return redirect("/signin")
    return render_template('index.html', rooms=model.Room.query.all())

@login_required
@app.route('/rooms', methods=['GET'])
def rooms():
    all_rooms = model.Room.query.all()
    return render_template('rooms.html', rooms=all_rooms)

@login_required
@app.route('/profile', methods=['GET', 'POST'])
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

@login_required
@app.route('/admin', methods=['GET'])
def admin():
    if current_user.is_admin:
        return render_template('admin.html', form=AddRoomForm())

@login_required
@app.route('/stats', methods=['GET'])
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

@login_required
@app.route('/room/<room_id>', methods=['GET'])
def room(room_id):
    room = model.Room.query.filter_by(id=room_id).first()
    if not room:
        abort(404)
    return render_template('room.html', room=room)

##Actions
@login_required
@app.route('/user/add', methods=['POST'])
def add_user():
    if current_user.is_admin:
        print request.form
        admin()
    #return render_template('admin.html', form=AddRoomForm())

@login_required
@app.route('/add/room', methods=['POST'])
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

@login_required
@app.route('/checkin', methods=['GET'])
def checkin():
    room = model.Room.query.filter_by(id=request.args.get('id')).first()
    ci = model.UserHistory(current_user, room)
    db.session.add(ci)
    db.session.commit()
    flash("Checked in to {}!".format(room.title), "success")
    return redirect("/")

##Misc
@login_required
@app.route('/js/<remainder>',methods=['GET'])
@app.route('/img/<remainder>',methods=['GET'])
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
