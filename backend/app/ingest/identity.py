"""Capturing the real identifier, once, before redaction deletes it.

`redact.py` removes identifier *values* from the text that is stored and sent. This module does the
opposite job for the one value the system is allowed to keep: the student's own identifier, which
goes into `student_identities` and never leaves the database (FR-04).

The two live in different modules on purpose. One deletes, one files; sharing a regex between them
would invite the mistake of a value being captured for storage from code that is meant to erase it.
"""

import re

# "Nama : Muhammad Attharsyah Firdaus Sultan" (the real files open this way), also "Nama|: X" when
# exported through a table cell.
_NAME_LABEL = re.compile(r"nama\s*[:|]\s*([^\n|]{3,80})", re.IGNORECASE)

# The archive names every file "<Assignment>_<Full Name>.pdf".
_NAME_IN_FILENAME = re.compile(r"_(?P<name>[^_]+?)(?:\.[A-Za-z0-9]+)$")


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" :|\t")


def extract_identity(filename: str, text: str) -> str | None:
    """Return the student's real identifier, or None when nothing recognises it.

    Filename first: it is the one place a name is guaranteed to appear in this archive, whereas the
    labelled line is missing from some files. The labelled value wins when both exist, because it is
    the student's own declaration rather than a name the lecturer typed into a filename.
    """
    labelled = _NAME_LABEL.search(text)
    if labelled:
        value = _clean(labelled.group(1))
        if value:
            return value

    from_name = _NAME_IN_FILENAME.search(filename)
    if from_name:
        value = _clean(from_name.group("name"))
        if value:
            return value
    return None
