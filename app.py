import os

from accounts import create_app

config_type = os.getenv("FLASK_ENV")

app = create_app(config_type)

if __name__ == "__main__":
    app.run()
