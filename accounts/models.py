import os
import typing as t
import requests

from datetime import datetime, timedelta

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy import event, or_
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlalchemy.ext.declarative import DeclarativeMeta

from werkzeug.exceptions import InternalServerError, HTTPException
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from flask import current_app, url_for

from flask_login.mixins import UserMixin

from accounts.extensions import database as db
from accounts.utils import (
    get_unique_id,
    get_unique_filename,
    remove_existing_file,
    unique_security_token,
    generate_unique_username,
)


class BaseModel(db.Model):
    """
    A Base Model class for other models.
    """

    __abstract__ = True

    id = db.Column(
        db.String(36),
        default=get_unique_id,
        primary_key=True,
        nullable=False,
        unique=True,
    )

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


class User(BaseModel, UserMixin):
    """
    A Base User model class.
    """

    __tablename__ = "user"

    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # common account settings
    active = db.Column(db.Boolean, default=False, nullable=False, server_default="0")
    change_email = db.Column(db.String(120), default="")

    @classmethod
    def authenticate(
        cls, username: t.AnyStr = None, password: t.AnyStr = None
    ) -> t.Optional["User"]:
        """
        Authenticates a user based on their username or email and password.

        :param username: The (username or email) of the user attempting to authenticate.
        :param password: The password of the user attempting to authenticate.

        :return: The authenticated user object if credentials are correct, otherwise None.
        """
        user = cls.query.filter(
            or_(
                cls.username == username,
                cls.email == username,
            )
        ).first()

        if user and user.check_password(password):
            return user

        return None

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new user instance, set the password,
        and save it to the database.

        :return: The newly created user instance.

        :raises InternalServerError: If there is an error while creating or saving the user.
        """
        password = kwargs.get("password")

        try:
            user = cls(**kwargs)
            user.set_password(password)
            user.save()
        except Exception as e:
            print("Error creating user: %s" % e)
            # Handle database error by raising an internal server error.
            raise InternalServerError

        return user

    @classmethod
    def get_or_create(cls, **kwargs) -> "User":
        """
        Get an existing user or create a new one if it doesn't exist.

        :return: The existing or newly created user instance.
        """
        email = kwargs.get("email")
        username = kwargs.get("username")

        # Check if the user already exists by email.
        user = cls.get_user_by_email(email)

        if not user:
            username_exist = cls.get_user_by_username(username)

            if username_exist:
                kwargs["username"] = generate_unique_username(email)

            user = cls.create(**kwargs)

        return user

    @classmethod
    def get_user_by_id(cls, user_id: t.AnyStr, raise_exception: bool = False):
        """
        Retrieves a user instance from the database
        based on their User ID.

        :param user_id: The ID of the user to retrieve instance.
        """
        if raise_exception:
            return cls.query.get_or_404(user_id)

        return cls.query.get(user_id)

    @classmethod
    def get_user_by_username(cls, username: t.AnyStr):
        """
        Retrieves a user instance from the database
        based on their username.

        :param username: The username of the user to retrieve.
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_user_by_email(cls, email: t.AnyStr):
        """
        Retrieves a user instance from the database
        based on their email address.

        :param email: The email address of the user to retrieve.
        """
        return cls.query.filter_by(email=email).first()

    def set_password(self, password: t.AnyStr):
        """
        Sets the password for the user after hashing it.

        :param password: The plain-text password to hash and set.
        """
        self.password = generate_password_hash(password)

    def check_password(self, password: t.AnyStr) -> bool:
        """
        Checks if the provided password matches the hashed password.

        :param password: The plain-text password to check.
        """
        return check_password_hash(self.password, password)

    def generate_token(self, salt: str) -> t.AnyStr:
        """
        Generates a new security token for the user.

        :return: The newly created security token.
        """
        instance = UserSecurityToken.create_new(salt=salt, user_id=self.id)
        return instance.token

    @staticmethod
    def verify_token(
        token: t.AnyStr, salt: str, raise_exception: bool = True
    ) -> t.Union[t.Optional["UserSecurityToken"], HTTPException, None]:
        """
        Verifies whether a security token is valid and not expired.

        :param token: The security token to verify.
        :param raise_exception: If True, raises a 404 error if the token is not found. Defaults to True.

        :return: `True` if the token exists and is not expired, `False` otherwise.
        """
        instance = UserSecurityToken.query.filter_by(token=token, salt=salt)

        if raise_exception:
            token = instance.first_or_404()
        else:
            token = instance.first()

        if token and not token.is_expired:
            return token

        return None

    def send_confirmation(self):
        """
        Sends a confirmation email to the user for account activation.
        """
        from accounts.email_utils import send_confirmation_mail

        send_confirmation_mail(self)

    def create_oauth_provider(
        self, provider: str = "google", provider_id: str = None
    ) -> "OAuthProvider":
        """
        Creates a new OAuth provider instance for the user.

        provider: The name of the OAuth provider (e.g., "google").
        provider_id: The unique 'sub' provided by the OAuth provider.

        :return: The newly created OAuth provider instance.
        """

        instance = OAuthProvider(
            provider=provider,
            provider_id=provider_id,
            user_id=self.id,
        )
        instance.save()

        return instance

    def remove_oauth_provider(self, provider: str = "google"):
        """
        Removes the OAuth provider instance associated with the user.

        :param provider: The name of the OAuth provider to remove.
        """
        instance = OAuthProvider.query.filter_by(provider=provider, user_id=self.id)

        if instance:
            instance.delete()

            # Commit the changes to the database.
            db.session.commit()

    @property
    def profile(self):
        """
        Retrieves the user's profile instance from the database.

        :return: The user's profile object, or None if no instance is found.
        """
        profile = Profile.query.filter_by(user_id=self.id).first()
        return profile

    @property
    def is_active(self) -> bool:
        """
        Checks if the user's account is active.

        :return: `True` if the user account is active, otherwise `False`.
        """
        return self.active

    def is_social_user(self, provider: str = "google") -> bool:
        """
        Checks if a user account is connected to any oauth provider.

        :return: `True` if connected with oauth provider, otherwise `False`.
        """
        instance = OAuthProvider.query.filter_by(
            provider=provider, user_id=self.id
        ).first()

        return instance is not None

    def __repr__(self):
        return "<User '{}'>".format(self.username)


