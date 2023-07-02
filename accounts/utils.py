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

def page_not_found():
    return render_template('error.html')

def send_mail(subject, recipients, body):
    sender = os.environ.get('MAIL_USERNAME', None)
    print(sender)
    message = Message(
            subject=subject, sender=sender, recipients=[recipients]
        )
    message.body = body
    print(message.body)
    mail.connect()
    mail.send(message)

def send_reset_password(email=None):

    subject = "Resest Your Password."
    recipient = email

    reset_link = url_for('accounts.reset_password')
    content = f"Please click the following link to reset your password:\n {reset_link}"
    send_mail(subject=subject, recipients=recipient, body=content)

def send_reset_email(email=None):

    subject = "Please Confirm Your Email."
    recipient = email

    confirmation_link = ""
    content = f"Please click the following link to confirm your email:\n {confirmation_link}"
    send_mail(subject=subject, recipients=recipient, body=content)