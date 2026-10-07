# Data Layer Architecture — Managed Postgres + Object Storage for a Serverless FastAPI Backend

Scope: PostgreSQL candidates (free tier), serverless-client/pooler semantics for psycopg3 + SQLAlchemy + `langgraph-checkpoint-postgres`, Row-Level Security support, and whether object storage is needed at all.

All facts below were fetched from primary provider/driver documentation **today, 2026-10-07**; URL + access date accompanies every claim. `[UNVERIFIED: reason]` marks anything not confirmed on a primary page today.

---

## 1. Managed PostgreSQL comparison

### 1a. Genuinely free today, viable for a persistent backend

| Provider | Free storage/compute | Suspend/pause rule | Wake | Conn. limit (direct/pooled) | Pooler (mode) | Backups (free) | SEA region | On exceeding limit |
|---|---|---|---|---|---|---|---|---|
| **Neon** | 1 GB/project (20 GB account cap), 100 CU‑hrs/project/mo, autoscale to 2 CU | Scale‑to‑zero after **5 min idle**, fixed on Free (cannot disable) | Automatic, ~100–300 ms on next query | 0.25 CU ≈ 104 direct (97 usable); pooled up to 10,000 client conns via PgBouncer | Yes — **PgBouncer, transaction mode** (`pool_mode=transaction`); protocol‑level prepared statements supported (PgBouncer ≥1.22) | PITR 6 h / ≤1 GB change history, 1 manual snapshot; no scheduled backups | Yes — `aws-ap-southeast-1` (Singapore) | No auto‑billing; compute suspended until next cycle/upgrade; writes blocked at storage cap; **no data deleted** |
| **Supabase** | 500 MB DB, 500 MB RAM (Micro), 1 GB file storage, 5 GB egress, 2 active projects/org | **Paused after 1 week of inactivity** | Manual unpause via dashboard (exact auto‑wake‑on‑connect trigger `[UNVERIFIED: dedicated /docs/guides/platform/pause page 404'd]`) | 60 direct / 200 pooled (Micro) | Yes — **Supavisor**, both session (5432) and transaction (6543) mode; dedicated PgBouncer is paid‑only | None on Free; manual `supabase db dump` recommended | Yes — `ap-southeast-1` (Singapore) | `[UNVERIFIED: exact behavior past 500 MB/5 GB — hard block vs read-only not stated]` |
| **Aiven for PostgreSQL** | 1 VM, 1 CPU, 1 GB RAM, 1 GB disk | Aiven may power off services with no initial or continuing activity (warning sent first) | **Manual** restart | `max_connections = 20` | **None** — explicitly no pooling on free tier | Included; single backup only, no PITR | Listed as available (`sgp`) but free‑tier docs separately say region can't be chosen — **contradictory** `[UNVERIFIED]` | Hard resource cap; idle → powered off, not deleted |
| **CockroachDB Basic (Serverless)** | $15/mo free resource credit = 50M RU + 10 GiB storage/org/mo | Scales to zero on idle (no cost) | Automatic on next request | `[UNVERIFIED: not stated]` | `[UNVERIFIED: not stated on fetched page]` | `[UNVERIFIED]` | `[UNVERIFIED: Singapore not confirmed]` | RU exhausted → cluster **disabled** until next cycle/raise; storage cap → writes blocked; no auto-delete |
| **YugabyteDB Aeon Sandbox** | "Free forever" single‑node sandbox | `[UNVERIFIED]` | `[UNVERIFIED]` | `[UNVERIFIED]` | `[UNVERIFIED]` | `[UNVERIFIED]` | `[UNVERIFIED]` | `[UNVERIFIED]` — explicitly **not for production** |
| **Nile** (multi‑tenant Postgres) | 1 GB storage, 50M query tokens/mo (abstracted compute unit, no vCPU/RAM figure) | **Never pauses** — "no cold start time on the free tier," always on | N/A (always on) | 500 connections (not split direct/pooled) | Listed as included, but software + mode **not named** `[UNVERIFIED]` | **Not available** — "Coming soon" on every tier including free | Listed as "All" but Singapore not individually named `[UNVERIFIED]` | No auto-suspend/auto-bill; notified at 70%, can pay for more capacity even on free tier |
| **Prisma Postgres** | 200,000 ops/mo, 1.01 GB storage, 50 DBs; billed by operation not compute‑time | No documented suspend state found `[UNVERIFIED]` | N/A | 10 pooled / 10 direct, 60‑min idle timeout | Yes — **dedicated PgBouncer** instance per DB (mode not named) + separate HTTP driver for edge runtimes | None on Free; Starter+ only (7‑day retention) | Yes — `ap-southeast-1` (Singapore) | `[UNVERIFIED: exact overage mechanism]`; fixed 10 s query timeout even on Free |
| **Koyeb Postgres** | 0.25 vCPU, 1 GB RAM, 1 GB data, **5 compute‑hrs/month cap** | Auto‑sleep after 5 min idle | **Automatic** on next query | ≈112 (computed from RAM), pooled figure undocumented | Not documented — appears direct‑only `[UNVERIFIED]` | `[UNVERIFIED: not stated]` | Yes — **Singapore explicitly confirmed** (with Frankfurt, Washington D.C.) | `[UNVERIFIED: behavior after 5 compute-hrs/mo exhausted not stated]` |

