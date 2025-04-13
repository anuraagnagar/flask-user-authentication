import click

from flask import Flask
from flask import current_app

from accounts.models import User


def register_cli_command(app: Flask):
    """
    Registers custom CLI commands to the Flask application instance.
    """

    @app.cli.command("createtestuser")
    def create_test_user():
        """
        Create an initial test user using credentials from app config.
        """
        user_data = {
            "username": current_app.config["TEST_USER_USERNAME"],
            "email": current_app.config["TEST_USER_EMAIL"],
            "first_name": "Test",
            "last_name": "User",
            "password": current_app.config["TEST_USER_PASSWORD"],
            "active": True,
        }

        # Check if the test user already exists.
        existing_user = User.get_user_by_email(email=user_data["email"])

        if existing_user:
            click.echo(f"Test user already created!")
            return

        try:
            # Create and add the demo guest user to the database.
            User.create(**user_data)
            
            click.echo(f"Test user created successfully!.")
        except Exception as e:
            raise click.ClickException("Failed to create Test User: {e}")
