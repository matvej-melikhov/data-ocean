import os
from dotenv import load_dotenv

load_dotenv()

class Configuration():
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

    # Railway даёт DATABASE_URL для PostgreSQL.
    # Локально используем SQLite.
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///base.db")
    # SQLAlchemy 2.x требует postgresql://, а не postgres://
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['ru', 'en']
