import re

from datetime import timedelta
from http import HTTPStatus
from requests.exceptions import ConnectionError
from werkzeug.exceptions import InternalServerError
from authlib.integrations.flask_client import OAuthError
from authlib.integrations.base_client.errors import TokenExpiredError

from flask import Blueprint, Response
from flask import abort, current_app, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user

from accounts.decorators import authentication_redirect, guest_user_exempt
from accounts.email_utils import (
    send_reset_password,
    send_reset_email,
)
from accounts.extensions import database as db, limiter, oauth
from accounts.models import User, OAuthProvider
from accounts.forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
    ChangeEmailForm,
    EditUserProfileForm,
    DeleteAccountForm,
)
from accounts.utils import (
    get_unique_id,
    get_username_from_email,
    download_and_save_image_from_url,
)

from flask_babel import lazy_gettext as _

"""
This accounts blueprint defines routes and templates related to user management
within our application.
"""
accounts = Blueprint("accounts", __name__, template_folder="templates")


@accounts.route("/login_as_guest", methods=["GET", "POST"])
@authentication_redirect
@limiter.limit("3/min", methods=["POST"])
def login_guest_user() -> Response:
    """
    Log in as a guest user with limited access.

    :return: Redirects to the homepage on success or the login page on failure.
    """

    if request.method == "POST":
        # Fetch the predefined guest user instance by username.
        test_user = User.get_user_by_username(username="testuser")

        if test_user:
            # Log in the guest user with a session duration of (1 day) only.
            login_user(test_user, remember=True, duration=timedelta(days=1))

            flash(_("You are logged in as a Guest User."), "success")
            return redirect(url_for("accounts.index"))

        flash(_("Test user not found."), "error")
        return redirect(url_for("accounts.login"))

    # Return a 404 error if accessed via GET
    return abort(HTTPStatus.NOT_FOUND)


@accounts.route("/register", methods=["GET", "POST"])
@authentication_redirect
@limiter.limit("3/min", methods=["POST"])
def register() -> Response:
    """
    Handling user registration.
    If the user is already authenticated, they are redirected to the index page.

    This view handles both GET and POST requests:
    - GET: Renders the registration form and template.
    - POST: Processes the registration form, creates a new user, and sends a confirmation email.

    :return: Renders the registration template on GET request
    or redirects to login after successful registration.
    """
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.data.get("username")
        first_name = form.data.get("first_name")
        last_name = form.data.get("last_name")
        email = form.data.get("email")
        password = form.data.get("password")

        # Attempt to create a new user and save to the database.
        user = User.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

        # Sends account confirmation mail to the user.
        user.send_confirmation()

        flash(
            "A confirmation link sent to your email. Please verify your account.",
            "success",
        )
        return redirect(url_for("accounts.login"))

    return render_template("register.html", form=form)


@accounts.route("/login", methods=["GET", "POST"])
@authentication_redirect
@limiter.limit("5/minute", methods=["POST"])
def login() -> Response:
    """
    Handling user login functionality.
    If the user is already authenticated, they are redirected to the index page.

    This view handles both GET and POST requests:
    - GET: Renders the login form and template.
    - POST: Validates the form and authenticates the user.

    :return: Renders the login template on GET request or redirects based on the login status.
    """
    form = LoginForm()  # A form class for Login Account.

    if form.validate_on_submit():
        username = form.data.get("username", None)
        password = form.data.get("password", None)
        remember = form.data.get("remember", True)

        # Attempt to authenticate the user from the database.
        user = User.authenticate(username=username, password=password)

        if not user:
            flash(_("Invalid username or password. Please try again."), "error")
        else:
            if not user.is_active:
                # User account is not active, send confirmation email.
                user.send_confirmation()

                flash(
                    "Your account is not activate. We sent a confirmation link to your email",
                    "error",
                )
                return redirect(url_for("accounts.login"))

            # Log the user in and set the session to remember the user for (15 days).
            login_user(user, remember=remember, duration=timedelta(days=15))

            flash(_("You are logged in successfully."), "success")
            return redirect(url_for("accounts.index"))

        return redirect(url_for("accounts.login"))

    return render_template("login.html", form=form)


