#!flask/bin/python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('app.config.Config')
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'

from app import views, models
