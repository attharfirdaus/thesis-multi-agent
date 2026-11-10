"""The LangGraph pipeline of PRD §6, one submission per run.

Node order is the PRD's own: preprocess, then the cognitive and the metacognitive agent in parallel,
then synthesis, then the rule-based evidence check. Routing is a rule, never a model call, so this
module holds orchestration only — each node either assembles a prompt and calls the provider client,
or applies a rule to what came back.

Three rules are visible in the code below, and they are the reason it is shaped this way:

- A failure in one dimension is a flag, not an exception. The two agent nodes run in parallel; letting
  either raise would lose the other dimension's score, and a batch must not lose a result because one
  provider call failed (PRD §11, reliability).
- A quote that cannot be found is not a quote. The evidence node locates every claimed quote in the
  stored text before the caller persists anything, so an unverifiable score is flagged for review
  instead of being presented as grounded.
- Keep the score, flag it. PRD §6: synthesis is told which quotes could not be located, and the score is
  stored with a `needs_review` flag rather than discarded.

Every key a node returns MUST exist on `GraphState` (app/agents/models.py): LangGraph 1.2 discards an
update for an undeclared key silently, so a mistyped key looks like a node that ran and produced
nothing. Add the field to the model first, then return it.
"""

import time
from collections.abc import Callable, Iterator
from typing import Any, Literal, cast

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from app.agents import prompts
from app.agents.evidence import locate_quote
from app.agents.models import (
    CognitiveResult,
    EvidenceSpan,
    GraphState,
    MetacognitiveResult,
    SegmentIndicators,
    SegmentLevel,
    SingleAgentResult,
    SynthesisResult,
)
from app.agents.segments import Segment, split_segments
from app.llm.client import ModelUnavailable, ProviderClient

# Flag tokens, stored per submission in `submissions.review_flags` and read by the UI badge. They are
# machine-readable on purpose: the lecturer sees "Perlu Ditinjau", not an agent name.
COGNITIVE_FAILED = "cognitive_agent_failed"
METACOGNITIVE_FAILED = "metacognitive_agent_failed"
SYNTHESIS_FAILED = "synthesis_agent_failed"
SINGLE_AGENT_FAILED = "single_agent_failed"
SYNTHESIS_RETRIED = "synthesis_retried"
SYNTHESIS_INCONSISTENCY = "synthesis_inconsistency"
EVIDENCE_UNVERIFIED = "evidence_unverified"
NEEDS_REVIEW = "needs_review"

# Which agent a quote came from. The evidence node labels failures with it so a review screen can say
# whose claim could not be found.
QuoteSource = Literal["cognitive", "metacognitive"]

# Exceptions that must stop the submission rather than become a per-agent flag: a run without its
# mandatory calibration, and a model the provider no longer serves (the worker flags the run).
_FATAL = (prompts.MissingCalibration, ModelUnavailable)


def _parsed[ModelT: BaseModel](parsed: object, expected: type[ModelT]) -> ModelT:
    """The client's validated model instance, checked rather than trusted.

    The client is a network boundary: it promises an instance of the schema it was asked for, and this
    is the one place that promise is verified, so a mismatch becomes a flagged agent failure instead of
    a wrongly typed object flowing into the state.
    """
    if not isinstance(parsed, expected):
        raise TypeError(f"provider returned {type(parsed).__name__}, expected {expected.__name__}")
    return parsed


def _calibration(state: GraphState) -> dict[str, Any]:
    """The seeded calibration block, one entry per analysis agent (PRD §14).

    Data, not code: the graph never invents rubric content. An absent or empty block is refused by
    `prompts.MissingCalibration` further down, per agent, rather than run uncalibrated.
    """
    return dict(state.get("prompts", {}).get("calibration") or {})


def preprocess(state: GraphState) -> dict[str, Any]:
    """The assessed segments of the analysis (Bab III.6). No model call.

    The text was redacted in phase 3 and is re-checked by the provider client before it leaves, so
    there is nothing to clean here. An empty analysis cannot be scored, and failing here costs no
    provider quota.
    """
    text = state.get("student_analysis_text") or ""
    if not text.strip():
        raise ValueError(
            "student analysis is empty: the submission was not segmented or its analysis segment "
            "is blank, so there is nothing to evaluate"
        )
    # The worker passes the split stored before measurement (KF-05); a caller without one (the tests,
    # a row from before migration 0008) gets the same rule applied here. Offsets of the segments, and of
    # every quote later, point into the text exactly as stored: it is not stripped here, because the
    # detail view re-slices the stored string.
    return {"segments": state.get("segments") or split_segments(text)}


