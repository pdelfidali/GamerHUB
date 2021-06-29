from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(1500), default='Miejsce na Twój opis')
    steamID = db.Column(db.String(100), default='')
    lolProfileLink = db.Column(db.String(100), default='')
    discord = db.Column(db.String(50), default='')

    @property
    def password(self):
        raise AttributeError('Password is protected')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def __repr__(self):
        return f'User: {self.username} , id: {self.id}, email: {self.email}'


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(64))
    title = db.Column(db.String(15))
    content = db.Column(db.String(1500))
    date = db.Column(db.DateTime)
    game = db.Column(db.String(64))
    open = db.Column(db.Boolean, default=True)
    amount = db.Column(db.Integer)
    lastEdit = db.Column(db.DateTime)

    def __repr__(self):
        return f'{self.creator}:{self.title}'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(64))
    content = db.Column(db.String(1500))
    date = db.Column(db.DateTime)
    announcement = db.Column(db.Integer)


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
