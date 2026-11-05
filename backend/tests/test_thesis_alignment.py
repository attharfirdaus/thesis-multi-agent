"""The Bab III features added on 2026-11-03: segment scores and their aggregation, R repetitions, the
final-evaluation freeze, score comments, evaluation-set exclusion, the rater sheet, the admin area, and
the model-unavailable flag."""

import csv
import io

from conftest import INDICATORS, QUOTE_COGNITIVE, make_admin

from app import db


def _csrf(seeded) -> dict:
    return {"X-CSRF-Token": seeded["csrf"]}


def test_scores_are_stored_per_segment_and_aggregated_to_the_text(scored_run, seeded):
    """Bab III.6: one Bloom level per segment, text level = the highest; indicators per segment,
    text level = the set found in any segment."""
    with db.tenant_tx(seeded["user"]) as conn:
        cognitive = conn.execute(
            "select segment_index, level from system_scores where run_id = %s and dimension = 'cognitive' "
            "order by segment_index nulls first",
            (scored_run,),
        ).fetchall()
        meta = conn.execute(
            "select indicator, level from system_scores where run_id = %s and dimension = 'metacognitive' "
            "and segment_index is null",
            (scored_run,),
        ).fetchall()
        per_segment = conn.execute(
            "select count(*) from system_scores where run_id = %s and dimension = 'metacognitive' "
            "and segment_index is not null",
            (scored_run,),
        ).fetchone()[0]
    assert cognitive == [(None, "C4"), (1, "C2"), (2, "C4"), (3, "C3")]
    assert dict(meta) == {
        "orientasi": "absent",
        "perencanaan": "absent",
        "pemantauan": "present",
        "evaluasi": "present",
    }
    assert per_segment == 3 * len(INDICATORS)

    detail = seeded["client"].get(f"/submissions/{seeded['submission']}").json()
    assert {s["dimension"] for s in detail["scores"]} == {"cognitive", "metacognitive"}
    assert all(s.get("segment_index") is None for s in detail["scores"])
    segment_two = next(
        s for s in detail["segment_scores"] if s["dimension"] == "cognitive" and s["segment_index"] == 2
    )
    analysis = detail["student_analysis_text"]
    assert QUOTE_COGNITIVE in analysis[segment_two["segment_start"] : segment_two["segment_end"]]


def test_both_specialists_were_shown_the_ai_output(scored_run, seeded):
    """The paired input reaches the provider: the AI output is in the cognitive and the metacognitive
    agent's user turn, and the turn is recorded in the trace (KNF-04)."""
    ai_output = "COSO adalah kerangka pengendalian internal"
    assert sum(ai_output in user for user in seeded["stub"].users) >= 3  # both specialists + synthesis
    with db.tenant_tx(seeded["user"]) as conn:
        inputs = dict(
            conn.execute(
                "select agent_name, input_ref from agent_traces where run_id = %s", (scored_run,)
            ).fetchall()
        )
    assert ai_output in inputs["cognitive"] and ai_output in inputs["metacognitive"]


def test_baseline_repeated_and_final_runs_are_admin_only(seeded):
    client = seeded["client"]
    url = f"/assignments/{seeded['assignment']}/runs"
    for query in ("?mode=single_agent", "?repetitions=3", "?final=true"):
        assert client.post(url + query, headers=_csrf(seeded)).status_code == 403


