"""Phase 3 gate for redaction and the egress guard.

All text here is synthetic: the real archived submissions must never end up in a test file.
"""

import pytest

from app.ingest.guard import EgressBlocked, assert_sendable
from app.ingest.models import RedactionClass
from app.ingest.redact import MARKER, find_identifiers, redact


def classes(result) -> list[tuple[RedactionClass, int]]:
    return [(event.cls, event.count) for event in result.events]


def test_labelled_name_keeps_the_label():
    result = redact("Nama : Muhammad Attharsyah Firdaus Sultan")
    assert result.text == f"Nama : {MARKER}"
    assert "Attharsyah" not in result.text
    assert classes(result) == [(RedactionClass.NAME_LABEL, 1)]


def test_labelled_name_in_a_table_row_keeps_the_row_shape():
    result = redact("Nama | : Muhammad Attharsyah Firdaus Sultan")
    assert result.text == f"Nama | : {MARKER}"


def test_nim_line_redacts_only_the_number():
    result = redact("NIM : 28225304")
    assert result.text == f"NIM : {MARKER}"
    assert classes(result) == [(RedactionClass.STUDENT_ID, 1)]


def test_bare_eight_digits_are_only_an_id_next_to_a_cue():
    clean = "Peringkat naik dari 12345678 kunjungan tahun lalu."
    assert redact(clean).text == clean
    assert find_identifiers(clean) == {}
    assert redact("NIM 28225304").text == f"NIM {MARKER}"


def test_figures_with_thousand_separators_survive():
    clean = "Aplikasi ini dipakai 180.000 users secara nasional."
    assert redact(clean).text == clean


def test_email_is_removed():
    text = redact("Hubungi budi.santoso@example.ac.id untuk detail.").text
    assert text == f"Hubungi {MARKER} untuk detail."


def test_phone_numbers_are_removed_in_both_shapes():
    assert redact("Telepon: +62 812-3456-7890").text == f"Telepon: {MARKER}"
    assert redact("WA 081234567890").text == f"WA {MARKER}"


def test_personal_drive_link_is_removed():
    text = "Lihat https://drive.google.com/file/d/abc123/view?usp=sharing sekarang."
    assert redact(text).text == f"Lihat {MARKER} sekarang."


def test_name_after_the_saya_cue_is_removed():
    result = redact("Analisis ini saya, Budi Santoso, susun sendiri.")
    assert result.text == f"Analisis ini saya, {MARKER}, susun sendiri."
    assert classes(result) == [(RedactionClass.NAMED_PERSON, 1)]


def test_marker_is_identical_for_different_students():
    first = redact("Nama : Budi Santoso").text
    second = redact("Nama : Rina Wijaya Putri").text
    assert first == second == f"Nama : {MARKER}"


def test_find_identifiers_counts_every_class():
    text = "\n".join(
        [
            "Nama : Budi Santoso",
            "NIM : 28225304",
            "Email : budi@example.ac.id",
            "Telp : +62 812-3456-7890",
            "https://docs.google.com/document/d/xyz",
            "Dibuat oleh Rina Wijaya.",
        ]
    )
    assert find_identifiers(text) == {
        RedactionClass.NAME_LABEL: 1,
        RedactionClass.STUDENT_ID: 1,
        RedactionClass.EMAIL: 1,
        RedactionClass.PHONE: 1,
        RedactionClass.PERSONAL_LINK: 1,
        RedactionClass.NAMED_PERSON: 1,
    }


def test_assert_sendable_passes_clean_text():
    # Raises on anything identifying; a plain figure like 180.000 must not trip it.
    assert_sendable("Hasil analisis menunjukkan peningkatan sebesar 180.000 pengguna.")


def test_assert_sendable_blocks_and_reports_counts_only():
    with pytest.raises(EgressBlocked) as excinfo:
        assert_sendable("Nama : Budi Santoso\nNIM : 28225304")

    assert excinfo.value.classes == {RedactionClass.NAME_LABEL: 1, RedactionClass.STUDENT_ID: 1}
    assert "Budi" not in str(excinfo.value)
    assert "28225304" not in str(excinfo.value)


def test_redacted_output_passes_the_guard():
    dirty = "Nama : Budi Santoso\nEmail : budi@example.ac.id\nLihat https://drive.google.com/file/d/abc"
    assert_sendable(redact(dirty).text)
