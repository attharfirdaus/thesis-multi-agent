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
from scripts.seed_rubric import _calibration_from, rubric_content, version_to_insert

RUBRIC = {
    "version": 3,
    "levels": ["C1", "C2", "C3", "C4", "C5", "C6"],
    "indicators": ["elaborasi", "organisasi", "orientasi", "evaluasi"],
}
CALIBRATION_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "calibration.json"
ANALYSIS = "Saya membandingkan dua sumber lalu menyimpulkan kelemahan argumennya."
AI_OUTPUT = "Rangkuman keluaran AI yang dianalisis mahasiswa."
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
                "findings": [
                    {
                        "indicator": "evaluasi",
                        "present": True,
                        "strength": "kuat",
                        "evidence_quote": "kalibrasi-contoh-kutipan",
                        "rationale": "kalibrasi-contoh-alasan",
                    }
                ],
            }
        ],
    },
}


def test_levels_and_indicators_come_from_the_rubric_row():
    system, user = cognitive_prompt(RUBRIC, CALIBRATION, ANALYSIS)
    assert RUBRIC["levels"][4] in user
    assert "kalibrasi-contoh-alasan" in user
    assert ANALYSIS in user
    # The schema, not a template literal, tells the model what to return.
    assert "evidence_quote" in system


def test_a_renamed_level_replaces_the_stored_name():
    rubric = {**RUBRIC, "levels": ["Menimbang-Ulang Bukti"]}
    _, user = cognitive_prompt(rubric, CALIBRATION, ANALYSIS)
    assert "Menimbang-Ulang Bukti" in user
    assert "Mengingat" not in user
    assert "Mencipta" not in user


def test_indicators_come_from_the_rubric_row():
    rubric = {**RUBRIC, "indicators": ["indikator-uji-a", "indikator-uji-b"]}
    _, user = metacognitive_prompt(rubric, CALIBRATION, ANALYSIS)
    assert "indikator-uji-a" in user and "indikator-uji-b" in user
    assert "elaborasi" not in user


@pytest.mark.parametrize("build", [cognitive_prompt, metacognitive_prompt])
def test_empty_calibration_refuses_the_run(build):
    with pytest.raises(MissingCalibration):
        build(RUBRIC, {}, ANALYSIS)


def test_one_agent_without_its_block_refuses_only_that_agent():
    """Each agent reads its own block: supplying Bloom examples must not let the metacognitive agent
    run on them, which is the failure a single shared example list would hide."""
    only_cognitive = {"cognitive": CALIBRATION["cognitive"]}
    with pytest.raises(MissingCalibration):
        metacognitive_prompt(RUBRIC, only_cognitive, ANALYSIS)
    _, user = cognitive_prompt(RUBRIC, only_cognitive, ANALYSIS)
    assert "kalibrasi-contoh-alasan" in user


def test_synthesis_carries_the_analysis_and_the_ai_output():
    _, user = synthesis_prompt(
        RUBRIC,
        {"level": "Menganalisis", "rationale": "alasan-agen-kognitif"},
        {"findings": [{"indicator": "elaborasi", "present": True}]},
        ANALYSIS,
        AI_OUTPUT,
    )
    assert ANALYSIS in user
    assert AI_OUTPUT in user
    assert "alasan-agen-kognitif" in user
    assert "elaborasi" in user


def test_synthesis_retry_carries_the_evidence_failure_reason():
    reason = "kutipan tidak ditemukan di teks"
    _, first = synthesis_prompt(RUBRIC, {}, {}, ANALYSIS, AI_OUTPUT)
    _, retry = synthesis_prompt(RUBRIC, {}, {}, ANALYSIS, AI_OUTPUT, retry_reason=reason)
    assert reason not in first
    assert reason in retry


def test_single_agent_prompt_carries_the_full_rubric_and_both_calibration_blocks():
    system, user = single_agent_prompt(RUBRIC, CALIBRATION, ANALYSIS)
    assert RUBRIC["levels"][4] in user
    assert "elaborasi" in user and "evaluasi" in user
    assert "kalibrasi-contoh-alasan" in user
    assert ANALYSIS in user
    # One judgement task: the schema carries the level and the findings together.
    assert "evidence_quote" in system
    assert "findings" in system


@pytest.mark.parametrize(
    "calibration",
    [{}, {"cognitive": CALIBRATION["cognitive"]}, {"metacognitive": CALIBRATION["metacognitive"]}],
)
def test_single_agent_prompt_refuses_without_both_calibration_blocks(calibration):
    with pytest.raises(MissingCalibration):
        single_agent_prompt(RUBRIC, calibration, ANALYSIS)


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

    _, cognitive = cognitive_prompt(RUBRIC, calibration, ANALYSIS)
    _, metacognitive = metacognitive_prompt(RUBRIC, calibration, ANALYSIS)

    assert "saya susun alur keputusan sendiri untuk tim kami" in cognitive
    assert "elaborasi" not in cognitive  # the SRL block belongs to the other agent
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


def test_seeded_rubric_carries_the_four_srl_codes_and_the_six_bloom_codes():
    content = rubric_content()
    assert content["indicators"] == ["elaborasi", "organisasi", "orientasi", "evaluasi"]
    assert content["levels"] == ["C1", "C2", "C3", "C4", "C5", "C6"]
    # The names come from Atthar's calibration (Anderson & Krathwohl). No threshold is seeded: that is
    # the supervisors' rater guideline's job (PRD §13), and inventing one here would be the mistake.
    assert content["descriptors"]["levels"]["C4"] == "Analyze"
    assert content["descriptors"]["indicators"] == {}
    assert content["descriptors"]["pending_supervisors"] is True
    assert "threshold" not in json.dumps(content["descriptors"]).lower()