### 1b. Free but not durable / unsuitable

| Provider | Verdict | Why | Source |
|---|---|---|---|
| **Render Postgres** | Free, but **expires 30 days after creation** regardless of usage, 14‑day grace, then **permanently deleted**. No pooler, no backups on free. 256 MB RAM / 1 GB storage, 100 conns. | Hard calendar deletion makes it unusable as a persistent $0 backend without a recurring manual recreate+migrate cycle. | render.com/pricing, render.com/docs/free (2026-10-07) |
| **Xata** | **No free hosted tier at all** today. Only free self-hosted OSS (Apache 2.0, you host it) or a 14‑day Cloud trial requiring a card afterward. | Pricing-page FAQ states verbatim: "Is there a free tier? No." | xata.io/pricing (2026-10-07) |
| **Tembo** | **Not a Postgres hosting product anymore.** Company pivoted to an AI coding‑agent SaaS platform; "Postgres" feature is a read-only monitoring integration against a user‑supplied existing DB. | docs.tembo.io/integrations/postgres, tembo.io/pricing (2026-10-07) |

### 1c. No current free tier (confirmed rejected)

| Provider | Reason | Source |
|---|---|---|
| Railway Postgres | No dedicated free DB product; only $1/mo or one-time $5 trial usage credit, consumed almost immediately by a DB workload | railway.com/pricing (2026-10-07) |
| Fly.io (Managed Postgres) | Cheapest plan $38/mo; no free cluster | fly.io/pricing (2026-10-07) |
| Google Cloud SQL | No always-free tier; only a 30-day free-trial instance or generic $300/90-day account credit, both expire with a deletion grace period | docs.cloud.google.com/sql/docs/postgres/free-trial-instance; docs.cloud.google.com/free/docs/free-cloud-features (2026-10-07) |
| DigitalOcean Managed PG | Starts at $15.15/mo, no free tier | digitalocean.com/products/managed-databases-postgresql (2026-10-07) |
| Timescale Cloud | Managed cloud is consumption-billed from day one; only self-hosted extension is free | (2026-10-07) |
| EDB BigAnimal | 14-day trial only | enterprisedb.com (2026-10-07) |
| Clever Cloud | Explicit company policy: no free tier | clever.cloud/blog (2026-10-07) |
| ScaleGrid | 7–30 day trial only | help.scalegrid.io (2026-10-07) |
| Turso | Free tier exists but it's **SQLite**, not Postgres — excluded | turso.tech/pricing (2026-10-07, via search) |

**Verdict on PostgreSQL provider:** for a persistent $0 backend that must survive indefinitely without manual recreation, the realistic candidates are **Neon** (best overall: generous SEA region, documented pooler semantics, scale-to-zero with automatic wake, no data loss on overage) or **Supabase** (comparable, but weekly-inactivity pause needs a keep-alive or accepted manual-unpause workflow). Nile is attractive for "never pauses" but its pooler mode and backups are undocumented/absent. Aiven is viable but has no pooler at all and only 20 connections.

