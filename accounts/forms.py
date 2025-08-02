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

from flask_babel import lazy_gettext as _


class RegisterForm(FlaskForm):
    """
    Flask Form class for user registration during signup.
    """

    username = StringField(
        _("Username"),
        validators=[
            DataRequired(),
            Length(1, 30),
            StrongUsername(),
            Unique(
                User,
                User.username,
                message=_("Username already exists choose another."),
            ),
        ],
    )
    first_name = StringField(
        _("First Name"), validators=[DataRequired(), Length(3, 20), StrongNames()]
    )
    last_name = StringField(
        _("Last Name"), validators=[DataRequired(), Length(3, 20), StrongNames()]
    )
    email = EmailField(
        _("Email Address"),
        validators=[
            DataRequired(),
            Email(),
            Length(8, 150),
            Unique(User, User.email, message=_("User already registered with us.")),
        ],
    )
    password = PasswordField(
        _("Password"), validators=[DataRequired(), Length(8, 20), StrongPassword()]
    )
    recaptcha = RecaptchaField()
    remember = BooleanField(
        _("I agree & accept all terms of services."), validators=[DataRequired()]
    )
    submit = SubmitField(_("Continue"))


class LoginForm(FlaskForm):
    """
    Flask Form class for user authentication during login.
    """

    username = StringField(
        _("Username or Email Address"), validators=[DataRequired(), Length(5, 150)]
    )
    password = PasswordField(_("Password"), validators=[DataRequired(), Length(8, 20)])
    recaptcha = RecaptchaField()
    remember = BooleanField(_("Remember me"), validators=[DataRequired()])
    submit = SubmitField(_("Continue"))


class ForgotPasswordForm(FlaskForm):
    """
    Flask Form class for users to request a password reset link.
    """

    email = EmailField(
        _("Email Address"), validators=[DataRequired(), Length(8, 150), Email()]
    )
    remember = BooleanField(
        _("I agree & accept all terms of services."), validators=[DataRequired()]
    )
    submit = SubmitField(_("Send Reset Link"))


class ResetPasswordForm(FlaskForm):
    """
    Flask Form class for resetting a user's password.
    """

    password = PasswordField(
        _("New Password"), validators=[DataRequired(), Length(8, 20), StrongPassword()]
    )
    confirm_password = PasswordField(
        _("Confirm New Password"),
        validators=[DataRequired(), Length(8, 20), StrongPassword()],
    )
    remember = BooleanField(_("Remember me"), validators=[DataRequired()])
    submit = SubmitField(_("Submit"))


class ChangePasswordForm(FlaskForm):
    """
    Flask Form class for authenticated users to change their current password.
    """

    old_password = PasswordField(
        _("Old Password"), validators=[DataRequired(), Length(8, 20)]
    )
    new_password = PasswordField(
        _("New Password"), validators=[DataRequired(), Length(8, 20)]
    )
    confirm_password = PasswordField(
        _("Confirm New Password"), validators=[DataRequired(), Length(8, 20)]
    )
    remember = BooleanField(_("Remember me"), validators=[DataRequired()])
    submit = SubmitField(_("Submit"))


class ChangeEmailForm(FlaskForm):
    """
    Flask Form class for authenticated users to change their current email address.
    """

    email = EmailField(
        _("Email Address"), validators=[DataRequired(), Length(8, 150), Email()]
    )
    remember = BooleanField(
        _("I agree & accept all terms of services."), validators=[DataRequired()]
    )
    submit = SubmitField(_("Send Confirmation Mail"))


class EditUserProfileForm(FlaskForm):
    """
    Flask Form for users to edit and update their profile details.
    """

    username = StringField(
        _("Username"), validators=[DataRequired(), Length(1, 30), StrongUsername()]
    )
    first_name = StringField(
        _("First Name"), validators=[DataRequired(), Length(3, 25), StrongNames()]
    )
    last_name = StringField(
        _("Last Name"), validators=[DataRequired(), Length(3, 25), StrongNames()]
    )
    profile_image = FileField(
        _("Profile Image"),
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "svg"],
                _("Upload only image files (.jpg, .jpeg, .png, .svg)."),
            ),
            FileSize(
                max_size=1000000,
                message=_("Profile image size should not greater than 1MB."),
            ),
        ],
    )
    about = TextAreaField(_("About Me"))
    submit = SubmitField(_("Save Profile"))


class DeleteAccountForm(FlaskForm):
    """
    Flask Form class for users account deletion.
    """

    password = PasswordField(
        _("Type your password"), validators=[DataRequired(), Length(8, 20)]
    )

    submit = SubmitField(_("Delete"))
