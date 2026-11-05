"""The assessed unit of Bab III.6: a deterministic sentence split, and the text-level aggregation."""

from app.agents.segments import highest_level, split_segments


def test_sentences_split_on_end_punctuation_and_blank_lines_not_on_wrapped_lines():
    sample = (
        "Jadi begini: AI menjelaskan COSO dengan benar. Namun ISO 31000 tidak disebut\nsama sekali!\n"
        "Oke.\nSaya cek dokumentasi resmi.\n\nTanpa titik di akhir paragraf\n\nParagraf terakhir"
    )
    found = split_segments(sample)
    assert [s.text for s in found] == [
        "Jadi begini: AI menjelaskan COSO dengan benar.",
        "Namun ISO 31000 tidak disebut\nsama sekali!",
        # A connector sentence ("Oke.") is merged into the sentence after it.
        "Oke.\nSaya cek dokumentasi resmi.",
        "Tanpa titik di akhir paragraf",
        "Paragraf terakhir",
    ]
    assert [s.index for s in found] == [1, 2, 3, 4, 5]
    assert all(sample[s.start : s.end] == s.text for s in found)


def test_the_text_level_is_the_highest_segment_level_in_rubric_order():
    assert highest_level(["C2", "C4", "C3"], ["C1", "C2", "C3", "C4", "C5", "C6"]) == "C4"
    assert highest_level([], ["C1"]) is None
