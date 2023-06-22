from flask import Blueprint, render_template, redirect, url_for, flash
from flask import Markup as _
from accounts.forms import (
        RegisterForm, 
        LoginForm, 
        ForgetPasswordForm,
        ChangePasswordForm,
        ChangeEmailForm
    )

accounts = Blueprint('accounts', __name__, template_folder='templates')


@accounts.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.data)
        return redirect(url_for('accounts.login'))
    return render_template('register.html', form=form)


@accounts.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.data)
        flash(_(f"Incorrect password, Please try again or '<a class='text-decoration-none' href='{url_for('accounts.forgot_password')}'>Forgot Password</a>' to reset."), category='error')
        return redirect(url_for('accounts.login'))
    return render_template('login.html', form=form)


@accounts.route('/forget/password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        print(form.data)
        return redirect(url_for('accounts.forget_password'))
    return render_template('forget_password.html', form=form)


@accounts.route('/change/password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        print(form.data)
        return redirect(url_for('accounts.change_password'))
    return render_template('change_password.html', form=form)


@accounts.route('/change/email', methods=['GET', 'POST'])
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        print(form.data)
        return redirect(url_for('accounts.change_password'))
    return render_template('change_email.html', form=form)


@accounts.route('/')
@accounts.route('/home')
def index():
    from .modals import User
    user = User.objects.get_or_404(_id='6484627789acf20f0e4f33fe')
    print(user)
    return render_template('index.html')
