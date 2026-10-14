# Phase-2 Runbook — Run the API locally against Neon (optional public URL)

Supersedes `phase2-render-neon-runbook.md`, deleted 2026-10-14. The backend is **not** hosted on any
cloud platform: every card-requiring provider is closed to the owner — Google Cloud rejects the card
at billing setup (`OR_MIVEM_02`) and Render asked for a card in the manual Web Service flow too
(`docs/phase-2/billing-free-hosts.md`). This is a hard constraint, not a preference. The backend runs
on the owner's Mac; Neon (Singapore) still holds the database; Vercel still serves the frontend.

Gate for this phase is the phase-2 gate in `PRD.md` §13: *"login works on the deployed URL."*

Evidence base for every number below:

- `docs/phase-2/billing-free-hosts.md` — why every card-requiring host is closed (2026-10-14)
- `docs/phase-2/arch-data-layer.md` — Neon free tier, pooler behaviour, roles, RLS (2026-10-07)
- `PRD.md` §8, §11, §13; `DECISIONS.md`; `README.md`; `scripts/dev.sh`; `backend/.env.example`

## 1. What is already done — do not redo it

- **Neon project exists**, `thesis-multi-agent`, region **AWS Asia Pacific (Singapore)**
  (`aws-ap-southeast-1`), PostgreSQL 18. Both roles and the migrated schema are already there; §2
  records what they require, should the project ever need recreating.
- **The frontend is live** on Vercel Hobby at <https://thesis-multi-agent.vercel.app>.
- **No cloud backend host exists and none will be created.** Do not re-open the Cloud Run or Render
  paths — both demanded a card.
- **Do not create a Render Postgres.** It expires 30 days after creation and is then deleted with all
  its data (`arch-data-layer.md`). Neon is the database.

## 2. Neon — what still has to be right

Two roles with different rights (`backend/migrations/0001_init.sql`, `backend/scripts/bootstrap_db.sh`):

| Role | Owns | Used by | URL |
| --- | --- | --- | --- |
| `thesis_migrator` | the schema; runs migrations | you, from the Mac | **direct** — no `-pooler` in the host |
| `thesis_app` | nothing — deliberately **not** the table owner | the API at runtime | **pooled** — `-pooler` in the host |

Same database, two hostnames: the **pooled** one is PgBouncer in transaction mode (free tier fans up
to 10,000 client connections onto ≈104 direct ones, 0.25 CU ≈ 97 usable); the **direct** one goes
straight to the compute (`arch-data-layer.md`). Create both roles through Neon's **SQL** interface:
SQL-created roles miss the `neon_superuser` membership that carries `BYPASSRLS`, so `thesis_app` stays
subject to the `FORCE ROW LEVEL SECURITY` policies and a query without
`SET LOCAL app.current_user_id` returns zero rows instead of another lecturer's data
(`neon.com/docs/manage/roles`, read 2026-10-07).

Migration — once, by hand, direct URL only:

```bash
cd backend
MIGRATION_DATABASE_URL='postgresql://thesis_migrator:<pw>@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require' \
  uv run python -m scripts.migrate
```

Expected on a fresh database: `applied: 0001_init.sql`, then `0002_no_raw_document_storage.sql`. The
runner applies `migrations/*.sql` in filename order and records each in `schema_migrations`, so
re-running is safe. `0001_init.sql` grants `thesis_app` its privileges only if that role already
exists — create both roles first.

**Password warning.** Use plain alphanumerics for both role passwords. Characters a connection URL
treats as syntax (`@ : / ? # %`) must be percent-encoded, and every copy-paste of the URL — into
`.env`, a shell, a Vercel dashboard field — is a place that encoding gets lost. Alphanumeric passwords
remove the whole class of failure. Keep `sslmode=require` in both URLs.

## 3. Run the whole stack locally

```bash
cd backend && cp -n .env.example .env      # first time only
cd ../frontend && cp -n .env.example .env.local
./scripts/dev.sh
```

