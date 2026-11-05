"""Prompt builder tests.

The builders are pure functions over the rubric dict, so nothing here needs a database. The rubric
below is shaped like a RubricVersion row; its values are test data on purpose, because the point of
several of these tests is that the builder carries whatever the row holds instead of a literal.
"""

import json
import pathlib

import pytest

from app.agents.prompts import (
    MissingCalibration,
    cognitive_prompt,
    metacognitive_prompt,
    single_agent_prompt,
    synthesis_prompt,
)
from app.agents.segments import split_segments
from scripts.seed_rubric import _calibration_from, rubric_content, version_to_insert

RUBRIC = {
    "version": 3,
    "levels": ["C1", "C2", "C3", "C4", "C5", "C6"],
    "indicators": ["orientasi", "perencanaan", "pemantauan", "evaluasi"],
}
CALIBRATION_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "calibration.json"
ANALYSIS = "Saya membandingkan dua sumber lalu menyimpulkan kelemahan argumennya."
AI_OUTPUT = "Rangkuman keluaran AI yang dianalisis mahasiswa."
SEGMENTS = split_segments(ANALYSIS)
#: The paired input every specialist builder takes after the rubric and the calibration.
PAIRED = (AI_OUTPUT, SEGMENTS)
CALIBRATION = {
    "cognitive": {
        "instructions": "Kalibrasi uji untuk agen kognitif.",
        "examples": [
            {
                "analisis_mhs": "teks contoh",
                "level": "C4",
                "evidence_quote": "kalibrasi-contoh-kutipan",
                "rationale": "kalibrasi-contoh-alasan",
            }
        ],
    },
    "metacognitive": {
        "instructions": "Kalibrasi uji untuk agen metakognitif.",
        "examples": [
            {
                "analisis_mhs": "teks contoh",
                "indicators": [
                    {
                        "indicator": "evaluasi",
                        "evidence_quote": "kalibrasi-contoh-kutipan",
                        "rationale": "kalibrasi-contoh-alasan",
                    }
                ],
            }
        ],
    },
}


def test_levels_and_indicators_come_from_the_rubric_row():
    system, user = cognitive_prompt(RUBRIC, CALIBRATION, *PAIRED)
    assert RUBRIC["levels"][4] in system
    assert "kalibrasi-contoh-alasan" in system
    assert f"[1] {ANALYSIS}" in user
    # The schema, not a template literal, tells the model what to return.
    assert "evidence_quote" in system


def test_a_renamed_level_replaces_the_stored_name():
    rubric = {**RUBRIC, "levels": ["Menimbang-Ulang Bukti"]}
    system, _ = cognitive_prompt(rubric, CALIBRATION, *PAIRED)
    assert "Menimbang-Ulang Bukti" in system
    assert "Mengingat" not in system
    assert "Mencipta" not in system


def test_indicators_come_from_the_rubric_row():
    rubric = {**RUBRIC, "indicators": ["indikator-uji-a", "indikator-uji-b"]}
    system, _ = metacognitive_prompt(rubric, CALIBRATION, *PAIRED)
    assert "indikator-uji-a" in system and "indikator-uji-b" in system
    assert "perencanaan" not in system


@pytest.mark.parametrize("build", [cognitive_prompt, metacognitive_prompt])
def test_empty_calibration_refuses_the_run(build):
    with pytest.raises(MissingCalibration):
        build(RUBRIC, {}, *PAIRED)


def test_one_agent_without_its_block_refuses_only_that_agent():
    """Each agent reads its own block: supplying Bloom examples must not let the metacognitive agent
    run on them, which is the failure a single shared example list would hide."""
    only_cognitive = {"cognitive": CALIBRATION["cognitive"]}
    with pytest.raises(MissingCalibration):
        metacognitive_prompt(RUBRIC, only_cognitive, *PAIRED)
    system, _ = cognitive_prompt(RUBRIC, only_cognitive, *PAIRED)
    assert "kalibrasi-contoh-alasan" in system


