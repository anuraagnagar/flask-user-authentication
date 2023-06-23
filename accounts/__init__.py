import os
from flask import Flask
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def create_app():
    """
    Create and configure the Flask application instance.
    """
    app = Flask(__name__, template_folder="templates")

    # application configuration.
    config_application(app)
    # register account blueprint.
    config_blueprint(app)
    # config application extension. 
    config_extention(app)

    return app

def config_application(app):
    app.config["DEBUG"] = True
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", None)

    # SQLAlchemy configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

def config_blueprint(app):
    """
    Configure and register blueprints with the Flask application.
    """
    from .views import accounts
    app.register_blueprint(accounts)

def config_extention(app):
    """
    Configure application extensions.
    """
    from .extentions import login_manager
    from .extentions import bootstrap
    from .extentions import database
    from .extentions import migrate
    from .extentions import csrf
    
    login_manager.init_app(app)
    bootstrap.init_app(app)
    database.init_app(app)
    migrate.init_app(app, db=database)
    csrf.init_app(app)
    config_manager(login_manager)

def config_manager(manager):
    """
    Configure with Flask-Login manager.
    """
    from .modals import User

    manager.login_message = "You are not logged in to your account."
    manager.login_message_category = "warning"
    manager.login_view = "accounts.login"

    @manager.user_loader
    def user_loader(id):
        return User.query.get_or_404(id)