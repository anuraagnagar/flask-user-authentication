import re

from wtforms import ValidationError


class Unique(object):
    """
    Validator that checks if a field value is unique in the database.
    """

    def __init__(self, instance=None, field=None, message=None):
        self.instance = instance
        self.field = field
        self.message = message

    def __call__(self, form, field):
        if self.instance.query.filter(self.field == field.data).first():
            if not self.message:
                self.message = "{} already exists.".format(field.name)
            raise ValidationError(self.message)


class StrongNames(object):
    """
    Validator that checks if a field contains only alphabetic characters.
    """

    def __init__(self, message=None):
        self.message = message
        if not self.message:
            self.message = "Field contains only alphabet."

    def __call__(self, form, field):
        if not re.match("^[a-zA-Z]+$", field.data):
            raise ValidationError(self.message)


class StrongUsername(object):
    """
    Validator that checks if a username contains only allowed characters.

    Allowed characters: A-Z, a-z, 0-9, underscore (_), hyphen (-), and period (.).
    """

    def __init__(self, message=None):
        self.message = message
        if not self.message:
            self.message = "Username contain only (A-Za-z0-9_-.) characters."

    def __call__(self, form, field):
        username = field.data
        if not re.match("^[a-zA-Z0-9_.-]+$", username):
            raise ValidationError(self.message)


class StrongPassword(object):
    """
    Validator that checks if a password is strong.

    A strong password must contain at least 8 characters, one uppercase letter,
    one lowercase letter, one digit, and one special character from (!@#$%^&*).
    """

    def __init__(self, message=None):
        self.message = message
        if not self.message:
            self.message = "Please choose a strong password."

    def __call__(self, form, field):
        password = field.data
        if not re.match(
            r"(?=^.{8,}$)(?=.*\d)(?=.*[!@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$",
            password,
        ):
            raise ValidationError(self.message)