@accounts.route("/account/confirm", methods=["GET", "POST"])
def confirm_account() -> Response:
    """
    Handling account confirmation request via a token.
    If the token is valid and not expired, the user is activated.

    This view handles both GET and POST requests:
    - GET: Renders the account confirmation template.
    - POST: Activates the user account if the token is valid,
            logs the user in, and redirects to the index page.

    :return: Renders the confirmation template on GET request,
    redirects to login or index after POST.
    """
    token: str = request.args.get("token", None)

    # Verify the provided token and return token instance.
    auth_token = User.verify_token(
        token=token, salt=current_app.config["SALT_ACCOUNT_CONFIRM"]
    )

    if auth_token:
        # Retrieve the user instance associated with the token by providing user ID.
        user = User.get_user_by_id(auth_token.user_id, raise_exception=True)

        if request.method == "POST":
            try:
                # Activate the user's account and expire the token.
                user.active = True
                auth_token.expire = True

                # Commit changes to the database.
                db.session.commit()
            except Exception as e:
                # Handle database error that occur during the account activation.
                raise InternalServerError

            # Log the user in and set the session to remember the user for (15 days).
            login_user(user, remember=True, duration=timedelta(days=15))

            flash(
                f"Welcome {user.username}, You're registered successfully.", "success"
            )
            return redirect(url_for("accounts.index"))

        return render_template("confirm_account.html", token=token)

    # If the token is invalid, return a 404 error
    return abort(HTTPStatus.NOT_FOUND)


@accounts.route("/logout", methods=["GET", "POST"])
@login_required
def logout() -> Response:
    """
    Logs out the currently authenticated user
    and redirect them to the login page.

    :return: A redirect response to the login page with a success flash message.
    """
    # Log out the user and clear the session.
    logout_user()

    flash(_("You're logout successfully."), "success")
    return redirect(url_for("accounts.login"))


@accounts.route("/forgot/password", methods=["GET", "POST"])
@guest_user_exempt
@limiter.limit("3/minute", methods=["POST"])
def forgot_password() -> Response:
    """
    Handling forgot password requests by validating the provided email
    and sending a password reset link if the email is registered.

    This view handles both GET and POST requests:
    - GET: Renders the forgot password form and template.
    - POST: Validates the email and sends a reset link if the email exists in the system.

    :return: Renders the forgot password form on GET,
    redirects to login on success, or reloads the form on failure.
    """
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.data.get("email")

        # Attempt to find the user by email from the database.
        user = User.get_user_by_email(email=email)

        if user:
            # Send a reset password link to the user's email.
            send_reset_password(user)

            flash(
                _("A reset password link sent to your email. Please check."), "success"
            )
            return redirect(url_for("accounts.login"))

        flash(_("Email address is not registered with us."), "error")
        return redirect(url_for("accounts.forgot_password"))

    return render_template("forgot_password.html", form=form)


@accounts.route("/password/reset", methods=["GET", "POST"])
@limiter.limit("5/min", methods=["POST"])
def reset_password() -> Response:
    """
    Handling password reset requests.

    This function allows users to reset their password by validating a token
    and ensuring the new password meets security criteria.

    This view handles both GET and POST requests:
    - GET: Renders the reset password form and template, if the token is valid.
    - POST: Validates the form, checks password strength, and updates the user's password.

    :return: Renders the reset password form on GET,
    redirects to login on success, or reloads the form on failure.
    """
    salt = current_app.config["SALT_RESET_PASSWORD"]
    token = request.args.get("token", None)

    # Verify the provided token and return token instance.
    auth_token = User.verify_token(token=token, salt=salt)

    if auth_token:
        form = ResetPasswordForm()  # A form class to Reset User's Password.

        if form.validate_on_submit():
            password = form.data.get("password")
            confirm_password = form.data.get("confirm_password")

            if not (password == confirm_password):
                flash(_("Your new password field's did not match."), "error")
            else:
                try:
                    # Retrieve the user by the ID from the token and update their password.
                    user: User = User.get_user_by_id(
                        auth_token.user_id, raise_exception=True
                    )

                    if user.check_password(password):
                        flash(
                            "Your new password cannot be the same as the previous one.",
                            "error",
                        )
                    else:
                        user.set_password(password)

                        # Mark the token as expired after the password is reset.
                        auth_token.expire = True

                        # Commit changes to the database.
                        db.session.commit()

                        if current_user.is_authenticated:
                            flash(
                                "Your password is changed successfully.",
                                "success",
                            )
                            return redirect(url_for("accounts.index"))

                        flash(
                            "Your password reset successfully. Please login.", "success"
                        )
                        return redirect(url_for("accounts.login"))
                except Exception as e:
                    # Handle database error by raising an internal server error.
                    raise InternalServerError

            return redirect(url_for("accounts.reset_password", token=token))

        return render_template("reset_password.html", form=form, token=token)

    # If the token is invalid, abort with a 404 Not Found status.
    return abort(HTTPStatus.NOT_FOUND)