def test_r_repetitions_share_one_group_and_a_final_run_freezes_its_versions(seeded):
    make_admin(seeded["user"])
    client = seeded["client"]
    created = client.post(
        f"/assignments/{seeded['assignment']}/runs?repetitions=3&final=true", headers=_csrf(seeded)
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert len(body["group_run_ids"]) == 3 and body["repetitions"] == 3 and body["final_evaluation"]

    with db.tenant_tx(seeded["user"]) as conn:
        runs = conn.execute(
            "select repetition_group, repetition_index, model_config, prompt_version_ids "
            "from runs order by repetition_index"
        ).fetchall()
        frozen_rubric = conn.execute("select frozen_at from rubric_versions").fetchone()[0]
        frozen_prompts = conn.execute(
            "select count(*) from prompt_versions where frozen_at is not null"
        ).fetchone()[0]
    assert [r[1] for r in runs] == [1, 2, 3]
    assert len({r[0] for r in runs}) == 1 and runs[0][0] is not None
    # Identical configuration across the group: the precondition of the consistency measure.
    assert len({str(r[2]) for r in runs}) == 1 and len({tuple(r[3]) for r in runs}) == 1
    assert frozen_rubric is not None and frozen_prompts == 4

    for run_id in body["group_run_ids"]:
        assert client.post(f"/runs/{run_id}/process", headers=_csrf(seeded)).json()["status"] == "done"


def test_only_the_newest_prompt_version_per_agent_is_snapshotted(seeded):
    """Two calibration rows in one run made the worker pick one arbitrarily."""
    with db.tenant_tx(seeded["user"]) as conn:
        conn.execute(
            "insert into prompt_versions (owner_id, agent_name, version, template) "
            "values (%s, 'calibration', 2, '{}')",
            (seeded["user"],),
        )
    run = seeded["client"].post(f"/assignments/{seeded['assignment']}/runs", headers=_csrf(seeded)).json()
    with db.tenant_tx(seeded["user"]) as conn:
        names = conn.execute(
            "select p.agent_name, p.version from runs r "
            "join prompt_versions p on p.id = any(r.prompt_version_ids) "
            "where r.id = %s order by p.agent_name",
            (run["id"],),
        ).fetchall()
    assert ("calibration", 2) in names and ("calibration", 1) not in names


def test_a_comment_is_kept_beside_the_review_not_instead_of_it(scored_run, seeded):
    client = seeded["client"]
    with db.tenant_tx(seeded["user"]) as conn:
        score_id = conn.execute(
            "select id from system_scores where run_id = %s and dimension = 'cognitive' "
            "and segment_index is null",
            (scored_run,),
        ).fetchone()[0]
    client.post(
        f"/system_scores/{score_id}/review",
        json={"action": "override", "new_level": "C5", "reason": "Ada penilaian."},
        headers=_csrf(seeded),
    )
    commented = client.post(
        f"/system_scores/{score_id}/comments", json={"body": "Cek lagi segmen 3."}, headers=_csrf(seeded)
    )
    assert commented.status_code == 201, commented.text

    detail = client.get(f"/submissions/{seeded['submission']}").json()
    cognitive = next(s for s in detail["scores"] if s["dimension"] == "cognitive")
    assert [c["body"] for c in cognitive["comments"]] == ["Cek lagi segmen 3."]
    assert detail["reviews"][0]["action"] == "override"

    blank = client.post(f"/system_scores/{score_id}/comments", json={"body": "  "}, headers=_csrf(seeded))
    assert blank.status_code == 422


def test_a_metacognitive_override_uses_presence_not_a_bloom_level(scored_run, seeded):
    with db.tenant_tx(seeded["user"]) as conn:
        score_id = conn.execute(
            "select id from system_scores where run_id = %s and dimension = 'metacognitive' "
            "and segment_index is null limit 1",
            (scored_run,),
        ).fetchone()[0]
    url = f"/system_scores/{score_id}/review"
    bloom = {"action": "override", "new_level": "C5", "reason": "x"}
    presence = {"action": "override", "new_level": "absent", "reason": "Tidak ada jejak."}
    assert seeded["client"].post(url, json=bloom, headers=_csrf(seeded)).status_code == 422
    assert seeded["client"].post(url, json=presence, headers=_csrf(seeded)).status_code == 201


def test_exclusion_is_recorded_and_exported_and_the_rater_sheet_lists_segments(scored_run, seeded):
    client = seeded["client"]
    patched = client.patch(
        f"/submissions/{seeded['submission']}/exclusion",
        json={"reason": "calibration_source"},
        headers=_csrf(seeded),
    )
    assert patched.json() == {"reason": "calibration_source"}
    bad = client.patch(
        f"/submissions/{seeded['submission']}/exclusion", json={"reason": "bosan"}, headers=_csrf(seeded)
    )
    assert bad.status_code == 422
    assert (
        client.get(f"/submissions/{seeded['submission']}").json()["exclusion_reason"] == "calibration_source"
    )

    assert client.get(f"/assignments/{seeded['assignment']}/segments.csv").status_code == 403
    make_admin(seeded["user"])
    research = list(
        csv.DictReader(
            io.StringIO(
                client.get(f"/assignments/{seeded['assignment']}/research-export.csv").content.decode(
                    "utf-8-sig"
                )
            )
        )
    )
    assert {row["exclusion_reason"] for row in research} == {"calibration_source"}
    segment_rows = [row for row in research if row["segment_index"]]
    assert all(row["segment_text"] for row in segment_rows)

    sheet = list(
        csv.DictReader(
            io.StringIO(
                client.get(f"/assignments/{seeded['assignment']}/segments.csv").content.decode("utf-8-sig")
            )
        )
    )
    assert [row["segment_index"] for row in sheet] == ["1", "2", "3"]
    # The rater units are exactly the units the system scored.
    scored = {(row["segment_index"], row["segment_text"]) for row in segment_rows}
    assert {(row["segment_index"], row["segment_text"]) for row in sheet} <= scored


def test_the_admin_area_is_admin_only_and_saves_rubric_versions(scored_run, seeded):
    client = seeded["client"]
    assert client.get("/admin/rubric").status_code == 403
    make_admin(seeded["user"])

    assert [u["email"] for u in client.get("/admin/users").json()] == ["runs@example.ac.id"]
    config = client.get("/admin/config").json()
    assert "api_key" not in config["llm"] and config["prompt_versions"]
    runs = client.get("/admin/runs").json()
    assert runs[0]["id"] == scored_run
    traces = client.get(f"/admin/runs/{scored_run}/traces").json()
    assert {t["agent_name"] for t in traces} == {"cognitive", "metacognitive", "synthesis"}

    saved = client.post(
        "/admin/rubric",
        json={
            "levels": ["C1", "C2"],
            "indicators": ["orientasi"],
            "descriptors": {"levels": {"C1": "Ingat"}},
        },
        headers=_csrf(seeded),
    )
    assert saved.status_code == 201, saved.text
    assert saved.json()["version"] == 2
    with db.tenant_tx(seeded["user"]) as conn:
        pinned = conn.execute(
            "select rv.version from assignments a join rubric_versions rv on rv.id = a.rubric_version_id"
        ).fetchone()[0]
        old_run = conn.execute(
            "select rv.version from runs r join rubric_versions rv on rv.id = r.rubric_version_id "
            "where r.id = %s",
            (scored_run,),
        ).fetchone()[0]
    assert pinned == 2 and old_run == 1


def test_a_run_whose_model_changed_is_flagged_not_silently_rescored(seeded, monkeypatch):
    """KNF-04: the run snapshotted one model; if another is configured now, the run is marked."""
    client = seeded["client"]
    run_id = client.post(f"/assignments/{seeded['assignment']}/runs", headers=_csrf(seeded)).json()["id"]
    with db.tenant_tx(seeded["user"]) as conn:
        conn.execute(
            'update runs set model_config = model_config || \'{"model": "model-lama"}\' where id = %s',
            (run_id,),
        )
    monkeypatch.setenv("LLM_MODEL", "model-baru")
    from app.config import get_settings

    get_settings.cache_clear()
    try:
        client.post(f"/runs/{run_id}/process", headers=_csrf(seeded))
    finally:
        # Back to the conftest's forced blank, never unset: unset falls through to backend/.env.
        monkeypatch.setenv("LLM_MODEL", "")
        get_settings.cache_clear()

    run = client.get(f"/runs/{run_id}").json()
    assert run["model_unavailable"] is True
    assert run["jobs"] == {"failed": 1}
    with db.tenant_tx(seeded["user"]) as conn:
        assert (
            conn.execute("select count(*) from system_scores where run_id = %s", (run_id,)).fetchone()[0] == 0
        )
