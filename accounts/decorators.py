from functools import wraps

from flask import flash, redirect, request
from flask_login import current_user


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
            and current_user.username == "test_user"
        ):
            flash("Guest user limited to read-only access.", "error")
            return redirect(request.path)
        return func(*args, **kwargs)

    return decorator


def authentication_redirect(endpoint: str = "accounts.index"):
    """
    Decorator to redirect authenticated users to the index page.
    """

    def decorator(func):
        @wraps(func)
        def decorator_func(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(url_for(endpoint))
            return func(*args, **kwargs)

        return decorator_func

    return decorator
