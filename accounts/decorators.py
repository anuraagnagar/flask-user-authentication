from functools import wraps

from flask import current_app, flash, redirect, request, url_for
from flask_login import current_user
from flask_babel import lazy_gettext as _


def guest_user_exempt(func):
    """
    Decorator to restrict access for authenticated users
    who are `Test User` to read-only access.
    """

    @wraps(func)
    def decorator(*args, **kwargs):
        if (
            current_user.is_authenticated
            and not request.method == "GET"
            and current_user.username == current_app.config["TEST_USER_USERNAME"]
        ):
            flash(_("Guest user limited to read-only access."), "error")
            return redirect(url_for("accounts.index"))
        return func(*args, **kwargs)

    return decorator


def authentication_redirect(func):
    """
    Decorator to redirect authenticated users to the index page.
    """

    @wraps(func)
    def decorator_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("accounts.index"))
        return func(*args, **kwargs)

    return decorator_func
