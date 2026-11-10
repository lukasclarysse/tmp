
import difflib
import io

from docx import Document


def apply_accepted_changes(
    original_text: str,
    corrected_text: str,
    changes: list,
    paragraph_id: int,
    accepted_changes: set
) -> str:
    """
    Apply only the changes accepted by the user.

    Rejected changes retain their original wording.
    """

    original_words = original_text.split()
    corrected_words = corrected_text.split()

    matcher = difflib.SequenceMatcher(
        None,
        original_words,
        corrected_words
    )

    output_words = []
    change_index = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":
            output_words.extend(original_words[i1:i2])

        else:
            selection_id = f"{paragraph_id}:{change_index}"

            if selection_id in accepted_changes:
                output_words.extend(corrected_words[j1:j2])
            else:
                output_words.extend(original_words[i1:i2])

            change_index += 1

    return " ".join(output_words)


def create_corrected_document(
    file_path: str,
    results: list,
    accepted_changes: set
):
    """
    Create a corrected DOCX document in memory.

    The original document is never modified.
    Only accepted proofreading suggestions are applied.
    """

    document = Document(file_path)

    for result in results:

        paragraph_id = result["paragraph_id"]

        if paragraph_id >= len(document.paragraphs):
            continue

        paragraph = document.paragraphs[paragraph_id]

        corrected_text = apply_accepted_changes(
            original_text=result["original_text"],
            corrected_text=result["corrected_text"],
            changes=result["changes"],
            paragraph_id=paragraph_id,
            accepted_changes=accepted_changes
        )

        paragraph.text = corrected_text

    output = io.BytesIO()

    document.save(output)

    output.seek(0)

    return output
