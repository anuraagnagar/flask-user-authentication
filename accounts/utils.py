from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for
from flask_mail import Message
from accounts.extensions import mail
import uuid
import secrets
import os

def unique_uid():
    return str(uuid.uuid4())

def unique_security_token(token_len=48):
    return secrets.token_hex(token_len)

def get_unique_filename(filename=None):
    if not filename:
        return None
    filename = secure_filename(filename).split(".")
    return "{}.{}".format(str(uuid.uuid4()), filename[len(filename)-1])

def remove_existing_file(path=None):
    if os.path.isfile(path=path):
        os.remove(path)

def send_mail(subject, recipients, body):
    sender = os.environ.get('MAIL_USERNAME', None)
    message = Message(
            subject=subject, sender=sender, recipients=[recipients]
        )
    message.body = body
    print(message.body)
    mail.connect()
    mail.send(message)

def send_reset_password(user=None):

    subject = "Resest Your Password."
    recipient = user.email

    reset_link = url_for('accounts.reset_password', token=user.security_token)
    content = f"""
    Reset Your Password

    Please click the following link to reset your password
    {reset_link}
    """
    send_mail(subject=subject, recipients=recipient, body=content)

def send_reset_email(user=None):

    subject = "Please Confirm Your Email."
    recipient = user.change_email

    confirmation_link = url_for('accounts.confirm_email', token=user.security_token)
    content = f"Please click the following link to confirm your email:\n {confirmation_link}"
    send_mail(subject=subject, recipients=recipient, body=content)