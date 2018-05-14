from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config as conf
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(conf)
login_manager = LoginManager()
login_manager.init_app(app=app)
db = SQLAlchemy(app)

from . import controller
