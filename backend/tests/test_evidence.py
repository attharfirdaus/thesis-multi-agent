"""Gate for the evidence rule of PRD §6, step 4.

The rule has two halves and both are tested: it forgives the formatting differences a model introduces
while copying a passage, and it refuses a paraphrase. Offsets are checked by slicing the original text
back out, because that is exactly what the stored `Evidence.start_offset/end_offset` pair has to do.
"""

from app.agents.evidence import locate_quote, normalise


def test_normalise_collapses_whitespace_strips_and_case_folds():
    assert normalise("  Data   Yang\nDipakai ") == "data yang dipakai"


def test_normalise_unifies_quote_glyphs():
    assert normalise("“kutipan”") == normalise('"kutipan"')


def test_quote_re_wrapped_across_a_line_is_found_and_slices_the_original():
    text = "Saya memeriksa\nulang   data yang dipakai model sebelum menulis."
    quote = "memeriksa ulang data yang dipakai model"
    span = locate_quote(text, quote)
    assert span is not None
    start, end = span
    assert text[start:end] == "memeriksa\nulang   data yang dipakai model"


def test_line_break_hyphenation_is_joined():
    text = "Analisis kri-\ntis terhadap keluaran AI."
    # The break joins the halves: no space may appear where the word was split.
    assert normalise(text) == "analisis kritis terhadap keluaran ai."
    span = locate_quote(text, "Analisis kritis terhadap keluaran AI")
    assert span is not None
    assert normalise(text[span[0] : span[1]]) == normalise("Analisis kritis terhadap keluaran AI")


def test_soft_hyphen_is_dropped():
    assert locate_quote("Data\u00adbase itu dipakai.", "Database itu dipakai") is not None


def test_compound_hyphen_inside_a_line_survives():
    text = "Pendekatan well-known itu saya pakai."
    span = locate_quote(text, "well-known itu saya pakai")
    assert span is not None
    assert text[span[0] : span[1]] == "well-known itu saya pakai"


def test_curly_quotes_in_the_source_match_straight_quotes_in_the_quote():
    text = 'Ia menulis “data yang dipakai model” di laporan.'
    span = locate_quote(text, '"data yang dipakai model"')
    assert span is not None
    assert text[span[0] : span[1]] == "“data yang dipakai model”"


def test_different_case_is_matched():
    text = "Data yang dipakai model perlu diperiksa."
    span = locate_quote(text, "DATA YANG DIPAKAI MODEL")
    assert span is not None
    assert text[span[0] : span[1]] == "Data yang dipakai model"


def test_offsets_start_where_the_passage_starts_not_at_zero():
    text = "Pendahuluan panjang sekali. Lalu saya memeriksa ulang data."
    span = locate_quote(text, "memeriksa ulang data")
    assert span is not None
    assert span[0] == text.index("memeriksa")
    assert text[span[0] : span[1]] == "memeriksa ulang data"


def test_paraphrase_is_not_accepted():
    text = "Saya memeriksa ulang data yang dipakai model tersebut."
    assert locate_quote(text, "saya menilai keluaran AI itu kurang tepat") is None


def test_reordered_words_are_not_accepted():
    text = "Hasil keluaran AI saya bandingkan dengan jurnal."
    assert locate_quote(text, "jurnal saya bandingkan dengan hasil keluaran AI") is None


def test_empty_quote_matches_nothing():
    assert locate_quote("Teks apa saja.", "   ") is None


def test_quote_longer_than_the_text_matches_nothing():
    assert locate_quote("Teks pendek.", "Teks pendek yang jauh lebih panjang daripada sumbernya.") is None
