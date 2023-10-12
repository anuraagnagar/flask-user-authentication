from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate


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
migrate = Migrate(command='db') 
