from flask import abort, render_template, request, redirect, url_for, flash
from flask import Blueprint
from flask_login import (
        current_user,
        login_required,
        login_user,
        logout_user
    )

from accounts.extensions import database as db
from accounts.models import User, Profile
from accounts.forms import (
        RegisterForm, 
        LoginForm, 
        ForgotPasswordForm,
        ResetPasswordForm,
        ChangePasswordForm,
        ChangeEmailForm,
        EditUserProfileForm
    )
from accounts.utils import (
        unique_security_token,
        get_unique_filename,
        send_reset_password,
        send_reset_email
    )

from datetime import datetime, timedelta
import re
import os


"""
This accounts blueprint defines routes and templates related to user management
within our application.
"""
accounts = Blueprint('accounts', __name__, template_folder='templates')


@accounts.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    form = RegisterForm()

    if current_user.is_authenticated:
        return redirect(url_for('accounts.index'))

    if form.validate_on_submit():
        username = form.data.get('username')
        first_name = form.data.get('first_name')
        last_name = form.data.get('last_name')
        email = form.data.get('email')
        password = form.data.get('password')

        try:
            user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )
            user.set_password(password)
            user.save()
            user.send_confirmation()
            flash("A confirmation link sent to your email. Please verify your account.", 'info')
            return redirect(url_for('accounts.login'))
        except Exception as e:
            flash("Something went wrong", 'error')
            return redirect(url_for('accounts.register'))

    return render_template('register.html', form=form)


@accounts.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('accounts.index'))

    if form.validate_on_submit():
        username = form.data.get('username')
        password = form.data.get('password')

        user = User.get_user_by_username(username) or User.get_user_by_email(username)

        if not user:
            flash("User account doesn't exists.", 'error')
        elif not user.check_password(password):
            flash("Your password is incorrect. Please try again.", 'error')
        else:
            if not user.is_active():
                user.send_confirmation()
                flash("Your account is not activate.", 'error')
                return redirect(url_for('accounts.login'))

            login_user(user, remember=True, duration=timedelta(days=15))
            flash("You are logged in successfully.", 'success')
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.login'))

    return render_template('login.html', form=form)


@accounts.route('/account/confirm?token=<string:token>', methods=['GET', 'POST'], strict_slashes=False)
def confirm_account(token=None):
    auth_user = User.query.filter_by(security_token=token).first_or_404()

    if auth_user and not auth_user.is_token_expire():
        if request.method == "POST":
            try:
                auth_user.active = True
                auth_user.security_token = None
                db.session.commit()
                login_user(auth_user, remember=True, duration=timedelta(days=15))
                flash(f"Welcome {auth_user.username}, You're registered successfully.", 'success')
                return redirect(url_for('accounts.index'))
            except Exception as e:
                flash("Something went wrong.", 'error')
                return redirect(url_for('accounts.login'))

        return render_template('confirm_account.html', token=token)

    return abort(404)


@accounts.route('/logout', strict_slashes=False)
@login_required
def logout():
    logout_user()
    flash("You're logout successfully.", 'success')
    return redirect(url_for('accounts.login'))


@accounts.route('/forgot/password', methods=['GET', 'POST'], strict_slashes=False)
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.data.get('email')
        user = User.get_user_by_email(email=email)

        if user:
            try:
                user.security_token = unique_security_token()
                user.is_send = datetime.now()
                db.session.commit()
                send_reset_password(user)
                flash("A reset password link sent to your email. Please check.", 'success')
                return redirect(url_for('accounts.login'))
            except Exception as e:
                flash("Something went wrong", 'error')
                return redirect(url_for('accounts.forgot_password'))

        flash("Email address is not registered with us.", 'error')
        return redirect(url_for('accounts.forgot_password'))

    return render_template('forget_password.html', form=form)


