# What LangGraph's Own Docs Say About Deployment

All sources fetched 2026-10-07 from `docs.langchain.com` (LangChain/LangGraph's primary docs site) and `github.com/langchain-ai/langgraph`. As of October 2025 LangChain renamed "LangGraph Platform" → **"LangSmith Deployment"**; the underlying managed runtime is now called **Agent Server**. This is a doc-site rename, not a product change — the same three deployment surfaces exist as before.

---

## 1. Supported deployment options

LangGraph documents exactly **two fundamentally different ways to run a graph**, with the first offered in several infrastructure flavors.

### A. LangSmith Deployment / Agent Server (managed runtime)
> "LangSmith Deployment is a workflow orchestration runtime purpose-built for agent workloads. It provides the managed infrastructure agents need to run reliably in production at scale... Deploy to Cloud, BYOC, or your own infrastructure."
— [Deployment overview](https://docs.langchain.com/langsmith/deployment), accessed 2026-10-07

Agent Server itself always needs, regardless of who hosts it:
> "When you deploy Agent Server, you are deploying one or more graphs, a database for persistence, and a task queue."
> "Agent Server persists three types of data, all backed by PostgreSQL by default... Redis handles the signaling, cancellation, and streaming pub/sub between API servers and queue workers."
— [Agent Server](https://docs.langchain.com/langsmith/agent-server), accessed 2026-10-07

Four topologies are documented, all running the same Agent Server image:

| Topology | Who hosts control/data plane | Doc |
|---|---|---|
| Cloud (managed) | LangChain hosts everything (AWS/GCP) | [Deploy to Cloud](https://docs.langchain.com/langsmith/deploy-to-cloud-overview) |
| Hybrid | LangChain hosts control plane; you host Agent Servers + DB/Redis | [Hybrid](https://docs.langchain.com/langsmith/hybrid) |
| Self-hosted with control plane | You host everything, full LangSmith product | [Deploy with control plane](https://docs.langchain.com/langsmith/deploy-with-control-plane) |
| **Standalone server** | You host Agent Server (API+queue containers) + your own Postgres/Redis, **no control plane** | [Self-host standalone servers](https://docs.langchain.com/langsmith/deploy-standalone-server) |

All four require a long-lived server process (see §5) and a database; none are "serverless" in the request/response sense except the Cloud "Serverless" *deployment type*, which is still a long-lived container that scales to zero on idle, not a per-request function (see §3).

### B. Self-hosted in your own FastAPI app / as a library
LangGraph is also just a Python library. The compiled graph (`builder.compile(checkpointer=...)`) is a plain object you can `.invoke()`/`.ainvoke()` from any Python process — no Agent Server required. Evidence:

- The checkpointer quickstart shows compiling and invoking a graph directly in Python with no server: 
  > "Compile your graph with a checkpointer, a store, or both: `graph = builder.compile(checkpointer=checkpointer, store=store)` ... `result = graph.invoke(...)`"
  — [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), accessed 2026-10-07
- `langgraph-checkpoint-postgres`'s own README demonstrates raw `psycopg` connections and `PostgresSaver.from_conn_string(DB_URI)` used standalone, with no Agent Server in the loop — this is literally "library" usage.
  — [`libs/checkpoint-postgres/README.md`](https://raw.githubusercontent.com/langchain-ai/langgraph/main/libs/checkpoint-postgres/README.md), accessed 2026-10-07
- Agent Server explicitly treats this as the alternative path: "Agent Server handles persistence automatically... When using the Agent Server, you do not need to implement or configure checkpointers or stores manually." The implication (and explicit statement elsewhere) is that outside Agent Server, you *do* configure the checkpointer yourself inside your own process — i.e., inside your own FastAPI app, in the same `.py` process that holds your HTTP routes.
- The OSS "Deployment" page frames this explicitly as a choice of "hosting model": "choose a hosting model that fits your stack" rather than mandating Agent Server.
  — [Deployment](https://docs.langchain.com/oss/python/langgraph/deploy), accessed 2026-10-07

Requirements for option B: your own long-lived Python process (FastAPI/uvicorn or any other host), your own database connection management, no Redis, no Agent Server image/queue — you write the loop that calls `graph.invoke()`/`graph.astream()` and persists via whatever checkpointer you instantiate.

---

## 2. Durability: checkpointing, resume-after-failure, cron/background runs

### Checkpointing and resume (library-level, no managed platform required)
This is a pure-library feature, independent of Agent Server:

> "Checkpointing provides fault-tolerance and error recovery: if one or more nodes fail at a given superstep, you can restart your graph from the last successful step."
> "When a graph node fails mid-execution at a given super-step, LangGraph stores pending checkpoint writes from any other nodes that completed successfully at that super-step. When you resume graph execution from that super-step you don't re-run the successful nodes."
— [Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers), accessed 2026-10-07

Three **durability modes** (library-level, settable per call, e.g. `graph.stream(..., durability="sync")`):
> - `"exit"`: persists only on exit; best performance, no mid-run recovery.
> - `"async"`: persists asynchronously between steps; good performance, small window of data loss on crash.
> - `"sync"`: persists synchronously before the next step; highest durability, some performance cost.
— same page, "Durability modes" section, accessed 2026-10-07

None of this requires Agent Server — it requires only that you pass a persistent checkpointer (e.g. `PostgresSaver`/`AsyncPostgresSaver`) to `.compile()` and keep using the same `thread_id`.

### Cron / background-run — these DO require Agent Server
Unlike checkpointing, scheduled/background execution is **not** a plain-library feature — it's an Agent Server API surface:

> "LangSmith Deployment supports cron jobs, which run on a user-defined schedule. The user specifies a schedule, an assistant, and some input... The LangSmith Deployment API provides several endpoints for creating and managing cron jobs."
— [Use cron jobs](https://docs.langchain.com/langsmith/cron-jobs), accessed 2026-10-07

> "This guide covers how to kick off background runs for your agent. This can be useful for long running jobs." (via `client.runs.create(...)` against a deployed Agent Server, polled/joined asynchronously)
— [How to kick off background runs](https://docs.langchain.com/langsmith/background-run), accessed 2026-10-07

Both cron and background-run are client calls against the Agent Server's `/runs` and `/runs/crons` REST endpoints (any of the four topologies in §1A). **If you use LangGraph purely as a library (§1B) you get no cron/background-run primitive from LangGraph itself** — you would schedule/queue the `graph.invoke()` call yourself (e.g., with your own scheduler or FastAPI `BackgroundTasks`/a worker), and LangGraph only contributes the checkpoint/resume mechanics once invoked.

---

## 3. Documented caveats about serverless environments

Two distinct "serverless" caveats are documented, for two different things.

### (a) Running the Agent Server binary itself in a request-scoped serverless host (e.g. AWS Lambda, Cloud Run jobs that scale to zero mid-request) — explicitly forbidden:
> "Do not run standalone servers in serverless environments. Scale-to-zero may cause task loss and scaling up will not work reliably."
— [Self-host standalone servers](https://docs.langchain.com/langsmith/deploy-standalone-server), accessed 2026-10-07 (bolded Warning callout in the doc)

This is the single clearest load-bearing sentence for this report's question of minimum process model: Agent Server (API + queue worker containers) is designed around persistent, always-listening processes and is explicitly documented as broken under scale-to-zero.

### (b) LangChain's own "Serverless" *deployment type* on managed Cloud — different thing, still not per-request Lambda semantics
> "Serverless | Scales to zero after inactivity, wakes on the next request | Shared, multi-tenant | Background or latency-tolerant agents..."
> "A Serverless deployment scales to zero after a period of inactivity and wakes on the next request... the first request after scale-down takes longer to respond while the deployment starts."
> "Agent Server is fault-tolerant: it automatically recovers from transient Redis or Postgres interruptions and retries failed background runs."
— [Cloud platform features](https://docs.langchain.com/langsmith/cloud-platform-features), accessed 2026-10-07

This "Serverless" tier is still a container running the full Agent Server (API+queue) that LangChain manages the scale-to-zero/wake-up lifecycle for — it is not you deploying LangGraph inside a bare FaaS function. The doc flags it is still **beta** ("Scale to zero is in beta"). No connection-pooling or execution-time-limit numbers are published for it.

### (c) No documentation found for running LangGraph as a library inside a third-party FaaS (AWS Lambda/Vercel/Cloud Run request-scoped functions)
There is no official LangGraph doc page describing deployment as a bare Lambda/FaaS function. The closest official guidance is the explicit warning in (a) against serverless hosting of the *Agent Server*, plus the general library behavior in §1B/§2 (checkpointing works per-invocation regardless of host, but nothing in the docs addresses cold starts, execution-time limits, or Lambda-specific connection handling). This is marked `[UNVERIFIED]` for FaaS-specific guidance — no primary source found.

---

## 4. `langgraph-checkpoint-postgres` with pooled/managed Postgres

The README is explicit about connection setup requirements, but says nothing about PgBouncer/transaction-pooling providers (Supabase, Neon, RDS Proxy) specifically — no primary-source statement on pooler compatibility was found.

What is documented, from the official README (`langchain-ai/langgraph` `libs/checkpoint-postgres/README.md`, accessed 2026-10-07):

> "When manually creating Postgres connections and passing them to `PostgresSaver` or `AsyncPostgresSaver`, make sure to include `autocommit=True` and `row_factory=dict_row`... Why these parameters are required: `autocommit=True`: Required for the `.setup()` method to properly commit the checkpoint tables... `row_factory=dict_row`: Required because the PostgresSaver implementation accesses database rows using dictionary-style syntax."

> "By default, `langgraph-checkpoint-postgres` installs `psycopg` (Psycopg 3) without any extras."

> "Set `LANGGRAPH_STRICT_MSGPACK=true` or pass an explicit `allowed_msgpack_modules` list when creating your checkpointer. This restricts checkpoint deserialization to known-safe types, preventing code execution if the database is compromised."

Separately, the Agent Server self-hosted guide documents `DATABASE_URI` as "a valid Postgres connection URI" and explicitly supports *sharing one Postgres instance across multiple deployments* via different database names on the same host — implying a normal `postgresql://` connection string is expected, not a specific pooling mode:
> "`DATABASE_URI`: Postgres connection details. Postgres will be used to store assistants, threads, runs, persist thread state and long term memory, and to manage the state of the background task queue with 'exactly once' semantics."
— [Self-host standalone servers](https://docs.langchain.com/langsmith/deploy-standalone-server), accessed 2026-10-07

**Not found in any primary doc:** explicit guidance on PgBouncer transaction-mode pooling, max pool size recommendations, or compatibility statements for managed free-tier Postgres (Supabase/Neon/Railway) pooled connection strings. `[UNVERIFIED]`.

---

## 5. Minimal self-hosted deployment: process model, health checks, concurrency, background/cron triggers

The clearest primary source is the standalone-server Docker Compose example and the Agent Server architecture page.

### Process model (from the official Docker Compose example)
> `docker compose up` with a compose file defining **three services**: `langgraph-redis` (redis:6), `langgraph-postgres` (postgres:16), `langgraph-api` (your built image, listening on container port 8000, mapped to 8123).
— [Self-host standalone servers](https://docs.langchain.com/langsmith/deploy-standalone-server), accessed 2026-10-07

> "A typical deployment consists of two kinds of long-running containers, both built from the same Docker image... **API servers** handle client requests... but do not execute agent code themselves. **Queue workers** are the execution engine. They listen to the durable task queue, execute your graph code, and write checkpoints."
> "Containers are **stateless** but persistent. At least 1 queue worker must listen to the task queue at any time to ensure no runs are orphaned."
— [Agent Server](https://docs.langchain.com/langsmith/agent-server), accessed 2026-10-07

The simplest self-hosted mode collapses API+queue into one process:
> "Single host: The API server manages the task queue directly with no separate queue workers. This is the default for self-hosted deployments and is suitable for development and low-traffic use cases."
— same page

### Health check
> `curl --request GET --url 0.0.0.0:8123/ok` → `{"ok":true}`
— [Self-host standalone servers](https://docs.langchain.com/langsmith/deploy-standalone-server), accessed 2026-10-07 (Compose file also wires Postgres/Redis `healthcheck:` probes via `pg_isready`/`redis-cli ping`)

### Concurrency
> "Each worker executes up to `N_JOBS_PER_WORKER` runs concurrently (default: 10), so a single worker container serves many runs in parallel. This bounds concurrent run execution, not the number of API requests the deployment can serve."
> "The queue enforces that at most 1 run can be executed for a given thread at one time."
— [Agent Server](https://docs.langchain.com/langsmith/agent-server), accessed 2026-10-07

### How background/cron runs are triggered
Both go through the Agent Server REST API, not a cron daemon you run yourself:
- Cron: `client.crons.create(assistant_id, schedule="27 15 * * *", input={...})` — Agent Server itself evaluates the schedule and enqueues a run; "All cron schedules are interpreted in UTC."
  — [Use cron jobs](https://docs.langchain.com/langsmith/cron-jobs), accessed 2026-10-07
- Background run: `client.runs.create(thread_id, assistant_id, input=...)` then poll/`join` — the queue worker in the same container pool executes it asynchronously.
  — [How to kick off background runs](https://docs.langchain.com/langsmith/background-run), accessed 2026-10-07

### Custom lifespan / your own FastAPI app inside Agent Server
Agent Server explicitly supports wrapping a user-supplied FastAPI app (for DB pools, custom routes) via `langgraph.json`'s `"http": {"app": "./src/agent/webapp.py:app"}`, with the caveat "Python only... currently only support custom lifespan events in Python deployments with `langgraph-api>=0.0.26`."
— [How to add custom lifespan events](https://docs.langchain.com/langsmith/custom-lifespan), accessed 2026-10-07

---

## 6. Cost / pricing of the managed option at prototype scale

From the live LangSmith pricing page (https://www.langchain.com/pricing, accessed 2026-10-07):

| Plan | Price | Deployment included |
|---|---|---|
| **Developer** | $0/seat/mo | **"N/A"** — no deployment included on the free plan |
| **Plus** | $39/seat/mo + pay-as-you-go | "1 free Serverless (Small) deployment included." Additional Serverless/Dedicated deployments metered: Runtime Compute 0.0675 LSU/vCPU-hr, Runtime Memory 0.0090 LSU/GiB-hr, Database Compute 0.177 LSU/vCPU-hr, Database Memory 0.025 LSU/GiB-hr ($1.00/LSU) |
| **Enterprise** | Custom | Self-hosted/hybrid, custom pricing |

> "Agent deployments running on Cloud require a Plus plan or above."
— [Deploy to Cloud](https://docs.langchain.com/langsmith/deploy-to-cloud-overview), accessed 2026-10-07

**There is no $0 tier for LangSmith Deployment / Agent Server managed hosting.** The $0 Developer plan is observability/tracing only (5k traces/mo) and explicitly lists "Deployment: N/A". The cheapest path to a managed Agent Server deployment is the $39/seat/mo Plus plan, which includes one free Small Serverless deployment; beyond that, usage is metered in LSUs ($1 = 1 LSU).

A secondary, now-superseded data point found in a LangChain changelog post (not the current pricing page, so lower-confidence / historical):
> "If you want to try out a basic version of our LangGraph server in your environment, you can also self-host on our Developer plan and get up to 100k nodes executed per month for free."
— [LangChain Changelog, "LangGraph Platform GA"](https://changelog.langchain.com/announcements/ann_FBl5ubLj8ZCAP), dated ~11 months prior to access, accessed via search 2026-10-07 — **this free self-hosted node-count allowance does not appear on the current (2026-10-07) pricing page**, which shows self-hosted only under the custom-priced Enterprise plan requiring "an Enterprise plan and the LangSmith license key." Treat the changelog's "free self-host" claim as **stale/superseded** `[UNVERIFIED for current pricing]`.

Self-hosting itself today requires Enterprise:
> "Self-hosted deployments require an Enterprise plan and the LangSmith license key delivered with that plan."
— [Deploy to self-hosted](https://docs.langchain.com/langsmith/deploy-to-self-hosted-overview), accessed 2026-10-07

So at prototype scale with a strict $0 budget, **the managed/self-hosted Agent Server product (any topology) is not a documented free option** — only the pure-library usage pattern (§1B) is free, since it has no LangChain-operated component at all (you just run `pip install langgraph langgraph-checkpoint-postgres` inside your own free-tier host).

---

## Comparison table

| | Agent Server (any topology) | LangGraph as a library in your own FastAPI app |
|---|---|---|
| Process model | Long-lived container(s): API + queue worker (can be 1 combined process in "single host" mode) | Whatever you run it in — long-lived process or one-shot script; your choice |
| Requires its own DB | Yes, Postgres mandatory (+Redis for pub/sub/queue signaling) | Only if you want persistence — you supply any `BaseCheckpointSaver`, e.g. `PostgresSaver` |
| Checkpointing / resume-after-crash | Automatic, managed by server | Available, but you wire it: `.compile(checkpointer=PostgresSaver(...))` |
| Durability modes (`exit`/`async`/`sync`) | Same library feature, exposed via server config | Same library feature, you set `durability=` per call |
| Cron jobs | Built-in REST API (`/runs/crons`) | **Not provided by LangGraph** — bring your own scheduler |
| Background runs | Built-in REST API (`client.runs.create` + poll/join) | **Not provided by LangGraph** — bring your own queue/async task |
| Serverless-host compatibility | **Explicitly forbidden** for standalone server ("Do not run standalone servers in serverless environments... task loss") | Works in any Python process per-invocation; no FaaS-specific guidance found |
| $0 tier | **None** — cheapest managed deployment needs Plus ($39/seat/mo); self-host needs Enterprise | Free — standard OSS package install, host anywhere |

---

## Minimum process model for a checkpointed LangGraph batch pipeline — direct answer

**It can run as short-lived invocations of your own FastAPI app, provided you do NOT run LangGraph's own Agent Server component.**

Evidence chain:
1. Checkpointing/resume is a library feature triggered purely by passing a `BaseCheckpointSaver` (e.g. `PostgresSaver`/`AsyncPostgresSaver`) to `.compile()` and invoking with a stable `thread_id` — nothing in that mechanism requires a long-lived server process; it requires only a durable Postgres row per super-step (§2, §1B).
2. The explicit "do not run in serverless" warning (§3a) applies specifically to **the Agent Server binary** (its API+queue-worker container pair, built for a persistent task queue with leases and at-least-one-worker-listening semantics) — not to the `langgraph` Python library itself.
3. Therefore a FastAPI endpoint that, per HTTP request (or per cron-triggered invocation from an external scheduler, since LangGraph's own cron/background-run APIs are Agent-Server-only, §2), calls `graph.ainvoke(..., config={"configurable": {"thread_id": ...}})` with `durability="sync"` or `"async"` against a `PostgresSaver`, is fully supported by the docs and needs no long-lived worker of its own — each invocation can start cold, pick up the last checkpoint by `thread_id`, run to completion or crash, and the next invocation resumes correctly from the last persisted checkpoint.
4. What you lose by not running Agent Server: LangGraph-native cron scheduling and background-run REST endpoints (bring your own scheduler/trigger), and the "retries failed background runs automatically" fault tolerance that Agent Server's queue provides (§3b) — a bare-library invocation that crashes mid-run simply leaves its last checkpoint in place; nothing automatically retries it unless your own invocation layer does.

**Conclusion:** A long-lived worker is required only if you want LangGraph's own queue/cron/background-run machinery (i.e., you choose to run Agent Server). If you accept triggering runs yourself (e.g., an external cron hitting a FastAPI route, or a platform-native scheduled job), short-lived invocations are fully compatible with checkpointed, resumable LangGraph execution per the docs — the "serverless" warning in the docs is scoped to Agent Server's own binary, not to the underlying library.

---

## Not verified / gaps

- **PgBouncer/pooled-Postgres compatibility**: no primary LangGraph/LangChain doc states whether `PostgresSaver`/`AsyncPostgresSaver` works correctly against transaction-mode connection poolers (Supabase, Neon, RDS Proxy). The `autocommit=True` requirement in the README raises a plausible but unconfirmed interaction concern with poolers that don't support session-level settings in transaction mode — this inference is **not** sourced from an official statement and should be verified against the target provider's own pooler docs or by testing.
- **FaaS-specific caveats for the library path** (cold start overhead loading `langgraph`/`psycopg`, execution-time limits, connection-count blowup under concurrent Lambda invocations): no official LangGraph page addresses deploying the library (not Agent Server) inside AWS Lambda, Vercel Functions, or similar. The forbidding statement found is scoped to the Agent Server binary only (§3a).
- **Current status of the "100k free self-hosted nodes/month" claim**: found only in an older LangChain changelog post, not reflected on the current (2026-10-07) pricing page, which shows self-hosting gated behind Enterprise. Treated as stale; not relied upon for the cost conclusion.
- **Exact inactivity window before Cloud "Serverless" deployment type scales to zero**: docs state it "may change as the feature rolls out" without giving a current number.
- No official LangGraph doc enumerates numeric execution-time limits (e.g., "runs longer than N minutes will fail") for any deployment option — the only timing guidance found is qualitative ("first request after scale-down takes longer to respond").
