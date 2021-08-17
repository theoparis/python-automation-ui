from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from werkzeug.security import generate_password_hash
from flask_login import LoginManager

db: SQLAlchemy = SQLAlchemy()
DB_NAME = "database.sqlite"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "58cc386f862812a6b89102ca3c329f6519cd24805f84f2"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    create_database(app)

    # Create admin user if it doesn't exist
    with app.app_context():
        admin_exists = db.session.query(User.username).filter_by(
            username="admin").first() is not None
        if not admin_exists:
            admin_user = User(username="admin", password=generate_password_hash(
                "toor", method="sha256"))
            db.session.add(admin_user)
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app: Flask):
    if not path.exists("assistant/" + DB_NAME):
        db.create_all(app=app)
        print("Created database.")
