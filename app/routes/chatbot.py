import logging

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from app.models import ProofreadingRun

from agents.explanation import ExplanationAgent

from llm.mock import MockLLM
from llm.ollama import OllamaProvider


chatbot = Blueprint("chatbot", __name__)

logger = logging.getLogger(__name__)


def create_explanation_agent():

    provider_name = current_app.config["LLM_PROVIDER"]

    if provider_name == "mock":

        provider = MockLLM([
            {
                "answer": (
                    "This is a demonstration response. "
                    "Switch to Ollama to enable real AI explanations."
                )
            }
        ])

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

    return ExplanationAgent(provider)


@chatbot.route(
    "/chat/<int:run_id>",
    methods=["POST"]
)
@login_required
def chat(run_id):

    proofreading_run = ProofreadingRun.query.filter_by(
        id=run_id,
        user_id=current_user.id
    ).first_or_404()

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid request."
        }), 400

    question = data.get("question")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "Please enter a question."
        }), 400

    if len(question) > 2000:
        return jsonify({
            "error": "Your question is too long."
        }), 400

    history = data.get("history", [])

    if not isinstance(history, list):
        return jsonify({
            "error": "Invalid conversation history."
        }), 400

    paragraph_index = data.get("paragraph_index")
    change_index = data.get("change_index")

    results = proofreading_run.result

    original = ""
    corrected = ""
    changes = []

    # A selected correction provides focused context.
    if paragraph_index is not None:

        if (
            isinstance(paragraph_index, bool)
            or not isinstance(paragraph_index, int)
            or paragraph_index < 0
            or paragraph_index >= len(results)
        ):
            return jsonify({
                "error": "Invalid paragraph."
            }), 400

        paragraph = results[paragraph_index]

        original = paragraph.get("original_text", "")
        corrected = paragraph.get("corrected_text", "")

        paragraph_changes = paragraph.get("changes", [])

        if change_index is not None:

            if (
                isinstance(change_index, bool)
                or not isinstance(change_index, int)
                or change_index < 0
                or change_index >= len(paragraph_changes)
            ):
                return jsonify({
                    "error": "Invalid correction."
                }), 400

            changes = [paragraph_changes[change_index]]

        else:
            changes = paragraph_changes

    else:

        # Whole-document context.
        original = "\n\n".join(
            p.get("original_text", "")
            for p in results
        )[:12000]

        corrected = "\n\n".join(
            p.get("corrected_text", "")
            for p in results
        )[:12000]

        changes = [
            change
            for paragraph in results
            for change in paragraph.get("changes", [])
        ][:50]

    try:

        agent = create_explanation_agent()

        answer = agent.explain(
            original=original,
            corrected=corrected,
            question=question,
            changes=changes,
            conversation_history=history
        )

        return jsonify({
            "answer": answer
        })

    except Exception:

        logger.exception(
            "Chatbot failed for proofreading run %s",
            run_id
        )

        return jsonify({
            "error": "Sorry, something went wrong. Please try again."
        }), 500