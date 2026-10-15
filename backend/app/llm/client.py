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
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.ingest.guard import EgressBlocked, assert_sendable

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class ProviderNotConfigured(RuntimeError):
    """The environment names no provider, key or model, so no call can be made at all."""


class ProviderError(RuntimeError):
    """The provider was not reachable, or never returned a response matching the schema."""


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
    ) -> Completion:
        """Send one request and return the response parsed into `schema`.

        The schema leaves twice on purpose: as `response_format` for endpoints that support
        constrained decoding, and inside the prompt because not every free endpoint honours it.

        `temperature` and `seed` fall back to configuration, so the caller decides reproducibility
        per run and never by editing a constant here.
        """
        settings = self._settings
        base_url, api_key, model = self._route(settings)
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        user_content = f"{user}\n\nReply with JSON only, matching this schema:\n{schema_json}"
        self._assert_sendable(f"{system}\n\n{user_content}")

        body: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            "temperature": settings.llm_temperature if temperature is None else temperature,
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
        )
        attempts = settings.llm_max_attempts
        if self._http is None:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as http:
                return self._send(http, request, schema, attempts)
        return self._send(self._http, request, schema, attempts)

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
        self, http: httpx.Client, request: httpx.Request, schema: type[SchemaT], attempts: int
    ) -> Completion:
        """Post `request`, retrying any unusable answer up to `attempts` times in total."""
        last_reason = "no attempt was made"
        for attempt in range(1, attempts + 1):
            started = time.perf_counter()
            try:
                response = http.send(request)
                response.raise_for_status()
                raw = response.json()["choices"][0]["message"]["content"]
                parsed = schema.model_validate(json.loads(raw))
            # Transport failures, a non-2xx status, malformed JSON, a missing choice and a schema
            # violation are one case on purpose: the only thing to do with any of them is try again,
            # and only the reason differs. ValidationError is a ValueError.
            except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
                last_reason = f"{type(exc).__name__}: {exc}"
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
