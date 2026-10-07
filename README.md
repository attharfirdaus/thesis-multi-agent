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
| Database | Neon PostgreSQL 18 (Singapore) | LangGraph's checkpointer is Postgres/SQLite only; Neon's free tier carries no training-on-content clause and is covered by a DPA (PRD §8) |
| Hosting | Google Cloud Run for the API (`asia-southeast1`, Singapore); Next.js on Vercel Hobby | no server administration, no cold-start quota, and Cloud Build builds the image in the cloud (PRD §8) |
| Containers | none on the development machine | Cloud Build compiles the backend image from source in the cloud; local development uses uv + npm + Homebrew Postgres |

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

Uploaded documents are never stored. A submission file is parsed in memory on upload (PDF/DOCX via a
file-like object, no filesystem path), the extracted text is redacted, and the original binary is
discarded — there is no object store and no raw file on any host (PRD §8, O-3).

## Free-tier limits — Cloud Run and Neon checked 2026-10-07, re-check before the defence

Figures are from the providers' own pages on the dates shown. Cloud Run and Neon evidence lives in
[`docs/phase-2/`](./docs/phase-2/) (`arch-compute-platforms.md`, `arch-data-layer.md`); the earlier
provider survey is in [`docs/phase-1/phase1-hosting-free-tiers.md`](./docs/phase-1/phase1-hosting-free-tiers.md).

| Service | Free tier | Notes |
| --- | --- | --- |
| Google Cloud Run | 2M requests, 180,000 vCPU-s, 360,000 GiB-s/month, 1 GB egress; request timeout configurable to 3,600 s | perpetual always-free tier; card required to activate billing; free `*.run.app` HTTPS or a custom domain (docs/phase-2/arch-compute-platforms.md) |
| Neon | 1 GB/project (20 GB account cap), 100 CU-hrs/project/month; scale-to-zero after 5 min idle, auto-wake | Singapore `aws-ap-southeast-1`; PgBouncer transaction-mode pooler; no data deleted at the cap (docs/phase-2/arch-data-layer.md) |
| Cloudflare Workers AI | 10,000 Neurons/day (≈0.3–1.1M input tokens depending on model) | no training on or sharing of Customer Content |
| Vercel Hobby | 2 GB / 1 vCPU functions, 300 s max duration; frontend hosting only | **"non-commercial personal use only"** — the clause Atthar must own; Cloudflare Pages is the drop-in alternative (PRD §8) |
| Render free | 512 MB / 0.1 CPU, sleeps after 15 min idle | not used |
| Supabase free | 500 MB DB, pauses after 7 days idle | not used |
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