@accounts.route('/password/reset/token?<string:token>', methods=['GET', 'POST'], strict_slashes=False)
def reset_password(token=None):
    user = User.query.filter_by(security_token=token).first_or_404()

    if user and not user.is_token_expire():
        form = ResetPasswordForm()

        if form.validate_on_submit():
            password = form.data.get('password')
            confirm_password = form.data.get('confirm_password')

            if not (password == confirm_password):
                flash("Your new password field's not match.", 'error')
            elif not re.match(r"(?=^.{8,}$)(?=.*\d)(?=.*[!@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$", password):
                flash("Please choose strong password. It contains at least one alphabet, number, and one special character.", 'warning')
            else:
                user.set_password(password)
                user.security_token = None
                db.session.commit()
                flash("Your password is changed successfully. Please login.", 'success')
                return redirect(url_for('accounts.login'))

            return redirect(url_for('accounts.reset_password', token=token))

        return render_template('reset_password.html', form=form, token=token)

    return abort(404)


@accounts.route('/change/password', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        old_password = form.data.get('old_password')
        new_password = form.data.get('new_password')
        confirm_password = form.data.get('confirm_password')

        user = User.query.get_or_404(current_user.id)
        
        if current_user.username == 'test_user':
            flash("Test user limited to read-only access.", 'error')
        elif not user.check_password(old_password):
            flash("Your old password is incorrect.", 'error')
        elif not (new_password == confirm_password):
            flash("Your new password field's not match.", 'error')
        elif not re.match(r"(?=^.{8,}$)(?=.*\d)(?=.*[!@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$", new_password):
            flash("Please choose strong password. It contains at least one alphabet, number, and one special character.", 'warning')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash("Your password changed successfully.", 'success')
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.change_password'))
    return render_template('change_password.html', form=form)


@accounts.route('/change/email', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def change_email():
    form = ChangeEmailForm()

    if form.validate_on_submit():
        email = form.data.get('email')

        user = User.query.get_or_404(current_user.id)

        if email == user.email:
            flash("Email is already verified with your account.", 'warning')  
        elif email in [u.email for u in User.query.all() if email != user.email]:
            flash("Email address is already registered with us.", 'warning')  
        else:
            try:
                user.change_email = email
                user.security_token = unique_security_token()
                user.is_send = datetime.now()
                db.session.commit()
                send_reset_email(user=user)
                flash("A reset email link sent to your new email address. Please verify.", 'success')
                return redirect(url_for('accounts.index'))
            except Exception as e:
                flash("Something went wrong.", 'error')
                return redirect(url_for('accounts.change_email'))
            
        return redirect(url_for('accounts.change_email'))

    return render_template('change_email.html', form=form)


@accounts.route('/account/email/confirm?token=<string:token>', methods=['GET', 'POST'], strict_slashes=False)
def confirm_email(token=None):
    user = User.query.filter_by(security_token=token).first_or_404()

    if user and not user.is_token_expire():
        if request.method == "POST":
            try:
                user.email = user.change_email
                user.change_email = None
                user.security_token = None
                db.session.commit()
                flash(f"Your email address updated successfully.", 'success')
                return redirect(url_for('accounts.index'))
            except Exception as e:
                flash("Something went wrong", 'error')
                return redirect(url_for('accounts.index'))

        return render_template('confirm_email.html', token=token)

    return abort(404)


@accounts.route('/', strict_slashes=False)
@accounts.route('/home', strict_slashes=False)
@login_required
def index():
    profile = Profile.query.filter_by(user_id=current_user.id).first_or_404()
    return render_template('index.html', profile=profile)


@accounts.route('/profile', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def profile():
    form = EditUserProfileForm()

    user = User.query.get_or_404(current_user.id)
    profile = Profile.query.filter_by(user_id=user.id).first_or_404()

    if form.validate_on_submit():
        username = form.data.get('username')
        first_name = form.data.get('first_name')
        last_name = form.data.get('last_name')
        profile_image = form.data.get('profile_image')
        about = form.data.get('about')

        if current_user.username == 'test_user':
            flash("Test user limited to read-only access.", 'error')
        elif username in [user.username for user in User.query.all() if username != current_user.username]:
            flash("Username already exists. Choose another.", 'error')
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            profile.bio = about

            if profile_image and getattr(profile_image, "filename"):
                profile.set_avator(profile_image)
            
            db.session.commit()
            flash("Your profile update successfully.", 'success')
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.profile'))
        
    return render_template('profile.html', form=form, profile=profile)

