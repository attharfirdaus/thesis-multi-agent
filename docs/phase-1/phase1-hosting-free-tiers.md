# Phase 1 — Free-tier hosting options (backend FastAPI + LangGraph + CPU IndoBERT; frontend Next.js; Postgres)

Research date: **2026-10-06** (every claim below fetched today unless marked otherwise). Method: primary provider docs/pricing pages only; secondary sources used only as leads. No recommendations, no selection — options + evidence only.

Scope: (a) frontend Next.js → Vercel Hobby; (b) backend FastAPI + LangGraph + CPU-only IndoBERT (torch/transformers, no GPU, no local LLM) on Render free web service, Hugging Face Spaces free CPU (Docker and non-Docker SDKs), plus alternatives verified today (Koyeb, Fly.io, Railway, PythonAnywhere, Oracle Cloud Always Free ARM, Google Cloud Run, Azure App Service free, Vercel container functions); (c) Postgres → Supabase free, Neon free.

Memory-arithmetic baseline used throughout (see §5 for the derivation):
**minimum viable host RAM for one resident IndoBERT-base CPU worker ≈ 2 GB; 512 MB hosts cannot load the model at all.**

---

## 1. Frontend — Vercel Hobby

| Field | Value | Source (accessed 2026-10-06) |
|---|---|---|
| Tier | Hobby, $0, "non-commercial, personal use only" (fair-use guidelines) | https://vercel.com/docs/plans/hobby (page `last_updated: 2026-09-14`) |
| Included usage/mo | 100 GB Fast Data Transfer, 10 GB Fast Origin Transfer, 1,000,000 CDN requests, 1,000,000 Function Invocations, 4 Active CPU-hrs, 360 GB-hrs Provisioned Memory, 50,000 Web Analytics events, 1 hour runtime logs | same page |
| Function max duration | Hobby: 300 s default **and** max (Pro: 300 s default / 800 s / 1800 s beta) | https://vercel.com/docs/functions/limitations (`last_updated: 2026-08-24`) |
| Function memory/CPU | Hobby: 2 GB / 1 vCPU (max = default) | same page |
| Function size limit | 250 MB uncompressed (500 MB Python); "Large functions" beta up to 5 GB | same page |
| Request/response body | 4.5 MB max (413 `FUNCTION_PAYLOAD_TOO_LARGE`) | same page |
| Builds | Hobby: 2 vCPU, 8 GB build memory, 32 GB build disk, 100 deployments/day, 200 projects | https://vercel.com/docs/plans/hobby |
| Sleep/cold start | Functions scale to zero with traffic; instances with no traffic for 5 min in production scale down (container functions), `SIGTERM` + 30 s grace | https://vercel.com/kb/guide/docker-on-vercel-vs-render (published 2026-07-13, `last_updated: 2026-08-12`) |
| Docker required? | **No.** Native Next.js/Node build; Docker is optional (`Dockerfile.vercel` / prebuilt OCI image to Vercel Container Registry) | same KB page |
| Persistent process | **No.** Functions are stateless request/response; state in backing services | same KB page |
| Credit card | Not required for Hobby (no billing cycle; over-limit = wait, typically 30 days) | https://vercel.com/docs/plans/hobby |
| Log retention | Hobby: 1 hour of runtime logs | https://vercel.com/docs/plans/hobby |

Note: over-limit on Hobby does not bill — you wait until the 30-day window resets (Web Analytics pause = 7 days).

---

## 2. Backend hosts

### 2.1 Render — Free web service

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Tier | Free compute plan (workspace Hobby, $0) | https://render.com/docs/free ; https://render.com/pricing |
| RAM / CPU | **512 MB RAM, 0.1 CPU** | https://render.com/pricing ("Free / $0/month / 512 MB RAM"), https://render.com/docs/free (glossary: "`free`: 0.1 CPU / 512 MB RAM") |
| Sleep rule (exact) | "Render *spins down* a Free web service that goes **15 minutes** without receiving any inbound traffic." Spin-up "takes about one minute" | https://render.com/docs/free |
| Ephemeral vs persistent disk | Ephemeral filesystem; **Free web services cannot attach persistent disks**; local changes lost on redeploy/restart/spin-down | https://render.com/docs/free |
| Monthly hours | 750 Free instance hours per workspace per month; exhausted ⇒ all free web services suspended until next month (no roll-over) | https://render.com/docs/free |
| Bandwidth / egress | Workspace Hobby: **5 GB included/month**, then $0.15/GB; no payment method + overage ⇒ free services suspended for rest of month | https://render.com/pricing ; https://render.com/docs/free |
| Build limits | Hobby standard build pipeline **500 mins/month** (then $5/1000 mins); Docker builds allowed; Docker image builds "can run for up to 120 minutes" | https://render.com/pricing ; https://vercel.com/kb/guide/docker-on-vercel-vs-render |
| Log retention | Hobby: **7 days** | https://render.com/pricing |
| Docker required? | **Either.** Native runtimes: "Node.js / Bun, Python, Ruby, Go, Rust, and Elixir"; Docker also supported | https://render.com/docs/faq ; https://render.com/pricing |
| Persistent process | Yes while awake (a real long-running server process), but killed on 15-min idle spin-down; restarts lose in-memory state (model must reload) | https://render.com/docs/free |
| Request timeout | No fixed request-timeout value found on Render's own docs (FAQ + Free docs + Web Services pages). **Gap.** | — |
| Credit card | Not required to deploy free services; adding one only matters if you exceed included bandwidth/pipeline minutes | https://render.com/docs/faq |
| Free Postgres (separate) | 1 GB storage, **expires 30 days after creation** (+14-day grace then deleted), 1 per workspace, 100 connections, 256 MB RAM, no backups, no managed pooling | https://render.com/docs/free ; https://render.com/pricing |

