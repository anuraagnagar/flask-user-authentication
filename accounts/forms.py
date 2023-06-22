from flask_wtf.form import FlaskForm
from wtforms.fields import (
    StringField, PasswordField, EmailField, BooleanField, SubmitField
)
from wtforms.validators import DataRequired, Length


class RegisterForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(1, 30)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 20)])
    email = EmailField('Email Address', validators=[DataRequired(), Length(8, 150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 20)])
    remember = BooleanField('I agree & accept all terms of services. ', validators=[DataRequired()])
    submit = SubmitField('Continue')


class LoginForm(FlaskForm):

    email = EmailField('Email Address', validators=[DataRequired(), Length(8, 150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 20)])
    remember = BooleanField('Remember me', validators=[DataRequired()])
    submit = SubmitField('Login')


class ForgetPasswordForm(FlaskForm):

    email = EmailField('Email Address', validators=[DataRequired(), Length(8, 150)])
    remember = BooleanField('I agree & accept all terms of services.', validators=[DataRequired()])
    submit = SubmitField('Send Reset Link')


class ChangePasswordForm(FlaskForm):

    old_password = PasswordField('Old Password', validators=[DataRequired(), Length(8, 20)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(8, 20)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), Length(8, 20)])
    remember = BooleanField('Remember me', validators=[DataRequired()])
    submit = SubmitField('Submit Changes')


class ChangeEmailForm(FlaskForm):

    email = EmailField('Email Address', validators=[DataRequired(), Length(8, 150)])
    remember = BooleanField('I agree & accept all terms of services.', validators=[DataRequired()])
    submit = SubmitField('Send Confirmation Mail')
