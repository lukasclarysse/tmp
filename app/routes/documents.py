import os
import uuid

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    send_from_directory,
    abort
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Document
from app.forms import UploadForm

documents = Blueprint("documents", __name__)


@documents.route("/")
@login_required
def dashboard():
    form = UploadForm()

    user_documents = Document.query.filter_by(
        user_id=current_user.id
    ).order_by(Document.upload_date.desc()).all()

    return render_template(
        "dashboard.html",
        documents=user_documents,
        form=form
    )


@documents.route("/upload", methods=["POST"])
@login_required
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        uploaded_file = form.file.data

        original_filename = secure_filename(uploaded_file.filename)

        if not original_filename:
            flash("Invalid filename.", "error")
            return redirect(url_for("documents.dashboard"))

        extension = original_filename.rsplit(".", 1)[-1].lower()

        stored_filename = f"{uuid.uuid4().hex}.{extension}"

        upload_path = current_app.config["UPLOAD_FOLDER"]

        uploaded_file.save(
            os.path.join(upload_path, stored_filename)
        )

        document = Document(
            filename=stored_filename,
            original_filename=original_filename,
            user_id=current_user.id
        )

        db.session.add(document)
        db.session.commit()

        flash("Document uploaded successfully!", "success")

    else:
        for errors in form.errors.values():
            for error in errors:
                flash(error, "error")

    return redirect(url_for("documents.dashboard"))


@documents.route("/download/<int:document_id>")
@login_required
def download(document_id):
    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first_or_404()

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        document.filename,
        as_attachment=True,
        download_name=document.original_filename
    )


@documents.route("/delete/<int:document_id>", methods=["POST"])
@login_required
def delete(document_id):
    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first_or_404()

    file_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        document.filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(document)
    db.session.commit()

    flash("Document deleted successfully.", "success")

    return redirect(url_for("documents.dashboard"))