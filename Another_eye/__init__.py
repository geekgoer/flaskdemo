"""
__init__.py文件的存在是为了将一个文件夹作为一个包来处理，
它可以包含初始化代码和定义包级别的变量、函数或类。
无需显式导入__init__.py文件
"""

import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


WIN= sys.platform.startswith('win')
if WIN :
    prefix='sqlite:///'
else :
    prefix='sqlite:////'

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path),os.getenv('DATASET_FILE','data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','dev')

db = SQLAlchemy(app)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    from Another_eye.models import User
    user = User.query.get(int(user_id))
    return user

login_manager.login_view = 'login'

@app.context_processor
def inject_user():
    from Another_eye.models import User
    user = User.query.first()
    return dict(user=user)


# @app.shell_context_processors
# def make_shell_context():
#     return dict(db=db)

from Another_eye import errors, views, commands