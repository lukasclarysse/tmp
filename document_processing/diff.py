
import difflib
import re


def build_diff(original: str, corrected: str) -> list[dict]:
    """
    Generate canonical diff segments.

    Whitespace is preserved exactly.
    Every changed segment receives a stable change_index.
    """

    original_tokens = re.findall(r"\s+|[^\s]+", original)
    corrected_tokens = re.findall(r"\s+|[^\s]+", corrected)

    matcher = difflib.SequenceMatcher(
        None,
        original_tokens,
        corrected_tokens,
        autojunk=False
    )

    segments = []
    change_index = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        old = "".join(original_tokens[i1:i2])
        new = "".join(corrected_tokens[j1:j2])

        if tag == "equal":
            segments.append({
                "type": "equal",
                "original": old,
                "replacement": new,
                "change_index": None
            })

        else:
            segments.append({
                "type": "change",
                "original": old,
                "replacement": new,
                "change_index": change_index
            })

            change_index += 1

    return segments
