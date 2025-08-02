from http import HTTPStatus
from types import MappingProxyType

from werkzeug.exceptions import (
    HTTPException,
    BadRequest,
    Unauthorized,
    MethodNotAllowed,
    NotFound,
    InternalServerError,
    ServiceUnavailable,
    TooManyRequests,
)

from flask import Flask as FlaskAuth
from flask import redirect, request, session, url_for, current_app
from flask_babel import lazy_gettext as _


def create_app(config_type):
    """
    Create and configure the Flask application instance.
    """
    app = FlaskAuth(__name__)

    # application configuration.
    config_application(app, config_type)

    # configure application extension.
    config_extention(app)

    # configure application blueprints.
    config_blueprint(app)

    # configure command-line interface.
    config_cli_command(app)

    # configure google oauth.
    config_google_oauth(app)

    # configure error handlers.
    config_errorhandler(app)

    # add view for changing theme
    @app.get("/change-theme")
    def change_theme():
        theme = request.args.get("theme", app.config["BOOTSTRAP_DEFAULT_THEME"])

        if theme in app.config["BOOTSTRAP_BOOTSWATCH_THEMES"]:
            session["_theme_preference"] = theme
            app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = theme
            return redirect(url_for("accounts.index"))

    @app.get("/change-lang")
    def change_lang():
        lang = request.args.get("lang", app.config["BABEL_DEFAULT_LOCALE"])

        if lang in app.config["LANGUAGES"]:
            # not sure why both?
            session["_lang_preference"] = lang
            app.config["BABEL_LOCALE"] = lang
        else:
            session["_lang_preference"] = app.config["BABEL_DEFAULT_LOCALE"]
            app.config["BABEL_LOCALE"] = app.config["BABEL_DEFAULT_LOCALE"]
        return redirect(url_for("accounts.index"))

    return app


def config_application(app, config_type):
    """
    Configure the application based on the specified `configuration` type.
    """

    import config as conf

    if not config_type:
        raise RuntimeError("Configuration type must be provided.")

    # Immutable mapping of configuration types to their corresponding config objects.
    config_map = MappingProxyType(
        {
            "development": conf.development,
            "production": conf.production,
            "testing": conf.testing,
        }
    )

    # Get the configuration object based on the provided `config_type`.
    config = config_map.get(config_type)

    if not config:
        raise RuntimeError("Invalid configuration type: '%s'" % config_type)

    # Application configuration from object.
    app.config.from_object(config)


def config_blueprint(app):
    """
    Configure/register blueprints for the application.
    """
    from .views import accounts

    app.register_blueprint(accounts)


def get_locale():
    return current_app.config["BABEL_LOCALE"]


def config_extention(app):
    """
    Configure application extensions.
    """
    from .extensions import login_manager
    from .extensions import limiter
    from .extensions import bootstrap
    from .extensions import database
    from .extensions import migrate
    from .extensions import csrf
    from .extensions import mail
    from .extensions import oauth
    from .extensions import babel

    login_manager.init_app(app)
    limiter.init_app(app)
    bootstrap.init_app(app)
    database.init_app(app)
    migrate.init_app(app, db=database)
    csrf.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    config_login_manager(login_manager)


def config_login_manager(manager):
    """
    Configure the Flask-Login for managing user's sessions.
    """
    from .models import User

    manager.login_message = _("You are not logged in to your account.")
    manager.login_message_category = "warning"
    manager.login_view = "accounts.login"

    @manager.user_loader
    def user_loader(user_id):
        return User.get_user_by_id(user_id)


def config_cli_command(app):
    """
    Configure application custom commands.
    """

    from .cli import register_cli_command

    register_cli_command(app)


def config_google_oauth(app):
    from authlib.integrations.flask_client import OAuthError

    from .extensions import oauth

    _client_id = app.config.get("GOOGLE_CLIENT_ID")
    _client_secret = app.config.get("GOOGLE_CLIENT_SECRET")

    _server_meta_url = app.config.get("GOOGLE_DISCOVERY_URL")
    _scope = app.config.get("GOOGLE_SCOPE")
    _redirect_uri = app.config.get("GOOGLE_REDIRECT_URI")

    try:
        oauth.register(
            name="google",
            client_id=_client_id,
            client_secret=_client_secret,
            server_metadata_url=_server_meta_url,
            client_kwargs={"scope": _scope},
            redirect_uri=_redirect_uri,
        )
    except Exception as err:
        raise OAuthError(f"Failed to connect Google OAuth client: {err}")


def config_errorhandler(app):
    """
    Configure error handlers for application.
    """
    from flask import flash, render_template, redirect, request, url_for

    @app.errorhandler(BadRequest)
    def bad_request(e: HTTPException):
        flash(
            _("Oops! There was a problem with your request. Please try again."), "error"
        )
        return redirect(url_for("accounts.index"))

    @app.errorhandler(Unauthorized)
    def unauthorized(e: HTTPException):
        flash(_("You are not authorized to access this resource."), "error")
        return redirect(url_for("accounts.index"))

    @app.errorhandler(NotFound)
    def page_not_found(e: HTTPException):
        return render_template("errors/404.html"), HTTPStatus.NOT_FOUND

    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed(e: HTTPException):
        flash(_("Method not allowed."), "error")
        return redirect(url_for("accounts.index"))

    @app.errorhandler(TooManyRequests)
    def too_many_request(e: HTTPException):
        return render_template("errors/429.html"), HTTPStatus.TOO_MANY_REQUESTS

    @app.errorhandler(InternalServerError)
    def internal_server_error(e: HTTPException):
        return (render_template("errors/500.html"), HTTPStatus.INTERNAL_SERVER_ERROR)

    @app.errorhandler(ServiceUnavailable)
    def service_unavailable(e: HTTPException):
        flash(e.description, "error")
        return redirect(request.path or url_for("accounts.login"))
