"""Phase-4 acceptance for the queue and the runner: enqueue, exclusive claim, tenancy, retry.

These run against the real test database, because everything worth checking here is what Postgres
does — row-level security refusing another tenant's rows, `FOR UPDATE SKIP LOCKED` handing a job to
one claimant, and `attempts` reaching the cap in the right order. The graph is stubbed: it is
phase 4's other half and its own tests cover it, while the behaviour under test is what the worker
records when it succeeds or raises.

The rubric and prompt rows below are fixtures of the interim seed, not rubric content: no level,
indicator or descriptor is decided here.
"""

import json
import uuid

import pytest
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app import db
from app.agents.models import CognitiveResult
from app.jobs import worker
from app.jobs.queue import claim_jobs, enqueue_run

# A graph that produced nothing is not a successful evaluation — the worker refuses to mark it done
# (see the guard test at the end of this file). The stubs therefore return a state that looks like a
# real one: at least one agent produced a result.
OK_COGNITIVE = CognitiveResult(
    level="Memahami",
    evidence_quote="kutipan contoh yang cukup panjang",
    rationale="alasan contoh yang cukup panjang",
)

ANALYSIS = "Menurut analisis saya, hasil tersebut belum membahas risiko residual, jadi perlu diuji ulang."
AI_OUTPUT = "COSO adalah kerangka manajemen risiko yang menekankan pengendalian internal."
CALIBRATION = {
    "cognitive": {"instructions": "uji", "examples": [{"level": "C4", "evidence_quote": ANALYSIS}]},
    "metacognitive": {"instructions": "uji", "examples": [{"analisis_mhs": ANALYSIS}]},
}
# The codes the interim seed writes, quoted from the seed's contract; the tests only need the
# rubric dict to be non-empty, and nothing here may become rubric content for the thesis.
LEVELS = ["C1", "C2", "C3", "C4", "C5", "C6"]
INDICATORS = ["elaborasi", "organisasi", "orientasi", "evaluasi"]


@pytest.fixture(autouse=True)
def pool():
    """The API opens the pool in its lifespan; these tests drive the queue without a request."""
    db.open_pool()
    yield
    db.close_pool()


def make_lecturer(submissions: int = 3, *, rubric: bool = True, calibration: bool = True) -> dict:
    """A lecturer holding an assignment, N redacted submissions and one run with a frozen rubric."""
    owner, assignment, run = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    ids = [uuid.uuid4() for _ in range(submissions)]
    with db.plain_tx() as conn:
        conn.execute(
            "insert into users (id, email, name, password_hash) values (%s, %s, 'Dosen', 'x')",
            (owner, f"job-{owner}@example.ac.id"),
        )
    with db.tenant_tx(owner) as conn, conn.cursor() as cur:
        cur.execute(
            "insert into assignments (id, owner_id, title, course) values (%s, %s, 'Tugas', 'MRTI')",
            (assignment, owner),
        )
        for submission in ids:
            cur.execute(
                "insert into submissions (id, owner_id, assignment_id, pseudonym,"
                " student_analysis_text, ai_output_text) values (%s, %s, %s, 'P-01', %s, %s)",
                (submission, owner, assignment, ANALYSIS, AI_OUTPUT),
            )
        cur.execute(
            "insert into runs (id, owner_id, assignment_id, mode) values (%s, %s, %s, 'multi_agent')",
            (run, owner, assignment),
        )
        if rubric:
            version = uuid.uuid4()
            cur.execute(
                "insert into rubric_versions (id, owner_id, version, dimensions, levels, indicators,"
                " descriptors) values (%s, %s, 1, %s, %s, %s, '{}'::jsonb)",
                (version, owner, Jsonb({"cognitive": "Bloom"}), Jsonb(LEVELS), Jsonb(INDICATORS)),
            )
            # The run snapshots a row per agent, as the seeder does; only the calibration row is read
            # back, so the others are here to prove an unknown agent name is carried, not consulted.
            versions = [
                ("cognitive", "templat kognitif"),
                ("metacognitive", "templat metakognitif"),
                ("synthesis", "templat sintesis"),
            ]
            if calibration:
                versions.insert(0, ("calibration", json.dumps(CALIBRATION)))
            prompt_ids = []
            for agent, template in versions:
                prompt_id = uuid.uuid4()
                prompt_ids.append(prompt_id)
                cur.execute(
                    "insert into prompt_versions (id, owner_id, agent_name, version, template)"
                    " values (%s, %s, %s, 1, %s)",
                    (prompt_id, owner, agent, template),
                )
            cur.execute(
                "update runs set rubric_version_id = %s, prompt_version_ids = %s where id = %s",
                (version, prompt_ids, run),
            )
    return {"owner": owner, "run": run, "submissions": ids, "assignment": assignment}


