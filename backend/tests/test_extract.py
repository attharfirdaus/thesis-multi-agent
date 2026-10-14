"""Extraction tests.

Every input is built here: no network, no real submission, no fixture file to keep in sync with
the code. The PDF path is driven through a stub because generating a table-bearing PDF would need
a second, heavier dependency; the stub carries line geometry and table boxes so it exercises the
real branch (`tables + outside text → text → image`) and the block shapes the segmenter reads.
"""

import io
import zipfile

import docx
import pytest

from app.ingest import extract as extract_mod
from app.ingest.models import BlockKind


class _Table:
    """Stand-in for a pdfplumber table: its box plus the rows inside it."""

    def __init__(self, bbox: tuple[float, float, float, float], rows: list[list[str | None]]) -> None:
        self.bbox = bbox
        self._rows = rows

    def extract(self) -> list[list[str | None]]:
        return self._rows


def _text_line(text: str, top: float) -> dict:
    """One line of a stubbed page, shaped like the `char` objects `Page.filter` inspects."""
    return {"object_type": "char", "text": text, "x0": 0.0, "x1": 100.0, "top": top, "bottom": top + 10}


class _Page:
    """Stand-in for a pdfplumber page: text lines carrying their geometry, and the tables in them.

    `lines` is the text *outside* the tables, which is what the real filtered page returns; a
    table's own text arrives through `find_tables()`.
    """

    def __init__(
        self,
        lines: list[dict],
        tables: list[tuple[tuple[float, float, float, float], list[list[str | None]]]] = (),
    ) -> None:
        self._lines = list(lines)
        self._tables = [_Table(bbox, rows) for bbox, rows in tables]

    def find_tables(self) -> list[_Table]:
        return self._tables

    def extract_text(self) -> str:
        return "\n".join(line["text"] for line in self._lines)

    def extract_text_lines(self) -> list[dict]:
        return [dict(line) for line in self._lines]

    def filter(self, predicate) -> "_Page":
        return _Page([line for line in self._lines if predicate(line)])


class _Pdf:
    def __init__(self, pages: list[_Page], metadata: dict[str, object]) -> None:
        self.pages = pages
        self.metadata = metadata

    def __enter__(self) -> "_Pdf":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def _docx_bytes(path, *, author: str = "") -> bytes:
    document = docx.Document()
    document.add_paragraph("Tugas 2")
    document.add_paragraph("")
    table = document.add_table(rows=3, cols=2)
    cells = [
        ("Prompt", "Hasil"),
        ("<pertanyaan>", "<jawaban AI>"),
        ("", "continuation of the answer across the page break"),
    ]
    for row, values in zip(table.rows, cells, strict=True):
        for cell, value in zip(row.cells, values, strict=True):
            cell.text = value
    document.add_paragraph("Nota penutup")
    if author:
        document.core_properties.author = author
    document.save(path)
    return path.read_bytes()


def test_docx_keeps_table_cells_and_document_order(tmp_path):
    path = tmp_path / "tugas-2.docx"
    data = _docx_bytes(path, author="Budi")

    result = extract_mod.extract("tugas-2.docx", data)

    assert result.source_format == "docx"
    assert result.metadata["author"] == "Budi"
    assert [b.order for b in result.blocks] == list(range(len(result.blocks)))
    kinds = [b.kind for b in result.blocks]
    assert kinds == [
        BlockKind.PARAGRAPH,
        BlockKind.TABLE_ROW,
        BlockKind.TABLE_ROW,
        BlockKind.TABLE_ROW,
        BlockKind.PARAGRAPH,
    ]
    assert result.blocks[0].text == "Tugas 2"
    assert result.blocks[1].cells == ["Prompt", "Hasil"]
    assert result.blocks[2].cells == ["<pertanyaan>", "<jawaban AI>"]
    continuation = result.blocks[3]
    assert continuation.cells == ["", "continuation of the answer across the page break"]
    assert continuation.text == " | continuation of the answer across the page break"
    assert continuation.text == " | ".join(continuation.cells)
    assert result.blocks[4].text == "Nota penutup"
    assert result.blocks[0].page is None
    assert "empty" not in result.warnings


def test_txt_splits_stanzas_and_replaces_invalid_utf8(tmp_path):
    path = tmp_path / "catatan.txt"
    path.write_bytes(b"stanza satu\nbaris dua\n\n\n   stanza dua   \n")

    result = extract_mod.extract("catatan.txt", path.read_bytes())

    assert result.source_format == "txt"
    assert [b.text for b in result.blocks] == ["stanza satu\nbaris dua", "stanza dua"]
    assert [b.order for b in result.blocks] == [0, 1]
    assert all(b.cells is None and b.page is None for b in result.blocks)
    assert result.has_text

    broken = extract_mod.extract("rusak.txt", b"nama: caf\xe9\n")
    assert "\ufffd" in broken.blocks[0].text


