from accounts import create_app, database

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        database.create_all()
    app.run()