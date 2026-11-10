from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length
)
from flask_wtf.file import FileField, FileRequired, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match.")
        ]
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")


class UploadForm(FlaskForm):
    file = FileField(
        "Choose a document",
        validators=[
            FileRequired(),
            FileAllowed(
                ["pdf", "docx", "md", "markdown"],
                "Only PDF, DOCX and Markdown files are allowed."
            )
        ]
    )

    submit = SubmitField("Upload")