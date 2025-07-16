import os
import secrets
import random
import string
import uuid
import typing as t

from werkzeug.utils import secure_filename

from flask import current_app


def get_unique_id() -> t.AnyStr:
    """
    Generate a unique identifier using `uuid4()`.

    Returns:
        str: A unique identifier string.
    """
    return str(uuid.uuid4())


def unique_security_token() -> t.AnyStr:
    """
    Generate a unique security token that does not already
    exist in the `UserSecurityToken` model.

    Recursively generates a new token if a collision is found.

    Returns:
        str: A unique security token.
    """
    from .models import UserSecurityToken

    generated_token = secrets.token_hex()

    token_exist = UserSecurityToken.is_exists(generated_token)

    if not token_exist:
        return generated_token

    return unique_security_token()


def get_unique_filename(filename: t.Text = None) -> t.Text:
    """
    Generate a unique filename by appending a `uuid4()` to the original file extension.

    Returns:
        str: A new filename with a unique `uuid4()` or None if no filename is provided.
    """
    if not filename:
        return None

    filename = secure_filename(filename).split(".")
    return "{}.{}".format(str(uuid.uuid4()), filename[len(filename) - 1])


def get_full_url(endpoint: str) -> str:
    """
    Construct a full url by combining the site `URL` from
    configuration with a given endpoint.

    Returns:
        str: The full `URL`.
    """
    domain = current_app.config["SITE_URL"]
    return "".join([domain, endpoint])


def remove_existing_file(path=None):
    """
    Remove an existing file from the filesystem.
    """
    if os.path.isfile(path=path):
        os.remove(path)


def get_username_from_email(email: str) -> str:
    """
    Create a username from the email address by taking the part before the '@'.

    Args:
        email (str): The email address.

    Returns:
        str: The username derived from the email.
    """
    if not email or "@" not in email:
        return None

    return email.split("@")[0]


def generate_unique_username(email: str = None) -> str:
    """
    Generates a random username.
    If email is provided, uses the prefix of the email as a base.

    Example output: john_doe_3f9x or user_7gkx

    :param email: Optional email to derive base username from.
    :return: A random unique-looking username string.
    """
    if email:
        base = email.split("@")[0].lower()
    else:
        base = "user"

    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{base}_{suffix}"


def download_and_save_image_from_url(
    url: str, save_path: str = None, filename: str = None
) -> str:
    """
    Downloads image from the url and saves to specific path.

    :params url: The URL of the image to download.
    :params save_path: Optional directory where the image will be saved.
    :params filename: Optional custom filename for the saved image.

    Returns:
        str: The filename of the saved image.
    """
    import requests

    from config import UPLOAD_FOLDER

    if not save_path:
        save_path = os.path.join(UPLOAD_FOLDER, "profile")

    os.makedirs(save_path, exist_ok=True)

    if not filename:
        filename = get_unique_filename(os.path.basename(url))

    file_path = os.path.join(save_path, filename)

    try:
        response = requests.get(url, stream=True, timeout=5)
        response.raise_for_status()

        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            return filename
        else:
            return None
    except requests.RequestException as e:
        current_app.logger.error(f"Error downloading image: {e}")
        return None
