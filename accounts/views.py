from flask import render_template, request, redirect, url_for, flash
from flask import Blueprint
from flask_login import (
        current_user,
        login_required,
        login_user,
        logout_user
    )
from accounts.extentions import database as db
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
from accounts.utils import page_not_found
from datetime import timedelta


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

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        user.set_password(password)
        user.save()
        
        return redirect(url_for('accounts.login'))
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
            flash("Incorrect password please try again.", 'error')
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
        user_exist = User.get_user_by_email(email=email)

        if not user_exist:
            flash("Email address is not registered with us.", 'error')
        

        return redirect(url_for('accounts.forgot_password'))
    return render_template('forget_password.html', form=form)


@accounts.route('/password/reset/token', methods=['GET', 'POST'])
def reset_password(token=None):
    form = ResetPasswordForm()
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
        elif new_password == confirm_password:
            flash("Your new password field's not match.", 'error')
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

        if not email:
            flash("Please provide an email address.", 'warning')
        elif email == current_user.email:
            flash("Email is already verify with your account.", 'warning')
        else:
            # add send email logic herre..abs
            # ...
            # ...
            return redirect(url_for('accounts.index'))
            
        return redirect(url_for('accounts.change_email'))

    return render_template('change_email.html', form=form)


@accounts.route('/')
@accounts.route('/home')
@login_required
def index():
    profile = Profile.query.filter_by(user_id=current_user.id).first_or_404()
    print(profile.bio)
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
        print(type(profile_image))
        # print(profile_image.save('static/assets/profile/{}'.format(profile_image)))
        
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        profile.bio = about
        db.session.commit()
        flash("Your profile update successfully.", 'success')
        return redirect(url_for('accounts.index'))

    return render_template('profile.html', form=form, profile=profile)