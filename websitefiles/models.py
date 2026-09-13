from sqlalchemy.sql import func
from flask_login import UserMixin

from . import db


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # Foreign key -> the "user" table's "id" column.
    # The table name is lowercase by default, so it's 'user.id', not 'User.id'.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    # Password hashes from modern Werkzeug (scrypt) are long, so give this room.
    password = db.Column(db.String(256))
    # Gives every User a .notes list, and every Note a .user back-reference.
    notes = db.relationship('Note', backref='user')