def _client(client: ProviderClient | None) -> ProviderClient:
    """Resolve the client at call time, so a run that never reaches a node never builds one."""
    return client if client is not None else ProviderClient()


def _elapsed_ms(started: float) -> int:
    """Wall-clock since `started`, for the failure path.

    The client reports the latency of a call that returned. A call that raised — three timed-out
    attempts, say — reports nothing, and that duration is exactly the number that says the provider is
    unhealthy: it was null in every failed trace until this existed (seen live, 2026-10-16).
    """
    return int((time.monotonic() - started) * 1000)


def _segments(state: GraphState) -> list[Segment]:
    return list(state.get("segments") or [])


# --------------------------------------------------------------------------- label validation
#
# A schema-valid answer can still be unusable: a level the rubric does not have, an indicator it does
# not list, a segment left out or numbered twice. These checks run inside the client's retry loop
# (`check=`), so such an answer is retried like a schema violation and, after the last attempt, fails
# the agent — which flags the submission for review (Bab III.4).


def _same_segments(numbers: list[int], segments: list[Segment]) -> None:
    expected = [segment.index for segment in segments]
    if sorted(numbers) != expected:
        raise ValueError(f"segments labelled {sorted(numbers)}, expected exactly {expected}")


def _check_levels(entries: list[SegmentLevel], state: GraphState) -> None:
    _same_segments([entry.segment for entry in entries], _segments(state))
    allowed = list(state["rubric"]["levels"])
    unknown = sorted({entry.level for entry in entries} - set(allowed))
    if unknown:
        raise ValueError(f"levels {unknown} are not in the rubric {allowed}")


def _check_indicators(entries: list[SegmentIndicators], state: GraphState) -> None:
    _same_segments([entry.segment for entry in entries], _segments(state))
    allowed = list(state["rubric"]["indicators"])
    for entry in entries:
        names = [finding.indicator for finding in entry.indicators]
        unknown = sorted(set(names) - set(allowed))
        if unknown:
            raise ValueError(f"indicators {unknown} in segment {entry.segment} are not in {allowed}")
        if len(names) != len(set(names)):
            raise ValueError(f"segment {entry.segment} lists an indicator twice")


def _agent_quotes(state: GraphState) -> Iterator[tuple[QuoteSource, int, str | None, str]]:
    """Every quote an agent claims to have taken from the student's analysis, with what it backs:
    `(source, segment, indicator, quote)`."""
    cognitive = state.get("cognitive")
    for entry in cognitive.segments if cognitive is not None else []:
        yield "cognitive", entry.segment, None, entry.evidence_quote
    metacognitive = state.get("metacognitive")
    for unit in metacognitive.segments if metacognitive is not None else []:
        for finding in unit.indicators:
            yield "metacognitive", unit.segment, finding.indicator, finding.evidence_quote


def _locate(state: GraphState, segment: int, quote: str) -> tuple[int, int] | None:
    """The quote's offsets in the stored text, searched only inside the segment it labels: a quote
    from another segment does not back this segment's label."""
    unit = next((s for s in _segments(state) if s.index == segment), None)
    if unit is None:
        return None
    found = locate_quote(unit.text, quote)
    return None if found is None else (unit.start + found[0], unit.start + found[1])


def _unverified(state: GraphState) -> list[str]:
    """Claimed quotes that are not in their segment, labelled `source[segment]: quote`."""
    return [
        f"{source}[{segment}]: {quote}"
        for source, segment, _indicator, quote in _agent_quotes(state)
        if _locate(state, segment, quote) is None
    ]


def _failure(flag: str, exc: Exception) -> dict[str, Any]:
    """A failed agent as state, never as an exception: flags and errors both merge, so a failure in one
    dimension cannot take the other dimension's score with it."""
    return {"flags": [flag], "errors": [f"{flag}: {exc!r}"]}