@accounts.route("/change/password", methods=["GET", "POST"])
@login_required
@guest_user_exempt
@limiter.limit("5/min", methods=["POST"])
def change_password() -> Response:
    """
    Handling user password change requests.

    This function allows authenticated users to change their password by
    verifying the old password and ensuring the new password meets security criteria.

    This view handles both GET and POST requests:
    - GET: Renders the change password form and template.
    - POST: Validates the form, checks old password correctness, ensures the new
      password meets security standards, and updates the user's password.

    :return: Renders the change password form on GET,
    redirects to index on success, or reloads the form on failure.
    """
    form = ChangePasswordForm()  # A form class to Change User's Password.

    if form.validate_on_submit():
        old_password = form.data.get("old_password")
        new_password = form.data.get("new_password")
        confirm_password = form.data.get("confirm_password")

        # Retrieve the fresh user instance from the database.
        user = User.get_user_by_id(current_user.id, raise_exception=True)

        # Regex pattern to validate password strength.
        re_pattern = (
            r"(?=^.{8,}$)(?=.*\d)(?=.*[!@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$"
        )

        if not user.check_password(old_password):
            flash(_("Your old password is incorrect."), "error")
        elif not (new_password == confirm_password):
            flash(_("Your new password field's not match."), "error")
        elif not re.match(re_pattern, new_password):
            flash(
                "Please choose strong password. It contains at least one alphabet, number, and one special character.",
                "warning",
            )
        else:
            try:
                # Update the user's password.
                user.set_password(new_password)

                # Commit changes to the database.
                db.session.commit()
            except Exception as e:
                # Handle database error by raising an internal server error.
                raise InternalServerError

            flash(_("Your password changed successfully."), "success")
            return redirect(url_for("accounts.index"))

        return redirect(url_for("accounts.change_password"))

    return render_template("change_password.html", form=form)


@accounts.route("/change/email", methods=["GET", "POST"])
@login_required
@guest_user_exempt
@limiter.limit("5/min", methods=["POST"])
def change_email() -> Response:
    """
    Handling email change requests for the logged-in user.

    Methods:
        GET: Render the email change form and template.
        POST: Process the form submission to change the user's email.

    Returns:
        Response: The rendered change email template or a redirect after form submission.
    """
    form = ChangeEmailForm()  # A form class for Change Email Address.

    if form.validate_on_submit():
        email = form.data.get("email", None)

        # Retrieve the fresh user instance based on their ID.
        user = User.get_user_by_id(current_user.id, raise_exception=True)

        if email == user.email:
            flash(_("Email is already verified with your account."), "warning")
        elif User.query.filter(User.email == email, User.id != user.id).first():
            flash(_("Email address is already registered with us."), "warning")
        else:
            try:
                # Update the new email as the pending email change.
                user.change_email = email

                # Commit changes to the database.
                db.session.commit()
            except Exception as e:
                # Handle database error by raising an internal server error.
                raise InternalServerError

            # Send a reset email to the new email address.
            send_reset_email(user)

            flash(
                "A reset email link sent to your new email address. Please verify.",
                "success",
            )
            return redirect(url_for("accounts.index"))

        return redirect(url_for("accounts.change_email"))

    return render_template("change_email.html", form=form)


