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
| Hosting | API runs locally on this machine; a Cloudflare Quick Tunnel publishes it at a public HTTPS URL for remote demos. Next.js on Vercel Hobby | every managed host requires a card whose verification fails, so local plus tunnel is the only free route left (PRD §8, `DECISIONS.md`) |
| Containers | optional | `scripts/dev.sh` runs the stack natively; the same `backend/Dockerfile` builds with `docker build backend/` when image parity matters |

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

To let someone else open the app (a supervisor, for example), publish the API through a Cloudflare
Quick Tunnel — no account, no card:

```bash
cloudflared tunnel --url http://127.0.0.1:8000     # prints a public https://….trycloudflare.com URL
```

Then run the API with `COOKIE_SAMESITE=none` and `COOKIE_SECURE=true`, and point Vercel's
`NEXT_PUBLIC_API_BASE` at that URL. With `lax` the login appears to succeed and the very next request
returns 401, because the browser withholds the cookie on a cross-site fetch — measured, not assumed
(`DECISIONS.md`, 2026-10-14). Full walkthrough: `docs/phase-2/phase2-local-neon-runbook.md`.

Two database roles exist on purpose: `thesis_migrator` owns the schema, `thesis_app` is what the API
connects as. The app role is not the owner, and every tenant table has `FORCE ROW LEVEL SECURITY`,
so a query without `SET LOCAL app.current_user_id` returns zero rows rather than someone else's data.

> **Never point `DATABASE_URL` at the Neon owner role.** `thesis_owner` is a member of
> `neon_superuser`, so it carries `BYPASSRLS` and every tenancy policy silently stops applying —
> verified on this project's Neon database on 2026-10-14 (`rolbypassrls = true` for the owner,
> `false` for `thesis_app` and `thesis_migrator`). The pooled URL with `thesis_app` is the runtime
> connection; the direct URL with `thesis_migrator` is only for migrations.

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

## Free-tier limits and the hosting constraint — checked 2026-10-14, re-check before the defence

Figures are from the providers' own pages on the dates shown. Evidence lives in
[`docs/phase-2/`](./docs/phase-2/) (`cardfree-paas.md`, `arch-data-layer.md`); the earlier
provider survey is in [`docs/phase-1/phase1-hosting-free-tiers.md`](./docs/phase-1/phase1-hosting-free-tiers.md).

| Service | Free tier | Notes |
| --- | --- | --- |
| Render · Cloud Run · Koyeb · Fly · Railway · Northflank | **not usable** | every one requires a payment card, and the owner's card fails verification at all of them (Google `OR_MIVEM_02`; Render asked for a card even on the manual free path) |
| Neon | 1 GB/project (20 GB account cap), 100 CU-hrs/project/month; scale-to-zero after 5 min idle, auto-wake | Singapore `aws-ap-southeast-1`; PgBouncer transaction-mode pooler; runtime role must be `thesis_app`, never the owner role (see the warning above) |
| Cloudflare Workers AI | 10,000 Neurons/day (≈0.3–1.1M input tokens depending on model) | no training on or sharing of Customer Content |
| Cloudflare Quick Tunnel | free, no account required | temporary public HTTPS URL for the local API; documented as development-only, and the URL changes on each restart |
| Vercel Hobby | 2 GB / 1 vCPU functions, 300 s max duration; frontend hosting only | **"non-commercial personal use only"** — the clause Atthar must own; Cloudflare Pages is the drop-in alternative (PRD §8) |

## Layout

```
backend/    FastAPI app, SQL migrations, tests (uv project)
frontend/   Next.js app (App Router, shadcn/ui)
scripts/    dev runner
docs/       phase-1 research evidence
PRD.md      the specification
DECISIONS.md  dated decision log
```