def job_rows(owner: uuid.UUID, run: uuid.UUID) -> list[dict]:
    with db.tenant_tx(owner) as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("select * from jobs where run_id = %s order by created_at", (run,))
        return cur.fetchall()


def stub_graph(
    monkeypatch,
    run=lambda state: {"submission_id": state["submission_id"], "cognitive": OK_COGNITIVE},
) -> list:
    """Replace the graph with `run`, returning the states it was given."""
    seen: list = []

    def fake(state, checkpointer=None):
        seen.append(state)
        return run(state)

    monkeypatch.setattr(worker, "evaluate_submission", fake)
    return seen


def test_enqueue_creates_one_job_per_submission():
    lecturer = make_lecturer(3)
    with db.tenant_tx(lecturer["owner"]) as conn:
        assert (
            enqueue_run(
                conn,
                owner_id=lecturer["owner"],
                run_id=lecturer["run"],
                submission_ids=lecturer["submissions"],
            )
            == 3
        )
    jobs = job_rows(lecturer["owner"], lecturer["run"])
    assert len(jobs) == 3
    assert {job["submission_id"] for job in jobs} == set(lecturer["submissions"])
    assert {(job["status"], job["attempts"]) for job in jobs} == {("queued", 0)}


def test_enqueue_with_no_submissions_queues_nothing():
    lecturer = make_lecturer(0)
    with db.tenant_tx(lecturer["owner"]) as conn:
        assert enqueue_run(conn, owner_id=lecturer["owner"], run_id=lecturer["run"], submission_ids=[]) == 0
    assert job_rows(lecturer["owner"], lecturer["run"]) == []


def test_claim_respects_the_limit_and_never_reaches_another_tenant():
    mine, theirs = make_lecturer(3), make_lecturer(3)
    for lecturer in (mine, theirs):
        with db.tenant_tx(lecturer["owner"]) as conn:
            enqueue_run(
                conn,
                owner_id=lecturer["owner"],
                run_id=lecturer["run"],
                submission_ids=lecturer["submissions"],
            )

    with db.tenant_tx(mine["owner"]) as conn:
        claimed = claim_jobs(conn, owner_id=mine["owner"], run_id=mine["run"], limit=2)
        assert len(claimed) == 2
        assert {job["run_id"] for job in claimed} == {mine["run"]}
        assert [job["attempts"] for job in claimed] == [0, 0]
        assert claim_jobs(conn, owner_id=mine["owner"], run_id=mine["run"], limit=0) == []

    assert [job["status"] for job in job_rows(theirs["owner"], theirs["run"])] == ["queued"] * 3
    assert [job["status"] for job in job_rows(mine["owner"], mine["run"])] == ["running"] * 2 + ["queued"]

    with db.tenant_tx(mine["owner"]) as conn:
        assert len(claim_jobs(conn, owner_id=mine["owner"], run_id=mine["run"], limit=10)) == 1


def test_a_claim_never_reaches_another_run_of_the_same_owner():
    """Two runs of one lecturer are two separate units of evidence.

    The caller persists the states it claimed under the run it asked about, so claiming the other
    run's job would file one run's scores under another run's rubric, prompts and model snapshot.
    That happened live on 2026-10-16, while the claim was owner-scoped.
    """
    lecturer = make_lecturer(1)
    second = uuid.uuid4()
    with db.tenant_tx(lecturer["owner"]) as conn, conn.cursor() as cur:
        cur.execute(
            "insert into runs (id, owner_id, assignment_id, mode) values (%s, %s, %s, 'multi_agent')",
            (second, lecturer["owner"], lecturer["assignment"]),
        )
    for run in (lecturer["run"], second):
        with db.tenant_tx(lecturer["owner"]) as conn:
            enqueue_run(
                conn,
                owner_id=lecturer["owner"],
                run_id=run,
                submission_ids=lecturer["submissions"],
            )

    with db.tenant_tx(lecturer["owner"]) as conn:
        claimed = claim_jobs(conn, owner_id=lecturer["owner"], run_id=lecturer["run"], limit=10)

    assert [job["run_id"] for job in claimed] == [lecturer["run"]]
    assert [job["status"] for job in job_rows(lecturer["owner"], second)] == ["queued"]


