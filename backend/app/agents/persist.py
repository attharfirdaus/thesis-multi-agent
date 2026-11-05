"""Persist one submission's pipeline result (PRD §10).

Input is a finished `GraphState`; output is rows. Kept out of the graph on purpose: a graph node that
writes to Postgres is a node that cannot be tested without a database, and PRD §6 asks for the graph
to be inspectable, not for it to own storage.

Idempotent per (run, submission): earlier rows for that pair are deleted first, so re-running a
submission after a correction or an interruption replaces its result instead of duplicating it.
`Evidence` cascades from `SystemScore`; `Feedback` is per submission.

Scores are written at two grains (Bab III.6, Bab I.3 luaran 4): one row per segment and label, and the
text-level rows derived from them — the highest Bloom level over the segments with the spread of segments
over the level groups, and for every indicator whether any segment shows it. The text-level rows
(`segment_index` null) are what the lecturer reviews; the segment rows are what the expert raters' labels
are compared with.

One honest limitation: `Evidence.system_score_id` is not nullable, so a quote is only stored when it
belongs to a score. Synthesis produces no quote at all — its output *is* the explanation
(`SystemScore.rationale`) and the per-student feedback (`Feedback`), which is why `EvidenceSpan.source`
admits only the two scoring agents.
"""

from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb
from pydantic import BaseModel

from app.agents.models import EvidenceSpan, GraphState, SynthesisResult
from app.agents.segments import Segment, distribution, highest_level

NEEDS_REVIEW = "needs_review"
PRESENT, ABSENT = "present", "absent"