@accounts.route("/account/email/confirm", methods=["GET", "POST"])
def confirm_email() -> Response:
    """
    Handle email confirmation via a token sent to the user's new email address.

    Methods:
        GET: Render the email confirmation template with the token.
        POST: Confirm the email change by verifying the token.

    Returns:
        Response: The rendered confirm email template, or a redirect after confirmation.
    """
    token = request.args.get("token", None)

    # Verify the provided token and return token instance.
    auth_token = User.verify_token(
        token=token, salt=current_app.config["SALT_CHANGE_EMAIL"]
    )

    if auth_token:
        if request.method == "POST":
            # Retrieve the user by the ID from the token and update email details.
            user = User.get_user_by_id(auth_token.user_id, raise_exception=True)

            try:
                # Update new email address to user.
                user.email = user.change_email
                user.change_email = None

                # Mark the token as expired after the new email is set.
                auth_token.expire = True

                # Commit changes to the database.
                db.session.commit()
            except Exception as e:
                # Handle database error by raising an internal server error.
                raise InternalServerError

            flash(_("Your email address updated successfully."), "success")
            return redirect(url_for("accounts.index"))

        return render_template("confirm_email.html", token=token)

    # If the token is invalid, abort with a 404 Not Found status.
    return abort(HTTPStatus.NOT_FOUND)


@accounts.get("/")
@accounts.get("/home")
@login_required
def index() -> Response:
    """
    Render the homepage for authenticated users.

    Returns:
        Response: Renders the `index.html` template.
    """
    return render_template("index.html")


@accounts.route("/profile", methods=["GET", "POST"])
@login_required
@guest_user_exempt
@limiter.limit("8/min", methods=["POST"])
def profile() -> Response:
    """
    Handling the user's profile page,
    allowing them to view and edit their profile information.

    Methods:
        GET: Render the profile template with the user's current information.
        POST: Update the user's profile with the submitted form data.

    Returns:
        Response: The rendered profile template or a redirect after form submission.
    """
    form = EditUserProfileForm()  # A form class to Edit User's Profile.

    # Retrieve the fresh user instance based on their ID.
    user = User.get_user_by_id(current_user.get_id(), raise_exception=True)

    if form.validate_on_submit():
        username = form.data.get("username")
        first_name = form.data.get("first_name")
        last_name = form.data.get("last_name")
        profile_image = form.data.get("profile_image")
        about = form.data.get("about")

        # Check if the new username already exists and belongs to a different user.
        username_exist = User.query.filter(
            User.username == username, User.id != current_user.id
        ).first()

        if username_exist:
            flash(_("Username already exists. Choose another."), "error")
        else:
            try:
                # Update the user's profile details.
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.profile.bio = about

                # Handle profile image upload if provided.
                if profile_image and getattr(profile_image, "filename"):
                    user.profile.set_avatar(profile_image)

                # Commit changes to the database.
                db.session.commit()
            except Exception as e:
                # Handle database error by raising an internal server error.
                print("Error while updating user profile:", e)
                raise InternalServerError

            flash(_("Your profile update successfully."), "success")
            return redirect(url_for("accounts.index"))

        return redirect(url_for("accounts.profile"))

    return render_template("profile.html", form=form)


@accounts.get("/account/settings")
@login_required
def settings() -> Response:
    """
    Render the settings page with delete account form.

    Returns:
        Response: Renders the `settings.html` template.
    """
    form = DeleteAccountForm()  # A form class to delete user's account.
    return render_template("settings.html", form=form)


@accounts.post("/account/delete")
@login_required
@guest_user_exempt
@limiter.limit("3/minute", methods=["POST"])
def delete_user() -> Response:
    """
    Handle the deletion of the current logged-in user's account.

    Returns:
        Response: A redirect to the login page on successful deletion, or the settings page on failure.
    """
    password = request.form.get("password", "")

    # Get the currently logged-in user.
    user: User = current_user

    if user and user.check_password(password):
        # Delete the currently logged-in user's account.
        user.delete()

        # Log the user out and remove their session.
        logout_user()

        flash(_("Your account has been deleted successfully."), "success")
        return redirect(url_for("accounts.login"))

    flash(_("Incorrect password. We're unable to delete your account."), "error")
    return redirect(url_for("accounts.settings"))


