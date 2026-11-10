from document_processing.parser import extract_paragraphs

file_path = "uploads/test.docx"

paragraphs = extract_paragraphs(file_path)

for paragraph in paragraphs:
    print(
        f"Paragraph {paragraph['paragraph_id']}: "
        f"{paragraph['text']}"
    )