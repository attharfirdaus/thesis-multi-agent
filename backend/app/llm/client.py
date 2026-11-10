"""The single egress point for submission text on its way to an inference provider (phase 4).

Two PRD rules meet in this file:

- PRD §11: this is the only client that talks to a provider, and it re-checks the text it is about to
  send. `assert_sendable` runs here and not at the call sites, so a new call site cannot bypass a
  check it does not know about.
- PRD §8: the provider, the key and the model are read from configuration, never named in code, so a
  route can be swapped without a deploy and a route whose free tier may train on prompts is never
  compiled in.

`ProviderNotConfigured` and `ProviderError` are deliberately separate: the first is a setup mistake
that must fail loudly, the second is a provider that misbehaved and must fail the single agent step,
leaving the rest of the batch intact (PRD §11).
"""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.ingest.guard import EgressBlocked, assert_sendable

SchemaT = TypeVar("SchemaT", bound=BaseModel)

# Per-segment answers grow with the analysis, so a fixed budget cannot hold them: a 71-segment analysis
# needed 5,416 completion tokens from the cognitive agent and 1,495 from the metacognitive one (76 and
# 21 per segment), against a cap of 1,024 sized for the old whole-text answer — every attempt was cut
# off mid-JSON and both dimensions failed (measured on the configured model, 2026-11-05). Each labelled
# segment therefore adds this much to `llm_max_tokens`, and the time to generate it to the timeout.
# ponytail: per-segment constants measured on one model; re-measure on a model swap.
TOKENS_PER_SEGMENT = 128
# The same call generated ~47 tokens/s; 40 leaves headroom for a slower moment on the free tier.
TOKENS_PER_SECOND = 40


class ProviderNotConfigured(RuntimeError):
    """The environment names no provider, key or model, so no call can be made at all."""


class ProviderError(RuntimeError):
    """The provider was not reachable, or never returned a response matching the schema."""


class ModelUnavailable(ProviderError):
    """The configured model is no longer served by the provider (Bab III, KNF-04).

    Not retried: the run is flagged instead of being silently scored by some other model.
    """


@dataclass(frozen=True)
class Completion:
    """An accepted agent response plus the numbers `AgentTrace` stores for it."""

    parsed: BaseModel
    raw: str
    latency_ms: int
    attempts: int


