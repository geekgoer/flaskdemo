from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from Another_eye import db

#注意name 分为Admin , Cityadmin , cityUser三类
class User(db.Model,UserMixin):
    # id = db.column(db.Integer,primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)


class Movie(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(60))
    year= db.Column(db.String(4))