"""Seed the interim rubric, the three prompt templates and the calibration row.

Usage:  uv run python -m scripts.seed_rubric [--email someone@example.com] [--calibration ex.json]

Idempotent by construction: every write is compared against the newest stored row for the same key
(owner_id for the rubric, owner_id + agent_name for the prompts) and skipped when the content already
matches, so a second run inserts nothing. Changed content inserts version + 1 instead of updating the
row, because PRD §10 makes RubricVersion and PromptVersion immutable once a run has used them: a run
snapshot has to keep pointing at the exact content it was scored with. `version_to_insert` is the one
rule both tables share.

Connects as the runtime role from DATABASE_URL — the role the app runs as — and sets
`app.current_user_id` to the owner before writing, since rubric_versions and prompt_versions are
under the FORCEd tenant policies of migration 0001. The owner is looked up by email, or is the first
admin when --email is omitted.

What is seeded is deliberately contentless: the six canonical Bloom level names, and exactly the four
G1 SRL codes (elaborasi, organisasi, orientasi, evaluasi). No descriptor, no threshold and no
per-indicator description is written, because the supervisors' rater guideline replaces all of it
(PRD §13) — the flags and the note in `descriptors` say so. The calibration examples are Atthar's
contribution (PRD §14): pass them as a JSON list with --calibration, or the row is written empty and
pending, and the cognitive and metacognitive agents then refuse to run (PRD §6).
"""

import argparse
import json
import pathlib
import sys
import uuid
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.agents.prompts import TEMPLATES
from app.config import get_settings

#: The six Bloom levels by code. Atthar's calibration (2026-10-15) states the scale as "C1 Remember …
#: C6 Create", and the agents return those codes, so the codes are what the rubric stores; the names
#: travel in `descriptors.levels`.
LEVELS = ["C1", "C2", "C3", "C4", "C5", "C6"]
LEVEL_NAMES = {
    "C1": "Remember",
    "C2": "Understand",
    "C3": "Apply",
    "C4": "Analyze",
    "C5": "Evaluate",
    "C6": "Create",
}
INDICATORS = ["elaborasi", "organisasi", "orientasi", "evaluasi"]
DIMENSIONS = ["cognitive", "metacognitive"]

RUBRIC_NOTE = (
    "Rubrik interim: empat kode SRL G1 sebagai placeholder untuk dimensi metakognitif, dan enam kode "
    "level Bloom revisi (Anderson & Krathwohl, 2001) beserta namanya untuk dimensi kognitif. Pedoman "
    "penilaian dari pembimbing menggantikan seluruh isi ini (PRD §13). Tidak ada ambang batas yang "
    "ditulis di sini."
)
CALIBRATION_NOTE = (
    "Blok kalibrasi per agen adalah kontribusi Atthar (PRD §14), termasuk contoh sintetis untuk level "
    "yang tidak punya contoh nyata di arsip. Selama blok seorang agen kosong, agen itu menolak "
    "berjalan (MissingCalibration, PRD §6), bukan berjalan tanpa kalibrasi."
)


def version_to_insert(stored: dict[str, Any] | None, content: dict[str, Any]) -> int | None:
    """The version to insert, or None when the newest stored row already holds `content`.

    This is the whole idempotency rule: identical content is a no-op, different content becomes the
    next version. `stored` is the newest row (its own keys plus `version`), `content` the columns
    (and `template`) this script would write.
    """
    if stored is not None and all(stored.get(key) == value for key, value in content.items()):
        return None
    return (stored["version"] if stored else 0) + 1


def rubric_content() -> dict[str, Any]:
    """The four jsonb columns of a RubricVersion, as seeded."""
    return {
        "dimensions": DIMENSIONS,
        "levels": LEVELS,
        "indicators": INDICATORS,
        "descriptors": {
            "levels": LEVEL_NAMES,
            "indicators": {},
            "interim": True,
            "pending_supervisors": True,
            "note": RUBRIC_NOTE,
        },
    }


def prompt_content(calibration: dict[str, Any]) -> dict[str, str]:
    """Agent name -> the PromptVersion.template text, including the `calibration` row.

    Each agent's template is its two turns, system and user, as JSON; the calibration row is the
    per-agent blocks plus their provenance flags, which is the shape the graph reads back (PRD §6
    stores the calibration as a versioned PromptVersion row). What the file says wins, so the source
    and the interim flags travel with the content they describe.
    """
    stored = {
        name: json.dumps({"system": system, "user": user}, ensure_ascii=False, indent=2)
        for name, (system, user) in TEMPLATES.items()
    }
    stored["calibration"] = json.dumps(
        {**calibration, "note": CALIBRATION_NOTE}, ensure_ascii=False, indent=2
    )
    return stored


