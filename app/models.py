#!flask/bin/python3
from app import db, lm
from flask_login import UserMixin


class User(UserMixin, db.Model):
    # __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    files = db.relationship('File', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}, Social {}>'.format(self.nickname, self.social_id)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_url = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % self.result_path


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
