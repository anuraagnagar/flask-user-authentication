from flask import Blueprint, render_template, redirect, url_for, flash
from flask import Markup as _
from flask_login import (
        current_user,
        login_required,
        login_user,
        logout_user
    )
from accounts.extentions import database as db
from accounts.forms import (
        RegisterForm, 
        LoginForm, 
        ForgetPasswordForm,
        ResetPasswordForm,
        ChangePasswordForm,
        ChangeEmailForm
    )
from accounts.modals import User

accounts = Blueprint('accounts', __name__, template_folder='templates')


@accounts.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.data)
        username = form.data.get('username')
        first_name = form.data.get('first_name')
        last_name = form.data.get('last_name')
        email = form.data.get('email')
        password = form.data.get('password')

        user = User(
            username=username,
            first_name=first_name,
            last_name=first_name,
            email=email,
            password=password
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('accounts.login'))
    return render_template('register.html', form=form)


@accounts.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.data)
        flash(_(f"Incorrect password, Please try again or <a class='alert-link' href='{url_for('accounts.forgot_password')}'>Forgot Password</a> to reset."), category='error')
        return redirect(url_for('accounts.login'))
    return render_template('login.html', form=form)


@accounts.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('accounts.index'))


@accounts.route('/forget/password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        print(form.data)
        return redirect(url_for('accounts.forget_password'))
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
        print(form.data)
        return redirect(url_for('accounts.change_password'))
    return render_template('change_password.html', form=form)


@accounts.route('/change/email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        print(form.data)
        return redirect(url_for('accounts.change_password'))
    return render_template('change_email.html', form=form)


@accounts.route('/')
@accounts.route('/home')
@login_required
def index():
    return render_template('index.html')


@accounts.route('/profile')
@login_required
def profile():
    return render_template('profile.html')