def _owner(conn: psycopg.Connection[dict[str, Any]], email: str | None) -> uuid.UUID:
    """Resolve the owner before any tenant context exists: `users` is not row-level secured."""
    if email:
        row = conn.execute(
            "select id from users where email = %s", (email.strip().lower(),)
        ).fetchone()
        missing = f"no user with email {email}"
    else:
        row = conn.execute(
            "select id from users where role = 'admin' order by created_at limit 1"
        ).fetchone()
        missing = "no admin user; run the seed with --email"
    if row is None:
        raise SystemExit(missing)
    return row["id"]


def _seed_rubric(conn: psycopg.Connection[dict[str, Any]], owner_id: uuid.UUID) -> str:
    content = rubric_content()
    stored = conn.execute(
        "select version, dimensions, levels, indicators, descriptors from rubric_versions"
        " where owner_id = %s order by version desc limit 1",
        (owner_id,),
    ).fetchone()
    version = version_to_insert(stored, content)
    if version is None:
        return f"rubric v{stored['version'] if stored else 0} unchanged"
    conn.execute(
        "insert into rubric_versions (owner_id, version, dimensions, levels, indicators, descriptors)"
        " values (%s, %s, %s, %s, %s, %s)",
        (
            owner_id,
            version,
            Jsonb(content["dimensions"]),
            Jsonb(content["levels"]),
            Jsonb(content["indicators"]),
            Jsonb(content["descriptors"]),
        ),
    )
    return f"rubric v{version} inserted ({len(LEVELS)} levels, {len(INDICATORS)} indicators)"


def _seed_prompt(
    conn: psycopg.Connection[dict[str, Any]],
    owner_id: uuid.UUID,
    agent_name: str,
    template: str,
) -> str:
    stored = conn.execute(
        "select version, template from prompt_versions where owner_id = %s and agent_name = %s"
        " order by version desc limit 1",
        (owner_id, agent_name),
    ).fetchone()
    version = version_to_insert(stored, {"template": template})
    if version is None:
        return f"{agent_name} v{stored['version'] if stored else 0} unchanged"
    conn.execute(
        "insert into prompt_versions (owner_id, agent_name, version, template) values (%s, %s, %s, %s)",
        (owner_id, agent_name, version, template),
    )
    return f"{agent_name} v{version} inserted"


def seed(database_url: str, email: str | None, calibration: dict[str, Any]) -> list[str]:
    """Write whichever versions are missing, and report one line per row touched."""
    with psycopg.connect(database_url, autocommit=True, row_factory=dict_row) as conn:
        owner_id = _owner(conn, email)
        # Session-scoped (is_local = false): one connection, one tenant, no pooling involved.
        conn.execute("select set_config('app.current_user_id', %s, false)", (str(owner_id),))
        report = [f"owner {owner_id}"]
        report.append(_seed_rubric(conn, owner_id))
        for agent_name, template in prompt_content(calibration).items():
            report.append(_seed_prompt(conn, owner_id, agent_name, template))
    return report


def _calibration_from(path: str) -> dict[str, Any]:
    """The calibration file: one block per analysis agent, each with instructions and examples.

    Both agents are checked here rather than at the first run, because a file missing the
    metacognitive block would seed cleanly and only fail once a job reached that agent.
    """
    parsed = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise SystemExit(f"{path} must hold a JSON object keyed by agent name, not a list.")
    for agent in ("cognitive", "metacognitive"):
        block = parsed.get(agent)
        if not isinstance(block, dict) or not block.get("examples"):
            raise SystemExit(f"{path}: `{agent}` needs an object with a non-empty `examples` list.")
    return parsed


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Seed the interim rubric, prompts and calibration.")
    parser.add_argument("--email", help="Owner of the seeded rows; defaults to the first admin.")
    parser.add_argument(
        "--calibration",
        default=str(pathlib.Path(__file__).with_name("calibration.json")),
        help="JSON file with the per-agent calibration blocks (PRD §14).",
    )
    args = parser.parse_args(argv)

    calibration = _calibration_from(args.calibration)
    print(f"calibration: {args.calibration}")
    for line in seed(get_settings().database_url, args.email, calibration):
        print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
