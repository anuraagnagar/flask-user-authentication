# User Authentication System in Flask/Python

### A Simple Authentication System Project with basic user functionality in Python Flask with SQLAlchemy.

## 👩‍💻 Live Demo

#### 🔗https://flaskauth.pythonanywhere.com

## Project features & functionality

- Create account
- Log In via (Username & Email address)
- Logout
- Account activation via verification link
- Reset password via reset link
- Reset new email via confirmation link
- Update profile details & add profile image
- Change password after login

## Framework & Library

1. [Flask](https://flask.palletsprojects.com/)
2. [Flask-Login](https://flask-login.readthedocs.io/)
3. [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
4. [Flask-WTF](https://flask-wtf.readthedocs.io/)
5. [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
6. [Flask-Migrate](https://flask-migrate.readthedocs.io)
7. [Bootstrap-Flask](https://bootstrap-flask.readthedocs.io/)
8. [Jinja2](https://jinja.palletsprojects.com/)

## Application Screenshots

### Register Page

![Register](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/register_page.png)

### Login Page

![Login](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/login_page.png)

### Forgot Password Page

![Forgot Password](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/forgot_password_page.png)

### Reset Password Page

![Reset Password](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/reset_password_page.png)

### Reset Email Page

![Reset Email](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/reset_email_page.png)

### Home Page

![Home](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/home_page.png)

### Edit Profile Page

![Edit Profile](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/profile_page.png)

### Change Password Page

![Change Password](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/change_password_page.png)

## Set up & Run locally.

### 1. Clone the git repository.

```bash
git clone https://github.com/anuraagnagar/flask-user-authentication.git
```

### 2. Go to the project directory.

```bash
cd flask-user-authentication
```

### 3. Create virtual environment.

```bash
python3 -m venv venv
```

### 4. Activate the environment.

On Windows

```bash
venv\scripts\activate
```

On MacOS/Linux

```bash
source venv/bin/activate
```

To run this project locally, you will need to change `.env.example` file to `.env` on base directory
and set the environment variables.

### 5. Install the requirement packages.

```bash
pip install -r requirements.txt
```

### 6. Migrate/Create a database.

**Note**: Before initializing the database, run the `flask run` command in your terminal to ensure that
the application is set up properly. This allows you to access the `flask db` command for database migrations.

Initialize the database migration directory.

```bash
flask db init
```

Run migrate command.

```bash
flask db migrate -m "initial_migration"
```

Upgrade the database for latest migration.

```bash
flask db upgrade
```

### 7. Last to run the server.

Once the database is set up, you can run the Flask server to start your application.

```bash
flask run
```

To access this application open `http://localhost:5000` in your web browser.

## Contributing

Contributions are welcome! If you find a bug or want to add a new feature, please open an issue or submit a pull request.
For more information checkout ![CONTRIBUTING.md](https://github.com/anuraagnagar/flask-user-authentication/blob/main/CONTRIBUTING.md)

## Licence

By contributing to this project, you agree that your contributions will be licensed under the ![MIT License](https://github.com/anuraagnagar/flask-user-authentication/blob/main/LICENSE).

## Author

[Anurag Nagar](mailto:nagaranurag1999@gmail.com)
