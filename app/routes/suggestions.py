
from flask import Blueprint, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import ProofreadingRun, ProofreadingSuggestion


suggestions = Blueprint("suggestions", __name__)


def get_user_run(run_id):
    return ProofreadingRun.query.filter_by(
        id=run_id,
        user_id=current_user.id
    ).first_or_404()


@suggestions.route(
    "/suggestion/<int:suggestion_id>/<action>",
    methods=["POST"]
)
@login_required
def update_suggestion(suggestion_id, action):

    if action not in ("accept", "reject"):
        abort(404)

    suggestion = (
        ProofreadingSuggestion.query
        .join(ProofreadingRun)
        .filter(
            ProofreadingSuggestion.id == suggestion_id,
            ProofreadingRun.user_id == current_user.id
        )
        .first_or_404()
    )

    suggestion.status = (
        "accepted" if action == "accept" else "rejected"
    )

    db.session.commit()

    flash(
        f"Suggestion {action}ed successfully.",
        "success"
    )

    return redirect(
        url_for(
            "processing.results",
            run_id=suggestion.proofreading_run_id
        )
    )


@suggestions.route(
    "/run/<int:run_id>/<action>",
    methods=["POST"]
)
@login_required
def update_all(run_id, action):

    if action not in ("accept-all", "reject-all"):
        abort(404)

    proofreading_run = get_user_run(run_id)

    new_status = (
        "accepted" if action == "accept-all" else "rejected"
    )

    for suggestion in proofreading_run.suggestions:
        suggestion.status = new_status

    db.session.commit()

    flash(
        f"All suggestions {new_status}.",
        "success"
    )

    return redirect(
        url_for(
            "processing.results",
            run_id=run_id
        )
    )
