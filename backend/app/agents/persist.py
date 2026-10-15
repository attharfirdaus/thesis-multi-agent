"""Persist one submission's pipeline result (PRD §10).

Input is a finished `GraphState`; output is rows. Kept out of the graph on purpose: a graph node that
writes to Postgres is a node that cannot be tested without a database, and PRD §6 asks for the graph
to be inspectable, not for it to own storage.

Idempotent per (run, submission): earlier rows for that pair are deleted first, so re-running a
submission after a correction or an interruption replaces its result instead of duplicating it.
`Evidence` cascades from `SystemScore`; `Feedback` is per submission.

One honest limitation: `Evidence.system_score_id` is not nullable, so a quote is only stored when it
belongs to a score. Synthesis produces no quote at all — its output *is* the explanation
(`SystemScore.rationale`) and the per-student feedback (`Feedback`), which is why `EvidenceSpan.source`
admits only the two scoring agents.
"""

from uuid import UUID

from psycopg.types.json import Jsonb

from app.agents.models import GraphState, MetacognitiveResult, SynthesisResult

NEEDS_REVIEW = "needs_review"


def _strength_label(present: bool, strength: str | None) -> str:
    """Map a finding onto the `SystemScore.level` column without inventing a scale.

    FR-08 asks for per-indicator presence and strength, and `strength` is already low/medium/high in
    the agent's schema, so absence is expressed as `absent` and nothing new is introduced.
    """
    if not present:
        return "absent"
    return strength or "present"


def persist_submission_result(
    conn,
    *,
    owner_id: UUID,
    run_id: UUID,
    submission_id: UUID,
    state: GraphState,
) -> dict[str, int]:
    """Write traces, scores, evidence, feedback and review flags. Returns counts for the summary."""
    cognitive = state.get("cognitive")
    metacognitive = state.get("metacognitive")
    synthesis = state.get("synthesis")
    latencies = state.get("latencies", {})
    spans = list(state.get("evidence", []))
    by_source: dict[str, list] = {}
    for span in spans:
        by_source.setdefault(span.source, []).append(span)

    counts = {"traces": 0, "scores": 0, "evidence": 0}

    with conn.cursor() as cur:
        cur.execute("delete from feedback where submission_id = %s", (submission_id,))
        cur.execute(
            "delete from system_scores where run_id = %s and submission_id = %s",
            (run_id, submission_id),
        )
        cur.execute(
            "delete from agent_traces where run_id = %s and submission_id = %s",
            (run_id, submission_id),
        )

        for agent, payload in (
            ("cognitive", cognitive),
            ("metacognitive", metacognitive),
            ("synthesis", synthesis),
        ):
            cur.execute(
                "insert into agent_traces "
                "(owner_id, run_id, submission_id, agent_name, output_json, latency_ms, error) "
                "values (%s, %s, %s, %s, %s, %s, %s)",
                (
                    owner_id,
                    run_id,
                    submission_id,
                    agent,
                    None if payload is None else Jsonb(payload.model_dump(mode="json")),
                    # The client's own measurement, carried in the state (PRD §10 AgentTrace): a free
                    # provider's latency is the app's evidence for the performance target in PRD §11.
                    latencies.get(agent),
                    None if payload is not None else "agent did not produce output",
                ),
            )
            counts["traces"] += 1

        if cognitive is not None:
            score_id = cur.execute(
                "insert into system_scores (owner_id, run_id, submission_id, dimension, level, rationale, "
                "explanation_type) values (%s, %s, %s, 'cognitive', %s, %s, 'evidence_span') returning id",
                (owner_id, run_id, submission_id, cognitive.level, cognitive.rationale),
            ).fetchone()[0]
            counts["scores"] += 1
            for span in by_source.get("cognitive", []):
                cur.execute(
                    "insert into evidence (owner_id, system_score_id, start_offset, end_offset, quote) "
                    "values (%s, %s, %s, %s, %s)",
                    (owner_id, score_id, span.start_offset, span.end_offset, span.quote),
                )
                counts["evidence"] += 1

        if isinstance(metacognitive, MetacognitiveResult):
            for finding in metacognitive.findings:
                score_id = cur.execute(
                    "insert into system_scores (owner_id, run_id, submission_id, dimension, "
                    "indicator, level, rationale, explanation_type) "
                    "values (%s, %s, %s, 'metacognitive', %s, %s, %s, 'evidence_span') returning id",
                    (
                        owner_id,
                        run_id,
                        submission_id,
                        finding.indicator,
                        _strength_label(finding.present, finding.strength),
                        finding.rationale,
                    ),
                ).fetchone()[0]
                counts["scores"] += 1
                # Match a quote to the indicator that produced it: several indicators may quote the
                # same passage, and attaching them all to one score would misattribute the evidence.
                if finding.present and finding.evidence_quote:
                    for span in by_source.get("metacognitive", []):
                        if span.quote == finding.evidence_quote:
                            cur.execute(
                                "insert into evidence "
                                "(owner_id, system_score_id, start_offset, end_offset, quote) "
                                "values (%s, %s, %s, %s, %s)",
                                (owner_id, score_id, span.start_offset, span.end_offset, span.quote),
                            )
                            counts["evidence"] += 1

        if isinstance(synthesis, SynthesisResult):
            cur.execute(
                "insert into feedback (owner_id, submission_id, generated_text) values (%s, %s, %s)",
                (owner_id, submission_id, synthesis.feedback_text),
            )
            # The synthesis rationale is NOT copied onto a score: a score's rationale belongs to the
            # agent that produced the score (FR-14), and the synthesis agent explains the submission as
            # a whole. It is already persisted verbatim in its AgentTrace row, which is where the
            # submission detail view reads it from.

        flags = list(state.get("flags", []))
        cur.execute(
            "update submissions set review_flags = %s where id = %s",
            (Jsonb(flags), submission_id),
        )

    return {
        **counts,
        "needs_review": int(NEEDS_REVIEW in state.get("flags", [])),
        "unlocated_quotes": len(state.get("evidence_failures", [])),
    }