def test_both_specialists_read_the_paired_input_with_role_markers():
    """Bab II.2.2 / Tabel III.5: the AI output as object of analysis and the segmented analysis, each
    behind its own role marker, plus the rule that the AI output is not a reference answer."""
    for build in (cognitive_prompt, metacognitive_prompt, single_agent_prompt):
        system, user = build(RUBRIC, CALIBRATION, *PAIRED)
        assert f"<keluaran_ai>\n{AI_OUTPUT}\n</keluaran_ai>" in user
        assert f"<teks_mahasiswa>\n[1] {ANALYSIS}\n</teks_mahasiswa>" in user
        assert "not a reference answer" in system


def test_synthesis_carries_the_analysis_and_the_ai_output_but_no_rubric():
    _, user = synthesis_prompt(
        {"segments": [{"segment": 1, "level": "C4", "rationale": "alasan-agen-kognitif"}]},
        {"segments": [{"segment": 1, "indicators": [{"indicator": "pemantauan"}]}]},
        AI_OUTPUT,
        SEGMENTS,
    )
    assert ANALYSIS in user
    assert AI_OUTPUT in user
    assert "alasan-agen-kognitif" in user
    assert "pemantauan" in user
    # Bab III.8: the synthesis agent receives the labels without the labelling rubric.
    assert "Rubrik versi" not in user and "orientasi" not in user


def test_synthesis_retry_carries_the_evidence_failure_reason():
    reason = "kutipan tidak ditemukan di teks"
    _, first = synthesis_prompt({}, {}, AI_OUTPUT, SEGMENTS)
    _, retry = synthesis_prompt({}, {}, AI_OUTPUT, SEGMENTS, retry_reason=reason)
    assert reason not in first
    assert reason in retry


def test_single_agent_prompt_carries_the_full_rubric_and_both_calibration_blocks():
    system, user = single_agent_prompt(RUBRIC, CALIBRATION, *PAIRED)
    assert RUBRIC["levels"][4] in system
    assert "perencanaan" in system and "evaluasi" in system
    assert "kalibrasi-contoh-alasan" in system
    assert ANALYSIS in user
    # One judgement task: the schema carries both dimensions' segment labels together.
    assert "evidence_quote" in system
    assert '"metacognitive"' in system and '"cognitive"' in system


@pytest.mark.parametrize(
    "calibration",
    [{}, {"cognitive": CALIBRATION["cognitive"]}, {"metacognitive": CALIBRATION["metacognitive"]}],
)
def test_single_agent_prompt_refuses_without_both_calibration_blocks(calibration):
    with pytest.raises(MissingCalibration):
        single_agent_prompt(RUBRIC, calibration, *PAIRED)


def test_seeder_version_rule_skips_identical_content_and_bumps_changed_content():
    stored = {"version": 2, **rubric_content()}
    assert version_to_insert(stored, rubric_content()) is None
    changed = {**rubric_content(), "levels": ["Menimbang-Ulang Bukti"]}
    assert version_to_insert(stored, changed) == 3
    assert version_to_insert(None, changed) == 1


def test_the_shipped_calibration_reaches_both_prompts_without_its_provenance_notes():
    """The shipped file is Atthar's content (2026-10-15): Bloom examples for one agent, SRL for the
    other. Each agent must see only its own block, and the reader-facing provenance notes must stay
    out of the prompt."""
    calibration = json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))

    cognitive, _ = cognitive_prompt(RUBRIC, calibration, *PAIRED)
    metacognitive, _ = metacognitive_prompt(RUBRIC, calibration, *PAIRED)

    assert "saya susun alur keputusan sendiri untuk tim kami" in cognitive
    assert "perencanaan" not in cognitive  # the metacognitive block belongs to the other agent
    assert "Kualitas analisis tinggi tidak otomatis berarti" in metacognitive  # the zero-code case
    assert "C4" not in metacognitive
    for prompt in (cognitive, metacognitive):
        assert "catatan_sumber" not in prompt
        assert "SYNTHETIC" not in prompt


