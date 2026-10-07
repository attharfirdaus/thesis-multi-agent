# Phase-2 Runbook — Deploy the API to Cloud Run and the Database to Neon

Audience: anyone who has never opened a cloud console. Follow the steps in order. Each step is split
into a **Console** path (click through the web UI) and a **CLI** path (paste into a terminal); do
whichever you prefer — they produce the same result.

This runbook deploys the phase-2 skeleton: an empty FastAPI app with auth and the database schema.
The gate at the end (step 9) is the phase-2 gate from `PRD.md` §13 ("login works on the deployed URL").

Evidence base for every number below, all retrieved 2026-10-07:

- `docs/phase-2/arch-compute-platforms.md` — Cloud Run limits, free tier, build-from-source, regions
- `docs/phase-2/arch-data-layer.md` — Neon free tier, pooler behaviour, RLS, connection limits
- `docs/phase-2/arch-background-jobs.md` — how the batch runs without a server
- `docs/phase-2/arch-privacy-topology.md` — which providers may process data
- `docs/phase-2/phase2-version-pins.md` — pinned versions
- `PRD.md` §8 (stack), §11 (privacy), §13 (phases)

Decisions behind this topology are recorded in `DECISIONS.md` (O-2, O-3, O-5). `scripts/deploy-cloudrun.sh`
is the executable form of step 6.

---

## 0. What you are building

```
browser ──HTTPS──> Vercel (Next.js frontend)  ──HTTPS──> Cloud Run (FastAPI, asia-southeast1)
                                                                │  psycopg, pooled
                                                                ▼
                                                        Neon Postgres (aws-ap-southeast-1)
```

Two managed services, no server to patch. The frontend is a static/SSR host only; the browser calls the
API directly, so no frontend provider ever touches student text (`PRD.md` §11).

Accounts and tools you need first:

1. A Google Cloud account with billing enabled. A card is required to activate billing even while usage
   stays in the free tier (`arch-compute-platforms.md`: Cloud Run "Credit card required to activate GCP
   billing account").
2. A Neon account (card not required for the free plan — `arch-data-layer.md`).
3. A Vercel account (Hobby).
4. Locally: `gcloud` CLI, `uv` 0.12.23, and this repository checked out. No Docker is needed anywhere
   (`PRD.md` §8).

---

## 1. Create the Neon project in Singapore

**Console**

1. Sign in at <https://console.neon.tech> and choose **New Project**.
2. Name it `thesis-multi-agent`.
3. Under **Region**, pick **AWS Asia Pacific (Singapore)** — Neon's region id is `aws-ap-southeast-1`
   (`arch-data-layer.md`; also `arch-privacy-topology.md`, which confirms Singapore residency is what
   keeps the data-protection argument intact). Do not pick a US or EU region.
4. Under **Postgres version**, choose **18** (`phase2-version-pins.md` pins PostgreSQL 18.6).
5. Create the project. Neon shows two ready-made connection strings — note both (step 2).

**CLI** — Neon has no first-class CLI project-create flow in the free tier, so use the Console for
this one step, or the Neon API. The rest of this runbook is CLI-friendly.

---

## 2. Know the two connection strings (pooled vs. direct)

Neon exposes the same database over **two hostnames**:

| String | Host contains | What it is | Who uses it here |
| --- | --- | --- | --- |
| **Pooled** | `-pooler` in the hostname (Neon's convention) | Neon's PgBouncer in **transaction mode**: it multiplexes many client connections onto few Postgres backends. Free-tier direct limit is ≈104 connections (0.25 CU ≈ 97 usable); the pooler fans up to 10,000 client connections onto them (`arch-data-layer.md`) | The **app** (runtime), as `DATABASE_URL` |
| **Direct** | no `-pooler` | A plain connection straight to your compute | **Migrations** and any admin SQL (step 4) |

Why it matters — transaction-mode pooling is **not** transparent to psycopg3 (`arch-data-layer.md`):

- SQL-level `PREPARE`/`DEALLOCATE`, `SET`/`RESET`, `LISTEN/NOTIFY`, advisory locks and held cursors are
  **not supported** through the pooled endpoint. Session state does not survive between statements.
- The app therefore connects through the **pooled** string and sets psycopg's `prepare_threshold=None`
  so prepared statements are disabled across pooled backends (`PRD.md` §8). This is exactly the setup
  the app code already expects; you only supply the URLs.
- Migrations run **once**, by a human, over the **direct** string. Neon's own docs recommend the direct
  connection for schema changes and admin work (`arch-data-layer.md`).

Row-level security also depends on this: because a pooled backend is reassigned after every transaction,
the tenant context must be set with `SET LOCAL` inside the same transaction as the gated query — never a
plain `SET` (`arch-data-layer.md`, §3). The migration already does this.

`scripts/deploy-cloudrun.sh` treats the direct URL as a workstation-only value, and its comment shows
the expected direct shape:

```
postgresql://...@ep-xxxx.ap-southeast-1.aws.neon.tech/thesis?sslmode=require
```

---

## 3. Create the two database roles

The schema expects **two roles with different rights** (`backend/migrations/0001_init.sql`,
`backend/scripts/bootstrap_db.sh`):

- `thesis_migrator` — owns the schema, runs migrations.
- `thesis_app` — the runtime role the API connects as. It is deliberately **not** the table owner, and
  every tenant table has `FORCE ROW LEVEL SECURITY`, so a query without `SET LOCAL app.current_user_id`
  returns zero rows instead of another lecturer's data (`README.md`; `backend/migrations/0001_init.sql`).

Connect to Neon as the **project owner role** (the default `neondb_owner`, over the **direct** string —
role creation is DDL, which the pooler does not handle) and run:

```sql
create role thesis_migrator login password '<strong-password-1>';
create role thesis_app      login password '<strong-password-2>';

-- Mirrors backend/scripts/bootstrap_db.sh: the migrator may create objects; the app may connect.
grant connect on database neondb to thesis_migrator, thesis_app;
grant usage, create on schema public to thesis_migrator;
```

Then build the two URLs you will use later:

- `DATABASE_URL` = **pooled** string, user `thesis_app`, database `neondb`, `?sslmode=require`.
- `MIGRATION_DATABASE_URL` = **direct** string, user `thesis_migrator`, database `neondb`, `?sslmode=require`.

Treat both as secrets (step 5). Passwords never go in a file that is committed.

---

## 4. Apply the migrations

Migrations are **not** run at container start and **not** run by the deploy script
(`scripts/deploy-cloudrun.sh` header). Run them by hand, from a machine that can reach Neon, with the
**direct** URL:

```bash
cd backend
MIGRATION_DATABASE_URL='postgresql://thesis_migrator:<pw>@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require' \
  uv run python -m scripts.migrate
```

`scripts/migrate.py` reads `MIGRATION_DATABASE_URL` (preferred) or `DATABASE_URL`, applies
`migrations/*.sql` in filename order, and records each in `schema_migrations`. Re-running it is safe:
already-applied files are skipped. Migration `0001_init.sql` grants the runtime role its privileges
(`grant usage on schema public, app to thesis_app`, table/sequence/function privileges) **if
`thesis_app` already exists** — that is why you created both roles in step 3 before migrating.

Expected output on a fresh database: `applied: 0001_init.sql`.

Run this **before** the first Cloud Run deploy, or `/healthz` (step 9) reports `database: error`.

---

## 5. Put the secrets in Google Secret Manager

These values are secrets and must live in **Google Secret Manager**, never in the repository, never in
`--set-env-vars`, never in the deploy script (`PRD.md` §11; `arch-compute-platforms.md`):

| Secret | Value | Needed by |
| --- | --- | --- |
| `neon-database-url` | the **pooled** `DATABASE_URL` (runtime role `thesis_app`) | the Cloud Run service |
| `LLM_API_KEY` | the Cloudflare Workers AI API key (`LLM_API_KEY` in `backend/.env.example`) | phase 4; same manager, added then |

`MIGRATION_DATABASE_URL` is also a secret but is used only from the workstation in step 4 — it is never
given to the service. Cloud Run reads Secret Manager natively, mounted as an env var (`arch-compute-platforms.md`).

**Console**

1. Open **Secret Manager** → **Create secret**.
2. Name `neon-database-url`, paste the pooled URL, create.
3. Then **Add another secret**: `LLM_API_KEY` (can be a placeholder in phase 2, filled at phase 4).

**CLI**

```bash
gcloud secrets create neon-database-url --data-file=- <<< "$DATABASE_URL"
gcloud secrets create LLM_API_KEY --data-file=- <<< "$API_KEY"
```

Grant the Cloud Run service account `roles/secretmanager.secretAccessor` on each secret.

---

## 6. Deploy the Cloud Run service from source (no local Docker)

`gcloud run deploy --source ./backend` uploads the source to **Cloud Build**, which builds the container
in the cloud (`backend/Dockerfile`), pushes it to Artifact Registry and deploys. No Docker daemon runs
on your machine (`arch-compute-platforms.md`; `PRD.md` §8).

**Console**

1. **Cloud Run** → **Create service** → **Deploy from source repository / source**.
2. Region: **asia-southeast1 (Singapore)** — the same region family as Neon, and the region the privacy
   analysis assumed (`arch-compute-platforms.md`; `PRD.md` §11).
3. Set the flags from the script below in the UI equivalents (timeout 3600 s, memory 1 GiB, CPU 1,
   min instances 0, max instances 3, allow unauthenticated, env vars).

**CLI** — this is exactly `scripts/deploy-cloudrun.sh` (service name and region overridable via
`$SERVICE` / `$REGION`):

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

FRONTEND_ORIGIN='https://<deployed-frontend-origin>'   # set after step 7
gcloud run deploy thesis-multi-agent-api \
  --source ./backend \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --timeout 3600 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --set-env-vars "ENV=production,COOKIE_SECURE=true,ALLOWED_ORIGINS=[\"$FRONTEND_ORIGIN\"]"
```

Add the database URL from Secret Manager by appending (or with a follow-up
`gcloud run services update`):

```bash
  --set-secrets "DATABASE_URL=neon-database-url:latest"
```

Flag by flag:

- `--source ./backend` — Cloud Build builds in the cloud; no local Docker (`arch-compute-platforms.md`).
- `--timeout 3600` — the Cloud Run service maximum is 3,600 s (default 300 s). A batch makes several
  sequential LLM calls per submission (≈10–60 s each), so a whole small batch runs 10–60 minutes and
  must not be cut off at the 300 s default (`arch-background-jobs.md`; `arch-compute-platforms.md`).
  The end state decomposes the batch so each submission is its own invocation for retry granularity
  (`PRD.md` §8), but 3600 s is what lets a single small batch request complete meanwhile.
- `--min-instances 0` / `--max-instances 3` — scale to zero when idle; the cap bounds pressure on Neon,
  because each container opens its own psycopg pool and only `--max-instances` of them may exist at once
  (`arch-data-layer.md`; the script's own comment). Cold start is ~2–5 s and Cloud Run may keep an
  instance warm up to 15 minutes (`arch-compute-platforms.md`).
- `--allow-unauthenticated` — the API is a public web service behind the frontend.
- `--set-env-vars "ENV=production,COOKIE_SECURE=true,ALLOWED_ORIGINS=[...]"` — CORS and cookie settings;
  see step 8.

After deploy, note the service URL: `https://thesis-multi-agent-api-<hash>-as.a.run.app`
(the `*.run.app` hostname with free managed HTTPS — `arch-compute-platforms.md`).

---

## 7. Deploy the frontend to Vercel Hobby

The Next.js app deploys **separately** (frontend and API are not served from one origin here;
`PRD.md` §8).

1. Push the repository to GitHub.
2. In Vercel: **Add New → Project → Import** the repo. Set **Root Directory** to `frontend/`.
   Zero configuration; every `git push` redeploys.
3. Set an environment variable **`NEXT_PUBLIC_API_BASE`** to the Cloud Run URL from step 6, e.g.
   `https://thesis-multi-agent-api-<hash>-as.a.run.app` (this is the value `frontend/.env.example`
   documents for production). Redeploy so it is baked into the client bundle.
4. Note the deployed frontend origin, e.g. `https://thesis-multi-agent.vercel.app` — step 8 needs it.

**Clause to own.** Vercel Hobby is restricted to *"non-commercial personal use only"*, and its
definition reaches *"a paid employee or consultant writing the code"* (`arch-compute-platforms.md`;
`PRD.md` §8). This is a research thesis, so decide explicitly whether that applies. **Cloudflare Pages**
is the drop-in alternative with no such restriction (`PRD.md` §8) — connect the same repo and set the
same `NEXT_PUBLIC_API_BASE`; Next.js on Pages needs a build adapter, which is a frontend concern, not a
change to this runbook. No student text reaches either host — the browser calls the API directly
(`PRD.md` §11).

---

## 8. CORS and cookies in production

Two settings must match the deployed frontend or login will fail:

1. **`ALLOWED_ORIGINS`** must list the deployed frontend origin. The API's CORS middleware uses it as
   `allow_origins` with `allow_credentials=True` (`backend/app/main.py`; `backend/app/config.py`). Set
   it in step 6:
   ```
   ALLOWED_ORIGINS=["https://thesis-multi-agent.vercel.app"]
   ```
   It is a JSON list; add more origins inside the brackets. If the origin is missing, the browser
   refuses every credentialed response (the comment in `frontend/.env.example` says the same).
2. **`COOKIE_SECURE=true`** is required because the app is served over HTTPS. `backend/app/config.py`
   documents it: *"Must be true on the real host (HTTPS). False is for local http development only."*
   The session/CSRF cookies are set `Secure`, so they are only sent over HTTPS — which is exactly what
   Cloud Run's `*.run.app` TLS provides. The deploy script already sets it in `--set-env-vars`.

Optionally set `COOKIE_DOMAIN` to the API hostname if you use a custom domain, so cookies are not sent
to other subdomains (`backend/app/config.py`).

---

## 9. Verify — the phase-2 gate

**9a. Health check.** Hit `/healthz`; it runs `select 1` and reports the database state
(`backend/app/routers/health.py`):

```bash
curl -s https://thesis-multi-agent-api-<hash>-as.a.run.app/healthz
```

Expected: `{"status":"ok","env":"production","database":"ok"}`. A `503` with `"database":"error"` means
`DATABASE_URL` or the migrations (step 4) are wrong — the pooled URL must point at `thesis_app` and
`0001_init.sql` must be applied.

**9b. Browser walkthrough (this is the gate).** Open the deployed frontend URL and:

1. **Sign up** a lecturer account (`POST /auth/signup`).
2. **Log out** (`POST /auth/logout`).
3. **Log back in** (`POST /auth/login`), then confirm the session survives a refresh
   (`GET /auth/me`).

If all three succeed in a real browser against the deployed URL, the **phase-2 gate passes** — `PRD.md`
§13: *"Skeleton … Gate: login works on the deployed URL."* Because sign-up, login and the session
cookie all exercised the pooled Neon connection end to end, this simultaneously proves CORS,
`COOKIE_SECURE`, the two roles and RLS are wired correctly.

---

## 10. Cost and free tier (dated)

All figures are from the providers' own pages, retrieved **2026-10-07**, and cited to the phase-2 file
that captured them:

| Service | Free tier | Source |
| --- | --- | --- |
| Google Cloud Run | Perpetual always-free: 2,000,000 requests, 180,000 vCPU-seconds, 360,000 GiB-seconds per month, 1 GB egress. Request timeout configurable up to 3,600 s (default 300 s). Card required to activate billing; overage at PAYG | `docs/phase-2/arch-compute-platforms.md` |
| Neon | 1 GB storage per project (20 GB account cap), 100 CU-hours/project/month, autoscale to 2 CU. Scale-to-zero after 5 min idle, auto-wake ~100–300 ms. No data deleted at the cap | `docs/phase-2/arch-data-layer.md` |
| Vercel Hobby | 2 GB / 1 vCPU functions, 300 s max duration; non-commercial personal use only | `docs/phase-2/arch-compute-platforms.md`; `PRD.md` §8 |
| Cloudflare Workers AI | 10,000 Neurons/day (≈0.3–1.1M input tokens depending on model); no training on Customer Content | `PRD.md` §11 (no-training rule); `README.md` free-tier table |

Steady state for a single thesis pilot: both Cloud Run and Neon bills stay at $0 as long as the batch
stays inside those monthly grants; Neon scaling to zero only adds a ~100–300 ms wake to the first query
(`arch-data-layer.md`). Re-check the providers' pages before the defence — the numbers change
(`README.md`).

## 11. Not verified / gaps

- **Neon project-create via CLI/API** is not a documented first-class free-tier flow; step 1 uses the
  Console. Not exercised end to end in this runbook.
- **Creating the two roles on Neon** — the SQL mirrors `backend/scripts/bootstrap_db.sh`, but Neon's
  permission surface for `create role` from the owner role was not tested against a live project here.
- **The `-pooler` hostname convention** is Neon's documented naming; the free-tier/pooler *behaviour* is
  in `arch-data-layer.md`, but the exact hostname string was not re-fetched today.
- **`--max-instances 3` connection math** against Neon's `max_connections` was reasoned from
  `arch-data-layer.md` figures, not measured on a live deployment; confirm the in-container pool size
  before raising the cap.
- **Cloud Run request timeout of 3600 s** is the documented maximum (`arch-compute-platforms.md`), but
  whether a full 100-submission batch fits one request is a phase-4 measurement, not assumed here.
- **Vercel Hobby vs. Cloudflare Pages** — the non-commercial clause is quoted from `PRD.md` §8 /
  `arch-compute-platforms.md`; the final host choice is Atthar's to own.
- **Secret Manager IAM grant** (`secretAccessor`) is the expected role but was not exercised against a
  live project in this runbook.
