import os
import typing as t

from smtplib import SMTPException
from werkzeug.exceptions import ServiceUnavailable

from flask import current_app, render_template, url_for
from flask_mail import Message

from accounts.extensions import mail
from accounts.models import User
from accounts.utils import get_full_url


def send_mail(subject: t.AnyStr, recipients: t.List[str], body: t.Text):
    """
    Sends an email using the Flask-Mail extension.

    :param subject: The subject of the email.
    :param recipients: A list of recipient email addresses.
    :param body: The body content of the email.

    :raises ValueError: If the `MAIL_USERNAME` environment variable is not set.
    :raises ServiceUnavailable: If the SMTP service is unavailable.
    """
    sender: str = os.environ.get("MAIL_USERNAME", None)

    if not sender:
        raise ValueError("`MAIL_USERNAME` environment variable is not set")

    message = Message(subject=subject, sender=sender, recipients=recipients)
    message.body = body

    print(message.body)

    try:
        mail.connect()
        mail.send(message)
    except (SMTPException, Exception) as e:
        raise ServiceUnavailable(
            description=(
                "The SMTP mail service is currently not available. "
                "Please try later or contact the developers team."
            )
        )


def send_confirmation_mail(user: User = None):
    subject: str = "Verify Your Account"

    token: str = user.generate_token(salt=current_app.config["AACCOUNT_CONFIRM_SALT"])

    verification_link: str = get_full_url(
        url_for("accounts.confirm_account", token=token)
    )

    context = render_template(
        "emails/verify_account.txt",
        username=user.username,
        verification_link=verification_link,
    )

    send_mail(subject=subject, recipients=[user.email], body=context)


def send_reset_password(user: User = None):
    subject: str = "Reset Your Password"

    token: str = user.generate_token(salt=current_app.config["RESET_PASSWORD_SALT"])

    reset_link: str = get_full_url(url_for("accounts.reset_password", token=token))

    context = render_template(
        "emails/reset_password.txt", username=user.username, reset_link=reset_link
    )

    send_mail(subject=subject, recipients=[user.email], body=context)


def send_reset_email(user: User = None):
    subject: str = "Confirm Your Email Address"

    token: str = user.generate_token(salt=current_app.config["CHANGE_EMAIL_SALT"])

    confirmation_link: str = get_full_url(
        url_for("accounts.confirm_email", token=token)
    )

    context = render_template(
        "emails/reset_email.txt",
        username=user.username,
        confirmation_link=confirmation_link,
    )

    send_mail(subject=subject, recipients=[user.change_email], body=context)
