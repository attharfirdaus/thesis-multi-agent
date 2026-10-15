"""Prompt builder tests.

The builders are pure functions over the rubric dict, so nothing here needs a database. The rubric
below is shaped like a RubricVersion row; its values are test data on purpose, because the point of
several of these tests is that the builder carries whatever the row holds instead of a literal.
"""

import pytest

from app.agents.prompts import (
    MissingCalibration,
    cognitive_prompt,
    metacognitive_prompt,
    synthesis_prompt,
)
from scripts.seed_rubric import rubric_content, version_to_insert

RUBRIC = {
    "version": 3,
    "levels": ["Mengingat", "Memahami", "Menerapkan", "Menganalisis", "Mengevaluasi", "Mencipta"],
    "indicators": ["elaborasi", "organisasi", "orientasi", "evaluasi"],
}
ANALYSIS = "Saya membandingkan dua sumber lalu menyimpulkan kelemahan argumennya."
AI_OUTPUT = "Rangkuman keluaran AI yang dianalisis mahasiswa."
CALIBRATION = [
    {
        "level": "Menganalisis",
        "evidence_quote": "kalibrasi-contoh-kutipan",
        "rationale": "kalibrasi-contoh-alasan",
    }
]


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
        build(RUBRIC, [], ANALYSIS)


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


def test_seeder_version_rule_skips_identical_content_and_bumps_changed_content():
    stored = {"version": 2, **rubric_content()}
    assert version_to_insert(stored, rubric_content()) is None
    changed = {**rubric_content(), "levels": ["Menimbang-Ulang Bukti"]}
    assert version_to_insert(stored, changed) == 3
    assert version_to_insert(None, changed) == 1


def test_seeded_rubric_carries_the_four_srl_codes_and_no_descriptors():
    content = rubric_content()
    assert content["indicators"] == ["elaborasi", "organisasi", "orientasi", "evaluasi"]
    assert len(content["levels"]) == 6
    assert content["descriptors"]["levels"] == {}
    assert content["descriptors"]["indicators"] == {}
    assert content["descriptors"]["pending_supervisors"] is True
