# Multi-Agent LLM Evaluation System for AI-Permitted Assignments

Design artefact of Atthar's ITB master's thesis: a web application that evaluates the cognitive and
metacognitive depth of students' analyses of AI output in AI-permitted assignments.

The full specification lives in [`PRD.md`](./PRD.md). Decisions taken so far, with the options that
were rejected and who decided, live in [`DECISIONS.md`](./DECISIONS.md). Phase-1 research evidence
(every provider limit, licence and model claim, with source URL and access date) is archived under
[`docs/phase-1/`](./docs/phase-1/).

**Status: phase 2 (skeleton).** Auth, database schema, CI and a local run path exist. There is no
ingestion, no agent pipeline and no review UI yet — those are phases 3–5.

## Stack

| Layer | Choice | Why |
| --- | --- | --- |
| Frontend | Next.js 16 App Router, TypeScript, Tailwind v4, shadcn/ui | PRD §8 |
| Backend | FastAPI + Python 3.13, LangGraph added in phase 4 | same language as the analysis scripts |
| Database | PostgreSQL 18, self-hosted on the VM | LangGraph's checkpointer is Postgres/SQLite only; the identity mapping stays off third-party databases |
| Hosting | One Oracle Cloud Always Free ARM VM (2 OCPU / 12 GB / 200 GB), Caddy for TLS | no cold start, no quota, no third party in the student-data path |
| Containers | none, anywhere | the VM runs native systemd services; development uses uv + npm + Homebrew Postgres |

## Prerequisites

- macOS with Homebrew, Node 24 LTS, Python 3.13 via [uv](https://docs.astral.sh/uv/)
- PostgreSQL 18: `brew install postgresql@18`
- Roles and databases, once per machine: `cd backend && ./scripts/bootstrap_db.sh`

## Local development

```bash
cd backend && cp -n .env.example .env      # first time only
cd ../frontend && cp -n .env.example .env.local
./scripts/dev.sh                            # Postgres (if needed) → migrate → API + web
```

- Web: <http://localhost:3000> · API: <http://localhost:8000/docs>
- Tests: `cd backend && uv run pytest`
- Lint and types: `cd backend && uv run ruff check . && uv run mypy app`; `cd frontend && npm run lint && npx tsc --noEmit`

Two database roles exist on purpose: `thesis_migrator` owns the schema, `thesis_app` is what the API
connects as. The app role is not the owner, and every tenant table has `FORCE ROW LEVEL SECURITY`,
so a query without `SET LOCAL app.current_user_id` returns zero rows rather than someone else's data.

## Privacy rules in force (O-6, O-7)

- No prompt text is sent to any provider whose free tier may train on or human-review it.
- Only the text segment an agent needs leaves the machine — never the submission file, its filename,
  document metadata, images, the pseudonymisation mapping or any identifier.
- Identifiers found inside the text are deleted, not replaced with a stable per-student code.
- The provider client is the single egress point and re-checks each payload (phase 4).
- The frontend fetches from the API in the browser, so no hosting provider ever processes student text.

## Free-tier limits — checked 2026-10-06 (phase 1), re-check before the defence

All figures verified from the providers' own pages on the date shown; full evidence in
[`docs/phase-1/phase1-hosting-free-tiers.md`](./docs/phase-1/phase1-hosting-free-tiers.md).

| Service | Free tier | Notes |
| --- | --- | --- |
| Oracle Cloud Always Free | 2 OCPU / 12 GB ARM, 200 GB block volume, always-on | may be reclaimed if CPU, network **and** memory all stay under 20% for 7 days; card required at signup |
| Cloudflare Workers AI | 10,000 Neurons/day (≈0.3–1.1M input tokens depending on model) | no training on or sharing of Customer Content |
| Vercel Hobby | 2 GB / 1 vCPU functions, 300 s max duration | **"non-commercial personal use only"** — why the frontend is not hosted there |
| Render free | 512 MB / 0.1 CPU, sleeps after 15 min idle | not used |
| Supabase free | 500 MB DB, pauses after 7 days idle | not used |
| Neon free | 1 GB per project, scale-to-zero after 5 min | not used |
| Hugging Face Spaces | cpu-basic 2 vCPU / 16 GB | Gradio and Docker Spaces now need a paid PRO plan |

## Layout

```
backend/    FastAPI app, SQL migrations, tests (uv project)
frontend/   Next.js app (App Router, shadcn/ui)
scripts/    dev runner
docs/       phase-1 research evidence
PRD.md      the specification
DECISIONS.md  dated decision log
```
