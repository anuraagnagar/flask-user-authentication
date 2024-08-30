import os
import typing as t

from datetime import datetime, timedelta

from sqlalchemy import Index
from sqlalchemy import event, or_
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlalchemy.ext.declarative import DeclarativeMeta

from werkzeug.exceptions import InternalServerError, HTTPException
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from flask import url_for
from flask_login.mixins import UserMixin

from accounts.extensions import database as db
from accounts.utils import (
    get_unique_filename,
    remove_existing_file,
    unique_security_token,
    get_unique_id,
)


class BaseModel(db.Model):
    """
    A Base Model class for other models.
    """

    __abstract__ = True

    id = db.Column(
        db.String(38),
        primary_key=True,
        default=get_unique_id,
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

    active = db.Column(db.Boolean, default=False, nullable=False, server_default="0")
    change_email = db.Column(db.String(120), default="")

    @classmethod
    def authenticate(
        cls, username: t.AnyStr = None, password: t.AnyStr = None
    ) -> t.Optional["User"]:
        """
        Authenticates a user based on their username or email and password.

        :param username: The username or email of the user attempting to authenticate.
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
            # Handle database error by raising an internal server error.
            raise InternalServerError

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

    def generate_token(self) -> t.AnyStr:
        """
        Generates a new security token for the user.

        :return: The newly created security token.
        """
        instance = UserSecurityToken.create_new(user_id=self.id)
        return instance.token

    @staticmethod
    def verify_token(
        token: t.AnyStr, raise_exception: bool = True
    ) -> t.Union[t.Optional["UserSecurityToken"], HTTPException, None]:
        """
        Verifies whether a security token is valid and not expired.

        :param token: The security token to verify.
        :param raise_exception: If True, raises a 404 error if the token is not found. Defaults to True.

        :return: `True` if the token exists and is not expired, `False` otherwise.
        """
        instance = UserSecurityToken.query.filter_by(token=token)

        if raise_exception:
            token = instance.first_or_404()
        else:
            token = instance.first()

        if token and not token.is_expired:
            return token

        return None

    def send_confirmation(self):
        """
        Sends user's account confirmation email.
        """
        from accounts.email_utils import send_confirmation_mail

        send_confirmation_mail(self)

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

    def __repr__(self):
        return "<User '{}'>".format(self.username)


class Profile(BaseModel):
    """
    A User profile model class.
    """

    __tablename__ = "user_profile"

    bio = db.Column(db.String(200), default="")
    avator = db.Column(db.String(250), default="")

    user_id = db.Column(
        db.String(38), db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    user = db.Relationship("User", foreign_keys=[user_id])

    def set_avator(self, profile_image):
        """
        Set a new avatar for the user by removing the existing avatar (if any), saving the new one,
        and updating the user's avatar field in the database.

        :param profile_image: The uploaded image file to be set as the new avatar.

        :raises InternalServerError: If there is an error during the file-saving process.
        """
        from config import UPLOAD_FOLDER

        if self.avator:
            path = os.path.join(UPLOAD_FOLDER, self.avator)
            remove_existing_file(path=path)

        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)

        self.avator = get_unique_filename(profile_image.filename)

        try:
            # Save the new avatar file to the file storage.
            profile_image.save(os.path.join(UPLOAD_FOLDER, self.avator))
        except Exception as e:
            # Handle exceptions that might occur during file saving.
            print("Error saving avatar: %s" % e)
            raise InternalServerError

    def __repr__(self):
        return "<Profile '{}'>".format(self.user.username)


class UserSecurityToken(BaseModel):
    """
    A token class for storing security token for url.
    """

    __tablename__ = "user_token"

    __table_args__ = (
        Index("ix_user_token_token", "token"),
        Index("ix_user_token_expire", "expire"),
    )

    token = db.Column(
        db.String(72), default=unique_security_token, nullable=False, unique=True
    )

    expire = db.Column(db.Boolean, default=False, nullable=False, server_default="0")

    user_id = db.Column(
        db.String(38), db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    user = db.Relationship("User", foreign_keys=[user_id])

    @classmethod
    def create_new(cls, user_id: t.AnyStr) -> t.AnyStr:
        """
        Creates a new security token instance for a user
        and saves it to the database.

        :param user_id: The ID of the user for whom the token is being created.
        :return: The generated security token string.

        :raises InternalServerError: If there is an error saving the token to the database.
        """
        try:
            instance = cls(user_id=user_id)
            instance.save()
        except Exception as e:
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
    def is_exists(cls, token: t.AnyStr = None):
        """
        Check if a token already exists in the database.

        :param token: The token to check for existence.

        :return: The first instance found with the specified token,
        or None if not found.
        """
        return cls.query.filter_by(token=token).first()

    def __repr__(self):
        return "<Token '{}' by {}>".format(self.token, self.user)


@event.listens_for(User, "after_insert")
def create_profile_for_user(
    mapper: Mapper, connection: Connection, target: DeclarativeMeta
):
    # Create a Profile instance for the recently created user.
    profile = Profile(user_id=target.id)

    # Execute an INSERT statement to add the user's profile table to the database.
    connection.execute(Profile.__table__.insert(), {"user_id": profile.user_id})
