"""Test fixtures. Requires a local Postgres with the thesis_migrator/thesis_app roles
(see scripts/bootstrap_db.sh). Migrations are applied on the test database once per session."""

import os
import pathlib
import sys

import pytest

BACKEND = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

# Forced, not setdefault: these fixtures TRUNCATE every tenant table, so an inherited
# DATABASE_URL from the shell (for example after `source .env`) must never be honoured here.
os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "postgresql://thesis_app:app_local_pw@localhost:5432/thesis_test"
os.environ["MIGRATION_DATABASE_URL"] = (
    "postgresql://thesis_migrator:migrator_local_pw@localhost:5432/thesis_test"
)
os.environ["COOKIE_SECURE"] = "false"
# Also forced: `source .env` in bash strips the quotes from this JSON list, and Settings prefers
# an environment variable over the file, so an inherited value would fail to parse.
os.environ["ALLOWED_ORIGINS"] = '["http://localhost:3000"]'

for _var in ("DATABASE_URL", "MIGRATION_DATABASE_URL"):
    if not os.environ[_var].rsplit("/", 1)[-1].startswith("thesis_test"):
        raise RuntimeError(f"Refusing to run tests against {_var}: it is not the test database.")

import io  # noqa: E402
import json  # noqa: E402
import uuid  # noqa: E402

import docx  # noqa: E402
import psycopg  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app import db  # noqa: E402
from app.agents import graph as graph_module  # noqa: E402
from app.agents.models import (  # noqa: E402
    CognitiveResult,
    IndicatorFinding,
    MetacognitiveResult,
    SynthesisResult,
)
from app.llm.client import Completion  # noqa: E402
from app.main import app  # noqa: E402  (import after settings are in place)
from scripts.migrate import run as run_migrations  # noqa: E402
from scripts.setup_checkpointer import setup as setup_checkpointer  # noqa: E402

TENANT_TABLES = [
    "feedback", "lecturer_reviews", "evidence", "system_scores", "jobs", "agent_traces",
    "runs", "student_identities", "submissions", "prompt_versions", "assignments",
    "rubric_versions", "sessions", "users",
]


@pytest.fixture(scope="session", autouse=True)
def migrated():
    run_migrations(os.environ["MIGRATION_DATABASE_URL"])
    # The graph checkpoints into its own tables, which LangGraph owns rather than our migrations
    # (scripts/setup_checkpointer.py). The worker writes to them on every node transition, so a test
    # database without them would fail in a confusing place.
    setup_checkpointer(os.environ["MIGRATION_DATABASE_URL"])


@pytest.fixture(autouse=True)
def clean_db():
    with psycopg.connect(os.environ["MIGRATION_DATABASE_URL"], autocommit=True) as conn:
        conn.execute(f"truncate {', '.join(TENANT_TABLES)} cascade")
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ------------------------------------------------------- a scored batch, for every phase-4/5 test

# Every quote below appears verbatim in the fixture document, so the evidence check must locate it.
QUOTE_COGNITIVE = "COSO berfokus pada pengendalian internal"
QUOTE_METACOGNITIVE = "saya membandingkan COSO dengan ISO 31000"

ANALYSIS = (
    "Dari hasil prompt di atas, saya membandingkan COSO dengan ISO 31000 dan menemukan perbedaan fokus. "
    "COSO berfokus pada pengendalian internal, sedangkan ISO menekankan proses identifikasi risiko. "
    "Evaluasi saya, keduanya saling melengkapi dan tidak bisa dipakai sendiri-sendiri."
)

LEVELS = ["C1", "C2", "C3", "C4", "C5", "C6"]
INDICATORS = ["elaborasi", "organisasi", "orientasi", "evaluasi"]


class StubClient:
    """Returns one canned answer per schema. Counts calls so a test can prove both agents ran."""

    def __init__(self) -> None:
        self.calls: list[type] = []

    def complete_json(self, *, system, user, schema, temperature=None, seed=None):
        self.calls.append(schema)
        payload = {
            CognitiveResult: CognitiveResult(
                level="C4",
                evidence_quote=QUOTE_COGNITIVE,
                rationale="Mahasiswa menilai dua kerangka kerja dan membandingkan fokusnya.",
            ),
            MetacognitiveResult: MetacognitiveResult(
                findings=[
                    IndicatorFinding(
                        indicator="elaborasi",
                        present=True,
                        strength="kuat",
                        evidence_quote=QUOTE_METACOGNITIVE,
                        rationale="Memperluas dengan membandingkan dua kerangka kerja.",
                    ),
                    IndicatorFinding(
                        indicator="evaluasi",
                        present=True,
                        strength="sedang",
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
        # The rubric columns hold the values themselves, the shape scripts/seed_rubric.py writes:
        # `levels` is the list of level codes the cognitive agent returns.
        rubric_id = conn.execute(
            "insert into rubric_versions (owner_id, version, dimensions, levels, indicators, descriptors) "
            "values (%s, 1, %s, %s, %s, '[]'::jsonb) returning id",
            (
                user,
                json.dumps({"cognitive": "Bloom", "metacognitive": "SRL G1"}),
                json.dumps(LEVELS),
                json.dumps(INDICATORS),
            ),
        ).fetchone()[0]
        for agent in ("cognitive", "metacognitive", "synthesis"):
            conn.execute(
                "insert into prompt_versions (owner_id, agent_name, version, template) "
                "values (%s, %s, 1, %s)",
                (user, agent, "template placeholder — the real templates live in app/agents/prompts.py"),
            )
        # Shaped like the seeded row: one calibration block per analysis agent, plus the flags that
        # mark whose content it is (PRD §14).
        conn.execute(
            "insert into prompt_versions "
            "(owner_id, agent_name, version, template) values (%s, 'calibration', 1, %s)",
            (
                user,
                json.dumps(
                    {
                        "cognitive": {
                            "instructions": "kalibrasi uji",
                            "examples": [{"level": "C4", "evidence_quote": "contoh"}],
                        },
                        "metacognitive": {
                            "instructions": "kalibrasi uji",
                            "examples": [{"analisis_mhs": "contoh"}],
                        },
                        "interim": True,
                    }
                ),
            ),
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
        "submission": upload.json()["files"][0]["submission_id"],
        "pseudonym": upload.json()["files"][0]["pseudonym"],
        "csrf": client.cookies.get("ta_csrf"),
        "stub": stub,
    }


@pytest.fixture
def scored_run(seeded):
    """The `seeded` batch evaluated once. Returns the run id, so a test starts from stored scores."""
    client, csrf = seeded["client"], seeded["csrf"]
    run_id = client.post(
        f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
    ).json()["id"]
    processed = client.post(f"/runs/{run_id}/process?limit=5", headers={"X-CSRF-Token": csrf})
    assert processed.status_code == 200, processed.text
    assert processed.json()["processed"] == 1, processed.text
    return run_id
