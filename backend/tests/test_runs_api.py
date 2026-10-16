"""Phase-4 gate: one batch evaluates end to end, with evidence and an explanation per score.

Only the provider is stubbed — the real one needs an API key that is not in the repository and CI has
no network. Everything else is the real thing: the ingest API, the Postgres queue, the LangGraph graph
with its parallel agents and rule-based evidence check, persistence, and the results endpoint.

The decisive assertion is not "a score exists" but "the stored evidence offsets slice exactly the
quote out of the stored text", because that is what makes a score traceable to the student's own words
(PRD §2, FR-10).

The `seeded` batch itself lives in `conftest.py`: phase 5's lecturer-UI tests score the same way.
"""

from conftest import INDICATORS, QUOTE_COGNITIVE, StubClient, build_submission_docx

from app import db
from app.agents.models import CognitiveResult, MetacognitiveResult
from app.jobs.queue import claim_jobs


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
    assert cognitive["level"] == "C4"
    assert cognitive["rationale"]

    indicators = {s["indicator"]: s for s in submission["scores"] if s["dimension"] == "metacognitive"}
    assert set(indicators) == set(INDICATORS)
    assert indicators["elaborasi"]["level"] == "kuat"
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

    # PRD §10 keeps a latency per trace. It was null in every row until the state carried the client's
    # own measurement, which is the app's evidence for the PRD §11 performance target.
    with db.tenant_tx(seeded["user"]) as conn:
        traces = conn.execute(
            "select agent_name, latency_ms from agent_traces where run_id = %s", (run_id,)
        ).fetchall()
    assert {name for name, _ in traces} == {"cognitive", "metacognitive", "synthesis"}, traces
    assert {latency for _, latency in traces} == {7}, traces


def test_a_new_run_does_not_inherit_the_previous_run_s_flags(seeded, monkeypatch):
    """A completed run leaves a checkpoint behind, and `flags` merges.

    The checkpointer's thread used to be the submission id, so a second run of the same submission resumed
    the first run's channels instead of starting clean: a `cognitive_agent_failed` from a run whose call
    timed out stuck to a submission the next run scored fine, and the lecturer kept reading "Perlu ditinjau
    dosen" next to a score that existed (seen live, 2026-10-16).
    """
    client, csrf = seeded["client"], seeded["csrf"]
    import app.agents.graph as graph_module

    def evaluate_with(stub):
        def run(state, checkpointer=None):
            return graph_module.evaluate_submission(state, client=stub, checkpointer=checkpointer)

        return run

    def start_run() -> str:
        return client.post(
            f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
        ).json()["id"]

    monkeypatch.setattr(
        "app.jobs.worker.evaluate_submission", evaluate_with(_CognitiveFails(StubClient()))
    )
    first = start_run()
    client.post(f"/runs/{first}/process?limit=5", headers={"X-CSRF-Token": csrf})
    with db.tenant_tx(seeded["user"]) as conn:
        assert conn.execute("select review_flags from submissions").fetchone()[0] == [
            "cognitive_agent_failed"
        ]

    monkeypatch.setattr("app.jobs.worker.evaluate_submission", evaluate_with(StubClient()))
    second = start_run()
    client.post(f"/runs/{second}/process?limit=5", headers={"X-CSRF-Token": csrf})

    with db.tenant_tx(seeded["user"]) as conn:
        flags = conn.execute("select review_flags from submissions").fetchone()[0]
        scores = conn.execute(
            "select count(*) from system_scores where run_id = %s", (second,)
        ).fetchone()[0]
    assert scores > 0, "the second run must actually have scored, or this proves nothing"
    assert flags == [], f"a run that scored every dimension must not inherit an old failure: {flags}"


class _CognitiveFails:
    """The canned answers, except the cognitive call, which fails like a dead provider."""

    def __init__(self, inner) -> None:
        self.inner = inner

    def complete_json(self, *, system, user, schema, temperature=None, seed=None):
        if schema is CognitiveResult:
            raise RuntimeError("provider unreachable")
        return self.inner.complete_json(system=system, user=user, schema=schema)


def _score_the_batch(seeded) -> str:
    """Create a run over the assignment and process it, so its submissions carry scores."""
    client, csrf = seeded["client"], seeded["csrf"]
    run_id = client.post(
        f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
    ).json()["id"]
    client.post(f"/runs/{run_id}/process?limit=10", headers={"X-CSRF-Token": csrf})
    return run_id