class Profile(BaseModel):
    """
    A User profile model class.
    """

    __tablename__ = "user_profile"

    bio = db.Column(db.String(200), default="")
    avatar = db.Column(db.String(250), default="")

    user_id = db.Column(
        db.String(36), db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    user = db.Relationship("User", foreign_keys=[user_id])

    @property
    def get_avatar(self) -> t.Optional[t.Text]:
        """
        Returns the URL of the user's avatar image if it exists,
        otherwise returns the `default-avatar` image URL.
        """
        # Check if the avatar file exists in the `local` upload folder.
        file_exist = os.path.isfile(current_app.root_path + self.avatar)

        if not self.avatar or not file_exist:
            return url_for("static", filename="assets/images/default_avatar.png")

        return self.avatar

    def set_avatar(self, profile_image, file_path: t.Optional[t.Text] = "profile"):
        """
        Set a new avatar for the user by removing the existing avatar (if any), saving the new one,
        and updating the user's avatar field in the database.

        :param profile_image: The uploaded image file to be set as the new avatar.
        :param file_path: The path where the avatar image will be saved.

        :raises InternalServerError: If there is an error during the file-saving process.
        """
        from config import UPLOAD_FOLDER

        # Construct the save path for the avatar image.
        save_path = os.path.join(UPLOAD_FOLDER, file_path)

        if self.avatar:
            try:
                # Remove the existing avatar file if it exists.
                path = current_app.root_path + self.avatar
                remove_existing_file(path)
            except OSError as e:
                # Handle the case where the path is not valid.
                print("Error getting avatar path: %s" % e)

        # Ensure the upload folder exists.
        os.makedirs(os.path.join(save_path), exist_ok=True)

        # Generate a unique filename for the new avatar.
        filename = get_unique_filename(profile_image.filename)

        # Set the avatar URL to the database avatar field.
        self.avatar = url_for(
            "static", filename="assets/uploads/%s/%s" % (file_path, filename)
        )

        try:
            # Save the new avatar file to the local file storage.
            profile_image.save(os.path.join(save_path, filename))
        except Exception as e:
            # Handle exceptions that might occur during file saving.
            print("Error saving avatar: %s" % e)
            raise InternalServerError

    def __repr__(self):
        return "<Profile '{}'>".format(self.user.username)


class UserSecurityToken(BaseModel):
    """
    A token class for storing security tokens for url.
    """

    __tablename__ = "user_security_token"

    __table_args__ = (
        Index("ix_user_token_token", "token"),
        Index("ix_user_token_expire", "expire"),
        UniqueConstraint("token", "salt", name="uq_token_salt"),
    )

    token = db.Column(
        db.String(72), default=unique_security_token, nullable=False, unique=True
    )

    salt = db.Column(db.String(20), nullable=False)

    expire = db.Column(db.Boolean, default=False, nullable=False, server_default="0")

    user_id = db.Column(
        db.String(36), db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    user = db.Relationship("User", foreign_keys=[user_id])

    @classmethod
    def create_new(cls, **kwargs) -> "UserSecurityToken":
        """
        Creates a new security token instance for a user
        and saves it to the database.

        :param user_id: The ID of the user for whom the token is being created.
        :return: The generated security token string.

        :raises InternalServerError: If there is an error saving the token to the database.
        """
        try:
            instance = cls(**kwargs)
            instance.save()
        except Exception as e:
            # Handle database error by raising an internal server error.
            print("Error creating security token: %s" % e)
            raise InternalServerError

        return instance

    @property
    def is_expired(self) -> bool:
        """
        Checks if the token has expired based
        on its creation time and expiration period.
        """
        if not self.expire:
            expiry_time = self.created_at + timedelta(minutes=15)
            current_time = datetime.now()

            if not expiry_time <= current_time:
                return False

        self.delete()
        return True

    @classmethod
    def is_exists(cls, token: t.AnyStr = None) -> t.Optional["UserSecurityToken"]:
        """
        Check if a token already exists in the database.

        :param token: The token to check for existence.

        :return: The first instance found with the specified token,
        or None if not found.
        """
        return cls.query.filter_by(token=token).first()

    def __repr__(self):
        return "<Token '{}' by {}>".format(self.token, self.user)


class OAuthProvider(BaseModel):
    """
    A Class represents a user's OAuth login provider
    and their associated provider ID.
    """

    __tablename__ = "user_oauth_provider"
    __table_args__ = (
        UniqueConstraint(
            "provider", "provider_id", "user_id", name="uq_oauth_providers"
        ),
    )

    # Provider name and provider ID.
    provider = db.Column(db.String(50), nullable=False, index=True)
    provider_id = db.Column(db.String(200), unique=True, nullable=False, index=True)

    user_id = db.Column(
        db.String(36), db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    def __repr__(self):
        return f"OAuthProvider {self.provider} for User {self.user_id}"


@event.listens_for(User, "after_insert")
def create_profile_for_user(
    mapper: Mapper, connection: Connection, target: DeclarativeMeta
):
    # Create a Profile instance for the recently created user.
    profile = Profile(user_id=target.id)

    # Execute an INSERT statement to add the user's profile table to the database.
    connection.execute(Profile.__table__.insert(), {"user_id": profile.user_id})
