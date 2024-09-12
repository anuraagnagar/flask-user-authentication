import os

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

MEDIA_ROOT = os.path.join(BASE_DIR, "accounts", "static", "assets")

UPLOAD_FOLDER = os.path.join(MEDIA_ROOT, "profile")

load_dotenv(os.path.join(BASE_DIR, ".env"))


class BaseConfig:
    # Application configuration
    DEBUG = False
    TESTING = False

    SITE_URL = os.getenv("SITE_DOMAIN")

    # Site secret key or bootstrap UI theme.
    SECRET_KEY = os.getenv("SECRET_KEY", "my-sekret-key")
    BOOTSTRAP_BOOTSWATCH_THEME = "sketchy"

    # WTF Form and recaptcha configuration
    WTF_CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", None)
    WTF_CSRF_ENABLED = True

    RECAPTCHA_PUBLIC_KEY = os.getenv("PUBLIC_KEY", None)
    RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_KEY", None)

    # SQLAlchemy (ORM) configuration
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", None)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)
    MAIL_PORT = 465
    MAIL_USE_TLS = False

    # Default Salt string for security tokens
    ACCOUNT_CONFIRM_SALT = os.getenv("ACCOUNT_CONFIRM_SALT", "account_confirm_salt")
    RESET_PASSWORD_SALT = os.getenv("RESET_PASSWORD_SALT", "reset_password_salt")
    CHANGE_EMAIL_SALT = os.getenv("CHANGE_EMAIL_SALT", "change_email_salt")


class Development(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", None)


class Production(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", None)


class Testing(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR, "db.testing.sqlite3"
    )

    # Disable CSRF protection for testing.
    WTF_CSRF_ENABLED = False


development = Development()

production = Production()

testing = Testing()