@accounts.post("/account/google-login")
@guest_user_exempt
@limiter.limit("3/minute", methods=["POST"])
def google_login() -> Response:
    """
    Initiates the Google OAuth login process.
    """
    redirect_uri = url_for("accounts.google_login_callback", _external=True)

    try:
        return oauth.google.authorize_redirect(redirect_uri)
    except (ConnectionError, OAuthError) as e:
        flash(
            "Unable to login with Google. Please check your connection and try again.",
            "error",
        )
        return redirect(url_for("accounts.login"))


@accounts.get("/account/google-login/callback")
@guest_user_exempt
def google_login_callback() -> Response:
    """
    Handles the callback from Google OAuth provider after user authentication.

    Returns:
        Response: Redirects to the login page with a success or error message.
    """
    try:
        token = oauth.google.authorize_access_token()
    except (OAuthError, TokenExpiredError) as e:
        flash(_("Google login failed. Please try again."), "error")
        return redirect(url_for("accounts.login"))

    if token:
        # Fetch the user's information from Google.
        user_info = token.get("userinfo")

        email = user_info.get("email")
        email_verified = user_info.get("email_verified", False)

        if email and email_verified:
            # Check if the oauth user already exists into the database.
            oauth_user = OAuthProvider.query.filter_by(
                provider="google", provider_id=user_info.get("sub")
            ).first()

            if current_user.is_authenticated:
                # If the user is authenticated, check if the Google account is already linked.
                if oauth_user and oauth_user.user_id != current_user.id:
                    flash(
                        "This Google account is already linked with another user account.",
                        "error",
                    )
                    return redirect(url_for("accounts.settings"))

                # If the user already exists, retrieve the user instance.
                user = User.get_user_by_id(current_user.get_id(), raise_exception=True)

                # Create a new OAuth provider for the user.
                user.create_oauth_provider(provider_id=user_info.get("sub", ""))

                flash(_("Your Google account has been linked successfully."), "success")

            else:
                if not oauth_user:
                    # If the user does not exist, create a new user
                    user = User.get_or_create(
                        username=get_username_from_email(email),
                        first_name=user_info.get("given_name", ""),
                        last_name=user_info.get("family_name", ""),
                        email=email,
                        password=get_unique_id(),  # Password is not needed for social login.
                    )

                    # Ensure the user is active.
                    user.active = True

                    # Create a new OAuth provider for the user.
                    user.create_oauth_provider(provider_id=user_info.get("sub", ""))
                else:
                    # If the user already exists, retrieve the user instance.
                    user = User.get_user_by_id(oauth_user.user_id)

            user_profile = user.profile

            # Updating users profile data.
            if user_profile and not user_profile.avatar:
                picture_url = user_info.get("picture", "")

                # Download and save the user's profile picture.
                avatar = download_and_save_image_from_url(
                    url=picture_url, filename=f"{get_unique_id()}.jpg"
                )

                user_profile.avatar = url_for(
                    "static", filename="assets/uploads/profile/%s" % avatar
                )

            # Commit changes to the database.
            db.session.commit()

            if not current_user.is_authenticated:
                # Log the user in and set the session to remember the user for (15 days).
                login_user(user, remember=True, duration=timedelta(days=15))

                flash(_("You are logged in successfully."), "success")
                return redirect(url_for("accounts.index"))

            return redirect(url_for("accounts.settings"))

    flash(_("Google login failed. Please try again."), "error")
    return redirect(url_for("accounts.login"))


@accounts.post("/account/oauth/remove")
@login_required
@limiter.limit("3/minute", methods=["POST"])
def remove_oauth_provider() -> Response:
    """
    Remove the OAuth provider (e.g; Google) from the user's account.

    Returns:
        Response: A redirect to the settings page with a success message.
    """
    provider = request.args.get("provider", "google")

    if not provider in current_app.config["OAUTH_PROVIDERS"]:
        flash(_("Something wrong with your request."), "error")
        return redirect(url_for("accounts.settings"), code=HTTPStatus.BAD_REQUEST)

    user = User.get_user_by_id(current_user.get_id(), raise_exception=True)

    if user and user.is_social_user():
        # Remove the `provider` account from the user's account.
        user.remove_oauth_provider(provider)

        flash(
            f"Your {provider} login provider has been removed successfully.", "success"
        )
        return redirect(url_for("accounts.settings"))

    flash(f"Failed to remove {provider} provider.", "error")
    return redirect(url_for("accounts.settings"))
