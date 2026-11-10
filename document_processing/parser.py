from docx import Document


def extract_paragraphs(file_path: str) -> list[dict]:
    """
    Extract non-empty paragraphs from a DOCX document.

    Returns paragraphs with their original indices so that
    we can identify them when applying corrections later.
    """

    document = Document(file_path)

    paragraphs = []

    for index, paragraph in enumerate(document.paragraphs):

        text = paragraph.text.strip()

        if not text:
            continue

        paragraphs.append({
            "paragraph_id": index,
            "text": text
        })

    return paragraphs