### 2.2 Hugging Face Spaces — free CPU

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Tier | `cpu-basic` hardware listed FREE in the hardware table: **2 vCPU, 16 GB RAM, 50 GB disk** | https://huggingface.co/docs/hub/en/spaces-gpus ; https://huggingface.co/pricing |
| **Eligibility (decisive)** | "Static Spaces are free for everyone. **Gradio and Docker Spaces run on compute and require a paid plan to create: PRO for personal accounts**, Team or Enterprise for organizations. Free personal accounts in good standing can still host up to 2 Gradio Spaces running on ZeroGPU." | https://huggingface.co/docs/hub/en/spaces-overview |
| Creation failure mode | "Without a subscription, creating, duplicating or moving a Gradio or Docker Space on `cpu-basic` fails with a payment error (HTTP 402)." | https://huggingface.co/docs/huggingface_hub/en/guides/manage-spaces |
| Sleep rule (exact) | "If your Space runs on the default `cpu-basic` hardware, it will go to sleep if inactive for more than a set time (currently, **48 hours**). Anyone visiting your Space will restart it automatically." Custom sleep time not configurable on cpu-basic | https://huggingface.co/docs/hub/en/spaces-gpus ; https://huggingface.co/docs/huggingface_hub/en/guides/manage-spaces |
| Ephemeral vs persistent disk | "Each Spaces environment is limited to 16GB RAM, 2 CPU cores and **50GB of (not persistent) disk space** by default." | https://huggingface.co/docs/hub/en/spaces-overview |
| Networking | Outbound requests allowed on ports 80, 443 and 8080 only | same page |
| Docker required? | **Either.** SDKs: Gradio, Docker, static HTML (Docker required only if you pick the Docker SDK; a Gradio/FastAPI app still counts as "running on compute" and needs the paid plan) | https://huggingface.co/docs/hub/en/spaces-overview |
| Persistent process | Yes — a Space is a long-running container (not request-scoped), so a resident torch process fits; it dies on the 48 h idle sleep | https://huggingface.co/docs/hub/en/spaces-gpus |
| Price if paid | PRO **$9/month** (includes "8× Spaces quota", "Gradio & Docker Spaces on compute") | https://huggingface.co/pro ; https://huggingface.co/pricing |
| Free-account alternative | ZeroGPU only (Gradio, GPU-seconds quota); not usable for a CPU FastAPI service | https://huggingface.co/docs/hub/en/spaces-overview ; https://huggingface.co/pricing |
| Log retention | Not documented on the pages read. **Gap.** | — |
| Credit card | Required for PRO; free accounts cannot create compute Spaces at all | https://huggingface.co/docs/hub/en/spaces-overview |
| Disk-at-rest billing | Spaces storage is volume-based ($12/TB/mo public, $18/TB/mo private at base tier) | https://huggingface.co/pricing |

### 2.3 Koyeb — Free Instance

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Tier | One `free` web Service per organization | https://www.koyeb.com/docs/reference/instances ; https://www.koyeb.com/docs/faqs/pricing |
| RAM / CPU / disk | **512 MB RAM, 0.1 vCPU, 2 GB SSD** | https://www.koyeb.com/docs/reference/instances |
| Regions | Frankfurt or Washington, D.C. only | same page |
| Sleep rule (exact) | "The Koyeb Free Instance automatically scales down to zero when it doesn't receive any traffic for **1 hour**. Scale-to-zero on this Instance cannot be disabled, and the idle period cannot be customized." Cold start (deep sleep) "1 to 5 seconds" for the platform; app-level model load is additional | https://www.koyeb.com/docs/run-and-scale/scale-to-zero ; https://www.koyeb.com/docs/reference/instances |
| Free-instance restrictions | No Worker Services, no custom scaling, **no Volumes (no persistent storage)** | https://www.koyeb.com/docs/reference/instances |
| Egress | Koyeb docs (last updated 2026-05-27) and pricing FAQ: "We provide **100GB of outbound bandwidth per month for free**, usage after this allowance will cost $0.04 per GB. We will notify you ahead of time once we begin charging" | https://www.koyeb.com/docs/faqs/pricing |
| Docker required? | **Either.** Builds from `Dockerfile` or from buildpacks (Python is a supported buildpack language); prebuilt images also supported | https://www.koyeb.com/docs/build-and-deploy/build-from-git |
| Persistent process | Yes while awake; scale-to-zero after 1 h idle kills the process | https://www.koyeb.com/docs/run-and-scale/scale-to-zero |
| Free Postgres (separate) | "One free PostgreSQL database limited to **5 hours of active time and 1GB of storage**" | https://www.koyeb.com/docs/faqs/pricing |
| Credit card | **Required even for the free instance.** "We require a credit card to prevent fraud and abuse" ($29 pre-auth hold); signup also charges the prorated amount for the selected plan (Pro by default) until you downgrade to Starter | https://www.koyeb.com/docs/faqs/pricing |
| Corporate status | Banner on all Koyeb docs/pricing pages: "Koyeb is joining Mistral AI to Build The Future of AI Infrastructure" | https://www.koyeb.com/docs/reference/instances |
| Log retention | Build logs stored 30 days; runtime log retention not documented. Partial **gap** | https://www.koyeb.com/docs/build-and-deploy/build-from-git |

