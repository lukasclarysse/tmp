
import os
import io
import logging

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    request,
    send_file
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Document, ProofreadingRun
from document_processing.parser import extract_paragraphs
from document_processing.writer import create_corrected_document
from agents.proofreading import ProofreadingAgent
from llm.mock import MockLLM
from llm.ollama import OllamaProvider


processing = Blueprint("processing", __name__)

logger = logging.getLogger(__name__)


def create_proofreading_agent(paragraphs):
    """Create an agent using the configured LLM provider."""

    provider_name = current_app.config["LLM_PROVIDER"]

    if provider_name == "mock":
        mock_response = [
            {
                "corrected_text": paragraph["text"],
                "changes": []
            }
            for paragraph in paragraphs
        ]

        provider = MockLLM(mock_response)

    elif provider_name == "ollama":
        provider = OllamaProvider(
            model=current_app.config["LLM_MODEL"],
            base_url=current_app.config["LLM_BASE_URL"],
            timeout=300
        )

    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_name}"
        )

    return ProofreadingAgent(provider)


@processing.route(
    "/<int:document_id>/proofread",
    methods=["POST"]
)
@login_required
def proofread(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first_or_404()

    if not document.original_filename.lower().endswith(".docx"):
        flash("Only DOCX documents are currently supported.", "error")
        return redirect(url_for("documents.dashboard"))

    file_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        document.filename
    )

    if not os.path.isfile(file_path):
        flash("The uploaded document could not be found.", "error")
        return redirect(url_for("documents.dashboard"))

    try:
        logger.info("Starting proofreading for document %s", document.id)

        paragraphs = extract_paragraphs(file_path)

        if not paragraphs:
            flash("This document contains no readable paragraphs.", "error")
            return redirect(url_for("documents.dashboard"))

        agent = create_proofreading_agent(paragraphs)

        results = []

        for index, paragraph in enumerate(paragraphs):

            logger.info(
                "Processing paragraph %s/%s",
                index + 1,
                len(paragraphs)
            )

            result = agent.process(
                text=paragraph["text"],
                language="English"
            )

            results.append({
                "paragraph_id": paragraph["paragraph_id"],
                "original_text": result["original_text"],
                "corrected_text": result["corrected_text"],
                "changes": result["changes"]
            })

        proofreading_run = ProofreadingRun(
            document_id=document.id,
            user_id=current_user.id,
            result=results,
            status="completed"
        )

        db.session.add(proofreading_run)
        db.session.commit()

        logger.info(
            "Proofreading completed for document %s",
            document.id
        )

        flash("Proofreading completed successfully!", "success")

        return redirect(
            url_for(
                "processing.results",
                run_id=proofreading_run.id
            )
        )

    except Exception:
        db.session.rollback()

        logger.exception(
            "Proofreading failed for document %s",
            document.id
        )

        flash(
            "Something went wrong while proofreading your document.",
            "error"
        )

        return redirect(url_for("documents.dashboard"))


@processing.route("/results/<int:run_id>")
@login_required
def results(run_id):

    proofreading_run = ProofreadingRun.query.filter_by(
        id=run_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "proofreading.html",
        proofreading_run=proofreading_run,
        results=proofreading_run.result
    )


@processing.route(
    "/results/<int:run_id>/download",
    methods=["POST"]
)
@login_required
def download_corrected(run_id):

    proofreading_run = ProofreadingRun.query.filter_by(
        id=run_id,
        user_id=current_user.id
    ).first_or_404()

    document = Document.query.filter_by(
        id=proofreading_run.document_id,
        user_id=current_user.id
    ).first_or_404()

    file_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        document.filename
    )

    if not os.path.isfile(file_path):
        flash("The original document could not be found.", "error")
        return redirect(
            url_for("processing.results", run_id=run_id)
        )

    try:
        # Each selected value has the format paragraph_id:change_index.
        accepted_changes = set(request.form.getlist("accepted_changes"))

        corrected_file = create_corrected_document(
            file_path=file_path,
            results=proofreading_run.result,
            accepted_changes=accepted_changes
        )

        original_name = secure_filename(
            document.original_filename
        )

        name_without_extension = os.path.splitext(original_name)[0]

        download_name = f"{name_without_extension}_corrected.docx"

        return send_file(
            corrected_file,
            as_attachment=True,
            download_name=download_name,
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

    except Exception:
        logger.exception(
            "Failed to generate corrected document for run %s",
            run_id
        )

        flash(
            "Something went wrong while generating your document.",
            "error"
        )

        return redirect(
            url_for("processing.results", run_id=run_id)
        )