class ProviderClient:
    """OpenAI-compatible chat-completions client driven entirely by configuration.

    `http` is injectable so a test can drive the client without a network. Production passes nothing:
    each call then opens its own short-lived connection, which keeps a long batch from holding sockets
    open against a free provider between submissions.
    """

    def __init__(self, http: httpx.Client | None = None) -> None:
        self._http = http
        self._settings: Settings = get_settings()

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema: type[SchemaT],
        temperature: float | None = None,
        seed: int | None = None,
        check: Callable[[BaseModel], None] | None = None,
        segments: int = 0,
    ) -> Completion:
        """Send one request and return the response parsed into `schema`.

        The schema leaves twice on purpose: as `response_format` for endpoints that support
        constrained decoding, and inside the prompt because not every free endpoint honours it.

        `temperature` and `seed` fall back to configuration, so the caller decides reproducibility
        per run and never by editing a constant here. `check` is the caller's own validation of a
        schema-valid answer (a level outside the rubric, a segment left unlabelled): it raises
        `ValueError`, and that answer is retried exactly like one that failed the schema.

        `segments` is how many segments the answer labels, one entry each: it raises the token budget
        and the timeout by `TOKENS_PER_SEGMENT` per segment, so a long analysis is not truncated.
        """
        settings = self._settings
        base_url, api_key, model = self._route(settings)
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        # The schema travels twice, not three times: every caller's system turn already states it, and
        # `response_format` carries it for endpoints that constrain decoding.
        user_content = user
        self._assert_sendable(f"{system}\n\n{user_content}")

        body: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            "temperature": settings.llm_temperature if temperature is None else temperature,
            # Bounded on purpose: an unbounded generation is a call that never returns (see
            # `llm_max_tokens` in app/config.py). A truncated answer is invalid JSON and costs one
            # attempt, which is the failure mode we want over an agent that hangs until the timeout.
            "max_tokens": settings.llm_max_tokens + TOKENS_PER_SEGMENT * segments,
            # The configured model is a reasoning model: it writes its deliberation into `reasoning`
            # and the answer into `content`, out of the same token budget. Asked to score a
            # 9k-character analysis on 2026-10-16 it spent every token it was given on reasoning —
            # 1,024 and then 4,096 — and returned an empty `content` with `finish_reason: length`
            # both times, which is a dimension that can never be scored. Measured against this
            # endpoint on the same day: `reasoning_effort` (`none`/`minimal`/`{"effort":"none"}`) and
            # `thinking: false` are accepted and ignored, and this one disables deliberation —
            # `finish_reason: stop`, 427 characters of valid JSON, 5.7 s, zero reasoning tokens.
            # A model swap must re-check it; an endpoint that rejects the field fails loudly.
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "strict": True,
                    "schema": json.loads(schema_json),
                },
            },
        }
        if (chosen_seed := settings.llm_seed if seed is None else seed) is not None:
            body["seed"] = chosen_seed

        request = httpx.Request(
            "POST",
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=body,
            # Per request, so it also holds for an injected client.
            extensions={
                "timeout": httpx.Timeout(
                    settings.llm_timeout_seconds + TOKENS_PER_SEGMENT * segments / TOKENS_PER_SECOND
                ).as_dict()
            },
        )
        attempts = settings.llm_max_attempts
        if self._http is None:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as http:
                return self._send(http, request, schema, attempts, check)
        return self._send(self._http, request, schema, attempts, check)

    @staticmethod
    def _route(settings: Settings) -> tuple[str, str, str]:
        """The configured base URL, key and model, refusing an incomplete deployment.

        Called before anything else: a half-configured deployment must stop here, where the message
        names the missing variable, instead of sending a request the provider rejects with a 400 the
        lecturer cannot act on.
        """
        missing = [
            name
            for name, value in (
                ("LLM_BASE_URL", settings.llm_base_url),
                ("LLM_API_KEY", settings.llm_api_key),
                ("LLM_MODEL", settings.llm_model),
            )
            if not value
        ]
        if missing:
            raise ProviderNotConfigured(f"no inference provider configured: set {', '.join(missing)}")
        return settings.llm_base_url or "", settings.llm_api_key or "", settings.llm_model or ""

    @staticmethod
    def _assert_sendable(payload: str) -> None:
        """Block the call while the outgoing text still carries an identifier.

        Re-raised as `ProviderError` so the caller has one failure type to handle per agent step, and
        so an ingest mistake surfaces as a failed submission to review rather than as a leak.
        """
        try:
            assert_sendable(payload)
        except EgressBlocked as exc:
            raise ProviderError(f"refusing to send the payload: {exc}") from exc

    def _send(
        self,
        http: httpx.Client,
        request: httpx.Request,
        schema: type[SchemaT],
        attempts: int,
        check: Callable[[BaseModel], None] | None = None,
    ) -> Completion:
        """Post `request`, retrying any unusable answer up to `attempts` times in total."""
        last_reason = "no attempt was made"
        for attempt in range(1, attempts + 1):
            started = time.perf_counter()
            try:
                response = http.send(request)
                if _model_gone(response):
                    raise ModelUnavailable(
                        f"the provider no longer serves the configured model: {response.text[:300]}"
                    )
                response.raise_for_status()
                raw = response.json()["choices"][0]["message"]["content"]
                parsed = schema.model_validate(json.loads(raw))
                if check is not None:
                    check(parsed)
            # Transport failures, a non-2xx status, malformed JSON, a missing choice and a schema
            # violation are one case on purpose: the only thing to do with any of them is try again,
            # and only the reason differs. ValidationError is a ValueError.
            # TypeError is a `content: null` answer (`json.loads(None)`), which a reasoning model that
            # spent its budget before answering returns: retried like any other unusable answer.
            except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
                last_reason = f"{type(exc).__name__}: {exc}"
                if attempt < attempts and isinstance(exc, httpx.HTTPError):
                    time.sleep(_backoff(exc, attempt, self._settings.llm_retry_backoff_seconds))
                continue
            return Completion(
                parsed=parsed,
                raw=raw,
                latency_ms=int((time.perf_counter() - started) * 1000),
                attempts=attempt,
            )
        raise ProviderError(
            f"no valid {schema.__name__} in {attempts} attempts; last: {last_reason}"
        )


def _backoff(exc: httpx.HTTPError, attempt: int, base: float) -> float:
    """Seconds to wait before the next attempt: the provider's `Retry-After` when it sent one, else
    `base` doubled per attempt. Capped, so a hostile header cannot park a batch."""
    response = getattr(exc, "response", None)
    retry_after = response.headers.get("retry-after", "") if response is not None else ""
    wait = float(retry_after) if retry_after.isdigit() else base * 2 ** (attempt - 1)
    return min(wait, 60.0)


def _model_gone(response: httpx.Response) -> bool:
    """Whether the provider says the requested model does not exist.

    ponytail: status + wording heuristic (404, or a 400 that names the model as unknown); replace with
    the provider's documented error code once one is published for this route.
    """
    if response.status_code not in (400, 404):
        return False
    body = response.text.lower()
    gone = ("not found", "no such", "does not exist", "unknown")
    return "model" in body and any(word in body for word in gone)
