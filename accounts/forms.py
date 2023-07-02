from flask_wtf.form import FlaskForm
from wtforms.fields import (
    StringField, 
    PasswordField, 
    EmailField, 
    BooleanField, 
    SubmitField, 
    FileField, 
    TextAreaField
)
from wtforms.validators import (
    DataRequired, 
    Length, 
    Email
)
from accounts.validators import (
    Unique, 
    StrongUsername, 
    StrongPassword
)
from accounts.modals import User


class RegisterForm(FlaskForm):

    username = StringField('Username', 
        validators=[DataRequired(), Length(1, 30), StrongUsername(),
            Unique(User, User.username, message='Username already exists choose another.')]
    )   
    first_name = StringField('First Name', validators=[DataRequired(), Length(3, 20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(3, 20)])
    email = EmailField('Email Address', 
        validators=[DataRequired(), Length(8, 150), Email(),
            Unique(User, User.email, message='Email Address already registered with us.')]
    )
    password = PasswordField('Password', 
        validators=[DataRequired(), Length(8, 20), StrongPassword()]
    )
    remember = BooleanField('I agree & accept all terms of services. ', validators=[DataRequired()])
    submit = SubmitField('Continue')


class LoginForm(FlaskForm):

    username = StringField('Username or Email Address', validators=[DataRequired(), Length(5, 150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 20)])
    remember = BooleanField('Remember me', validators=[DataRequired()])
    submit = SubmitField('Continue')


class ForgotPasswordForm(FlaskForm):

    email = EmailField('Email Address', 
        validators=[DataRequired(), Length(8, 150), Email()]
    )
    remember = BooleanField('I agree & accept all terms of services.', validators=[DataRequired()])
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):

    password = PasswordField('Password', 
        validators=[DataRequired(), Length(8, 20), StrongPassword()]
    )
    confirm_password = PasswordField('Confirm Password', 
        validators=[DataRequired(), Length(8, 20), StrongPassword()]
    )
    remember = BooleanField('Remember me', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):

    old_password = PasswordField('Old Password', validators=[DataRequired(), Length(8, 20)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(8, 20)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), Length(8, 20)])
    remember = BooleanField('Remember me', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ChangeEmailForm(FlaskForm):

    email = EmailField('Email Address', 
        validators=[DataRequired(), Length(8, 150), Email()]
    )
    remember = BooleanField('I agree & accept all terms of services.', validators=[DataRequired()])
    submit = SubmitField('Send Confirmation Mail')


class EditUserProfileForm(FlaskForm):

    username = StringField('Username', 
        validators=[DataRequired(), Length(1, 30), StrongUsername()]
    )
    first_name = StringField('First Name', validators=[DataRequired(), Length(3, 25)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(3, 25)])
    profile_image = FileField('Profile Image')
    about = TextAreaField('About')
    submit = SubmitField('Save Profile')