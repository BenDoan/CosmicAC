from flask.ext.sqlalchemy import SQLAlchemy
from flask import Markup

import markdown

import calendar

from datetime import datetime, timedelta

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
                self.image = "/static/img/lab.jpg"

            def __str__(self):
                return "Room: {}".format((self.id, self.title, self.number, self.short_description, self.long_description))

            def get_id_num(self):
                return self.id

            def get_markdown_long_desc(self):
                return Markup(markdown.markdown(self.long_description))

        self.Room = Room

        class User(self.db.Model):
            __tablename__ = 'users'

            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(80), unique=True)
            email = db.Column(db.String(120), unique=True)
            password = db.Column(db.String)
            authenticated = db.Column(db.Boolean())
            is_admin = db.Column(db.Boolean())

            def __init__(self, name, email, is_admin=False):
                self.name = name
                self.email = email
                self.authenticated = False
                self.is_admin = is_admin

            def __str__(self):
                return "User: {}".format((self.id, self.name, self.email, self.password, self.authenticated, self.is_admin))

            def is_authenticated(self) :
                return self.authenticated

            def is_active(self) :
                return self.is_authenticated()

            def is_anonymous(self) :
                return False

            def get_id(self) :
                return self.email

            def get_id_num(self):
                return self.id

        class UserHistory(self.db.Model):
            __tablename__ = 'user_history'

            id = db.Column(db.Integer, primary_key=True)
            time = db.Column(db.DateTime, default=datetime.utcnow())

            user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
            user = db.relationship('User', backref=db.backref('UserHistory', lazy='dynamic'))

            room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
            room = db.relationship('Room', backref=db.backref('UserHistory', lazy='dynamic'))

            def __init__(self, user, room):
                self.user = user
                self.room = room

            def get_local_time(self):
                def utc_to_local(utc_dt):
                    # get integer timestamp to avoid precision lost
                    timestamp = calendar.timegm(utc_dt.timetuple())
                    local_dt = datetime.fromtimestamp(timestamp)
                    return local_dt.replace(microsecond=utc_dt.microsecond)
                return utc_to_local(self.time)

        self.User = User
        self.UserHistory = UserHistory
