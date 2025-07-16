# User Authentication System in Flask/Python

### A Simple Authentication System Project with basic user functionality in Python Flask with SQLAlchemy.

#### 🌐 [Go to Website](https://flaskauth.pythonanywhere.com)

## 🧩 Project features & functionality

### ✅ User Account Management

- Create an account
- Log In via username or email
- Social login with Google OAuth
- Log out effortlessly

### ✅ Account Security

- Email verification for account activation
- Reset password via secure link
- Update email address with confirmation link
- Google reCAPTCHA support for login and register forms

### ✅ Profile Customization

- Edit profile details and upload a profile image
- Change password anytime after logging in
- Set new theme preferences

## 🧰 Framework & Library

- [Flask](https://flask.palletsprojects.com)
- [Flask-Login](https://flask-login.readthedocs.io)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com)
- [Flask-WTF](https://flask-wtf.readthedocs.io)
- [Flask-Mail](https://pythonhosted.org/Flask-Mail)
- [Flask-Migrate](https://flask-migrate.readthedocs.io)
- [Flask-Limiter](https://flask-limiter.readthedocs.io)
- [Bootstrap-Flask](https://bootstrap-flask.readthedocs.io)
- [Authlib](https://docs.authlib.org)
- [Jinja2](https://jinja.palletsprojects.com)
- [Pytest](https://docs.pytest.org)

## ⚙️ Prerequisites

#### Before running this application, ensure you have the following installed:

- [Docker](https://www.docker.com)

- [Git](https://git-scm.com/downloads) (for cloning the repository)

For local (without Docker) setup, you’ll need:

- [Python 3.10+](https://www.python.org/downloads/)

- pip (Python package installer)

- [PostgreSQL](https://www.postgresql.org/download/) / [SQLite](https://www.sqlite.org) (depending on your DB setup ignore if using docker)

Make sure to also have:

- A `.env` file with required environment variables (see `.env.example`)

- Access to required API keys or credentials (e.g., for Flask-mail, OAuth logins, Google re-captcha)

## 📸 Application Demo Screenshots

### Register Page

![Register](/screenshots/register_page.png)

### Login Page

![Login](/screenshots/login_page.png)

### Forgot Password Page

![Forgot Password](/screenshots/forgot_password_page.png)

### Reset Password Page

![Reset Password](/screenshots/reset_password_page.png)

### Home Page

![Home](/screenshots/home_page.png)

### Edit Profile Page

![Edit Profile](/screenshots/profile_page.png)

### Reset Email Page

![Reset Email](/screenshots/reset_email_page.png)

### Change Password Page

![Change Password](/screenshots/change_password_page.png)

### Account Setting Page

![Change Password](/screenshots/account_setting_page.png)

## 🛠️ Set up project & Run locally.

#### 1. Clone the git repository.

```bash
git clone https://github.com/anuraagnagar/flask-user-authentication.git
```

#### 2. Go to the project directory.

```bash
cd flask-user-authentication
```

---

> **Note**: To run this project, you will need to change `.env.example` file to `.env` on base directory and set the environment variables.

### ❄️ Run With Docker

You can run this project with Docker. For that, you need to have [Docker](https://www.docker.com/get-started) installed and running on your machine.

To run the project with Docker, follow these steps:

#### Start the Docker container.

```bash
docker compose -f docker/docker-compose-local.yml up
```

### 🚀 Or Continue with Normal Setup

#### 3. Create and Activate the virtual environment.

On Windows

```bash
python -m venv venv
```

```bash
venv\scripts\activate
```

On MacOS/Linux/Unix

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

#### 4. Install the requirement packages.

```bash
pip install -r requirements.txt
```

#### 5. Migrate/Create a database.

> **Note**: In some cases, the `flask db` command might not appear until the application is started with `flask run` command. Make sure to run this command before proceeding with any database migrations.

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

#### 6. Creating initial test user.

Create a Initial Test User for our application.

```bash
flask createtestuser
```

#### 7. Last to run the server.

Once the database is set up, you can run the Flask server to start your application.

```bash
flask run
```

To access this application open `http://localhost:5000` in your web browser.

## 🤝 Contributing

Contributions are welcome! If you find a bug or want to add a new feature, please open an issue or submit a pull request.
For more information checkout [CONTRIBUTING.md](https://github.com/anuraagnagar/flask-user-authentication/blob/main/CONTRIBUTING.md)

## 🪪 Licence

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](https://github.com/anuraagnagar/flask-user-authentication/blob/main/LICENSE).

## 👤 Author

[Anurag Nagar](mailto:nagaranurag1999@gmail.com)
