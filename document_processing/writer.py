
import io

from docx import Document

from document_processing.diff import build_diff


def apply_accepted_changes(
    original_text: str,
    corrected_text: str,
    changes: list,
    paragraph_id: int,
    accepted_changes: set,
    diff_segments: list = None
) -> str:

    if diff_segments is None:
        diff_segments = build_diff(
            original_text,
            corrected_text
        )

    output = []

    for segment in diff_segments:

        if segment["type"] == "equal":

            output.append(segment["original"])
            continue

        selection_id = (
            f"{paragraph_id}:{segment['change_index']}"
        )

        if selection_id in accepted_changes:
            output.append(segment["replacement"])
        else:
            output.append(segment["original"])

    return "".join(output)


def create_corrected_document(
    file_path: str,
    results: list,
    accepted_changes: set
):
    """
    Generate a corrected DOCX in memory.

    Only explicitly accepted changes are applied.
    """

    document = Document(file_path)

    for result in results:

        paragraph_id = result["paragraph_id"]

        if paragraph_id >= len(document.paragraphs):
            continue

        paragraph = document.paragraphs[paragraph_id]

        diff_segments = result.get("diff_segments")

        if diff_segments is None:
            diff_segments = build_diff(
                result["original_text"],
                result["corrected_text"]
            )

        corrected_text = apply_accepted_changes(
            original_text=result["original_text"],
            corrected_text=result["corrected_text"],
            changes=result.get("changes", []),
            paragraph_id=paragraph_id,
            accepted_changes=accepted_changes,
            diff_segments=diff_segments
        )

        paragraph.text = corrected_text

    output = io.BytesIO()

    document.save(output)

    output.seek(0)

    return output