### 2.4 Fly.io — no free tier (free trial only)

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Tier | No free tier for new accounts; "New organizations use Pay As You Go pricing." Legacy Launch/Scale plans closed to new customers since 2024-10-07 | https://fly.io/docs/about/pricing ; https://fly.io/docs/about/discontinued-plans |
| Free trial | "2 hours of machine runtime or 7 days of access, whichever comes first"; 10 machines max; 20 GB volume storage; up to 2 vCPUs / 4 GB memory per machine; "Trial Machines are set to automatically stop after running for 5 minutes" | https://fly.io/docs/about/free-trial |
| After trial | Apps stop until a payment method is added | same page |
| Paid price refs | Smallest always-on Machine `shared-cpu-1x` 256 MB = $2.19/mo; `shared-cpu-1x` 1 GB = $6.70/mo; additional RAM $6.00/GB/mo; stopped Machine rootfs $0.15/GB/mo; outbound $0.02/GB (NA/EU) | https://fly.io/docs/about/pricing |
| Docker required? | No — Fly deploys OCI images you build (Docker/podman/nixpacks locally); Fly is container-native | https://fly.io/docs/about/pricing |
| Credit card | Required after the 2 h / 7-day trial | https://fly.io/docs/about/free-trial |

### 2.5 Railway

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Free plan | $0/month, **$1 of monthly usage credit**, max **1 vCPU / 0.5 GB RAM** per service, 1 replica, 1 project, 3 services, **0 custom domains**, 3-day log history, max volume 500 MB | https://railway.com/pricing ; https://docs.railway.com/reference/pricing/plans |
| Trial | $5 one-time credit, 30 days, up to 2 vCPU / 1 GB per service, 7-day logs | https://railway.com/pricing |
| Usage rates | RAM $10/GB/mo, CPU $20/vCPU/mo, egress $0.05/GB | https://railway.com/pricing |
| Sleep rule | No fixed idle-sleep rule documented for services (usage is per-second, stopped services cost nothing); sandbox idle timeout 5 min on Free/Trial | https://railway.com/pricing |
| Docker required? | No — Nixpacks/buildpacks or Dockerfile both supported | https://docs.railway.com/reference/pricing/plans |
| Credit card | Free/Trial needs no card; paid card required from March 30 (post-paid) for Hobby+ | https://railway.com/pricing ; https://docs.railway.com/reference/pricing/plans |
| Note | $1/month credit at $10/GB-RAM ≈ 100 GB-hours of RAM — not enough to keep a ~1–2 GB resident process alive continuously (see §5) | derived from the two pages above |

### 2.6 PythonAnywhere (free account)

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Tier | Free ("Beginner"-adjacent), $0 | https://help.pythonanywhere.com/pages/FreeAccountsFeatures/ |
| Limits | **100 CPU seconds** per day, **512 MiB disk**, **1 web app with 1 web worker and 1 month expiry**, 2 consoles. New accounts (created after 2026-01-15; EU 2026-01-08) get **no MySQL and no scheduled tasks** | https://help.pythonanywhere.com/pages/FreeAccountsFeatures/ |
| CPU-second semantics | "With every PythonAnywhere account, you get a number of CPU-seconds included **each day**. This applies to all code run through our in-browser consoles and in your scheduled tasks. **It does not currently apply to your web apps.**" Over-quota processes are "tarpitted" (lower priority) | https://help.pythonanywhere.com/pages/WhatAreCPUSeconds |
| Docker required? | **No Docker** — WSGI web app + web worker model only | https://help.pythonanywhere.com/pages/FreeAccountsFeatures/ |
| Persistent process | No — no always-on tasks on free accounts (scheduled tasks also unavailable to accounts created after 2026-01-15) | same page |
| Credit card | Not required for free accounts | https://www.pythonanywhere.com/pricing/ |

### 2.7 Oracle Cloud Always Free (ARM VM)

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Tier | Always Free, no time limit | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm (page last modified 2026-06-12) |
| ARM (Ampere A1) compute | "All tenancies get the first 1,500 OCPU hours and 9,000 GB hours per month for free for VM instances using the VM.Standard.A1.Flex shape... For Always Free tenancies, this is equivalent to **2 OCPUs and 12 GB of memory**." Flexible: 1 instance with 2 OCPU/12 GB, or two instances of 1 OCPU each | same page |
| AMD micro | Up to **two** VM.Standard.E2.1.Micro instances: 1/8 OCPU, **1 GB RAM**, 50 Mbps internet bandwidth | same page |
| Block volume | **200 GB total** (boot + block combined), 5 volume backups; minimum boot volume 47 GB; default boot 50 GB | same page |
| **Idle reclamation** | "Idle Always Free compute instances **may be reclaimed** by Oracle... deemed idle if, during a **7-day period**: CPU utilization for the 95th percentile is less than 20%, network utilization is less than 20%, memory utilization is less than 20% *(applies to A1 shapes only)*" | same page |
| Outbound email | Port 25 outbound blocked by default (needs a service-limit request) | same page |
| Database (separate) | 2× Autonomous AI Database (1 OCPU, 20 GB each, max 20 simultaneous sessions); NoSQL; MySQL HeatWave 50 GB | same page |
| Docker required? | No — full VM, you install whatever you want (systemd + uvicorn/torch directly, or Docker) | same page |
| Persistent process | **Yes** — always-on VM (subject to idle reclamation above) | same page |
| Credit card | **Required for signup:** "Select **Add payment verification method**, and then select **Credit Card**... You might see a small, temporary charge... your credit card won't be charged unless you elect to upgrade" | https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/signingup_topic-Sign_Up_for_Free_Oracle_Cloud_Promotion.htm |
| Caveat | Free-tier ARM allowance was halved from 4 OCPU/24 GB to 2 OCPU/12 GB effective 2026-06-15 (secondary reporting; the official page above now states 2 OCPU/12 GB) | https://www.infoq.com/news/2026/07/oracle-cloud-free-tier-limits |

