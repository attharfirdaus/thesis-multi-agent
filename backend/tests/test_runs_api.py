"""Phase-4 gate: one batch evaluates end to end, with evidence and an explanation per score.

Only the provider is stubbed — the real one needs an API key that is not in the repository and CI has
no network. Everything else is the real thing: the ingest API, the Postgres queue, the LangGraph graph
with its parallel agents and rule-based evidence check, persistence, and the results endpoint.

The decisive assertion is not "a score exists" but "the stored evidence offsets slice exactly the
quote out of the stored text", because that is what makes a score traceable to the student's own words
(PRD §2, FR-10).

The `seeded` batch itself lives in `conftest.py`: phase 5's lecturer-UI tests score the same way.
"""

from conftest import INDICATORS, QUOTE_COGNITIVE

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