`scripts/dev.sh` starts Homebrew PostgreSQL 18 if it is not already listening, applies migrations,
then runs the API (`uvicorn --reload`, port 8000) and the web app (`npm run dev`, port 3000)
together; Ctrl-C stops both applications and leaves Postgres running as a service. Expect API
<http://localhost:8000/docs> and web <http://localhost:3000>.

To point the local API at **Neon** instead of local Postgres, put the pooled URL in `DATABASE_URL` and
the direct URL in `MIGRATION_DATABASE_URL` in `backend/.env`; `dev.sh`'s migrate step picks up
`MIGRATION_DATABASE_URL`. For the defence itself, keep both on local Postgres.

**Docker is optional and not required.** The project runs natively (uv + npm + Homebrew Postgres) and
`dev.sh` involves no containers. `docker build backend/` still works if you want production parity
locally: the image is `python:3.13-slim`, exposes 8080, binds to `${PORT:-8080}`.

Confirm it works: `curl -s http://localhost:8000/healthz` → `{"status":"ok","env":"...","database":"ok"}`
(a 503 with `"database":"error"` means `DATABASE_URL` is wrong). Then in the browser **sign up →
log out → log back in** and refresh; the session must survive.

## 4. Optional: a public URL with a Cloudflare Quick Tunnel

Quick Tunnels need **no account and no card**. Install `cloudflared`, then:

```bash
cloudflared tunnel --url http://localhost:8000
```

It prints a public `https://<random>.trycloudflare.com` URL. Caveats: the URL **changes every run**; the
Mac and the tunnel must stay **running**; and Cloudflare documents Quick Tunnels as intended for
**testing/development**, not production.

## 5. The cookie consequence — the part that bites

With the frontend on `vercel.app` and the API on `trycloudflare.com`, the request is **cross-site**.
A `SameSite=Lax` cookie is not sent on a cross-site fetch, so login would appear to succeed and the
next request would be unauthenticated. Fix on the **API**:

```
COOKIE_SAMESITE=none
COOKIE_SECURE=true
ALLOWED_ORIGINS=["https://thesis-multi-agent.vercel.app"]
```

Browsers only accept `SameSite=None` when it is also `Secure`, and `Secure` requires HTTPS — both hold
on the tunnel. `ALLOWED_ORIGINS` stays exactly the deployed frontend origin: scheme + host, no trailing
slash, JSON list.

When both run on localhost (the default in `backend/.env.example`), keep `COOKIE_SAMESITE=lax` and
`COOKIE_SECURE=false` — the default for both in `backend/app/config.py`.

## 6. Pointing Vercel at the tunnel

Set `NEXT_PUBLIC_API_BASE` to the tunnel URL in Vercel and redeploy. It is inlined into the client
bundle **at build time**, so every new tunnel URL needs its own redeploy. Recommended order: run the
**fully local** stack for the defence itself, and use the tunnel only to let supervisors look beforehand.

## 7. Verification checklist

1. `curl -s http://localhost:8000/healthz` → `database: ok`.
2. Sign up, log out, log back in; refresh and stay logged in (`GET /auth/me`).
3. Local model only: cookie is `SameSite=Lax`, no `Secure` — visible in browser devtools.
4. Tunnel model: response is HTTPS, cookie is `SameSite=None; Secure`, and `Origin` is echoed only for
   `https://thesis-multi-agent.vercel.app`.
5. Vercel build uses the current tunnel URL, not a stale one.

## 8. Not verified / gaps

- **Quick Tunnels were not exercised end to end** for this project — no tunnel was created, and the
  cross-site cookie behaviour in §5 is derived from the `SameSite` rules, not observed here.
- **The Vercel rebuild was not exercised**; how fast the new `NEXT_PUBLIC_API_BASE` reaches the live
  bundle was not measured.
- Neon figures in §2 are quoted from `arch-data-layer.md` (2026-10-07) and not re-fetched; free-tier
  terms change without notice.
- `PRD.md` §8 and `README.md` still describe Render as the backend host. They were not edited here.
