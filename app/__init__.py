from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from app.config import Configuration


application = Flask(__name__)
application.config.from_object(Configuration)

db = SQLAlchemy(application)
login_manager = LoginManager(application)
migrate = Migrate(application, db, render_as_batch=True)
admin = Admin()
