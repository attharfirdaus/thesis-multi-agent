"""Phase 3 segmentation: the table shapes the archived submissions actually have.

Every fixture below is synthetic — the real student files are never read by a test. The cases are
the ones the design doc records as observed: the canonical Prompt/Hasil/Critical Review table, the
merged cell that continues into a row with an empty first cell, the page-break header row, and a
submission with no AI output at all.
"""

from app.ingest.models import Block, BlockKind, ExtractedDocument, SegmentationResult, SegmentKind
from app.ingest.segment import LABEL_CONFIDENCE, segment

QUESTION = "Apa itu UU ITE?"


def _row(*cells: str, page: int | None = None) -> Block:
    return Block(kind=BlockKind.TABLE_ROW, text=" | ".join(cells), order=0, page=page, cells=list(cells))


def _para(text: str) -> Block:
    return Block(kind=BlockKind.PARAGRAPH, text=text, order=0)


def _doc(*blocks: Block) -> ExtractedDocument:
    ordered = [block.model_copy(update={"order": index}) for index, block in enumerate(blocks)]
    return ExtractedDocument(filename="tugas.docx", source_format="docx", blocks=ordered)


def _output_of(result: SegmentationResult, kind: SegmentKind) -> str:
    return result.ai_output_text if kind is SegmentKind.AI_OUTPUT else result.student_analysis_text


def _assert_offsets(result: SegmentationResult) -> None:
    """Every segment must slice back out of the string it indexes; Evidence rows point there."""
    assert result.segments, "a segmentation result always explains itself with at least one segment"
    for piece in result.segments:
        text = _output_of(result, piece.kind)
        assert text[piece.start : piece.end] == piece.text


def _canonical() -> ExtractedDocument:
    return _doc(
        _row("Prompt", "Hasil"),
        _row("Prompt", QUESTION),
        _row("Hasil", "UU ITE mengatur informasi dan transaksi elektronik."),
        _row("Critical Review", "Menurut saya pasal ini masih tumpang tindih dengan KUHP."),
    )


def test_labelled_document_splits_ai_output_from_analysis():
    result = segment(_canonical())

    assert result.method == "label"
    assert result.has_ai_output
    assert result.warnings == []
    assert result.ai_output_text == "UU ITE mengatur informasi dan transaksi elektronik."
    assert result.student_analysis_text == "Menurut saya pasal ini masih tumpang tindih dengan KUHP."

    ai, analysis = result.segments
    assert ai.kind is SegmentKind.AI_OUTPUT
    assert ai.method == "label"
    assert ai.confidence == LABEL_CONFIDENCE
    assert ai.prompt_text == QUESTION
    assert analysis.kind is SegmentKind.STUDENT_ANALYSIS
    assert analysis.prompt_text is None
    _assert_offsets(result)


def test_prompt_and_answer_rows_may_hold_their_text_in_their_own_rows():
    """`| Prompt | <question> |` then `| Hasil | <answer> |`: the question is context, not output."""
    result = segment(
        _doc(
            _row("Prompt", QUESTION),
            _row("Hasil", "UU ITE adalah undang-undang tentang informasi dan transaksi elektronik."),
            _row("Critical Review", "Analisis saya."),
        )
    )

    assert QUESTION not in result.ai_output_text
    assert result.ai_output_text == "UU ITE adalah undang-undang tentang informasi dan transaksi elektronik."
    assert result.segments[0].prompt_text == QUESTION
    _assert_offsets(result)


def test_continuation_row_with_empty_first_cell_stays_in_student_analysis():
    result = segment(
        _doc(
            _row("Critical Review", "Analisis awal."),
            _row("", "Lanjutan analisis di sel gabungan."),
            _row("   ", "Dan penutupnya."),
        )
    )

    assert result.method == "label"
    assert result.student_analysis_text == (
        "Analisis awal.\nLanjutan analisis di sel gabungan.\nDan penutupnya."
    )
    assert result.ai_output_text == ""
    assert not result.has_ai_output
    _assert_offsets(result)


def test_continuation_row_after_the_answer_stays_in_ai_output():
    result = segment(
        _doc(
            _row("Hasil", "Jawaban bagian pertama."),
            _row("", "Jawaban bagian kedua, sel yang tergabung."),
        )
    )

    assert result.ai_output_text == "Jawaban bagian pertama.\nJawaban bagian kedua, sel yang tergabung."
    assert result.student_analysis_text == ""
    _assert_offsets(result)


def test_repeated_header_after_a_page_break_restarts_pairing_without_text():
    result = segment(
        _doc(
            _row("Hasil", "Jawaban halaman satu.", page=1),
            _row("Critical Review", "Analisis halaman satu.", page=1),
            _row("Prompt", "Hasil", page=2),
            _row("Hasil", "Jawaban halaman dua.", page=2),
            _row("Critical Review", "Analisis halaman dua.", page=2),
        )
    )

    assert result.ai_output_text == "Jawaban halaman satu.\nJawaban halaman dua."
    assert result.student_analysis_text == "Analisis halaman satu.\nAnalisis halaman dua."
    assert "Hasil" not in result.ai_output_text
    assert [segment.kind for segment in result.segments] == [
        SegmentKind.AI_OUTPUT,
        SegmentKind.AI_OUTPUT,
        SegmentKind.STUDENT_ANALYSIS,
        SegmentKind.STUDENT_ANALYSIS,
    ]
    _assert_offsets(result)


