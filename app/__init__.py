from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_babel import Babel, _

from app.config import Configuration


application = Flask(__name__)
application.config.from_object(Configuration)

db = SQLAlchemy(application)
login_manager = LoginManager(application)
migrate = Migrate(application, db, render_as_batch=True)
admin = Admin()

def get_locale():
    lang = request.cookies.get('lang')
    if lang:
        return lang
    return request.accept_languages.best_match(application.config['BABEL_SUPPORTED_LOCALES'])

babel = Babel(application, locale_selector=get_locale)


