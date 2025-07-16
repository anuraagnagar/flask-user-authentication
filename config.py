import os

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

MEDIA_ROOT = os.path.join(BASE_DIR, "accounts", "static", "assets")

UPLOAD_FOLDER = os.path.join(MEDIA_ROOT, "uploads")

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)


class BaseConfig:
    # Application configuration.
    DEBUG = False
    TESTING = False

    SITE_URL = os.getenv("SITE_DOMAIN")

    # Site secret key.
    SECRET_KEY = os.getenv("SECRET_KEY", "my-sekret-key")

    # Default media upload folder.
    DEFAULT_UPLOAD_FOLDER = UPLOAD_FOLDER

    # `Bootstrap UI` themes configuration.
    BOOTSTRAP_DEFAULT_THEME = "pulse"
    BOOTSTRAP_BOOTSWATCH_THEME = BOOTSTRAP_DEFAULT_THEME
    BOOTSTRAP_BOOTSWATCH_THEMES = ["pulse", "sketchy", "flatly", "journal", "lumen"]

    # `WTF Form` and recaptcha configuration.
    WTF_CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", None)
    WTF_CSRF_ENABLED = True

    # SupportedOAuth providers for our application
    OAUTH_PROVIDERS = ["google"]

    # `Google Recaptch` for form protection.
    RECAPTCHA_PUBLIC_KEY = os.getenv("PUBLIC_KEY", None)
    RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_KEY", None)
    RECAPTCHA_USE_SSL = True
    RECAPTCHA_OPTIONS = {"theme": "light"}

    # `Google OAuth` configuration keys.
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = os.getenv("GOOGLE_DISCOVERY_URL", None)
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", None)
    GOOGLE_SCOPE = os.getenv("GOOGLE_SCOPE", "email profile")

    # `SQLAlchemy (ORM)` configuration.
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # `Redis` configuration.
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_POST = os.getenv("REDIST_PORT", "6379")

    # `Flask-Mail` configuration.
    MAIL_SERVER = os.getenv("MAIL_SERVER", None)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # `Flask-Limiter` configuration.
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "True").lower() in ("true", "1")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    # Default `Salt` string for url security tokens.
    SALT_ACCOUNT_CONFIRM = os.getenv("ACCOUNT_CONFIRM_SALT", "account_confirm_salt")
    SALT_RESET_PASSWORD = os.getenv("RESET_PASSWORD_SALT", "reset_password_salt")
    SALT_CHANGE_EMAIL = os.getenv("CHANGE_EMAIL_SALT", "change_email_salt")

    # Default Guest User information.
    TEST_USER_USERNAME = "testuser"
    TEST_USER_EMAIL = "testuser@example.com"
    TEST_USER_PASSWORD = "Test@1234"


class Development(BaseConfig):
    DEBUG = True

    DATABASE_URI = os.getenv("DATABASE_URI")

    USE_LOCAL_DB = os.getenv("USE_LOCAL_DB")

    if USE_LOCAL_DB in ("False", "0") or DATABASE_URI:
        # Using PostgreSQL database in development env.
        SQLALCHEMY_DATABASE_URI = DATABASE_URI
    else:
        # Using SQLite in development env. If Database URI doesn't set.
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "db.sqlite3")


class Production(BaseConfig):
    from sqlalchemy.engine.url import URL
    from sqlalchemy.exc import ArgumentError, OperationalError

    DATABASE_URI = os.getenv("DATABASE_URI", None)

    try:
        if DATABASE_URI:
            SQLALCHEMY_DATABASE_URI = DATABASE_URI
        else:
            SQLALCHEMY_DATABASE_URI = URL.create(
                drivername="postgresql",
                username=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=int(os.getenv("POSTGRES_PORT")),
                database=os.getenv("POSTGRES_DB"),
            )
    except (ArgumentError, OperationalError) as e:
        raise Exception(f"Database connection failed: {e}")


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
