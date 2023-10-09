import os
from flask import Flask as FlaskAuth
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = os.path.join(BASE_DIR, "accounts", "static", "assets")

UPLOAD_FOLDER = os.path.join(MEDIA_ROOT, "profile")

load_dotenv(os.path.join(BASE_DIR, ".env"))

def create_app():
    """
    Create and configure the Flask application instance.
    """
    app = FlaskAuth(__name__, template_folder="templates")

    # application configuration.
    config_application(app)
    # configure application extension. 
    config_extention(app)
    # configure application blueprints.
    config_blueprint(app)
    # configure error handlers.
    config_errorhandler(app)

    return app

def config_application(app):
    # Application configuration
    app.config["DEBUG"] = False
    app.config["TESTING"] = False
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY', None)
    app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = 'Pulse'

    # WTF Form and recaptcha configuration
    app.config["WTF_CSRF_SECRET_KEY"] = os.getenv('CSRF_SECRET_KEY', None)
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["RECAPTCHA_PUBLIC_KEY"] = os.getenv('PUBLIC_KEY', None)
    app.config["RECAPTCHA_PRIVATE_KEY"] = os.getenv('RECAPTCHA_KEY', None)
    
    # SQLAlchemy configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI', None)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Flask-Mail configuration
    app.config["MAIL_SERVER"] = os.getenv('MAIL_SERVER', None)
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv('MAIL_USERNAME', None)
    app.config["MAIL_PASSWORD"] = os.getenv('MAIL_PASSWORD', None)

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
    from .extensions import login_manager
    from .extensions import bootstrap
    from .extensions import database
    from .extensions import migrate
    from .extensions import csrf
    from .extensions import mail
    
    login_manager.init_app(app)
    bootstrap.init_app(app)
    database.init_app(app)
    migrate.init_app(app, db=database)
    csrf.init_app(app)
    mail.init_app(app)
    config_manager(login_manager)

def config_manager(manager):
    """
    Configure with Flask-Login manager.
    """
    from .models import User

    manager.login_message = "You are not logged in to your account."
    manager.login_message_category = "warning"
    manager.login_view = "accounts.login"

    @manager.user_loader
    def user_loader(id):
        return User.query.get_or_404(id)

def config_errorhandler(app):
    """
    Configure error handlers for application.
    """
    from flask import render_template
    from flask import redirect
    from flask import url_for
    from flask import flash

    @app.errorhandler(400)
    def bad_request(e):
        flash("Something went wrong.", 'error')
        return redirect(url_for('accounts.index'))
    
    @app.errorhandler(401)
    def unauthorized(e):
        flash("You are not authorized to perform this action.", 'error')
        return redirect(url_for('accounts.index'))
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        flash("Method not allowed.", 'error')
        return redirect(url_for('accounts.index'))

    @app.errorhandler(500)
    def database_error(e):
        flash("Internal server error.", 'error')
        return redirect(url_for('accounts.index'))