def _paired_args(state: GraphState) -> dict[str, Any]:
    """The paired input both specialists read (Bab II.2.2): the AI output and the segmented analysis,
    with the rubric and the calibration examples."""
    return {
        "rubric": state["rubric"],
        "calibration": _calibration(state),
        "ai_output_text": state.get("ai_output_text", ""),
        "segments": _segments(state),
    }


def _cognitive_node(client: ProviderClient | None) -> Callable[[GraphState], dict[str, Any]]:
    def node(state: GraphState) -> dict[str, Any]:
        started = time.monotonic()
        user = ""
        try:
            system, user = prompts.cognitive_prompt(**_paired_args(state))
            completion = _client(client).complete_json(
                system=system,
                user=user,
                schema=CognitiveResult,
                segments=len(_segments(state)),
                check=lambda parsed: _check_levels(cast(CognitiveResult, parsed).segments, state),
            )
        except _FATAL:
            # Mandatory calibration (PRD §6): scores produced without it would look calibrated, which
            # is the exact tautology risk the PRD tells this system to interrogate rather than hide.
            raise
        except Exception as exc:
            return {
                "cognitive": None,
                "latencies": {"cognitive": _elapsed_ms(started)},
                "inputs": {"cognitive": user},
                **_failure(COGNITIVE_FAILED, exc),
            }
        return {
            "cognitive": _parsed(completion.parsed, CognitiveResult),
            "latencies": {"cognitive": completion.latency_ms},
            "inputs": {"cognitive": user},
        }

    return node


def _metacognitive_node(client: ProviderClient | None) -> Callable[[GraphState], dict[str, Any]]:
    def node(state: GraphState) -> dict[str, Any]:
        started = time.monotonic()
        user = ""
        try:
            system, user = prompts.metacognitive_prompt(**_paired_args(state))
            completion = _client(client).complete_json(
                system=system,
                user=user,
                schema=MetacognitiveResult,
                segments=len(_segments(state)),
                check=lambda parsed: _check_indicators(
                    cast(MetacognitiveResult, parsed).segments, state
                ),
            )
        except _FATAL:
            raise
        except Exception as exc:
            return {
                "metacognitive": None,
                "latencies": {"metacognitive": _elapsed_ms(started)},
                "inputs": {"metacognitive": user},
                **_failure(METACOGNITIVE_FAILED, exc),
            }
        return {
            "metacognitive": _parsed(completion.parsed, MetacognitiveResult),
            "latencies": {"metacognitive": completion.latency_ms},
            "inputs": {"metacognitive": user},
        }

    return node


def _check_single(parsed: BaseModel, state: GraphState) -> None:
    baseline = cast(SingleAgentResult, parsed)
    _check_levels(baseline.cognitive, state)
    _check_indicators(baseline.metacognitive, state)


def _single_agent_node(client: ProviderClient | None) -> Callable[[GraphState], dict[str, Any]]:
    """FR-15's baseline: one call over the full rubric, split into the same two shapes the
    multi-agent path produces, so the evidence node and persistence need no mode-specific branch.

    A failure here costs both dimensions, because one call produced them both — there is no
    partial result to keep the way the two parallel multi-agent nodes can keep each other's.
    """

    def node(state: GraphState) -> dict[str, Any]:
        started = time.monotonic()
        user = ""
        try:
            system, user = prompts.single_agent_prompt(**_paired_args(state))
            completion = _client(client).complete_json(
                system=system,
                user=user,
                schema=SingleAgentResult,
                segments=len(_segments(state)),
                check=lambda parsed: _check_single(parsed, state),
            )
        except _FATAL:
            raise
        except Exception as exc:
            return {
                "cognitive": None,
                "metacognitive": None,
                "single_agent": None,
                "latencies": {"single_agent": _elapsed_ms(started)},
                "inputs": {"single_agent": user},
                **_failure(SINGLE_AGENT_FAILED, exc),
            }
        baseline = _parsed(completion.parsed, SingleAgentResult)
        return {
            "cognitive": CognitiveResult(segments=baseline.cognitive),
            "metacognitive": MetacognitiveResult(segments=baseline.metacognitive),
            "single_agent": baseline,
            "latencies": {"single_agent": completion.latency_ms},
            "inputs": {"single_agent": user},
        }

    return node