---

## 2. Serverless-client / pooler semantics (psycopg3 + SQLAlchemy + langgraph-checkpoint-postgres)

### What breaks through a transaction-mode pooler
Source: psycopg docs (psycopg.org/psycopg3/docs/advanced/prepare.html, pool.html, 2026-10-07); PgBouncer docs (pgbouncer.org/config.html, pgbouncer.org/faq.html, 2026-10-07); Neon/Supabase pooling docs (2026-10-07).

- **Prepared statements**: psycopg3 auto-prepares a query after `Connection.prepare_threshold` (default 5) executions, using protocol-level `PQsendPrepare`/`PQsendQueryPrepared` — not SQL `PREPARE`. psycopg's own docs state plainly: *"Unless a connection pooling middleware explicitly declares otherwise, they are not compatible with prepared statements… you should disable prepared statements, by setting the `Connection.prepare_threshold` attribute to `None`."*
  - As of psycopg 3.2, protocol-level prepared statements **are** supported through PgBouncer, but **only** if: PgBouncer ≥ 1.22, `max_prepared_statements > 0` server-side, **and** the client's libpq is built against PostgreSQL 17+ (check via `Capabilities().has_send_close_prepared()`). If libpq 17 isn't available, prepared statements can still be used if deallocation is disabled (`Connection.prepared_max = None`).
  - SQL-level `PREPARE`/`EXECUTE`/`DEALLOCATE` are **never** supported through PgBouncer in transaction mode (forwarded straight to whatever backend happens to be attached, which is wrong).
- **Session state** (`SET`, `LISTEN/NOTIFY`, temp tables, session advisory locks, `WITH HOLD` cursors) does **not** survive between statements in transaction mode — the server connection returns to the pool after every transaction, not after client disconnect. `SET` must be scoped per-transaction (`SET LOCAL`) or avoided.
- **Connection reuse**: a client's "connection" in transaction mode is logical, not physical — the application must not assume two statements on the "same" connection hit the same backend process unless wrapped in one transaction.
- **psycopg_pool `ConnectionPool`**: a per-process pool with optional `configure`/`check`/`reset` callbacks; psycopg's own docs explicitly describe `NullConnectionPool` (3.1+) as intended for "deploy[ing] the application in several instances... and/or using an external connection pool process such as PgBouncer" — i.e. the driver docs themselves steer toward using **no** (or a null) client-side pool when PgBouncer already fronts the DB, to avoid stacking two pools. FastAPI's own `lifespan` hook is the documented place to open/close the pool.

### Provider-specific confirmation
- **Neon**: PgBouncer, `pool_mode=transaction`, server config `max_prepared_statements=1000` (not user-configurable) — protocol-level prepared statements work; SQL-level `PREPARE`, `SET`/`RESET`, `LISTEN/NOTIFY`, advisory locks, held cursors explicitly listed as unsupported on pooled connections. (neon.com/docs/connect/connection-pooling, 2026-10-07)
- **Supabase (Supavisor)**: session mode supports prepared statements; transaction mode supports **named** prepared statements only behind a feature flag (`NAMED_PREPARED_STATEMENTS_ENABLED`), otherwise prepared statements must be disabled — Supabase's own troubleshooting doc tells psycopg users to set `prepare_threshold = None`. (supabase.github.io/supavisor/faq; supabase.com/docs/guides/troubleshooting/disabling-prepared-statements-qL8lEL, 2026-10-07)
- **Prisma Postgres**: built-in dedicated PgBouncer per database, zero-config; pooling mode (session/transaction) not explicitly named in fetched docs `[UNVERIFIED]`.

### `langgraph-checkpoint-postgres` and poolers
Source: github.com/langchain-ai/langgraph `libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py` and README (raw, 2026-10-07); GitHub issue #8420 (2026-10-07).

