"""Bytes in, `ExtractedDocument` out.

Formats are dispatched by extension. PDF and DOCX are read *structurally* rather than by plain
text dump, because the archived submissions are Word tables exported to PDF and the only reliable
boundary between the AI's answer and the student's analysis is the label in the first column of a
table row — a raw text dump interleaves the columns and destroys it.

Two consequences drive the code below:

- An empty first cell is preserved verbatim. It marks the continuation of the previous cell across
  a page break; collapsing or dropping it would attribute the AI's answer to the wrong segment.
- A page with no text and no table is never dropped silently: it becomes an `IMAGE_ONLY` block plus
  a warning, because "the lecturer must know the page was not readable" beats "the submission looks
  shorter than it is".
- A page that does hold a table keeps the text outside its boxes as well. The table is not the
  whole page, and on the archived submissions the identifier block sits above it.
"""

import datetime as dt
import io
import pathlib
import re
import zipfile
from typing import Literal

import docx
import pdfplumber
from docx.document import Document as DocxDocument
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from app.ingest.models import Block, BlockKind, ExtractedDocument

SourceFormat = Literal["pdf", "docx", "txt"]

_BLOCK = tuple[BlockKind, str, int | None, list[str] | None]

_BLANK_LINE = re.compile(r"\n\s*\n")


def extract(filename: str, data: bytes) -> ExtractedDocument:
    """Extract one document. Raises `ValueError` for a type this module cannot read."""
    suffix = pathlib.Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(filename, data)
    if suffix == ".docx":
        return _extract_docx(filename, data)
    if suffix == ".txt":
        return _extract_txt(filename, data)
    if suffix == ".zip":
        raise ValueError(f"{filename}: a .zip holds several documents; call extract_zip()")
    raise ValueError(
        f"unsupported file type {suffix or filename!r}: expected .pdf, .docx, .txt or .zip"
    )


def extract_zip(filename: str, data: bytes) -> tuple[list[ExtractedDocument], list[str]]:
    """Unpack a ZIP in memory and extract every member.

    Returns the documents that worked and one message per member that did not, so a single
    unreadable file cannot fail the batch (FR-03). Anything a member raises is caught, not just
    `ValueError`: a truncated or password-protected entry is exactly the case FR-03 is about.
    """
    documents: list[ExtractedDocument] = []
    errors: list[str] = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            if info.is_dir() or _is_archive_junk(info.filename):
                continue
            try:
                documents.append(extract(info.filename, archive.read(info)))
            except Exception as exc:
                errors.append(f"{info.filename}: {exc}")
    return documents, errors


def _extract_pdf(filename: str, data: bytes) -> ExtractedDocument:
    items: list[_BLOCK] = []
    warnings: list[str] = []
    metadata: dict[str, str] = {}
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for key, value in (pdf.metadata or {}).items():
            if isinstance(value, str) and value.strip():
                metadata[key.lower()] = value.strip()
        for page_no, page in enumerate(pdf.pages, start=1):
            before = len(items)
            items.extend(_page_items(page, page_no))
            if len(items) == before:
                items.append((BlockKind.IMAGE_ONLY, "", page_no, None))
                warnings.append(f"page {page_no}: no extractable text or tables (image-only page)")
    return _build(filename, "pdf", items, metadata, warnings)


def _page_items(page, page_no: int) -> list[_BLOCK]:
    """Every block of one PDF page, in reading order.

    A page holding a table yields its rows *and* the text outside every table box. Emitting the
    rows alone silently drops the rest of the page: on the archived submissions the student's
    `Nama :` / `NIM :` header sits above a table and the surrounding prose sits below it.

    The two sorts of block are interleaved by vertical position, a table's rows keyed by the
    table's own `top` and a text line by its own. That order is load bearing rather than cosmetic:
    an empty first cell means "continuation of the row above", pdfplumber reads such a continuing
    row wherever it sits on the page, so the text of a table page must never simply be appended
    after the rows of that page.
    """
    tables = page.find_tables() or []
    if not tables:
        return [
            (BlockKind.PARAGRAPH, paragraph, page_no, None)
            for paragraph in _paragraphs(page.extract_text() or "")
        ]
    positioned: list[tuple[float, _BLOCK]] = []
    for table in tables:
        # Every row of one table shares the table's own `top`, so they stay together.
        for row in table.extract() or []:
            cells = [cell.strip() if isinstance(cell, str) else "" for cell in row]
            positioned.append(
                (table.bbox[1], (BlockKind.TABLE_ROW, " | ".join(cells), page_no, cells))
            )
    for line in _outside_tables(page, [table.bbox for table in tables]).extract_text_lines() or []:
        positioned.append((line["top"], (BlockKind.PARAGRAPH, line["text"], page_no, None)))
    positioned.sort(key=lambda item: item[0])
    return [item[1] for item in positioned]