def _synthesise(
    state: GraphState, client: ProviderClient | None, retry_reason: str | None
) -> tuple[SynthesisResult, int, str]:
    """One synthesis call, with its wall-clock milliseconds (PRD §10) and the user turn it sent.

    `retry_reason` is the evidence failure the retry has to answer (PRD §6)."""
    cognitive = state.get("cognitive")
    metacognitive = state.get("metacognitive")
    system, user = prompts.synthesis_prompt(
        # A dimension that failed is passed as an empty object: the synthesis agent explains what it
        # was given, and inventing a placeholder score here would fabricate a result.
        cognitive=cognitive.model_dump() if cognitive is not None else {},
        metacognitive=metacognitive.model_dump() if metacognitive is not None else {},
        ai_output_text=state.get("ai_output_text", ""),
        segments=_segments(state),
        retry_reason=retry_reason,
    )
    completion = _client(client).complete_json(system=system, user=user, schema=SynthesisResult)
    return _parsed(completion.parsed, SynthesisResult), completion.latency_ms, user


def _synthesis_node(client: ProviderClient | None) -> Callable[[GraphState], dict[str, Any]]:
    def node(state: GraphState) -> dict[str, Any]:
        if state.get("cognitive") is None and state.get("metacognitive") is None:
            # Nothing was labelled, so there is nothing to explain: a call here returned feedback
            # written from two empty objects and the job then counted as done (seen 2026-11-10).
            return {
                "synthesis": None,
                **_failure(SYNTHESIS_FAILED, RuntimeError("both analysis agents failed")),
            }
        # One call, not two. Which quotes cannot be located is known before synthesis starts, so the
        # reason PRD §6 sends back with the retry goes into the only call: the first one's answer was
        # always discarded, and no synthesis call can make another agent's quote findable.
        unverified = _unverified(state)
        started = time.monotonic()
        try:
            synthesis, latency, user = _synthesise(
                state, client, retry_reason="; ".join(unverified) or None
            )
        except ModelUnavailable:
            raise
        except Exception as exc:
            return {
                "synthesis": None,
                "latencies": {"synthesis": _elapsed_ms(started)},
                **_failure(SYNTHESIS_FAILED, exc),
            }

        # An unlocated quote or a rationale that does not match its quote is a reason to look, never a
        # reason to change a label: the synthesis agent does not re-score (Bab III.4, III.8).
        flags = [SYNTHESIS_INCONSISTENCY] if synthesis.inconsistencies else []
        if unverified or synthesis.inconsistencies:
            flags.append(NEEDS_REVIEW)
        return {
            "synthesis": synthesis,
            "flags": flags,
            "latencies": {"synthesis": latency},
            "inputs": {"synthesis": user},
        }

    return node


def evidence(state: GraphState) -> dict[str, Any]:
    """Locate every claimed quote inside the segment it labels and record the offsets (PRD §6, step 4).

    Every key returned here exists on `GraphState`, and that is a requirement, not a coincidence:
    langgraph 1.2 discards an update for a key the state schema does not declare, silently, so a new
    field has to be added to `app/agents/models.py` before any node returns it.

    Offsets point into `student_analysis_text` as stored, which is what the detail view re-slices to
    highlight the quote, so the found span is built from the original string and never from the
    normalised comparison form.
    """
    spans: list[EvidenceSpan] = []
    failures: list[str] = []
    for source, segment, indicator, quote in _agent_quotes(state):
        found = _locate(state, segment, quote)
        if found is None:
            failures.append(f"{source}[{segment}]: {quote}")
        else:
            spans.append(
                EvidenceSpan(
                    source=source,
                    segment=segment,
                    indicator=indicator,
                    quote=quote,
                    start_offset=found[0],
                    end_offset=found[1],
                )
            )

    flags = [EVIDENCE_UNVERIFIED] if failures else []
    if failures and NEEDS_REVIEW not in state.get("flags", []):
        flags.append(NEEDS_REVIEW)
    return {"evidence": spans, "evidence_failures": failures, "flags": flags}


