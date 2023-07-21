# User Authentication System in Flask/Python

A Simple Authentication Project in Python Flask and SQLAlchemy with basic user functionality.

## 👩‍💻 Live Demo

### 🔗https://anuraag01.pythonanywhere.com/home

## Project features & functionality

- Create account
- Log In via (Username & Email address)
- Logout
- Account activation via email
- Reset password via reset link
- Reset new email via confirmation link
- Update profile & add image
- Change password after login
- Internationalize & Language :
  - English, Hindi, French, Russian, & Spanish

## Framework & Library

1. [Flask](https://flask.palletsprojects.com/)
2. [Flask-Login](https://flask-login.readthedocs.io/)
3. [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
4. [Flask-WTF](https://flask-wtf.readthedocs.io/)
5. [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
6. [Flask-Migrate](https://flask-migrate.readthedocs.io)
7. [Bootstrap-Flask](https://bootstrap-flask.readthedocs.io/)
8. [Jinja2](https://jinja.palletsprojects.com/)

## Some Screenshots of our Project

### Register Page

![Register](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/register_page.jpg)

### Login Page

![Login](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/login_page.jpg)

### Forgot Password Page

![Forgot Password](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/forgot_password_page.jpg)

### Reset Password Page

![Reset Password](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/reset_password_page.jpg)

### Reset Email Page

![Reset Email](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/reset_email_page.jpg)

### Home Page

![Home](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/home_page.jpg)

### Edit Profile Page

![Edit Profile](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/profile_page.jpg)

### Change Password Page

![Change Password](https://github.com/anuraagnagar/flask-user-authentication/blob/main/screenshots/change_password_page.jpg)

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

### 5. Install the requirement package.

```bash
pip install -r requirements.txt
```

### 6. Migrate/Create a database.

```bash
flask db init
flask db migrate -m "initial_migration"
flask db upgrade
```

To run this project locally, you will need to add .env file on base directory and set following environment variables.

`FLASK_DEBUG=True`

`FLASK_APP=app.py`

`FLASK_ENV=development`

`SECRET_KEY=your-super-secret-key-here`

### 7. Last to run the application.

```bash
flask run
```
