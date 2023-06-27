from flask import flash
from wtforms import ValidationError 
from accounts.modals import User


class Unique(object):

    def __init__(self, instance=None, field=None, message=None):
        self.instance = instance
        self.field = field
        self.message = message

    def __call__(self, form, field):
        if self.instance.query.filter(self.field == field.data).first():
            if not self.message:
                self.message = '{} already exists.'.format(field.name)
            raise ValidationError(self.message)


class StrongPassword(object):

    def __call__(self, form, field):
        if field.data:
            pass