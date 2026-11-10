from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Text
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    documents = db.relationship(
        "Document",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

class ProofreadingRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("document.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    result = db.Column(db.JSON, nullable=False)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="completed"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    document = db.relationship(
        "Document",
        backref=db.backref(
            "proofreading_runs",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


class ProofreadingSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    proofreading_run_id = db.Column(
        db.Integer,
        db.ForeignKey("proofreading_run.id"),
        nullable=False
    )

    original = db.Column(db.Text, nullable=False)
    replacement = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)

    category = db.Column(
        db.String(30),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    proofreading_run = db.relationship(
        "ProofreadingRun",
        backref=db.backref(
            "suggestions",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))