def test_zip_yields_one_document_per_member_and_isolates_failures(tmp_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("tugas-2.docx", _docx_bytes(tmp_path / "tugas-2.docx"))
        archive.writestr("catatan.txt", "analisis mahasiswa\n")
        archive.writestr("screenshot.png", b"\x89PNG\r\n\x1a\n")
        archive.writestr("__MACOSX/", b"")
        archive.writestr("__MACOSX/._tugas-2.docx", b"junk")
        archive.writestr("catatan/.DS_Store", b"junk")

    documents, errors = extract_mod.extract_zip("kumpulan.zip", buffer.getvalue())

    assert sorted(d.filename for d in documents) == ["catatan.txt", "tugas-2.docx"]
    assert len(errors) == 1
    assert errors[0].startswith("screenshot.png: unsupported file type")


def test_unsupported_extension_raises_value_error():
    with pytest.raises(ValueError, match="unsupported file type"):
        extract_mod.extract("catatan.md", b"# heading")
    with pytest.raises(ValueError, match="extract_zip"):
        extract_mod.extract("kumpulan.zip", b"PK\x03\x04")


def test_pdf_keeps_page_numbers_table_cells_and_flags_image_only_page(monkeypatch):
    pages = [
        _Page(
            lines=[_text_line("Prompt", top=200.0), _text_line("Hasil", top=210.0)],
            tables=[((0.0, 195.0, 100.0, 230.0), [["Prompt", "Hasil"], [None, "jawaban AI"]])],
        ),
        _Page(lines=[]),
    ]
    monkeypatch.setattr(
        extract_mod.pdfplumber,
        "open",
        lambda stream: _Pdf(pages, {"Author": "Siti", "Producer": "", "Title": "Tugas 2"}),
    )

    result = extract_mod.extract("tugas-2.pdf", b"%PDF-1.4 stub")

    assert result.source_format == "pdf"
    assert result.metadata == {"author": "Siti", "title": "Tugas 2"}
    assert [b.kind for b in result.blocks] == [
        BlockKind.TABLE_ROW,
        BlockKind.TABLE_ROW,
        BlockKind.IMAGE_ONLY,
    ]
    assert [b.page for b in result.blocks] == [1, 1, 2]
    assert [b.order for b in result.blocks] == [0, 1, 2]
    assert result.blocks[1].cells == ["", "jawaban AI"]
    assert result.blocks[1].text == " | jawaban AI"
    assert result.blocks[2].text == ""
    assert len(result.warnings) == 1
    assert "page 2" in result.warnings[0]


def test_pdf_uses_text_when_a_page_has_no_tables(monkeypatch):
    pages = [
        _Page(
            lines=[
                _text_line("Analisis mahasiswa.", top=10.0),
                # the blank line between the two stanzas of the page's text
                _text_line("", top=15.0),
                _text_line("Kesimpulan: baik.", top=20.0),
            ]
        )
    ]
    monkeypatch.setattr(extract_mod.pdfplumber, "open", lambda stream: _Pdf(pages, {}))

    result = extract_mod.extract("tugas-5.pdf", b"%PDF-1.4 stub")

    assert [b.kind for b in result.blocks] == [BlockKind.PARAGRAPH, BlockKind.PARAGRAPH]
    assert [b.text for b in result.blocks] == ["Analisis mahasiswa.", "Kesimpulan: baik."]
    assert [b.page for b in result.blocks] == [1, 1]
    assert result.warnings == []


def test_pdf_interleaves_table_rows_with_the_text_outside_them(monkeypatch):
    header = _text_line("Nama : Budi", top=10.0)
    # pdfplumber reads a row that continues the previous table wherever it sits, so this line
    # belongs *after* table one and *before* table two.
    between = _text_line("  | lanjutan jawaban AI", top=250.0)
    footer = _text_line("Kesimpulan: baik.", top=600.0)
    page = _Page(
        lines=[header, between, footer],
        tables=[
            ((0.0, 100.0, 100.0, 200.0), [["Prompt", "Hasil"], [None, "jawaban AI"]]),
            ((0.0, 300.0, 100.0, 500.0), [["Nama", "NIM"], ["Budi", "28225304"]]),
        ],
    )
    monkeypatch.setattr(extract_mod.pdfplumber, "open", lambda stream: _Pdf([page], {}))

    result = extract_mod.extract("tugas-3.pdf", b"%PDF-1.4 stub")

    assert [b.kind for b in result.blocks] == [
        BlockKind.PARAGRAPH,
        BlockKind.TABLE_ROW,
        BlockKind.TABLE_ROW,
        BlockKind.PARAGRAPH,
        BlockKind.TABLE_ROW,
        BlockKind.TABLE_ROW,
        BlockKind.PARAGRAPH,
    ]
    assert [b.text for b in result.blocks] == [
        "Nama : Budi",
        "Prompt | Hasil",
        " | jawaban AI",
        "  | lanjutan jawaban AI",
        "Nama | NIM",
        "Budi | 28225304",
        "Kesimpulan: baik.",
    ]
    assert [b.order for b in result.blocks] == list(range(len(result.blocks)))
    assert result.warnings == []


def test_pdf_keeps_every_text_line_of_a_page_that_has_a_table(monkeypatch):
    """Regression: the table used to be emitted alone, dropping the rest of the page."""
    page = _Page(
        lines=[
            _text_line("Nama : Budi", top=10.0),
            _text_line("NIM : 28225304", top=20.0),
            _text_line("Analisis mahasiswa.", top=400.0),
        ],
        tables=[((0.0, 100.0, 100.0, 300.0), [["Prompt", "Hasil"], [None, "jawaban AI"]])],
    )
    monkeypatch.setattr(extract_mod.pdfplumber, "open", lambda stream: _Pdf([page], {}))

    result = extract_mod.extract("tugas-3.pdf", b"%PDF-1.4 stub")

    emitted = "".join(b.text for b in result.blocks if b.page == 1)
    for line in page.extract_text().splitlines():
        assert line in emitted
    assert result.warnings == []
