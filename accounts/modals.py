from flask_login.mixins import UserMixin
from werkzeug.security import (
        generate_password_hash,
        check_password_hash
    )
from accounts.extentions import database as db
from accounts.utils import unique_uid
from datetime import datetime


class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(db.String(38), primary_key=True, default=unique_uid(), unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    account = db.Relationship('Activation', backref='user', cascade='save-update, merge, delete')
    profile = db.Relationship('Profile', backref='user', cascade='save-update, merge, delete')

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def __repr__(self):
        return '<User> {}'.format(self.email)


class Activation(db.Model):

    __tablename__ = 'activation'

    id = db.Column(db.String(38), primary_key=True, default=unique_uid(), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=False, nullable=False)
    security_code = db.Column(db.String(6), default='', nullable=False)
    security_token = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    user_id = db.Column(db.String(38), db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return '<Activation> {}'.format(self.user.username)


class Profile(db.Model):

    __tablename__ = 'profile'

    id = db.Column(db.String(38), primary_key=True, default=unique_uid(), unique=True, nullable=False)
    bio = db.Column(db.String(200), default='')
    avator = db.Column(db.String(250), default='')

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    user_id = db.Column(db.String(38), db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return '<Profile> {}'.format(self.user.username)