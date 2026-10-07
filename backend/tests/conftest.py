"""Test fixtures. Requires a local Postgres with the thesis_migrator/thesis_app roles
(see scripts/bootstrap_db.sh). Migrations are applied on the test database once per session."""

import os
import pathlib
import sys

import pytest

BACKEND = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

os.environ.setdefault("ENV", "test")
os.environ.setdefault(
    "DATABASE_URL", "postgresql://thesis_app:app_local_pw@localhost:5432/thesis_test"
)
os.environ.setdefault(
    "MIGRATION_DATABASE_URL", "postgresql://thesis_migrator:migrator_local_pw@localhost:5432/thesis_test"
)
os.environ.setdefault("COOKIE_SECURE", "false")

import psycopg  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app.main import app  # noqa: E402  (import after settings are in place)
from scripts.migrate import run as run_migrations  # noqa: E402

TENANT_TABLES = [
    "feedback", "lecturer_reviews", "evidence", "system_scores", "jobs", "agent_traces",
    "runs", "student_identities", "submissions", "prompt_versions", "assignments",
    "rubric_versions", "sessions", "users",
]


@pytest.fixture(scope="session", autouse=True)
def migrated():
    run_migrations(os.environ["MIGRATION_DATABASE_URL"])


@pytest.fixture(autouse=True)
def clean_db():
    with psycopg.connect(os.environ["MIGRATION_DATABASE_URL"], autocommit=True) as conn:
        conn.execute(f"truncate {', '.join(TENANT_TABLES)} cascade")
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
