import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    csrf = CSRFProtect(app)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    from app import models

    from app.routes.auth import auth
    from app.routes.documents import documents
    from app.routes.processing import processing
    from app.routes.suggestions import suggestions
    from app.routes.chatbot import chatbot
    app.register_blueprint(auth)
    app.register_blueprint(documents)
    app.register_blueprint(processing)
    app.register_blueprint(suggestions)
    app.register_blueprint(chatbot)

    with app.app_context():
        db.create_all()

    return app