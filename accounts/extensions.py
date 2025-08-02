from authlib.integrations.flask_client import OAuth
from flask_bootstrap import Bootstrap5
from flask_login import current_user, LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate
from flask_babel import Babel

# A bootstrap5 class for styling client side.
bootstrap = Bootstrap5()

# csrf protection for form submission.
csrf = CSRFProtect()

# database for managing user data.
database = SQLAlchemy()

# login manager for managing user authentication.
login_manager = LoginManager()

# flask-mail for sending email.
mail = Mail()

# flask_migrate - Migration for database
migrate = Migrate()

# Oauth Client for Social Open Authenrication.
oauth = OAuth()

# Multi language support using Flask-Babel
babel = Babel()


def __key_func() -> str:
    """
    Key function for rate limiting. This function is used to identify the user.

    Returns:
        str: A unique key for the user or IP address.
    """
    if current_user.is_authenticated:
        return f"user_id:{current_user.get_id()}"
    else:
        ip_address = get_remote_address()
        return f"ip:{ip_address}"


# flask limiter for rate limiting.
limiter = Limiter(
    key_func=__key_func,
    default_limits=["200 per day", "85 per hour", "20 per minute"],
)
