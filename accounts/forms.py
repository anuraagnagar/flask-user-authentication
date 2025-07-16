from wtforms.fields import (
    StringField,
    PasswordField,
    EmailField,
    BooleanField,
    SubmitField,
    FileField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Email

from flask_wtf.form import FlaskForm
from flask_wtf.file import FileAllowed, FileSize
from flask_wtf.recaptcha import RecaptchaField

from accounts.models import User
from accounts.validators import Unique, StrongNames, StrongUsername, StrongPassword


class RegisterForm(FlaskForm):
    """
    Flask Form class for user registration during signup.
    """

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 30),
            StrongUsername(),
            Unique(
                User, User.username, message="Username already exists choose another."
            ),
        ],
    )
    first_name = StringField(
        "First Name", validators=[DataRequired(), Length(3, 20), StrongNames()]
    )
    last_name = StringField(
        "Last Name", validators=[DataRequired(), Length(3, 20), StrongNames()]
    )
    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(8, 150),
            Unique(User, User.email, message="User already registered with us."),
        ],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(8, 20), StrongPassword()]
    )
    recaptcha = RecaptchaField()
    remember = BooleanField(
        "I agree & accept all terms of services. ", validators=[DataRequired()]
    )
    submit = SubmitField("Continue")


class LoginForm(FlaskForm):
    """
    Flask Form class for user authentication during login.
    """

    username = StringField(
        "Username or Email Address", validators=[DataRequired(), Length(5, 150)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 20)])
    recaptcha = RecaptchaField()
    remember = BooleanField("Remember me", validators=[DataRequired()])
    submit = SubmitField("Continue")


class ForgotPasswordForm(FlaskForm):
    """
    Flask Form class for users to request a password reset link.
    """

    email = EmailField(
        "Email Address", validators=[DataRequired(), Length(8, 150), Email()]
    )
    remember = BooleanField(
        "I agree & accept all terms of services.", validators=[DataRequired()]
    )
    submit = SubmitField("Send Reset Link")


class ResetPasswordForm(FlaskForm):
    """
    Flask Form class for resetting a user's password.
    """

    password = PasswordField(
        "New Password", validators=[DataRequired(), Length(8, 20), StrongPassword()]
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), Length(8, 20), StrongPassword()],
    )
    remember = BooleanField("Remember me", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ChangePasswordForm(FlaskForm):
    """
    Flask Form class for authenticated users to change their current password.
    """

    old_password = PasswordField(
        "Old Password", validators=[DataRequired(), Length(8, 20)]
    )
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(8, 20)]
    )
    confirm_password = PasswordField(
        "Confirm New Password", validators=[DataRequired(), Length(8, 20)]
    )
    remember = BooleanField("Remember me", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ChangeEmailForm(FlaskForm):
    """
    Flask Form class for authenticated users to change their current email address.
    """

    email = EmailField(
        "Email Address", validators=[DataRequired(), Length(8, 150), Email()]
    )
    remember = BooleanField(
        "I agree & accept all terms of services.", validators=[DataRequired()]
    )
    submit = SubmitField("Send Confirmation Mail")


class EditUserProfileForm(FlaskForm):
    """
    Flask Form for users to edit and update their profile details.
    """

    username = StringField(
        "Username", validators=[DataRequired(), Length(1, 30), StrongUsername()]
    )
    first_name = StringField(
        "First Name", validators=[DataRequired(), Length(3, 25), StrongNames()]
    )
    last_name = StringField(
        "Last Name", validators=[DataRequired(), Length(3, 25), StrongNames()]
    )
    profile_image = FileField(
        "Profile Image",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "svg"],
                "Upload only image files (.jpg, .jpeg, .png, .svg).",
            ),
            FileSize(
                max_size=1000000,
                message="Profile image size should not greater than 1MB.",
            ),
        ],
    )
    about = TextAreaField("About")
    submit = SubmitField("Save Profile")


class DeleteAccountForm(FlaskForm):
    """
    Flask Form class for users account deletion.
    """

    password = PasswordField(
        "Type your password", validators=[DataRequired(), Length(8, 20)]
    )

    submit = SubmitField("Delete")