def test_a_calibration_file_missing_an_agent_block_is_rejected(tmp_path):
    """A file with only the cognitive block would seed cleanly and fail at the first metacognitive
    job, so it is refused when it is read."""
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps({"cognitive": {"examples": [{"level": "C4"}]}}), encoding="utf-8")
    with pytest.raises(SystemExit):
        _calibration_from(str(path))


def test_seeded_rubric_carries_the_thesis_indicators_and_the_six_bloom_codes():
    content = rubric_content()
    assert content["indicators"] == ["orientasi", "perencanaan", "pemantauan", "evaluasi"]
    assert content["levels"] == ["C1", "C2", "C3", "C4", "C5", "C6"]
    # The names come from Atthar's calibration (Anderson & Krathwohl), the definitions from Gambar II.1
    # and II.2, the groups from Xu Li dkk. (2026). No threshold is seeded.
    descriptors = content["descriptors"]
    assert descriptors["levels"]["C4"] == "Analyze"
    assert descriptors["level_definitions"]["C1"] == "Mengingat informasi spesifik"
    assert descriptors["indicators"]["pemantauan"].startswith("Memeriksa pemahaman dan ketidaksesuaian")
    assert set(descriptors["indicators"]) == set(content["indicators"])
    assert descriptors["groups"] == {"rendah": ["C1", "C2"], "menengah": ["C3", "C4"], "tinggi": ["C5", "C6"]}
    assert descriptors["pending_supervisors"] is True
    assert "threshold" not in json.dumps(content["descriptors"]).lower()


def test_the_shipped_metacognitive_calibration_uses_only_the_thesis_indicators():
    """Bab II.2.4: orientasi, perencanaan, pemantauan, evaluasi — nominal, no strength. Every quote is
    verbatim from its example, as the evidence rule demands of the model."""
    block = json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))["metacognitive"]
    used = set()
    for example in block["examples"]:
        for finding in example["indicators"]:
            assert finding["indicator"] in RUBRIC["indicators"]
            assert "strength" not in finding
            assert finding["evidence_quote"] in example["segmen"]
            used.add(finding["indicator"])
    assert used == set(RUBRIC["indicators"]), "every indicator needs at least one example"


def test_specialist_prompt_parts_follow_tabel_iii_5():
    """Tabel III.5's order: role and task, rubric, paired-input rule, few-shot examples, evidence rule,
    output schema, and the segment list last. The rubric carries each label's definition."""
    rubric = {"version": 3, **rubric_content()}
    for build in (cognitive_prompt, metacognitive_prompt, single_agent_prompt):
        system, user = build(rubric, CALIBRATION, *PAIRED)
        markers = ["Your role", "Rubrik versi", "Paired input.", "Contoh kalibrasi", "Evidence rule.",
                   "Reply with JSON only"]
        positions = [system.index(marker) for marker in markers]
        assert positions == sorted(positions), build.__name__
        assert user.rstrip().endswith("segmen).") and "<teks_mahasiswa>" in user
    system, _ = cognitive_prompt(rubric, CALIBRATION, *PAIRED)
    assert "- C1 Remember: Mengingat informasi spesifik" in system
    system, _ = metacognitive_prompt(rubric, CALIBRATION, *PAIRED)
    assert "- orientasi: Merujuk persyaratan tugas dan standar penilaian" in system


def test_shipped_cognitive_examples_label_one_segment_with_its_context():
    """Bab III.2.3 / Tabel III.5: one example is one sentence segment with a context snippet, and the
    segment is a real unit of the system's own split, holding the example's quote."""
    from app.agents.evidence import locate_quote

    block = json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))["cognitive"]
    assert [example["level"] for example in block["examples"]] == ["C1", "C2", "C3", "C4", "C5", "C6"]
    for example in block["examples"]:
        units = [segment.text for segment in split_segments(example["konteks_analisis"])]
        assert example["segmen"] in units
        assert locate_quote(example["segmen"], example["evidence_quote"]) is not None