### 2.8 Google Cloud Run (free tier)

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Free tier (request-based billing) | "CPU - First **180,000 vCPU-seconds** free per month; RAM - First **360,000 GiB-seconds** free per month; Requests - **2 million** requests free per month" (free tier aggregated per billing account, resets monthly) | https://cloud.google.com/run/pricing |
| Free tier (instance-based billing) | 240,000 vCPU-s / 450,000 GiB-s per month | same page |
| Runtime rates | Request-based: $0.000024/vCPU-s active, $0.0000025/GiB-s active, $0.40/M requests | same page |
| CPU allocation default | "Request-based billing (default): ... CPU is only allocated during request processing." Instance-based billing ("CPU always allocated") is opt-in; instance-based requires ≥512 MiB memory; "An instance will never stay idle for more than **15 minutes** after processing a request unless it is kept active using minimum instances" | https://docs.cloud.google.com/run/docs/configuring/billing-settings |
| Request timeout | "The timeout is set by default to **5 minutes (300 seconds)** and can be extended up to **60 minutes (3600 seconds)**" | https://docs.cloud.google.com/run/docs/configuring/request-timeout (last updated 2026-09-30) |
| Docker required? | Container required; **Dockerfile optional** — "If a Dockerfile is present in the source code directory, the uploaded source code is built using that Dockerfile. If no Dockerfile is present... Google Cloud's buildpacks automatically detects the language... Python" is a supported runtime | https://docs.cloud.google.com/run/docs/deploying-source-code |
| Persistent process | No by default (scale to zero, CPU throttled outside requests). Longer background work needs Cloud Tasks / instance-based billing + min instances, which consumes the free allowance | https://docs.cloud.google.com/run/docs/configuring/billing-settings |
| Image/disk | Container image in Artifact Registry (storage billed separately outside free tier) | https://docs.cloud.google.com/run/docs/deploying-source-code |
| Credit card | Required at Free Trial signup: "you must provide a credit card or other payment method that is valid for the period of the Free Trial"; Free Tier monthly limits persist after upgrading, but a billing account is needed | https://docs.cloud.google.com/free/docs/free-cloud-features |
| Log retention | Not on pages read (Cloud Logging has its own free 50 GiB/month ingestion + retention rules). **Gap** | — |

### 2.9 Azure App Service — Free (F1)

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Tier | F1 Free (shared compute, per-app metering) | https://azure.microsoft.com/en-us/pricing/details/app-service/linux/ |
| RAM / disk | **1 GB RAM, 1.00 GB storage** | same page; https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits (App Service limits table, page `ms.date: 2026-08-04`) |
| CPU quota | 60 CPU minutes/day, 3 CPU minutes per 5-minute window; "Memory (1 hour): **1,024 MB per App Service plan**" | limits table, same URL |
| Bandwidth | **165 MB/day** | limits table |
| Sleep rule | "Always On" is **not available** on Free/Shared (table row blank for Free/Shared), and "When Always On is turned off (default), **the app is unloaded after 20 minutes** without any incoming requests." Also a general idle request timeout of 230 s disconnects clients | limits table; https://learn.microsoft.com/en-us/azure/app-service/configure-common |
| Docker required? | **Either.** Limits table row "Linux code-only and containers | X" for Free (Free also supports Windows code-only). Custom containers need `WEBSITES_PORT`; container warmup default timeout 240 s, extendable via `WEBSITES_CONTAINER_START_TIME_LIMIT` (max 1800 s) | limits table; https://learn.microsoft.com/en-us/troubleshoot/azure/app-service/faqs-app-service-linux-new |
| Scaling | 1 shared instance; no scale-out, no autoscale on Free | limits table |
| Custom domains | 0 on Free ("azurewebsites.net subdomain only"), no custom-domain TLS | limits table |
| Quota enforcement | Exceeding CPU (5-min), CPU (day) or bandwidth ⇒ **app stopped until quota resets**, all requests return HTTP 403; exceeding memory ⇒ app stops temporarily | https://learn.microsoft.com/en-us/azure/app-service/web-sites-monitor |
| WebSockets | Linux Free: 5 per instance | limits table |
| Credit card | Required to create an Azure subscription (free account also needs verification) — not separately documented on the pricing page. **Partial gap** | — |
| Log retention | Not on pages read. **Gap** | — |

### 2.10 Dead / retired (verify before planning)