def test_a_claimed_job_is_not_claimed_twice():
    lecturer = make_lecturer(2)
    with db.tenant_tx(lecturer["owner"]) as conn:
        enqueue_run(
            conn,
            owner_id=lecturer["owner"],
            run_id=lecturer["run"],
            submission_ids=lecturer["submissions"],
        )
    with db.tenant_tx(lecturer["owner"]) as conn:
        first = claim_jobs(conn, owner_id=lecturer["owner"], run_id=lecturer["run"], limit=10)
    with db.tenant_tx(lecturer["owner"]) as conn:
        assert claim_jobs(conn, owner_id=lecturer["owner"], run_id=lecturer["run"], limit=10) == []
    assert len(first) == 2


def test_a_failing_graph_counts_attempts_and_fails_at_the_cap(monkeypatch):
    lecturer = make_lecturer(1)
    with db.tenant_tx(lecturer["owner"]) as conn:
        enqueue_run(
            conn,
            owner_id=lecturer["owner"],
            run_id=lecturer["run"],
            submission_ids=lecturer["submissions"],
        )

    def explode(_state):
        raise ValueError("model mengembalikan JSON yang tidak valid")

    stub_graph(monkeypatch, explode)

    expected = [(1, "queued", "skipped"), (2, "queued", "skipped"), (3, "failed", "failed")]
    for attempt, status, bucket in expected:
        summary = worker.process_run(lecturer["owner"], lecturer["run"])
        assert summary["claimed"] == 1
        assert summary[bucket] == 1
        assert summary["states"] == []
        job = job_rows(lecturer["owner"], lecturer["run"])[0]
        assert (job["attempts"], job["status"]) == (attempt, status)
        assert job["last_error"].startswith("ValueError: model mengembalikan JSON")

    # Out of retries: the job is not claimed again, so a dead provider cannot burn the batch twice.
    assert worker.process_run(lecturer["owner"], lecturer["run"])["claimed"] == 0
    assert job_rows(lecturer["owner"], lecturer["run"])[0]["attempts"] == worker.MAX_ATTEMPTS


def test_summary_counts_a_mixed_batch(monkeypatch):
    lecturer = make_lecturer(3)
    with db.tenant_tx(lecturer["owner"]) as conn:
        enqueue_run(
            conn,
            owner_id=lecturer["owner"],
            run_id=lecturer["run"],
            submission_ids=lecturer["submissions"],
        )
    broken = str(lecturer["submissions"][0])

    def sometimes_explodes(state):
        if state["submission_id"] == broken:
            raise RuntimeError("provider tidak terjangkau")
        return {"submission_id": state["submission_id"], "cognitive": OK_COGNITIVE}

    seen = stub_graph(monkeypatch, sometimes_explodes)

    summary = worker.process_run(lecturer["owner"], lecturer["run"])

    assert {key: summary[key] for key in ("claimed", "done", "failed", "skipped")} == {
        "claimed": 3,
        "done": 2,
        "failed": 0,
        "skipped": 1,
    }
    # The graph got the redacted text and the run's frozen rubric and prompts, not the newest ones.
    assert len(seen) == 3
    assert all(state["student_analysis_text"] == ANALYSIS for state in seen)
    assert all(
        sorted(state["rubric"]) == ["descriptors", "dimensions", "indicators", "levels", "version"]
        for state in seen
    )
    assert all(state["prompts"] == {"calibration": CALIBRATION} for state in seen)
    assert {state["submission_id"] for state in summary["states"]} == {
        str(submission) for submission in lecturer["submissions"][1:]
    }
    assert [job["status"] for job in job_rows(lecturer["owner"], lecturer["run"])] == [
        "queued",
        "done",
        "done",
    ]


def test_process_run_resumes_jobs_left_running_by_a_crash(monkeypatch):
    lecturer = make_lecturer(2)
    with db.tenant_tx(lecturer["owner"]) as conn:
        enqueue_run(
            conn,
            owner_id=lecturer["owner"],
            run_id=lecturer["run"],
            submission_ids=lecturer["submissions"],
        )
    # What a process killed between the claim and the outcome leaves behind.
    with db.tenant_tx(lecturer["owner"]) as conn:
        assert len(claim_jobs(conn, owner_id=lecturer["owner"], run_id=lecturer["run"], limit=1)) == 1
    stub_graph(monkeypatch)

    summary = worker.process_run(lecturer["owner"], lecturer["run"], limit=1)

    assert {key: summary[key] for key in ("claimed", "done", "failed", "skipped")} == {
        "claimed": 1,
        "done": 1,
        "failed": 0,
        "skipped": 0,
    }
    assert [job["status"] for job in job_rows(lecturer["owner"], lecturer["run"])] == ["done", "queued"]


