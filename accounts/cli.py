import os
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
            click.secho(f"Test user already created!", fg="green")
            return

        try:
            # Create and add the demo guest user to the database.
            User.create(**user_data)

            click.secho(f"✔ Test user created successfully!.", fg="green")
        except Exception as e:
            raise click.ClickException("Failed to create Test User: {e}")

    @app.cli.command("clear-migrations")
    def clear_migrations():
        """
        Clear all migration files in the migrations/versions directory.
        """
        base_dir = os.path.join(current_app.root_path, "..")
        migrations_dir = os.path.join(base_dir, "migrations", "versions")

        if not os.path.exists(migrations_dir):
            click.echo("No migrations/versions directory found.")
            return

        removed_files = 0

        for filename in os.listdir(migrations_dir):
            file_path = os.path.join(migrations_dir, filename)

            if os.path.isfile(file_path):
                os.remove(file_path)
                removed_files += 1
                click.secho(f"🗑 Removed: {filename}", fg="cyan")

        if removed_files:
            click.secho(f"\n✔ Cleared {removed_files} migration file(s).", fg="green")
        else:
            click.secho("No migration files to delete.", fg="green")
