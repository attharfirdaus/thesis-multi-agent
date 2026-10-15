"""Phase-4 gate: one batch evaluates end to end, with evidence and an explanation per score.

Only the provider is stubbed — the real one needs an API key that is not in the repository and CI has
no network. Everything else is the real thing: the ingest API, the Postgres queue, the LangGraph graph
with its parallel agents and rule-based evidence check, persistence, and the results endpoint.

The decisive assertion is not "a score exists" but "the stored evidence offsets slice exactly the
quote out of the stored text", because that is what makes a score traceable to the student's own words
(PRD §2, FR-10).
"""

import io
import json
import uuid

import docx
import pytest

from app import db
from app.agents import graph as graph_module
from app.agents.models import (
    CognitiveResult,
    IndicatorFinding,
    MetacognitiveResult,
    SynthesisResult,
)
from app.llm.client import Completion

# Every quote below appears verbatim in the fixture document, so the evidence check must locate it.
QUOTE_COGNITIVE = "COSO berfokus pada pengendalian internal"
QUOTE_METACOGNITIVE = "saya membandingkan COSO dengan ISO 31000"

ANALYSIS = (
    "Dari hasil prompt di atas, saya membandingkan COSO dengan ISO 31000 dan menemukan perbedaan fokus. "
    "COSO berfokus pada pengendalian internal, sedangkan ISO menekankan proses identifikasi risiko. "
    "Evaluasi saya, keduanya saling melengkapi dan tidak bisa dipakai sendiri-sendiri."
)

LEVELS = ["Mengingat", "Memahami", "Menerapkan", "Menganalisis", "Mengevaluasi", "Mencipta"]
INDICATORS = ["elaborasi", "organisasi", "orientasi", "evaluasi"]


class StubClient:
    """Returns one canned answer per schema. Counts calls so the test can prove both agents ran."""

    def __init__(self) -> None:
        self.calls: list[type] = []

    def complete_json(self, *, system, user, schema, temperature=None, seed=None):
        self.calls.append(schema)
        payload = {
            CognitiveResult: CognitiveResult(
                level="Menganalisis",
                evidence_quote=QUOTE_COGNITIVE,
                rationale="Mahasiswa menilai dua kerangka kerja dan membandingkan fokusnya.",
            ),
            MetacognitiveResult: MetacognitiveResult(
                findings=[
                    IndicatorFinding(
                        indicator="elaborasi",
                        present=True,
                        strength="high",
                        evidence_quote=QUOTE_METACOGNITIVE,
                        rationale="Memperluas dengan membandingkan dua kerangka kerja.",
                    ),
                    IndicatorFinding(
                        indicator="evaluasi",
                        present=True,
                        strength="medium",
                        evidence_quote=QUOTE_COGNITIVE,
                        rationale="Memberi penilaian tentang keterbatasan masing-masing.",
                    ),
                    IndicatorFinding(
                        indicator="organisasi",
                        present=False,
                        strength=None,
                        evidence_quote="",
                        rationale="Tidak terlihat penataan ulang materi.",
                    ),
                    IndicatorFinding(
                        indicator="orientasi",
                        present=False,
                        strength=None,
                        evidence_quote="",
                        rationale="Tidak ada perumusan tujuan belajar.",
                    ),
                ]
            ),
            SynthesisResult: SynthesisResult(
                rationale="Analisis menunjukkan perbandingan yang sadar antara dua kerangka kerja.",
                feedback_text="Perbandingan Anda sudah baik; tambahkan contoh penerapan agar lebih kuat.",
            ),
        }[schema]
        return Completion(parsed=payload, raw=json.dumps(payload.model_dump()), latency_ms=7, attempts=1)


def build_submission_docx() -> bytes:
    document = docx.Document()
    table = document.add_table(rows=0, cols=2)
    for label, content in [
        ("Prompt", "Apa perbedaan COSO dan ISO 31000?"),
        ("Hasil", "COSO adalah kerangka pengendalian internal; ISO 31000 adalah panduan manajemen risiko."),
        ("Critical Review", ANALYSIS),
    ]:
        row = table.add_row().cells
        row[0].text = label
        row[1].text = content
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