def test_a_run_records_when_it_started_and_keeps_that_moment(monkeypatch):
    """FR-13 keeps the run's timestamps, and `runs.started_at` was written by nobody until this."""
    lecturer = make_lecturer(1)
    with db.tenant_tx(lecturer["owner"]) as conn:
        enqueue_run(
            conn,
            owner_id=lecturer["owner"],
            run_id=lecturer["run"],
            submission_ids=lecturer["submissions"],
        )
        queued = conn.execute(
            "select started_at from runs where id = %s", (lecturer["run"],)
        ).fetchone()[0]
    assert queued is None, "a run that is only queued has not started"

    stub_graph(monkeypatch)
    worker.process_run(lecturer["owner"], lecturer["run"])
    with db.tenant_tx(lecturer["owner"]) as conn:
        first = conn.execute(
            "select started_at from runs where id = %s", (lecturer["run"],)
        ).fetchone()[0]
    assert first is not None
    with db.tenant_tx(lecturer["owner"]) as conn:
        status = conn.execute(
            "select status from runs where id = %s", (lecturer["run"],)
        ).fetchone()[0]
    assert status == "done", "a pass that finished every job has finished the run, whoever drove it"

    # A second pass finds nothing left to claim: it must not move the moment work began.
    worker.process_run(lecturer["owner"], lecturer["run"])
    with db.tenant_tx(lecturer["owner"]) as conn:
        again = conn.execute(
            "select started_at from runs where id = %s", (lecturer["run"],)
        ).fetchone()[0]
    assert again == first


def test_a_run_without_calibration_reaches_the_graph_as_an_empty_block(monkeypatch):
    """Passed through empty on purpose: the builders refuse an uncalibrated agent (PRD §6), so
    their refusal is the failure the job records rather than an example this loader invents."""
    lecturer = make_lecturer(1, calibration=False)
    with db.tenant_tx(lecturer["owner"]) as conn:
        enqueue_run(
            conn,
            owner_id=lecturer["owner"],
            run_id=lecturer["run"],
            submission_ids=lecturer["submissions"],
        )
    seen = stub_graph(monkeypatch)

    worker.process_run(lecturer["owner"], lecturer["run"])

    assert [state["prompts"] for state in seen] == [{"calibration": {}}]


def test_a_run_without_a_rubric_fails_its_jobs_without_calling_the_graph(monkeypatch):
    lecturer = make_lecturer(1, rubric=False)
    with db.tenant_tx(lecturer["owner"]) as conn:
        enqueue_run(
            conn,
            owner_id=lecturer["owner"],
            run_id=lecturer["run"],
            submission_ids=lecturer["submissions"],
        )
    seen = stub_graph(monkeypatch)

    summary = worker.process_run(lecturer["owner"], lecturer["run"])

    assert summary["skipped"] == 1
    assert seen == []
    assert job_rows(lecturer["owner"], lecturer["run"])[0]["last_error"].startswith("LookupError: run")


def test_a_graph_that_produced_nothing_is_not_recorded_as_done(monkeypatch):
    """The guard that keeps a silently broken pipeline from looking evaluated.

    Before it existed, a KeyError inside a prompt builder made all three agents fail, the job was
    marked `done`, and the submission appeared evaluated while carrying zero scores. A state with no
    agent output must therefore cost an attempt rather than count as success.
    """
    lecturer = make_lecturer(1)
    with db.tenant_tx(lecturer["owner"]) as conn:
        enqueue_run(
            conn,
            owner_id=lecturer["owner"],
            run_id=lecturer["run"],
            submission_ids=lecturer["submissions"],
        )
    stub_graph(monkeypatch, lambda state: {"submission_id": state["submission_id"], "errors": ["boom"]})

    summary = worker.process_run(lecturer["owner"], lecturer["run"])

    assert {key: summary[key] for key in ("claimed", "done", "failed", "skipped")} == {
        "claimed": 1,
        "done": 0,
        "failed": 0,
        "skipped": 1,
    }
    job = job_rows(lecturer["owner"], lecturer["run"])[0]
    assert job["status"] == "queued", "a first failure is retryable, not terminal"
    assert "no agent produced output" in (job["last_error"] or "")
    assert "boom" in (job["last_error"] or "")