def _insert_score(
    cur,
    *,
    owner_id: UUID,
    run_id: UUID,
    submission_id: UUID,
    dimension: str,
    indicator: str | None,
    level: str,
    rationale: str | None,
    segment: Segment | None,
    spans: list[EvidenceSpan],
    distribution: dict[str, int] | None = None,
) -> int:
    """One score row and its evidence. Returns how many evidence rows were written."""
    score_id = cur.execute(
        "insert into system_scores (owner_id, run_id, submission_id, dimension, indicator, level, "
        "rationale, explanation_type, segment_index, segment_start, segment_end, distribution) "
        "values (%s, %s, %s, %s, %s, %s, %s, 'evidence_span', %s, %s, %s, %s) returning id",
        (
            owner_id,
            run_id,
            submission_id,
            dimension,
            indicator,
            level,
            rationale,
            None if segment is None else segment.index,
            None if segment is None else segment.start,
            None if segment is None else segment.end,
            None if distribution is None else Jsonb(distribution),
        ),
    ).fetchone()[0]
    for span in spans:
        cur.execute(
            "insert into evidence (owner_id, system_score_id, start_offset, end_offset, quote) "
            "values (%s, %s, %s, %s, %s)",
            (owner_id, score_id, span.start_offset, span.end_offset, span.quote),
        )
    return len(spans)


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
    inputs = state.get("inputs", {})
    segments = {segment.index: segment for segment in state.get("segments") or []}
    rubric = state.get("rubric") or {}
    spans = list(state.get("evidence", []))

    def spans_for(source: str, segment: int | None = None, indicator: str | None = None):
        return [
            span
            for span in spans
            if span.source == source
            and (segment is None or span.segment == segment)
            and (indicator is None or span.indicator == indicator)
        ]

    counts = {"traces": 0, "scores": 0, "evidence": 0}
    ids: dict[str, Any] = {"owner_id": owner_id, "run_id": run_id, "submission_id": submission_id}

    with conn.cursor() as cur:
        # A baseline run produces no feedback (FR-15) and must not touch what a multi-agent run on the
        # same submission already wrote: `feedback` is keyed by submission, not by run, so deleting it
        # here would erase a real result the lecturer can still see and edit, for a mode that has nothing
        # to replace it with.
        if state.get("mode") != "single_agent":
            cur.execute("delete from feedback where submission_id = %s", (submission_id,))
        cur.execute(
            "delete from system_scores where run_id = %s and submission_id = %s",
            (run_id, submission_id),
        )
        cur.execute(
            "delete from agent_traces where run_id = %s and submission_id = %s",
            (run_id, submission_id),
        )

        # The baseline's one call gets exactly one trace row (FR-15), including on failure:
        # `cognitive`/`metacognitive` are pieces reconstructed from that single answer for scoring, not
        # separate calls, and `synthesis` never runs in this mode, so neither belongs in the trace.
        agent_payloads: list[tuple[str, BaseModel | None]] = (
            [("single_agent", state.get("single_agent"))]
            if state.get("mode") == "single_agent"
            else [
                ("cognitive", cognitive),
                ("metacognitive", metacognitive),
                ("synthesis", synthesis),
            ]
        )
        for agent, payload in agent_payloads:
            cur.execute(
                "insert into agent_traces "
                "(owner_id, run_id, submission_id, agent_name, input_ref, output_json, latency_ms, error) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    owner_id,
                    run_id,
                    submission_id,
                    agent,
                    # The user turn as sent (KNF-04: every step records its input). It holds only the
                    # redacted segments already stored on the submission, so it adds no new data.
                    inputs.get(agent),
                    None if payload is None else Jsonb(payload.model_dump(mode="json")),
                    # The client's own measurement, carried in the state (PRD §10 AgentTrace): a free
                    # provider's latency is the app's evidence for the performance target in PRD §11.
                    latencies.get(agent),
                    None if payload is not None else "agent did not produce output",
                ),
            )
            counts["traces"] += 1

        if cognitive is not None:
            for entry in cognitive.segments:
                counts["evidence"] += _insert_score(
                    cur,
                    **ids,
                    dimension="cognitive",
                    indicator=None,
                    level=entry.level,
                    rationale=entry.rationale,
                    segment=segments.get(entry.segment),
                    spans=spans_for("cognitive", entry.segment),
                )
                counts["scores"] += 1
            # Text level: the highest level any segment reached, explained and evidenced by the segment
            # that reached it, with the spread of segments over the rubric's level groups (Bab III.6,
            # KF-07).
            top = highest_level([e.level for e in cognitive.segments], list(rubric.get("levels") or []))
            deciding = next((e for e in cognitive.segments if e.level == top), None)
            if deciding is not None:
                counts["evidence"] += _insert_score(
                    cur,
                    **ids,
                    dimension="cognitive",
                    indicator=None,
                    level=deciding.level,
                    rationale=f"Tingkat tertinggi, pada segmen {deciding.segment}: {deciding.rationale}",
                    segment=None,
                    spans=spans_for("cognitive", deciding.segment),
                    distribution=distribution(
                        [e.level for e in cognitive.segments],
                        dict((rubric.get("descriptors") or {}).get("groups") or {}),
                    ),
                )
                counts["scores"] += 1

        if metacognitive is not None:
            found: dict[str, list[tuple[int, str]]] = {}
            for unit in metacognitive.segments:
                by_indicator = {finding.indicator: finding for finding in unit.indicators}
                for indicator in rubric.get("indicators") or []:
                    finding = by_indicator.get(indicator)
                    if finding is not None:
                        found.setdefault(indicator, []).append((unit.segment, finding.rationale))
                    # Every indicator gets a row in every segment, present or absent, so per-indicator
                    # agreement can be computed from the export without reconstructing absences.
                    counts["evidence"] += _insert_score(
                        cur,
                        **ids,
                        dimension="metacognitive",
                        indicator=indicator,
                        level=PRESENT if finding else ABSENT,
                        rationale=None if finding is None else finding.rationale,
                        segment=segments.get(unit.segment),
                        spans=spans_for("metacognitive", unit.segment, indicator) if finding else [],
                    )
                    counts["scores"] += 1
            # Text level: the set of indicators found in any segment (Bab III.6).
            for indicator in rubric.get("indicators") or []:
                hits = found.get(indicator, [])
                counts["evidence"] += _insert_score(
                    cur,
                    **ids,
                    dimension="metacognitive",
                    indicator=indicator,
                    level=PRESENT if hits else ABSENT,
                    rationale=(
                        "Ditemukan pada segmen "
                        + ", ".join(str(segment) for segment, _ in hits)
                        + f": {hits[0][1]}"
                        if hits
                        else "Tidak ditemukan pada segmen mana pun."
                    ),
                    segment=None,
                    spans=spans_for("metacognitive", None, indicator),
                )
                counts["scores"] += 1

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
