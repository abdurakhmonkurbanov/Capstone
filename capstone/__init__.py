from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from capstone.models import db

app = Flask(__name__)
db.app = app
db.init_app=app

from capstone import views