@pytest.fixture
def seeded(client, monkeypatch):
    """A lecturer with a seeded rubric, prompt versions and calibration, plus one imported submission."""
    client.post(
        "/auth/signup",
        json={"email": "runs@example.ac.id", "name": "Dosen Runs", "password": "kata-sandi-panjang-2026"},
    )
    user = uuid.UUID(client.get("/auth/me").json()["user"]["id"])

    with db.tenant_tx(user) as conn:
        rubric_id = conn.execute(
            "insert into rubric_versions (owner_id, version, dimensions, levels, indicators, descriptors) "
            "values (%s, 1, %s, %s, %s, '[]'::jsonb) returning id",
            (
                user,
                json.dumps({"cognitive": "Bloom", "metacognitive": "SRL G1"}),
                json.dumps({"levels": LEVELS}),
                json.dumps({"indicators": INDICATORS}),
            ),
        ).fetchone()[0]
        for agent in ("cognitive", "metacognitive", "synthesis"):
            conn.execute(
                "insert into prompt_versions (owner_id, agent_name, version, template) "
                "values (%s, %s, 1, %s)",
                (user, agent, "template placeholder — the real templates live in app/agents/prompts.py"),
            )
        # Calibration is stored exactly as scripts/seed_rubric.py writes it: an object carrying the
        # examples plus the flags that mark it interim.
        conn.execute(
            "insert into prompt_versions "
            "(owner_id, agent_name, version, template) values (%s, 'calibration', 1, %s)",
            (user, json.dumps({"examples": [{"text": "contoh", "level": "Memahami"}], "interim": True})),
        )
        assignment = conn.execute(
            "insert into assignments (owner_id, title, course, rubric_version_id) "
            "values (%s, %s, %s, %s) returning id",
            (user, "Tugas Risiko", "MRTI", rubric_id),
        ).fetchone()[0]

    upload = client.post(
        f"/assignments/{assignment}/submissions",
        files=[
            (
                "files",
                (
                    "Tugas 1_Dosen Runs.docx",
                    build_submission_docx(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
            )
        ],
        headers={"X-CSRF-Token": client.cookies.get("ta_csrf")},
    )
    assert upload.status_code == 201, upload.text
    assert upload.json()["files"][0]["status"] == "imported", upload.json()["files"][0]

    stub = StubClient()

    def fake_evaluate(state, checkpointer=None):
        # Passing the checkpointer through keeps the test on the same path the worker uses.
        return graph_module.evaluate_submission(state, client=stub, checkpointer=checkpointer)

    monkeypatch.setattr("app.jobs.worker.evaluate_submission", fake_evaluate)

    return {
        "client": client,
        "user": user,
        "assignment": assignment,
        "csrf": client.cookies.get("ta_csrf"),
        "stub": stub,
    }


def test_one_batch_evaluates_end_to_end_with_evidence(seeded):
    client, csrf = seeded["client"], seeded["csrf"]

    created = client.post(
        f"/assignments/{seeded['assignment']}/runs",
        headers={"X-CSRF-Token": csrf},
    )
    assert created.status_code == 201, created.text
    run_id = created.json()["id"]
    assert created.json()["jobs"] == {"queued": 1}

    processed = client.post(f"/runs/{run_id}/process?limit=5", headers={"X-CSRF-Token": csrf})
    assert processed.status_code == 200, processed.text
    body = processed.json()
    with db.tenant_tx(seeded["user"]) as conn:
        reason = conn.execute("select last_error from jobs where run_id = %s", (run_id,)).fetchone()[0]
    assert body["processed"] == 1, f"{body} | job error: {reason}"
    assert body["failed"] == 0, f"{body} | job error: {reason}"
    assert body["status"] == "done", body

    # Both scoring agents were called; the scheduler ran them as separate agents, not one merged call.
    assert CognitiveResult in seeded["stub"].calls
    assert MetacognitiveResult in seeded["stub"].calls

    results = client.get(f"/runs/{run_id}/results")
    assert results.status_code == 200, results.text
    payload = results.json()
    assert len(payload["submissions"]) == 1

    submission = payload["submissions"][0]
    assert submission["pseudonym"].startswith("S-")
    assert submission["feedback_text"], "FR-19 feedback must be stored"

    cognitive = next(s for s in submission["scores"] if s["dimension"] == "cognitive")
    assert cognitive["level"] == "Menganalisis"
    assert cognitive["rationale"]

    indicators = {s["indicator"]: s for s in submission["scores"] if s["dimension"] == "metacognitive"}
    assert set(indicators) == set(INDICATORS)
    assert indicators["elaborasi"]["level"] == "high"
    assert indicators["organisasi"]["level"] == "absent"

    # The decisive check: offsets must slice the quote out of the *stored* text, not out of something
    # that only existed while the graph ran.
    with db.tenant_tx(seeded["user"]) as conn:
        analysis = conn.execute("select student_analysis_text from submissions limit 1").fetchone()[0]

    assert cognitive["evidence"], "a cognitive score without evidence is not traceable"
    span = cognitive["evidence"][0]
    assert span["quote"] == QUOTE_COGNITIVE
    assert analysis[span["start_offset"] : span["end_offset"]] == span["quote"]

    metacog_span = indicators["elaborasi"]["evidence"][0]
    assert analysis[metacog_span["start_offset"] : metacog_span["end_offset"]] == metacog_span["quote"]


def test_run_status_reports_job_counts(seeded):
    client, csrf = seeded["client"], seeded["csrf"]
    run_id = client.post(
        f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
    ).json()["id"]

    before = client.get(f"/runs/{run_id}").json()
    assert before["jobs"] == {"queued": 1}
    assert before["status"] == "queued"

    client.post(f"/runs/{run_id}/process?limit=5", headers={"X-CSRF-Token": csrf})
    after = client.get(f"/runs/{run_id}").json()
    assert after["jobs"] == {"done": 1}
    assert after["status"] == "done"