def build_graph(checkpointer: Any = None, client: ProviderClient | None = None):
    """Compile the PRD §6 multi-agent graph. `checkpointer` is a LangGraph saver; `client` is
    injected in tests."""
    graph: StateGraph[GraphState] = StateGraph(GraphState)
    # The three factory-built nodes are cast because mypy 1.x cannot match a callable produced by a
    # factory against langgraph's node-protocol union (`_Node[NodeInputT] | ...`): a closure always
    # fails while a plain function reference passes. The cast hides only this wiring call — each node
    # function is annotated where it is defined, and `preprocess`/`evidence` need no cast at all.
    graph.add_node("preprocess", preprocess)
    graph.add_node("cognitive", cast(Any, _cognitive_node(client)))
    graph.add_node("metacognitive", cast(Any, _metacognitive_node(client)))
    graph.add_node("synthesis", cast(Any, _synthesis_node(client)))
    graph.add_node("evidence", evidence)
    graph.add_edge(START, "preprocess")
    # Both dimensions read the same text and share no output, so they run in the same step.
    graph.add_edge("preprocess", "cognitive")
    graph.add_edge("preprocess", "metacognitive")
    # Synthesis is the fan-in: it starts only once both dimensions have reported, including a
    # dimension that reported a failure.
    graph.add_edge("cognitive", "synthesis")
    graph.add_edge("metacognitive", "synthesis")
    graph.add_edge("synthesis", "evidence")
    graph.add_edge("evidence", END)
    return graph.compile(checkpointer=checkpointer)


def build_single_agent_graph(checkpointer: Any = None, client: ProviderClient | None = None):
    """Compile the FR-15 baseline graph: one judgement call, then the same evidence check.

    `preprocess` and `evidence` are the exact multi-agent nodes, unmodified: the baseline differs
    only in how the rubric is judged, not in how an empty submission is refused or a quote is
    located.
    """
    graph: StateGraph[GraphState] = StateGraph(GraphState)
    graph.add_node("preprocess", preprocess)
    graph.add_node("single_agent", cast(Any, _single_agent_node(client)))
    graph.add_node("evidence", evidence)
    graph.add_edge(START, "preprocess")
    graph.add_edge("preprocess", "single_agent")
    graph.add_edge("single_agent", "evidence")
    graph.add_edge("evidence", END)
    return graph.compile(checkpointer=checkpointer)


#: Mode -> graph builder (FR-15). The run's own `mode` column selects the pipeline; a mode this
#: dict does not know is a data error the worker must not paper over, so `evaluate_submission`
#: raises rather than default to a graph the run never asked for.
_GRAPH_BUILDERS: dict[str, Callable[..., Any]] = {
    "multi_agent": build_graph,
    "single_agent": build_single_agent_graph,
}


def evaluate_submission(
    state: GraphState, client: ProviderClient | None = None, checkpointer: Any = None
) -> GraphState:
    """Run one submission end to end and return the result. The caller persists it (PRD §6).

    With a checkpointer the run is written step by step, so an interrupted submission resumes at its last
    completed step rather than paying for the whole pipeline again. Without one the graph still runs — the
    caller then has job-level retry only, which is what the unit tests use.

    The checkpoint thread is the *run and submission*. Three cases, because `invoke(state)` on a thread
    that already holds a checkpoint does not resume it — it starts again and merges the old `flags` and
    `errors` into the new attempt, which is how a submission scored fine on its second attempt kept
    reading "three agents failed" (seen 2026-11-10):

    - the thread stopped mid-graph (a crash, or a node that raised): resume with `invoke(None)`, so only
      the steps that did not finish are paid for again;
    - the thread holds a finished earlier attempt: drop it and start clean;
    - the graph ran to its end: drop the thread. A finished checkpoint has nothing left to resume, and
      it is a second copy of the student's text that deleting the submission would not reach.

    `state["mode"]` picks the graph (FR-15); state built before the baseline existed carries no mode
    at all, so a missing key still means the multi-agent path it always meant.
    """
    mode = state.get("mode") or "multi_agent"
    try:
        build = _GRAPH_BUILDERS[mode]
    except KeyError:
        raise ValueError(f"unknown run mode {mode!r}") from None
    graph = build(client=client, checkpointer=checkpointer)
    if not checkpointer:
        return graph.invoke(state)
    thread_id = f"{state['run_id']}:{state['submission_id']}"
    config = {"configurable": {"thread_id": thread_id}}
    interrupted = bool(graph.get_state(config).next)
    if not interrupted:
        checkpointer.delete_thread(thread_id)
    result = graph.invoke(None if interrupted else state, config)
    checkpointer.delete_thread(thread_id)
    return result
