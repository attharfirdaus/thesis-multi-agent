"""The pipeline on the four real archived submissions.

Every other test uses a synthetic docx: faster, deterministic, and enough for the logic. It cannot
prove that ingest, segmentation, the graph, persistence and the evidence offsets survive the Word-table
PDFs the thesis actually scores, nor that an offset lands inside real Indonesian student text. That is
what this file covers. The PDFs are the owner's own archived submissions and are deliberately gitignored
(`.gitignore` lists `samples/`), so this file runs where they exist — the owner's machine — and skips in
CI, where the skip reason says exactly that. A skip is not a pass, and pretending otherwise would be the
kind of claim this project keeps out of its records.

The provider is stubbed as everywhere else. The calibration is the real one
(`scripts/calibration.json`, Atthar's content, PRD §14), and the stub answers with a slice of the
submission's own stored text, so the offsets still have to be computed by the real code under test.
"""

import json
import os
import pathlib
import uuid

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
from scripts.seed_rubric import seed as seed_rubric

SAMPLES = sorted(
    (pathlib.Path(__file__).resolve().parents[2] / "samples").glob("Tugas [1-4] *.pdf")
)
EMAIL = "real-corpus@example.ac.id"
PASSWORD = "kata-sandi-panjang-2026"
CALIBRATION_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "calibration.json"


class QuoteStub:
    """Answers every agent with a slice of the submission's own real analysis text."""

    def __init__(self, quotes: list[str]) -> None:
        self.quotes = quotes
        self.calls = 0

    def complete_json(self, *, system, user, schema, temperature=None, seed=None):
        self.calls += 1
        quote = self.quotes[self.calls % len(self.quotes)]
        payload = {
            CognitiveResult: CognitiveResult(
                level="C4",
                evidence_quote=quote,
                rationale="Mahasiswa membandingkan dua kerangka kerja pada bagian ini.",
            ),
            MetacognitiveResult: MetacognitiveResult(
                findings=[
                    IndicatorFinding(
                        indicator="elaborasi",
                        present=True,
                        strength="kuat",
                        evidence_quote=quote,
                        rationale="Membandingkan dua kerangka dan menjelaskan fokus masing-masing.",
                    ),
                    IndicatorFinding(
                        indicator="evaluasi",
                        present=True,
                        strength="sedang",
                        evidence_quote=self.quotes[0],
                        rationale="Menilai keterbatasan tiap kerangka.",
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
                feedback_text="Perbandingan Anda baik; tambahkan contoh penerapan pada konteks MRTI.",
            ),
        }[schema]
        return Completion(
            parsed=payload, raw=json.dumps(payload.model_dump()), latency_ms=3, attempts=1
        )


@pytest.mark.skipif(
    len(SAMPLES) != 4, reason="the four archived AI-permitted submissions are not in samples/"
)
def test_real_submissions_score_with_offsets_in_their_own_text(client, monkeypatch):
    signup = client.post(
        "/auth/signup", json={"email": EMAIL, "name": "Korpus Asli", "password": PASSWORD}
    )
    assert signup.status_code in (200, 201), signup.text
    user = uuid.UUID(client.get("/auth/me").json()["user"]["id"])
    headers = {"X-CSRF-Token": client.cookies.get("ta_csrf")}

    # The real seeder with the shipped calibration, so the run snapshots the content that ships.
    seed_rubric(
        os.environ["DATABASE_URL"],
        EMAIL,
        json.loads(CALIBRATION_PATH.read_text(encoding="utf-8")),
    )

    with db.tenant_tx(user) as conn:
        rubric_id = conn.execute("select id from rubric_versions limit 1").fetchone()[0]
        assignment_id = conn.execute(
            "insert into assignments (owner_id, title, course, rubric_version_id) "
            "values (%s, 'Tugas Risiko TI', 'MRTI', %s) returning id",
            (user, rubric_id),
        ).fetchone()[0]

    upload = client.post(
        f"/assignments/{assignment_id}/submissions",
        files=[("files", (path.name, path.read_bytes(), "application/pdf")) for path in SAMPLES],
        headers=headers,
    )
    assert upload.status_code == 201, upload.text
    assert [f["status"] for f in upload.json()["files"]] == ["imported"] * 4, upload.json()

    with db.tenant_tx(user) as conn:
        texts = {
            pseudonym: text or ""
            for pseudonym, text in conn.execute(
                "select pseudonym, student_analysis_text from submissions"
            ).fetchall()
        }
    assert len(texts) == 4
    for pseudonym, text in texts.items():
        assert len(text) > 200, f"{pseudonym}: only {len(text)} characters of analysis text"

    run = client.post(
        f"/assignments/{assignment_id}/runs", json={"mode": "multi_agent"}, headers=headers
    )
    assert run.status_code == 201, run.text
    run_id = run.json()["id"]

    def fake_evaluate(state, checkpointer=None):
        text = state["student_analysis_text"]
        midpoint = len(text) // 2
        quotes = [text[midpoint : midpoint + 120].strip(), text[40:140].strip()]
        stub = QuoteStub([quote for quote in quotes if quote] or [text[:60].strip()])
        return graph_module.evaluate_submission(state, client=stub, checkpointer=checkpointer)

    monkeypatch.setattr("app.jobs.worker.evaluate_submission", fake_evaluate)

    processed = client.post(f"/runs/{run_id}/process", headers=headers)
    assert processed.status_code == 200, processed.text
    assert processed.json()["jobs"] == {"done": 4}, processed.json()
    assert processed.json()["status"] == "done", processed.json()

    results = client.get(f"/runs/{run_id}/results")
    assert results.status_code == 200, results.text
    spans = 0
    for submission in results.json()["submissions"]:
        assert {score["dimension"] for score in submission["scores"]} == {
            "cognitive",
            "metacognitive",
        }, submission
        assert submission["feedback_text"], submission
        text = texts[submission["pseudonym"]]
        for score in submission["scores"]:
            assert score["rationale"], score
            for span in score["evidence"]:
                start, end = span["start_offset"], span["end_offset"]
                # The contract the lecturer's evidence view rests on: the offsets reproduce the quote,
                # and the quote really is in the text that was scored.
                assert text[start:end] == span["quote"], (score, span)
                spans += 1
    assert spans >= 8, f"expected evidence on both dimensions of every submission, saw {spans}"

    with db.tenant_tx(user) as conn:
        checkpoints = conn.execute("select count(*) from checkpoints").fetchone()[0]
    assert checkpoints > 0, "the graph did not checkpoint into Postgres"
