import os
from flask import Flask
from accounts.extentions import (
        login_manager,
        bootstrap,
        database,
        csrf
    )
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def create_app():

    app = Flask(__name__, template_folder="templates")

    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", None)

    # SQL configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SQLALCHEMY_ECHO"] = False

    # register account blueprint.
    config_blueprint(app=app)
    # config application extension. 
    config_app(app=app)

    return app

def config_app(app):
    from .modals import User
    login_manager.init_app(app)
    bootstrap.init_app(app)
    database.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        return User.query.get_or_404(id)

def config_blueprint(app):
    from .views import accounts
    app.register_blueprint(accounts)