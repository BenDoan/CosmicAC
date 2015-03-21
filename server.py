from flask import *

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from htmlmin import minify
from flask.ext.login import LoginManager,login_user,logout_user, current_user, login_required
from flask_wtf import Form
from wtforms import StringField, PasswordField, TextField, TextAreaField
from wtforms.validators import DataRequired
from passlib.hash import pbkdf2_sha256

from model import Model

app = Flask(__name__)
loginmanager = LoginManager()
loginmanager.init_app(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/cosmicac.db'

app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

assets = Environment(app)
assets.url_expire = False

css = Bundle('css/main.css', 'css/bootstrap.css', 'css/bootstrap-theme.css', filters="cssmin", output='css/gen/packed.css')
assets.register('css_all', css)

model = Model(app)
db = model.db

## Authentication
class LoginForm(Form):
    name = StringField('name',validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired()])

class SignupForm(Form):
    name = StringField('name',validators=[DataRequired()])
    email = StringField('email',validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired()])
    repeatpassword = PasswordField('repeatpassword',validators=[DataRequired()])

class AddRoomForm(Form):
    title = TextField('title',validators=[DataRequired()])
    number = TextField('number',validators=[DataRequired()])
    short_description = TextAreaField('short_description',validators=[DataRequired()])
    long_description = TextAreaField('long_description',validators=[DataRequired()])
    image = TextField('image',validators=[DataRequired()])

def create_user(username,email,password):
    newuser = model.User(username,email)
    newuser.password = pbkdf2_sha256.encrypt(password)
    db.session.add(newuser)
    db.session.commit()
    return newuser

@loginmanager.user_loader
def load_user(userid):
    users =  model.User.query.filter_by(username=userid)
    return users.first()

@app.route('/authenticate', methods=['GET','POST'])
def authenticate():
    print "Authenticating"
    form = LoginForm()
    if form.validate_on_submit():
        users = model.User.query.filter_by(username = request.form["name"])
        user = users.first()
        if user != None :
            if pbkdf2_sha256.verify(request.form["password"],user.password) :
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
    return render_template('index.html')

@login_required
@app.route('/rooms', methods=['GET'])
def rooms():
    return render_template('rooms.html')

@login_required
@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

@login_required
@app.route('/admin', methods=['GET'])
def admin():
    if current_user.is_admin:
        return render_template('admin.html', form=AddRoomForm())

##Actions
@login_required
@app.route('/user/add', methods=['POST'])
def add_user():
    if current_user.is_admin:
        print request.form
        admin()
    #return render_template('admin.html', form=AddRoomForm())

##Misc
@login_required
@app.route('/js/<remainder>',methods=['GET'])
@app.route('/img/<remainder>',methods=['GET'])
def get_static(remainder):
    return send_from_directory(app.static_folder,request.path[1:])

app.secret_key = "Secret"

if __name__ == "__main__":
    app.run(host="0.0.0")