- `PostgresSaver.from_conn_string()` opens its connection with **`prepare_threshold=0` hardcoded**, along with `autocommit=True` and `row_factory=dict_row`. `prepare_threshold=0` disables psycopg3's automatic statement preparation entirely — this makes the *synchronous* saver's default connection pooler-safe by construction, even though **no documentation anywhere in the repo (README, API reference, source comments) discusses PgBouncer or transaction-mode-pooler compatibility explicitly**. It is an undocumented, incidental safety, not a tested/declared guarantee.
- `PostgresSaver`/`AsyncPostgresSaver` also accept a `psycopg_pool.ConnectionPool`/`AsyncConnectionPool` directly as the `conn` argument, and explicitly raise `ValueError` if a `ConnectionPool` is combined with `pipeline=True`.
- **Known incompatibility**: GitHub issue **#8420** (opened 2026-07-23, still **open** as of today) reports that `AsyncPostgresSaver` unconditionally enables PostgreSQL **pipeline mode** (`conn.pipeline()`) via auto-detected server capability, which is incompatible with PgBouncer in transaction mode — PgBouncer multiplexes a client across different backend connections and cannot track pipeline protocol state across that boundary. Symptom: `psycopg.OperationalError: connection is closed`. A fix (`supports_pipeline=False` constructor flag) has an open PR (#8421) but is **not merged/released** as of 2026-10-07. The workaround today is a documented-nowhere monkeypatch: `cp.supports_pipeline = False` after construction.
- Practical consequence: the **synchronous** `PostgresSaver` is safe behind a transaction-mode pooler out of the box (prepared statements off by default). The **async** `AsyncPostgresSaver` is **not** safe out of the box when backed by a connection pool through PgBouncer transaction mode, until the `supports_pipeline=False` workaround is applied manually.

### Explicit verdict: does the pooler change application code?

**Yes.** Running through a transaction-mode pooler (Neon's built-in PgBouncer, Supabase's Supavisor, or any other) is not transparent to a Python psycopg3/SQLAlchemy stack. Required code-level accommodations:

