# Phase-2 Runbook — Deploy the API to Render (Free) and the Database to Neon

Supersedes `phase2-cloudrun-neon-runbook.md`, deleted 2026-10-14. Cloud Run was dropped because
activating a GCP billing account requires a credit card, which the owner cannot supply; Render is the
only card-free host that fits the design (verified 2026-10-14 — `local://cardfree-paas.md`). No
`gcloud` CLI, no Cloud Build, no Secret Manager and no `*.run.app` URL anywhere in this flow.

This deploys the phase-2 skeleton: an empty FastAPI app with auth and the database schema. The gate is
the phase-2 gate in `PRD.md` §13: *"login works on the deployed URL."*

Evidence base for every number below:

- `local://cardfree-paas.md` — Render card-free verification, free-tier limits, caveats (2026-10-14)
- `docs/phase-2/arch-data-layer.md` — Neon free tier, pooler behaviour, RLS, roles, connection limits (2026-10-07)
- `docs/phase-2/arch-privacy-topology.md` — which providers may process student data, and why
- `docs/phase-2/phase2-version-pins.md` — pinned versions (Python 3.13, PostgreSQL 18.6, uv 0.12.23)
- `PRD.md` §8 (stack), §11 (privacy); `DECISIONS.md`

## 0. What is already done — do not redo it

- **Neon project exists.** Name `thesis-multi-agent`, region **AWS Asia Pacific (Singapore)**
  (`aws-ap-southeast-1`), PostgreSQL 18. Both roles and the migrated schema are already there; §1–2
  record what they require, should the project ever need recreating.
- **The frontend is live** on Vercel Hobby at <https://thesis-multi-agent.vercel.app>. Only its
  `NEXT_PUBLIC_API_BASE` needs repointing at the Render URL (step 5b).
- **No GCP account is involved any more.** Do not create one, and ignore the old runbook.
- **Do not create a Render Postgres.** Free Render Postgres databases expire 30 days after creation
  (14-day grace, then deleted with all data — `arch-data-layer.md`), have no pooler and no backups.
  Neon is the database.

```
browser ──HTTPS──> Vercel (Next.js frontend) ──HTTPS──> Render Free web service (FastAPI, Singapore)
                                                              │  psycopg, pooled (-pooler host)
                                                              ▼
                                                      Neon Postgres (aws-ap-southeast-1)
```

## 1. Neon — the two roles and the two URLs

The schema expects two roles with different rights (`backend/migrations/0001_init.sql`,
`backend/scripts/bootstrap_db.sh`):

| Role | Owns | Connects as | URL |
| --- | --- | --- | --- |
| `thesis_migrator` | the schema; runs migrations | a human, from a workstation | **direct**, no `-pooler` in the host |
| `thesis_app` | nothing — deliberately **not** the table owner | the API at runtime | **pooled**, `-pooler` in the host |

Neon exposes the same database over two hostnames: the **pooled** one is PgBouncer in **transaction
mode**, fanning up to 10,000 client connections onto the free tier's ≈104 direct ones (0.25 CU ≈ 97
usable); the **direct** one goes straight to the compute (`arch-data-layer.md`).

Transaction-mode pooling is not transparent to psycopg3: SQL-level `PREPARE`/`DEALLOCATE`,
`SET`/`RESET`, `LISTEN/NOTIFY`, advisory locks and held cursors are unsupported through it, and session
state does not survive between statements. The app already handles this — pooled URL,
`prepare_threshold=None`, and every tenant context set with `SET LOCAL` inside the same transaction as
the gated query, never a plain `SET`, which would leak the tenant to the next client reusing that
backend (`arch-data-layer.md`; `DECISIONS.md`). You only supply the URLs.

**Why the RLS design holds.** Roles created through Neon's **SQL** interface get only basic
public-schema privileges; they do **not** get the `neon_superuser` membership (which carries
`BYPASSRLS`) that Console-, CLI- or API-created roles receive (`neon.com/docs/manage/roles`, read
2026-10-07). `thesis_app` is therefore subject to the policies, and every tenant table is `FORCE ROW
LEVEL SECURITY` — a query without `SET LOCAL app.current_user_id` returns zero rows instead of another
lecturer's data.

## 2. Apply the migrations (direct URL only)

Migrations run **once, by hand**, from a machine that can reach Neon. They are never run at container
start and never by the deploy path:

```bash
cd backend
MIGRATION_DATABASE_URL='postgresql://thesis_migrator:<pw>@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require' \
  uv run python -m scripts.migrate
```

`scripts/migrate.py` prefers `MIGRATION_DATABASE_URL`, applies `migrations/*.sql` in filename order and
records each in `schema_migrations`, so re-running is safe. Expected on a fresh database:
`applied: 0001_init.sql`. `0001_init.sql` grants `thesis_app` its privileges only if that role already
exists — which is why both roles were created before migrating.

## 3. Render — create the Free web service