def test_document_without_any_ai_output_is_all_student_analysis():
    result = segment(
        _doc(
            _para("Tugas 5"),
            _row("Analisis", "Teks analisis mahasiswa."),
            _row("", "Lanjutan teks analisis."),
        )
    )

    assert result.method == "none"
    assert result.ai_output_text == ""
    assert not result.has_ai_output
    assert result.student_analysis_text == (
        "Tugas 5\nAnalisis | Teks analisis mahasiswa.\nLanjutan teks analisis."
    )
    assert result.warnings and "no ai segment" in result.warnings[0].casefold()
    assert all(segment.kind is SegmentKind.STUDENT_ANALYSIS for segment in result.segments)
    _assert_offsets(result)


def test_labelled_document_without_ai_output_warns_instead_of_failing():
    result = segment(_doc(_row("Critical Review", "Analisis mahasiswa saja.")))

    assert result.method == "label"
    assert result.ai_output_text == ""
    assert result.warnings and "no ai segment" in result.warnings[0].casefold()
    _assert_offsets(result)


def test_short_row_followed_by_long_row_is_guessed_as_question_then_answer():
    answer = "Jawaban panjang dari AI. " * 30
    result = segment(_doc(_para(QUESTION), _para(answer), _para("Analisis mahasiswa yang singkat.")))

    assert result.method == "heuristic"
    assert result.ai_output_text == answer.strip()
    assert result.student_analysis_text == "Analisis mahasiswa yang singkat."
    assert result.warnings == []

    ai = result.segments[0]
    assert ai.kind is SegmentKind.AI_OUTPUT
    assert ai.method == "heuristic"
    assert ai.prompt_text == QUESTION
    assert ai.confidence is not None and ai.confidence < LABEL_CONFIDENCE
    _assert_offsets(result)


def test_heuristic_leaves_unpaired_rows_with_the_student():
    result = segment(_doc(_para("Judul singkat"), _para("Penjelasan pendek juga.")))

    assert result.method == "none"
    assert result.ai_output_text == ""
    assert result.student_analysis_text == "Judul singkat\nPenjelasan pendek juga."
    _assert_offsets(result)


def test_unlabelled_short_and_long_rows_without_a_question_stay_with_the_student():
    """The Tugas Akhir shape: a two-column table the student filled in. Nothing in it asks
    anything, so there is no AI output to find — pairing the rows would hand the student's own
    work to the scorers, which is exactly the mistake this bound exists to stop."""
    analysis = ("Analisis risiko proyek ini mencakup identifikasi, evaluasi, dan mitigasi. " * 16).strip()
    result = segment(_doc(_row("Nama", "Manajemen risiko"), _row("Uraian", analysis)))

    assert result.method == "none"
    assert result.ai_output_text == ""
    assert not result.has_ai_output
    assert result.student_analysis_text == f"Nama | Manajemen risiko\nUraian | {analysis}"
    assert all(segment.kind is SegmentKind.STUDENT_ANALYSIS for segment in result.segments)
    _assert_offsets(result)


def test_short_row_ending_in_a_question_mark_is_still_guessed_as_a_question():
    answer = ("Jawaban panjang dari AI tentang risiko proyek. " * 16).strip()
    result = segment(_doc(_row("Pertanyaan", "Apa saja risiko utamanya?"), _row(answer)))

    assert result.method == "heuristic"
    assert result.ai_output_text == answer
    assert result.student_analysis_text == ""
    assert result.warnings == []

    ai = result.segments[0]
    assert ai.method == "heuristic"
    assert ai.confidence is not None and ai.confidence < LABEL_CONFIDENCE
    assert ai.prompt_text == "Pertanyaan | Apa saja risiko utamanya?"
    _assert_offsets(result)


def test_short_row_opening_with_a_question_word_is_guessed_without_a_question_mark():
    answer = ("Jawaban panjang dari AI tentang risiko proyek. " * 16).strip()
    result = segment(_doc(_row("", "Bagaimana mitigasi risikonya"), _row("", answer)))

    assert result.method == "heuristic"
    assert result.ai_output_text == answer
    _assert_offsets(result)


def test_paragraph_between_two_analysis_rows_stays_in_the_student_analysis():
    """Text the extractor places outside the table box continues the cell it came from, so it must
    not open a second region or drop the label that follows it."""
    result = segment(
        _doc(
            _row("Critical Review", "Analisis awal."),
            _para("Lanjutan paragraf yang keluar dari kotak tabel."),
            _row("Critical Review", "Analisis penutup."),
        )
    )

    assert result.method == "label"
    assert result.ai_output_text == ""
    assert result.student_analysis_text == (
        "Analisis awal.\nLanjutan paragraf yang keluar dari kotak tabel.\nAnalisis penutup."
    )
    _assert_offsets(result)


def test_paragraph_before_the_first_label_is_analysis_and_keeps_the_label_path():
    """The identifier block sits above the table. It belongs to the student, and it must not turn
    the labelled run below it into a low-confidence guess."""
    result = segment(_doc(_para("Nama : Mahasiswa"), _row("Critical Review", "Analisis mahasiswa.")))

    assert result.method == "label"
    assert result.student_analysis_text == "Nama : Mahasiswa\nAnalisis mahasiswa."
    assert [segment.kind for segment in result.segments] == [SegmentKind.STUDENT_ANALYSIS]

    analysis = result.segments[0]
    assert analysis.method == "label"
    assert analysis.confidence == LABEL_CONFIDENCE
    _assert_offsets(result)


def test_image_only_blocks_contribute_no_text():
    result = segment(
        _doc(
            _row("Critical Review", "Analisis mahasiswa."),
            Block(kind=BlockKind.IMAGE_ONLY, text="", order=0, page=2),
        )
    )

    assert result.student_analysis_text == "Analisis mahasiswa."
    assert result.ai_output_text == ""
    _assert_offsets(result)