def _upload_one_more(client, csrf: str, assignment: str) -> str:
    """Upload a second submission through the ingest API and return its id."""
    response = client.post(
        f"/assignments/{assignment}/submissions",
        files=[
            (
                "files",
                (
                    "Tugas 2_Budi Santoso.docx",
                    build_submission_docx(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
            )
        ],
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 201, response.text
    return response.json()["files"][0]["submission_id"]


def test_only_ungraded_leaves_the_graded_submissions_alone(seeded):
    """The lecturer's "grade what is new" choice.

    A new batch of uploads must not re-grade everything already marked: that is provider quota and time
    spent on scores that already exist. Measured at ~15 s per submission, so the difference is real.
    """
    client, csrf = seeded["client"], seeded["csrf"]
    _score_the_batch(seeded)  # the seeded submission now has scores

    with db.tenant_tx(seeded["user"]) as conn:
        assert conn.execute("select count(*) from system_scores").fetchone()[0] > 0

    # The default is unchanged: it still covers every submission, which PRD §11's variance measurement
    # needs. Only the explicit choice skips the graded ones.
    everything = client.post(
        f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
    ).json()
    assert everything["jobs"] == {"queued": 1}

    refused = client.post(
        f"/assignments/{seeded['assignment']}/runs?only_ungraded=true", headers={"X-CSRF-Token": csrf}
    )
    assert refused.status_code == 409, refused.text
    assert refused.json()["detail"] == "Every submission in this assignment has already been graded."


def test_only_ungraded_queues_the_submissions_that_have_no_scores(seeded):
    client, csrf = seeded["client"], seeded["csrf"]
    _score_the_batch(seeded)  # scores the seeded submission
    extra = _upload_one_more(client, csrf, seeded["assignment"])

    run = client.post(
        f"/assignments/{seeded['assignment']}/runs?only_ungraded=true", headers={"X-CSRF-Token": csrf}
    )
    assert run.status_code == 201, run.text
    assert run.json()["jobs"] == {"queued": 1}, "only the new submission is queued"

    with db.tenant_tx(seeded["user"]) as conn:
        queued = conn.execute(
            "select submission_id from jobs where run_id = %s", (run.json()["id"],)
        ).fetchall()
    assert [str(row[0]) for row in queued] == [str(extra)]

    detail = client.get(f"/assignments/{seeded['assignment']}").json()
    assert (detail["submission_count"], detail["graded_count"]) == (2, 1)


def test_run_status_reports_job_counts(seeded):
    client, csrf = seeded["client"], seeded["csrf"]
    run_id = client.post(
        f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
    ).json()["id"]

    before = client.get(f"/runs/{run_id}").json()
    assert before["jobs"] == {"queued": 1}
    assert before["status"] == "queued"
    assert before["in_flight"] == [], "nothing is being graded yet"

    client.post(f"/runs/{run_id}/process?limit=5", headers={"X-CSRF-Token": csrf})
    after = client.get(f"/runs/{run_id}").json()
    assert after["jobs"] == {"done": 1}
    assert after["status"] == "done"


def test_cancel_reports_what_is_still_in_flight_instead_of_pretending_it_stopped(seeded):
    """Cancel stops the *queue*, not the process.

    A submission already claimed is being graded by a request the server cannot recall, and it will still
    store its scores; the response says so, with the submission named, rather than reporting a clean stop
    the user would then see contradicted by new scores appearing.
    """
    client, csrf = seeded["client"], seeded["csrf"]
    run_id = client.post(
        f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
    ).json()["id"]
    # Claim it the way the worker does, so the job is genuinely `running` and the API is not being told a
    # story: `in_flight` has to come from the queue's own state.
    with db.tenant_tx(seeded["user"]) as conn:
        claimed = claim_jobs(conn, owner_id=seeded["user"], run_id=run_id, limit=10)
    assert len(claimed) == 1

    running = client.get(f"/runs/{run_id}").json()
    assert [entry["pseudonym"] for entry in running["in_flight"]] == [seeded["pseudonym"]]
    assert running["in_flight"][0]["submission_id"] == str(seeded["submission"])

    body = client.post(f"/runs/{run_id}/cancel", headers={"X-CSRF-Token": csrf}).json()
    assert body["status"] == "cancelled"
    assert body["jobs"] == {"running": 1}
    assert [entry["pseudonym"] for entry in body["in_flight"]] == [seeded["pseudonym"]]


def test_a_cancelled_run_is_not_resurrected_by_the_next_pass(seeded):
    client, csrf = seeded["client"], seeded["csrf"]
    run_id = client.post(
        f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
    ).json()["id"]

    cancelled = client.post(f"/runs/{run_id}/cancel", headers={"X-CSRF-Token": csrf}).json()
    assert cancelled["status"] == "cancelled"
    assert cancelled["jobs"] == {"cancelled": 1}

    # The pass must neither claim the cancelled job nor relabel the run as running or done.
    after = client.post(f"/runs/{run_id}/process?limit=5", headers={"X-CSRF-Token": csrf}).json()
    assert after["status"] == "cancelled"
    assert after["jobs"] == {"cancelled": 1}
    assert after["processed"] == 0


def test_a_finished_run_cannot_be_cancelled_and_mislabelled(seeded):
    """`done` and `cancelled` mean different things to the thesis: one is a completed evaluation, the
    other a stopped queue, and a cancel must not be able to rewrite the first as the second."""
    client, csrf = seeded["client"], seeded["csrf"]
    run_id = client.post(
        f"/assignments/{seeded['assignment']}/runs", headers={"X-CSRF-Token": csrf}
    ).json()["id"]
    client.post(f"/runs/{run_id}/process?limit=5", headers={"X-CSRF-Token": csrf})

    response = client.post(f"/runs/{run_id}/cancel", headers={"X-CSRF-Token": csrf})
    assert response.status_code == 409, response.text
    assert client.get(f"/runs/{run_id}").json()["status"] == "done"