**Do not use the Blueprint flow — it is the one path that asks for payment information.** Render's
public API declares `402 Payment Required` ("You must enter payment information to perform this
request") on `POST /services`, which is the endpoint a Blueprint uses to create a service; a 2026 user
report describes the same thing — "Blueprint deployment also requires a card on file" — and reports
that creating the service by hand worked instead. Render's own tutorial, by contrast, states:
"This tutorial uses free Render resources. **No payment is required.**"

Create it by hand: **New → Web Service → Build and deploy from a Git repository**, then set:

| Field | Value |
| --- | --- |
| Service type | Web Service |
| Source | the GitHub repo, branch `main` |
| Runtime | **Docker** |
| Root Directory | `backend` |
| Dockerfile Path | `./Dockerfile` |
| Instance Type | **Free** |
| Region | **Singapore** |
| Health Check Path | `/healthz` |
| Auto-Deploy | Yes (every push to `main` redeploys) |

`render.yaml` in the repository records the same configuration. It sets `plan: free` deliberately:
Render's Blueprint spec says that **omitting** the plan field makes it default to a paid `0.5c-512mb`
instance, which is exactly the kind of default that turns a free deploy into a payment prompt.

- **Runtime Docker** reuses `backend/Dockerfile` unchanged; the free plan supports Docker builds.
- **Free instance** is 0.1 CPU / 512 MB RAM — the bottom edge of the backend's estimated ≈250–400 MB
  resident floor after the model weights were removed (O-4, `DECISIONS.md`).
- **Region Singapore** keeps compute in the same city as Neon, which the privacy analysis assumes
  (`arch-privacy-topology.md`; `PRD.md` §11), and avoids a cross-region round trip per query.
- **Render injects `PORT`** and routes to it. `backend/Dockerfile` already ends with
  `CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]` and `EXPOSE 8080`,
  so nothing needs overriding — the image binds to whatever port Render sets.

## 4. Environment variables on Render

Set these in the service's **Environment** tab. None of them belongs in the repository:

| Key | Value | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql://thesis_app:<pw>@ep-xxxx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require` | **the pooled host** (`-pooler` in it), runtime role `thesis_app`, `sslmode=require` kept. Set as a **secret** — never in `render.yaml`, never in the repo |
| `ENV` | `production` | selects production settings (`backend/app/config.py`) |
| `COOKIE_SECURE` | `true` | required over HTTPS; `false` is for local http development only |
| `ALLOWED_ORIGINS` | `["https://thesis-multi-agent.vercel.app"]` | JSON list used as CORS `allow_origins` with credentials; a missing origin makes the browser refuse every credentialed response |

- `MIGRATION_DATABASE_URL` is a secret too, but it is used **only** from the workstation in step 2 —
  never given to the service. `LLM_API_KEY` (Cloudflare Workers AI) is added in phase 4, the same way.
- Leave `COOKIE_DOMAIN` blank on Render's default `*.onrender.com` host; set it only for a custom
  domain. Saving any variable restarts the service.

## 5. Verify — the phase-2 gate

**5a. Health check.** `/healthz` runs `select 1` (`backend/app/routers/health.py`):

```bash
curl -s https://<service-name>.onrender.com/healthz
```

Expected: `{"status":"ok","env":"production","database":"ok"}`. A `503` with `"database":"error"` means
`DATABASE_URL` or step 2 is wrong. The **first** request after 15 idle minutes waits ~1 minute for the
cold start (`local://cardfree-paas.md`) — do not read that as a failure.

**5b. Point the frontend at Render.** In Vercel set `NEXT_PUBLIC_API_BASE` to the Render service URL and
redeploy so it enters the client bundle. Then, in a real browser against the deployed frontend: **sign
up** (`POST /auth/signup`), **log out** (`POST /auth/logout`), **log back in** (`POST /auth/login`) and
confirm the session survives a refresh (`GET /auth/me`). All three succeeding **passes the phase-2
gate**; because they exercised the pooled Neon connection end to end, they also prove CORS,
`COOKIE_SECURE`, the two roles and RLS are wired correctly.

## 6. Free-tier facts and accepted risks (dated 2026-10-14)

All from `local://cardfree-paas.md` unless noted.

- **No card** is required to sign up or to deploy a free service; a payment method is optional.
- **750 free instance hours per workspace per month** — more than a 31-day month (744 h), so one
  always-on service fits, but exhausting the grant suspends all free web services until next month.
- **Spins down after 15 minutes with no inbound traffic**; cold start ≈1 minute. Free services "might
  restart at any time". **5 GB egress/month** on Hobby (then $0.15/GB), and **service-initiated** traffic
  counts — this app's LLM API calls and its Neon queries included.
- **Suspension risk, named:** Render *"may suspend a Free web service that initiates an uncommonly high
  volume of traffic over the public internet"*, with *"Accessing an external database"* and *"Invoking
  external APIs"* as the examples — exactly this app's traffic pattern. Accepted because no card-free
  alternative fits; Modal Starter is the fallback runner, and the batch checkpoints in Postgres
  (`DECISIONS.md`) so a restart mid-batch loses at most one submission's work.
- **Privacy.** Render's Singapore region and subprocessor list are confirmed; its `/terms`, `/privacy`
  and `/dpa` pages are JS-rendered and their body text could not be read (`arch-privacy-topology.md`) —
  re-check them in a browser before the defence. Neon remains acceptable: DPA covers the free plan, no
  training on Customer Content, Singapore region.

## 7. Not verified / gaps

- This runbook was **not exercised against a live Render account**; every Render limit above is quoted
  from Render's own pages via `local://cardfree-paas.md`, not observed. Render also does not validate
  `render.yaml` against the table in §3 here — the file is the source of truth, and free-tier terms can
  change without notice.
- **Render's 100-minute HTTP response limit** appears on the render-vs-heroku comparison page, not the
  web-services or free-tier pages — provisional. Whether a forced restart aborts an in-flight request is
  unstated.
- **The exemption of SQL-created Neon roles from `BYPASSRLS`** rests on `neon.com/docs/manage/roles` as
  read 2026-10-07 (carried over from the retired runbook): not re-fetched, not exercised.
- **RAM headroom** (the ≈250–400 MB estimate vs a 512 MB instance) must be measured on Render, not
  assumed.