1. **psycopg3 direct use**: pass `prepare_threshold=None` (or rely on `langgraph-checkpoint-postgres`'s hardcoded `prepare_threshold=0`) to disable client-side statement auto-preparation, unless the specific provider's PgBouncer is confirmed ≥1.22 with `max_prepared_statements>0` and the client ships libpq 17+.
2. **SQLAlchemy**: configure the engine with `pool_pre_ping=True` and, when connecting through PgBouncer, disable SQLAlchemy's or the DBAPI's statement caching for the dialect (psycopg3 driver `prepare_threshold=None` propagated via `connect_args`), and never rely on `SET`/session-scoped GUCs surviving across calls.
3. **No SQL-level `PREPARE`/`DEALLOCATE`**, temp tables, `LISTEN/NOTIFY`, or session advisory locks over the pooled connection — these must go over a **direct** (non-pooled) connection, which most providers expose as a separate hostname/port.
4. **`SET LOCAL`, not `SET`**, for any per-request session variable (critical for RLS tenant context — see §3), scoped inside the same transaction as the guarded query.
5. **`AsyncPostgresSaver` specifically** needs the `supports_pipeline=False` monkeypatch until PR #8421 lands, or must be run with a direct (non-pooled) connection/pool.
6. A client-side `psycopg_pool.ConnectionPool` sized 1 (or a `NullConnectionPool`) is the psycopg-docs-recommended pattern when PgBouncer already fronts the database — stacking two full pools is explicitly discouraged by psycopg's own docs.

---

## 3. Row-Level Security support

| Provider | RLS support | Evidence |
|---|---|---|
| **Neon** | Standard Postgres RLS, unmodified. "Neon RLS/Authorize" is an additive JWT-policy helper, not a replacement. | neon.com/postgresql/administration/row-level-security (2026-10-07) |
| **Supabase** | Standard Postgres RLS, first-class documented feature (`auth.uid()` helpers layer on top of vanilla RLS). | supabase.com/docs/guides/database/postgres/row-level-security (2026-10-07) |
| **Aiven, Render, Railway, Prisma Postgres** | Standard managed-vanilla-Postgres hosting → `CREATE POLICY`/`FORCE ROW LEVEL SECURITY` should work unmodified, but **no dedicated RLS confirmation page was fetched for any of these** `[UNVERIFIED: inferred from "managed Postgres" positioning only]`. |
| **Xata** | `[UNVERIFIED: no Xata RLS doc fetched]`; moot given no free tier exists (§1b). |
| **Nile** | **Does NOT use RLS as its primary tenancy mechanism.** Nile's own docs: *"Nile enables tenant data isolation without any complex, buggy code or dealing with messy row-level security policies… setting a session context to a specific tenant (`SET nile.tenant_id = '<uuid>'`) is equivalent to pointing the connection to a specific tenant DB."* This is a proprietary virtual-tenant-DB model, not standard RLS policies — using Nile would mean abandoning the `CREATE POLICY` + `FORCE ROW LEVEL SECURITY` design entirely. | thenile.dev/docs/tenant-virtualization/tenant-isolation (2026-10-07) |

**Pooler interaction with RLS**: because transaction-mode PgBouncer returns a backend connection to the pool after every transaction (not after client disconnect), an RLS-driving session variable (e.g. `app.current_tenant_id` used inside a policy's `USING`/`WITH CHECK` clause) **must** be set with `SET LOCAL` inside the same transaction as the RLS-gated query. A plain `SET` would leak the tenant context to the next, unrelated client that reuses the same pooled backend connection — a real tenant-isolation bug, not just a style preference. This is inferred directly from PgBouncer's and Neon's documented transaction-mode session-state behavior; no provider doc explicitly frames it as "RLS guidance," so treat it as a derived requirement, not a quoted best practice.

**Verdict**: Neon and Supabase both support the planned `CREATE POLICY` + `FORCE ROW LEVEL SECURITY` design natively. Nile is **incompatible** with that design as specified (it offers its own tenancy primitive instead) and should be excluded if standard RLS is a hard requirement.

---

## 4. Object storage — is it needed at all?

### Verdict: **No object store is needed.** Parse PDF/DOCX entirely in memory on upload and persist only the extracted text in Postgres.

Confirmed from each library's own docs (all accessed 2026-10-07):
- **pypdf**: `PdfReader(stream: str | IO[Any] | Path, ...)` accepts any file-like object (e.g. `io.BytesIO`), not just a disk path; pypdf ships a dedicated "streaming-data" doc for exactly this use case. (pypdf.readthedocs.io/en/latest/user/extract-text.html; …/streaming-data.md)
- **python-docx**: `Document(docx: str | IO[bytes] | None)` has a documented "Opening a file-like document" pattern explicitly for when you "don't want to (or aren't allowed to) interact with the file system." (python-docx.readthedocs.io/en/latest/user/documents.html)
- **PyMuPDF**: `pymupdf.open(stream=data)` accepts raw bytes directly (no DOCX support in the free version — DOCX requires paid PyMuPDF Pro, so python-docx remains the correct free choice for DOCX). (pymupdf.readthedocs.io/en/latest/how-to-open-a-file.html)

No library in the stack requires a filesystem path. Extracted plaintext from a typical student assignment is tens of KB — thousands of submissions stay well under Supabase's 500 MB or Neon's 1 GB/project free DB cap, whereas storing raw PDF/DOCX binaries would burn through those same free quotas far faster. Discarding the original binary after extraction (keep only the extracted/redacted text and, optionally, a SHA-256 hash for integrity/audit) removes the object-store requirement entirely and simplifies the privacy story (no binary blob containing unredacted student identifiers sitting anywhere).

### If raw-file retention is ever required anyway — free object storage comparison

| Provider | Free storage | Egress | Ops/request limits | On exceeding free limit | Training-on-content clause |
|---|---|---|---|---|---|
| **Cloudflare R2** | 10 GB-month | **Zero egress fee**, always | 1M Class A + 10M Class B ops/mo free | Auto-billed if payment method on file ($0.015/GB-mo, $4.50/$0.36 per M ops); no hard suspension | Explicit: *"we do not use our customers' content to train any LLMs"* (cloudflare.com/trust-hub/responsible-ai/) |
| **Backblaze B2** | First 10 GB always free | Conflicting claims across official pages (1 GB/day vs 3× stored/mo) `[UNVERIFIED: which is current]` | 2,500 free Class B/C ops/day | Billed per GB beyond 10 GB, not deleted | No explicit training-prohibition clause found `[UNVERIFIED]` |
| **Supabase Storage** | 1 GB | 5 GB + 5 GB cached | 50 MB max upload on Free | `[UNVERIFIED: exact block behavior past 1 GB]` | Supabase ToS §8(b): will not use customer data to train AI **without prior written consent** — opt-in, clean by default |
| **AWS S3** | Legacy accounts: 5 GB/12 mo. New accounts (post Jul 2025): credit-funded 6-month Free Plan, not a dedicated S3 allowance | Legacy: 100 GB/12 mo | Legacy: 20,000 GET/2,000 PUT | New-plan account **auto-closes 6 months** after creation or when credit exhausted | General "will not access your data... except required by law" — no S3-specific AI-training clause found `[UNVERIFIED]` |
| **Vercel Blob (Hobby)** | 1 GB/mo | 10 GB/mo | 10,000 simple / 2,000 advanced ops | Hard 30-day lockout, no billing, no deletion | **Opt-out, not opt-in**: Privacy Notice states Hobby/Pro data "may" be disclosed de-identified to AI partners for training unless the user changes team settings — materially worse privacy default than R2/Supabase |

If ever needed, **Cloudflare R2** is the best fit on both cost (zero egress, matches the "near-$0" constraint for a batch job that reads files back) and privacy grounds (explicit no-training clause). But per the verdict above, this project should not need any object store at all.

---

## Not verified / gaps

- **Aiven**: free-tier Singapore region availability is contradicted between the pricing page (lists `sgp`) and the free-tier limitations doc (says region cannot be chosen) — needs a live signup-flow check.
- **CockroachDB Basic, YugabyteDB Aeon Sandbox**: connection limits, pooler software, backup/restore specifics, and SEA region availability not confirmed on the single pages fetched — would need deeper doc pages per provider.
- **Nile**: pooler software and session/transaction mode not named anywhere on its pricing page; Singapore/SEA region not individually confirmed (page only says "All" generically); exact behavior on persistent unpaid overage beyond "we'll reach out" not spelled out.
- **Prisma Postgres**: whether the free database itself can ever be suspended for inactivity is undocumented (absence of suspend language is not proof of absence of the behavior); PgBouncer pooling mode (session/transaction) not explicitly named; Prisma Accelerate's prepared-statement-under-pooler behavior page returned a stub — not fully retrieved.
- **Supabase**: exact automatic-vs-manual wake trigger for a paused Free project — the dedicated `/docs/guides/platform/pause` doc 404'd today; also the precise behavior when the 500 MB storage or 5 GB egress cap is exceeded mid-cycle is not spelled out on the fetched pages.
- **Koyeb**: pooler existence/mode and the exact behavior after the 5 free compute-hours/month are exhausted are not stated in the fetched docs; a version-support inconsistency (PG 14–17 vs 14–16) exists between two sections of the same docs page.
- **Render**: Southeast Asia region availability for the free Postgres product specifically was not found on the pages fetched.
- **RLS**: Aiven, Render, Railway, and Prisma Postgres have no dedicated RLS-confirmation doc page fetched — standard-Postgres RLS support is inferred, not quoted, for these four. Xata's RLS support is unverified (moot given it has no free tier).
- **`SET LOCAL` + RLS under transaction pooling**: the requirement to use `SET LOCAL` (not `SET`) for RLS tenant context is derived from PgBouncer's/Neon's general transaction-mode session-state documentation; no provider doc frames it explicitly as RLS guidance.
- **`langgraph-checkpoint-postgres` async pipeline/PgBouncer bug**: confirmed via an **open, unmerged** GitHub issue (#8420) and its linked PR (#8421) as of 2026-10-07 — this is the current state, not a resolved/documented-safe configuration; recheck before relying on it if building against a later release.
- **Object storage region/privacy**: Southeast Asia region availability for R2/B2/S3/Supabase Storage specifically, and Backblaze B2's/AWS S3's training-on-content stance, were not independently confirmed on dedicated region/AI-policy pages this pass.
