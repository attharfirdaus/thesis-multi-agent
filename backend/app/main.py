"""FastAPI entrypoint. Phase 2 carries health and auth only."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.config import get_settings
from app.routers import auth, health, ingest, runs


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.open_pool()
    yield
    db.close_pool()


app = FastAPI(title="Multi-Agent LLM Evaluation API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(runs.router)
