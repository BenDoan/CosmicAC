from flask.ext.sqlalchemy import SQLAlchemy

class Model():
    def __init__(self, app):
        self.db = SQLAlchemy(app)
        db = self.db

        class Room(db.Model):
            __tablename__ = 'rooms'

            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String)
            number = db.Column(db.String)
            short_description = db.Column(db.String)
            long_description = db.Column(db.String)
            image = db.Column(db.String)

            def __init__(self, title, number, short_description="", long_description="", image=""):
                self.title = title
                self.number = number
                self.short_description = short_description
                self.long_description = long_description
                self.image = image

            def __str__(self):
				return "Room: {}".format((self.id, self.title, self.number, self.short_description, self.long_description))
				
            def get_id_num(self):
			    return self.id

        self.Room = Room

        class User(self.db.Model):
            __tablename__ = 'users'

            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True)
            email = db.Column(db.String(120), unique=True)
            password = db.Column(db.String)
            authenticated = db.Column(db.Boolean())
            is_admin = db.Column(db.Boolean())

            def __init__(self, username, email, is_admin=False):
                self.username = username
                self.email = email
                self.authenticated = False
                self.is_admin = is_admin

            def __str__(self):
                return "User: {}".format((self.id, self.username, self.email, self.password, self.authenticated, self.is_admin))

            def is_authenticated(self) :
                return self.authenticated

            def is_active(self) :
                return self.is_authenticated()

            def is_anonymous(self) :
                return False

            def get_id(self) :
				return self.username
			
            def get_id_num(self):
			    return self.id

        class UserHistory(self.db.Model):
            __tablename__ = 'user_history'

            id = db.Column(db.Integer, primary_key=True)

            user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
            user = db.relationship('User', backref=db.backref('UserHistory', lazy='dynamic'))

            room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
            room = db.relationship('Room', backref=db.backref('UserHistory', lazy='dynamic'))

            def __init__(self, user, room):
                self.user = user
                self.room = room

        self.User = User
        self.UserHistory = UserHistory