def _outside_tables(page, boxes: list[tuple[float, float, float, float]]):
    """The page with every character that sits inside a table box removed.

    pdfplumber's documented recipe: `Page.filter` drops each object its predicate rejects, so the
    predicate keeps an object unless it is a character whose centre is inside one of the boxes.
    """

    def center_outside_tables(obj: dict) -> bool:
        if obj["object_type"] != "char":
            return True
        h_mid = (obj["x0"] + obj["x1"]) / 2
        v_mid = (obj["top"] + obj["bottom"]) / 2
        return not any(x0 <= h_mid < x1 and top <= v_mid < bottom for x0, top, x1, bottom in boxes)

    return page.filter(center_outside_tables)


def _extract_docx(filename: str, data: bytes) -> ExtractedDocument:
    document = docx.Document(io.BytesIO(data))
    items: list[_BLOCK] = []
    # `document.paragraphs` and `document.tables` are separate views that lose the interleaving;
    # walking the body itself is the only way to keep the document's own order.
    for element in document.element.body.iterchildren():
        if isinstance(element, CT_P):
            text = Paragraph(element, document).text.strip()
            if text:
                items.append((BlockKind.PARAGRAPH, text, None, None))
        elif isinstance(element, CT_Tbl):
            for row in Table(element, document).rows:
                cells = [cell.text.strip() for cell in row.cells]
                items.append((BlockKind.TABLE_ROW, " | ".join(cells), None, cells))
    return _build(filename, "docx", items, _core_properties(document))


def _extract_txt(filename: str, data: bytes) -> ExtractedDocument:
    text = data.decode("utf-8", errors="replace")
    items: list[_BLOCK] = [(BlockKind.PARAGRAPH, s, None, None) for s in _paragraphs(text)]
    return _build(filename, "txt", items)


def _build(
    filename: str,
    source_format: SourceFormat,
    items: list[_BLOCK],
    metadata: dict[str, str] | None = None,
    warnings: list[str] | None = None,
) -> ExtractedDocument:
    blocks = [
        Block(kind=kind, text=text, order=order, page=page, cells=cells)
        for order, (kind, text, page, cells) in enumerate(items)
    ]
    return ExtractedDocument(
        filename=filename,
        source_format=source_format,
        blocks=blocks,
        metadata=metadata or {},
        warnings=warnings or [],
    )


def _paragraphs(text: str) -> list[str]:
    """Blank-line separated stanzas.

    Used for TXT and for PDF pages that hold no table. Each one becomes its own block so the
    segmenter keeps the author's own breaks instead of receiving one undivided wall of text.
    """
    return [stanza.strip() for stanza in _BLANK_LINE.split(text) if stanza.strip()]


def _core_properties(document: DocxDocument) -> dict[str, str]:
    properties = document.core_properties
    metadata: dict[str, str] = {}
    for key in ("author", "last_modified_by", "created", "modified", "title"):
        value = getattr(properties, key, None)
        if value is None:
            continue
        text = value.isoformat() if isinstance(value, dt.datetime) else str(value)
        if text.strip():
            metadata[key] = text.strip()
    return metadata


def _is_archive_junk(name: str) -> bool:
    """Finder and Explorer litter (`__MACOSX`, `.DS_Store`) would otherwise show up as errors."""
    return name.startswith("__MACOSX/") or pathlib.PurePosixPath(name).name.startswith(".")