| Host | Status | Evidence (2026-10-06) |
|---|---|---|
| **Cyclic.sh** | **Dead.** Live page banner: "Cyclic is shutting down. New signups are disabled. Free tier after May 10th 2024. Paid tier after May 31th 2024." | https://www.cyclic.sh/pricing ; https://www.cyclic.sh/posts/cyclic-is-shutting-down (26 Apr 2024) |
| **Deta / Deta Space** | **Dead.** `https://deta.space` now returns **HTTP 530** (fetched today). `deta.sh` "retired"; Deta Space sunset on **2024-10-17** | https://deta.space (HTTP 530) ; https://news.ycombinator.com/item?id=41426388 ; https://shutdownlikeaboss.com/post/762742417220878336/reminder-space-is-shutting-down-in-3-weeks |
| **Fly.io free tier** | **Gone** (2 h / 7-day trial only, then pay-as-you-go) | https://fly.io/docs/about/free-trial |
| **Railway original free tier** | Replaced; today's "Free" = $1/month credit with 0.5 GB RAM cap | https://railway.com/pricing |

---

## 3. Postgres — Supabase free vs Neon free

### 3.1 Supabase Free

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Price / projects | $0; **2 active projects** max (paused projects don't count) | https://supabase.com/pricing ; https://supabase.com/docs/guides/platform/billing-on-supabase |
| Database size | **500 MB per project** (limit, then writes blocked) | https://supabase.com/pricing ; https://supabase.com/docs/guides/platform/billing-on-supabase |
| Compute (Nano, free) | Shared CPU, **"Up to 0.5 GB" RAM**; "Compute resources on the Free plan are subject to change." (Pricing page states "Shared CPU • 500 MB RAM"; the compute table lists Nano = "Up to 0.5 GB") | https://supabase.com/docs/guides/platform/compute-and-disk ; https://supabase.com/pricing |
| **Pausing (exact)** | "Free projects are **paused after 1 week of inactivity**" / "Supabase pauses Free Plan projects that show low activity over a **7-day period**... Typically a few user requests to the database each day over the previous week is enough to keep the project from being paused." Restore window: 1 year after pausing | https://supabase.com/pricing ; https://supabase.com/docs/guides/platform/free-project-pausing |
| Connections | Nano (free): **Database Max Connections 60**, **Connection Pooler Max Clients 200**; pooler = Supavisor (shared, IPv4-only) | https://supabase.com/docs/guides/platform/compute-and-disk |
| Egress | 5 GB included; 5 GB cached egress | https://supabase.com/pricing |
| File storage | 1 GB included; max upload 50 MB | https://supabase.com/pricing |
| Log retention | **1 day** (API & database); Auth audit logs 1 hour; log ingestion 1 GB | https://supabase.com/pricing |
| Backups | Not included on Free | https://supabase.com/pricing |
| Add-ons / card | Free needs no billing; Pro from $25/mo (unpause + 8 GB disk) requires a card. (Free-plan card requirement not stated on the pages read — **does not appear to be required**, marked as low-confidence) | https://supabase.com/pricing |

### 3.2 Neon Free

| Field | Value | Source (2026-10-06) |
|---|---|---|
| Price / projects / branches | $0/month, permanent (not a trial), **no credit card required**; 100 projects, 10 branches per project | https://neon.com/pricing ; https://neon.com/faqs/free-plan-limits-and-quotas |
| Storage | **1 GB Postgres storage per project, 20 GB account total** ("Free is capped at 1 GB of Postgres storage per project and 20 GB total across all projects"); over-limit blocks writes, no billing overage | https://neon.com/pricing ; https://neon.com/faqs/free-plan-limits-and-quotas |
| Compute | **100 CU-hours per project per month**; autoscaling **up to 2 CU (≈8 GB RAM)**; 1 CU ≈ 4 GB RAM + CPU + SSD | https://neon.com/pricing ; https://neon.com/faqs/free-plan-limits-and-quotas |
| Scale to zero (exact) | "Compute suspends automatically after inactivity (**scale-to-zero**)... Always enabled on Free (**suspends after 5 min**, cannot be turned off)"; suspended compute = $0, no CU-hours accrue | https://neon.com/pricing |
| Egress | **5 GB per project per month** (then compute suspended until next period) | https://neon.com/pricing ; https://neon.com/faqs/free-plan-limits-and-quotas |
| Connections | `max_connections` by compute size: 0.25 CU (1 GB) = **104**; 0.5 CU = 209; 1 CU = 419; 2 CU = 839. PgBouncer: `max_client_conn = 10000`, `default_pool_size = 0.9 × max_connections`, transaction mode, `query_wait_timeout = 120` s. Pooled hostname = suffix `-pooler` | https://neon.com/docs/connect/connection-pooling |
| History / snapshots | Instant restore history 6 hours (1 GB cap), 1 manual snapshot | https://neon.com/pricing ; https://neon.com/faqs/free-plan-limits-and-quotas |
| Monitoring/log retention | **1 day** | https://neon.com/pricing |
| Other quotas | Object Storage 5 GB/project; Functions 10 active Capacity-Hours, 400 waiting, 1M invocations; Managed Better Auth up to 60k MAU | https://neon.com/pricing |
| Card | "no credit card required" | https://neon.com/pricing |
| **Doc conflict (report it)** | Some Neon pages still render "**0.5 GB** storage per project" while the live pricing page and FAQ table today both say **1 GB per project** (e.g. search-cached FAQ snippets and `?a=` variant URL). Treat 1 GB as current; flag for the human | https://neon.com/pricing vs https://neon.com/faqs/free-plan-limits-and-quotas?a=9b8c4834-5d58-49ee-b654-a9a54a67429a |

### 3.3 Other free Postgres found (context)

| Provider | Free DB | Source (2026-10-06) |
|---|---|---|
| Render Postgres Free | 1 GB, **expires 30 days after creation**, 1 per workspace, 100 connections, no backups/pooling | https://render.com/docs/free ; https://render.com/pricing |
| Koyeb Postgres free | 1 GB storage but only **5 hours of active time** | https://www.koyeb.com/docs/faqs/pricing |
| Oracle Autonomous AI Database | 2 DBs, 1 OCPU, 20 GB each, max 20 simultaneous sessions | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm |

---

## 4. Docker-required answer (per host, explicit)

| Host | Docker required for a Python FastAPI service? | Evidence |
|---|---|---|
| Vercel Hobby | **No** (Python runtime / Next.js); Docker image optional via `Dockerfile.vercel` + Vercel Container Registry | https://vercel.com/kb/guide/docker-on-vercel-vs-render |
| Render | **Either** (native Python runtime *or* Docker) | https://render.com/docs/faq |
| HF Spaces | **Either** (Gradio/FastAPI SDK-style Space, or Docker SDK); both need a paid plan on free-account compute | https://huggingface.co/docs/hub/en/spaces-overview |
| Koyeb | **Either** (Dockerfile or Python buildpack) | https://www.koyeb.com/docs/build-and-deploy/build-from-git |
| Fly.io | Build-your-own-image (container-native) — Docker is the normal path | https://fly.io/docs/about/pricing |
| Railway | **Either** (buildpacks/Nixpacks or Dockerfile) | https://docs.railway.com/reference/pricing/plans |
| PythonAnywhere | **Neither** — WSGI app + web worker model, no Docker | https://help.pythonanywhere.com/pages/FreeAccountsFeatures/ |
| Oracle Always Free ARM | **No** — plain VM, install Python/torch directly | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm |
| Google Cloud Run | **Container required, Dockerfile optional** (Cloud Buildpacks build Python from source) | https://docs.cloud.google.com/run/docs/deploying-source-code |
| Azure App Service F1 | **Either** (limits table marks "Linux code-only and containers" as available on Free) | https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits |

---

## 5. Can this host run FastAPI + LangGraph + CPU IndoBERT at $0? (memory arithmetic shown)

**Arithmetic for one resident IndoBERT-base CPU worker** (assumptions stated; IndoBERT base = 12 layers, hidden 768, ~110M params):
- Weights fp32: 110M × 4 B ≈ **440 MB** (matches the ~400 MB figure in the task brief).
- Framework/runtime overhead: Python + torch + transformers + tokenizers + numpy ≈ **300–600 MB** RSS (torch alone typically 200–400 MB before the model).
- Model load transient (state dict + buffers + allocator fragmentation): peak typically **1.3–2× final weights** → extra ≈ **150–300 MB** during `from_pretrained`.
- Inference activations (fp32, seq 512, batch 8): a few hundred MB → **~200–400 MB** working headroom.
- FastAPI/uvicorn + LangGraph + LangChain + HTTP clients + DB driver: **~100–250 MB**.
- **Floor:** ~0.9–1.3 GB RSS just resident and idle; **realistic steady-state under load: ~1.3–2.0 GB.** Budget **2 GB+** to be safe; add headroom if batches exceed 8 or sequences exceed 512 tokens.

| Host (free tier) | RAM limit | Model fits? | Persistent process? | Verdict at $0 |
|---|---|---|---|---|
| Render free web service | 512 MB | **No.** 512 MB < 440 MB weights + 300–600 MB runtime before any activation. Fails at import/torch load. | Yes while awake, killed after **15 min** idle; no disk | **NO.** RAM 4× too small. Also 0.1 CPU. |
| HF Spaces `cpu-basic` | 2 vCPU / 16 GB | **Yes** (16 GB ≫ 2 GB). | Yes, but **only with PRO $9/mo**; free accounts cannot create Gradio/Docker Spaces (HTTP 402) | **NO at $0** (needs PRO). Would be a comfortable fit on paid PRO. |
| Koyeb free Instance | 512 MB / 0.1 vCPU | **No.** Same 512 MB wall. | Yes while awake, but scales to zero after **1 h** idle; no volumes | **NO** (RAM; card also required). |
| Fly.io | Trial only (≤4 GB/machine, 2 VM-hours total) | Technically yes within the 2 VM-hour trial (1 GB+ fits) | Trial machines auto-stop after 5 min | **NO** at $0 (trial = 2 h / 7 days, then paid; smallest 1 GB machine $6.70/mo). |
| Railway Free | **0.5 GB**/1 vCPU, $1/mo credit | **No** (0.5 GB). Even the 1 GB Trial tier is tight; $1/mo ≈ 100 GB-hours RAM ≈ ~2 days of a 2 GB process | Yes while credit lasts | **NO.** |
| PythonAnywhere free | 512 MiB disk; CPU-second quota; **no RAM figure published** | Effectively no: 512 MiB disk can't hold the HF cache (~440 MB weights + torch wheels ≈ GBs), and free accounts have no always-on tasks. | No | **NO.** |
| Oracle Always Free ARM A1 | **12 GB RAM, 2 OCPU**, 200 GB block, always-on | **Yes, comfortably** (12 GB ≫ 2 GB; 200 GB disk holds torch + checkpoints). | **Yes** — real always-on VM. Idle-reclamation rule: reclaimed if, over 7 days, 95th-pct CPU < 20% **and** network < 20% **and** memory < 20% (A1 only) — a resident model + real traffic keeps memory/CPU above that | **YES at $0** (card needed for signup; ARM wheels must be available for torch/transformers — verify wheel availability separately). |
| Google Cloud Run | Configurable up to 8 GB+; free tier 180k vCPU-s + 360k GiB-s + 2M req/month (request-based) | **Yes** if built as one service with the model baked into the image and instance memory set to e.g. 2–4 GB; but each cold start re-loads the model (~440 MB read + ~1 GB RSS spike) and burns GiB-seconds. Free-tier math at 4 GiB: 360,000 GiB-s ÷ 4 GiB = **90,000 s ≈ 25 h of instance time/month** — fine for sporadic requests, tight for a resident worker. | **No** by default (request-based billing throttles CPU outside requests; instance-based billing + min instances consume the allowance as compute cost) | **CONDITIONAL YES at $0** for request-driven use (card required at signup; model must be in the image; cold-start reload each idle expiry — instance idle max 15 min). |
| Azure App Service F1 | **1 GB RAM**, 1 GB storage, 60 CPU-min/day, 165 MB/day egress, **no Always On** (unloaded after 20 min idle) | **Borderline/improbable**: 1 GB is below the 1.3–2.0 GB realistic RSS; also no torch in a 1 GB footprint with LangChain/LangGraph overhead. | No (app unloaded after 20 min without requests; Always On unavailable) | **NO.** Also 60 CPU-min/day and 165 MB/day egress would be consumed quickly. |
| Vercel Hobby (container function) | **2 GB / 1 vCPU**, max duration **300 s** | Memory: 2 GB is marginal-but-plausible for a single inference; **but** the model must be bundled (Python function bundle ≤500 MB, large-functions beta 5 GB) and re-loaded per cold start, every invocation capped at 300 s | **No** — stateless functions, scale to zero; "Hobby plan restricts users to non-commercial, personal use only" | **CONDITIONAL NO at $0 for this thesis use**: works for a demo-sized single request, fails the "persistent CPU torch process" requirement, and Hobby is non-commercial-only. |
| (Dead) Cyclic, Deta | n/a | n/a | n/a | **Not available** (shut down; Deta Space URL now HTTP 530). |

**Bottom line of the arithmetic:** the 512 MB class (Render free, Koyeb free, Railway Free, PythonAnywhere) **cannot** host a resident IndoBERT CPU process — the weights alone (≈440 MB) exceed the entire RAM budget before any runtime overhead. The 1 GB class (Azure F1, Railway Trial) is below the 1.3–2.0 GB realistic RSS. The candidates with enough headroom are the **12 GB ARM VM (Oracle Always Free)**, **16 GB HF Spaces cpu-basic (paid PRO, not $0)**, and **Cloud Run with a 2–4 GB instance memory under the free allowance** (request-driven only).

---

## 6. Batch jobs longer than one HTTP request (what breaks where)

| Host | Constraint that breaks a long batch |
|---|---|
| Vercel Hobby | Function invocation capped at **300 s** (`FUNCTION_INVOCATION_TIMEOUT` 504); no background execution after response on request-based billing; 4 CPU-hrs and 360 GB-hrs/month hard caps | 
| Render free | Process is killed on **15 min** with no inbound traffic; any state in RAM (loaded model) is lost; no persistent disk on free; free instance hours (750/mo) can be exhausted; Render "may restart a Free web service at any time" |
| HF Spaces | Space sleeps after **48 h** idle (process gone, model reloads on next visit); free tier additionally requires paid plan |
| Koyeb free | Scales to zero after **1 h** idle; no volumes; free instance cannot be a Worker Service |
| Fly.io | Trial machines auto-stop after 5 min; paid auto-stop/auto-start is the normal long-batch pattern (billed per second) |
| Railway | Per-second billing; $1/month Free credit buys ≈100 GB-hours RAM → ~2 days of a 2 GB resident process |
| PythonAnywhere | 100 CPU-seconds/day quota on consoles+scheduled tasks (web apps excluded); free accounts created after 2026-01-15 have **no scheduled tasks** |
| Oracle Always Free | No run-duration cap; risk is idle reclamation (7-day <20% CPU/network/memory) and 200 GB block-volume limit |
| Google Cloud Run | Request timeout default **300 s**, max **3600 s**; container not terminated on timeout (may keep processing); CPU only during requests under default billing; instance idle max **15 min**; Cloud Tasks is the documented path for async up to 30 min |
| Azure App Service F1 | **60 CPU-minutes/day** shared quota → app returns HTTP 403 when exhausted; app unloaded after **20 min** idle; 230 s idle request disconnect; 165 MB/day egress; no Always On |
| Supabase (DB) | Pauses after **7 days** of low activity (DB unavailable until manually resumed) |
| Neon (DB) | Compute suspends after **5 min** idle (cold-start on next query); 100 CU-hours/project/month cap → compute suspended when exhausted |

---

## 7. Dated one-line summary (paste-ready for README)

> **Free-tier hosting snapshot — verified 2026-10-06 (all pages fetched this date):** Vercel Hobby = $0, 2 GB/1 vCPU functions, 300 s max duration, 100 GB transfer, 1 M invocations, 4 CPU-hrs/360 GB-hrs per month, non-commercial only, Docker optional, no persistent process; Render free = $0 but 512 MB/0.1 CPU with spin-down after 15 min idle (750 instance-hours/mo, 5 GB egress, no free persistent disk), native Python or Docker; Hugging Face free `cpu-basic` (2 vCPU/16 GB/50 GB non-persistent disk, sleeps after 48 h) now **requires a paid PRO ($9/mo) plan to create any Gradio/Docker Space** — HTTP 402 on free accounts; Koyeb free = 512 MB/0.1 vCPU/2 GB SSD, scale-to-zero after 1 h idle, 100 GB egress free, credit card required; Fly.io has **no free tier** (2 h machine runtime or 7 days trial); Railway Free = $1/mo credit with 0.5 GB RAM cap; PythonAnywhere free = 100 CPU-s/day, 512 MiB disk, no scheduled tasks for new accounts; Oracle Cloud Always Free = **2 OCPU / 12 GB ARM + 200 GB block (+2× 1 GB AMD micros)**, always-on, card required at signup, idle instances reclaimable after 7 days below 20% CPU/network/memory; Google Cloud Run free tier = 180 k vCPU-s + 360 k GiB-s + 2 M requests/month, container required (Dockerfile optional via buildpacks), 300 s default / 3600 s max request timeout, no persistent process by default; Azure App Service F1 = 1 GB RAM, 1 GB disk, 60 CPU-min/day, 165 MB/day egress, unloaded after 20 min idle, no Always On; Vercel/Cloud Run/Render/Koyeb/Railway support Docker-or-native except HF Spaces (needs paid plan) and PythonAnywhere (no Docker); Cyclic.sh and Deta/Deta Space are dead (Deta Space URL returns HTTP 530); Postgres: Supabase Free = 500 MB DB, 2 projects, **pauses after 7 days inactivity**, 60 direct / 200 pooler connections, 5 GB egress, 1-day logs; Neon Free = **1 GB/project (20 GB/account)** storage, 100 CU-hours/project/month, autoscale to 2 CU (~8 GB RAM), **scale-to-zero after 5 min**, 5 GB egress/project, PgBouncer pooling (max_client_conn 10 000; max_connections 104 @0.25 CU → 839 @2 CU), no credit card. **Memory verdict:** a resident IndoBERT-base CPU worker needs ≈1.3–2.0 GB RSS (440 MB fp32 weights + 300–600 MB torch stack + load transient + activations + ~100–250 MB FastAPI/LangGraph), so the 512 MB free tiers (Render, Koyeb, Railway Free, PythonAnywhere) cannot host it, the 1 GB tiers (Azure F1, Railway Trial) are below the realistic floor, and the free options with enough headroom are Oracle Always Free ARM (12 GB) or Cloud Run with 2–4 GB instance memory under the free allowance (request-driven, cold-start model reloads); HF Spaces cpu-basic (16 GB) would fit but is no longer $0.

---

## 8. Not verified / gaps

1. **Render HTTP request timeout**: no fixed value documented on Render's own pages (Web Services, Free, FAQ). Not found ⇒ treated as undocumented. [UNVERIFIED]
2. **Render runtime log retention on Free**: pricing page says Hobby = 7 days; the Free-plan docs page does not restate it. [ASSUMPTION: same 7-day workspace retention]
3. **HF Spaces log retention** and runtime-log limits: not documented on the pages fetched. [UNVERIFIED]
4. **HF Spaces free-account ZeroGPU quota** (5 GPU-min/day) came from a forum post, not a doc page fetched today; the official page fetched only says PRO = "8× Spaces quota" and "40 minutes of RTX Pro 6000 Blackwell compute". [UNVERIFIED]
5. **Azure App Service F1 + custom container**: the official limits table marks "Linux code-only and containers" as available in the Free tier, but Azure's custom-container guide does not list Free as a supported plan and 1 GB RAM makes containers impractical. The exact "custom container on F1" supportability is unresolved. [UNVERIFIED]
6. **Azure free-account credit-card requirement**: not stated on the pricing/docs pages fetched (Azure signup generally requires a card). [UNVERIFIED]
7. **Koyeb log retention** (runtime, not build) not documented; only "build logs are stored for 30 days". [UNVERIFIED]
8. **Koyeb egress claim conflict**: Koyeb's pricing FAQ says 100 GB/month free egress, while Koyeb's own Render-comparison page says both providers give 100 GB free egress — Render's live pricing page says Hobby gets **5 GB**. Koyeb's own FAQ is newer-looking ("not charged yet") and is the value used above; the comparison page conflicts with Render's primary pricing page. Flagged.
9. **Neon storage discrepancy**: live pricing page + FAQ table say **1 GB/project**; other Neon URLs (variant/`?a=` FAQ pages, search caches) still show **0.5 GB**. Reported the conflict; could not determine whether it is A/B, stale cache, or a recent increase.
10. **Supabase free-plan credit-card requirement**: not stated on the pricing/billing pages fetched. Not assumed.
11. **Google Cloud Run free-tier log retention** and **Artifact Registry storage billing for images built during free use**: not examined. [UNVERIFIED for cost impact]
12. **Oracle ARM wheel availability** for `torch`/`transformers` on aarch64 (Linux) was not verified today — it is a prerequisite for the "residential CPU IndoBERT on Oracle A1" verdict. [UNVERIFIED]
13. **Vercel Hobby "non-commercial" enforcement**: the plan page states the restriction but the enforcement mechanism/sanction for a thesis artefact was not examined.
14. **All prices/limits are provider-declared and change often** — several pages carry their own last-updated stamps (Vercel 2026-09-14 / 2026-08-24; Oracle 2026-06-12; Koyeb docs 2026-05-27; Azure ARM limits `ms.date` 2026-08-04; Cloud Run timeout page 2026-09-30). Re-verify before publishing the final artefact.
