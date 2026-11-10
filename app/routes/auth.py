from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_

from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("documents.dashboard"))

    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter(
            or_(
                User.username == form.username.data,
                User.email == form.email.data.lower()
            )
        ).first()

        if existing_user:
            flash("Username or email already exists.", "error")
            return render_template("register.html", form=form)

        user = User(
            username=form.username.data,
            email=form.email.data.lower()
        )

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("documents.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data.lower()
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user)

            return redirect(url_for("documents.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html", form=form)


@auth.route("/logout", methods=["POST"])
def logout():
    logout_user()

    flash("You have been logged out.", "success")

    return redirect(url_for("auth.login"))