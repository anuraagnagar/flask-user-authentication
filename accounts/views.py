from flask import render_template, request, redirect, url_for, flash
from flask import Blueprint
from flask_login import (
        current_user,
        login_required,
        login_user,
        logout_user
    )
from accounts.extensions import database as db
from accounts.modals import User, Profile
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
        send_reset_password,
        send_reset_email,
        page_not_found
    )
from datetime import timedelta
import re


accounts = Blueprint('accounts', __name__, template_folder='templates')


@accounts.route('/register', methods=['GET', 'POST'])
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


@accounts.route('/login', methods=['GET', 'POST'])
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
            login_user(user, remember=True, duration=timedelta(days=15))
            flash("You are logged in successfully.", 'success')
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.login'))

    return render_template('login.html', form=form)


@accounts.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You're logout successfully.", 'success')
    return redirect(url_for('accounts.login'))


@accounts.route('/forgot/password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.data.get('email')
        user = User.get_user_by_email(email=email)

        if user:
            send_reset_password(email=user.email)
            flash("A reset password link sent to your email. Please check.", 'success')
            return redirect(url_for('accounts.login'))

        flash("Email address is not registered with us.", 'error')
        return redirect(url_for('accounts.forgot_password'))

    return render_template('forget_password.html', form=form)


@accounts.route('/password/reset/token', methods=['GET', 'POST'])
def reset_password(token=None):
    form = ResetPasswordForm()

    if form.validate_on_submit():
        password = form.data.get('password')
        confirm_password = form.data.get('confirm_password')

        if not (password == confirm_password):
            flash("Your new password field's not match.", 'error')
        elif not re.match(r"(?=^.{8,}$)(?=.*\d)(?=.*[!@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$", password):
            flash("Please choose strong password. It contains at least one alphabet, number, and one special character.", 'warning')
        else:
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.reset_password'))
    return render_template('reset_password.html', form=form)


@accounts.route('/change/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        old_password = form.data.get('old_password')
        new_password = form.data.get('new_password')
        confirm_password = form.data.get('confirm_password')

        user = User.query.get_or_404(current_user.id)
        
        if not user.check_password(old_password):
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


@accounts.route('/change/email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()

    if form.validate_on_submit():
        email = form.data.get('email')

        user = User.query.get_or_404(current_user.id)

        if not email == user.email:
            try:
                send_reset_email(email=email)
                flash("A reset email sent to your new email address. Please verify.", 'success')
                return redirect(url_for('accounts.index'))
            except Exception as e:
                flash("Something went wrong.", 'error')
                return redirect(url_for('accounts.change_email'))
            
        flash("Email is already verify with your account.", 'warning')    
        return redirect(url_for('accounts.change_email'))

    return render_template('change_email.html', form=form)


@accounts.route('/')
@accounts.route('/home')
@login_required
def index():
    profile = Profile.query.filter_by(user_id=current_user.id).first_or_404()
    return render_template('index.html', profile=profile)


@accounts.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditUserProfileForm()
    user = User.query.get_or_404(current_user.id)
    profile = Profile.query.filter_by(user_id=user.id).first_or_404()
    form.about.data = profile.bio

    if form.validate_on_submit():
        username = form.data.get('username')
        first_name = form.data.get('first_name')
        last_name = form.data.get('last_name')
        profile_image = form.profile_image.data
        about = form.data.get('about')
        
        # print(profile_image.save('static/assets/profile/{}'.format(profile_image)))

        if username in [user.username for user in User.query.all() if username != current_user.username]:
            flash("Username already exists. Choose another.", 'error')
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            profile.bio = about
            db.session.commit()
            flash("Your profile update successfully.", 'success')
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.profile'))
    return render_template('profile.html', form=form, profile=profile)