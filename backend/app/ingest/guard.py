"""The single egress choke point for submission text.

This is the only place in the codebase where submission text may leave for an inference provider.
Phase 4's provider client calls `assert_sendable` before every request and refuses the call when it
raises, so a mistake in ingest redaction cannot reach a provider: there is one door, not one per
caller, and a new call site cannot bypass a check it does not know about.
"""

from app.ingest.models import RedactionClass
from app.ingest.redact import find_identifiers


class EgressBlocked(Exception):
    """Refusal to send a payload that still contains identifiers.

    Carries counts per class, never the removed values: the block has to be explainable to the
    lecturer without copying the student's data into a log or an error response.
    """

    def __init__(self, classes: dict[RedactionClass, int]) -> None:
        self.classes = classes
        named = ", ".join(f"{cls.value}={count}" for cls, count in classes.items())
        super().__init__(f"payload still contains identifiers: {named}")


def assert_sendable(payload: str) -> None:
    """Raise `EgressBlocked` unless `payload` is free of detectable identifiers."""
    found = find_identifiers(payload)
    if found:
        raise EgressBlocked(found)
