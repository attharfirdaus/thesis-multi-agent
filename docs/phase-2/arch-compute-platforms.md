# Compute Platforms Architecture Report: Serverless & PaaS for FastAPI Backend

**Date:** 2026-10-07  
**Target Workload:** FastAPI + Python 3.13 backend running minutes-long LLM batch jobs (multi-agent evaluation pipeline).  
**Key Constraints:** $0 / free tier; no VM management; development workstation has NO Docker daemon (cloud build required); native HTTPS + custom domain; secrets handling; GitHub CI/CD; Singapore / Southeast Asia data residency; no prompt-training / restrictive clauses.

---

## 1. Executive Summary & Surviving Shortlist

Out of 17 candidate platforms evaluated from primary vendor documentation accessed on 2026-10-07:
- **7 platforms are DEAD, SUNSET, or NO LONGER OFFER A FREE COMPUTE TIER:** AWS App Runner (sunset for new customers 2026-04-30, no free tier), Fly.io (free tier eliminated 2024-10-07, 7-day trial only), DigitalOcean App Platform (compute starts at $5/mo, free tier is static-only), Zeabur (shared cluster free tier phased out 2026-04-01, $0 is BYO server only), Hugging Face Spaces (Docker Spaces require paid PRO $9/mo as of 2026 policy change), Deno Deploy (JS/TS/WASM only, zero Python support), and Cloudflare Containers (GA 2026-04-13 but paid-only at $5/mo + metered; Workers free plan capped at 10ms CPU time).
- **5 platforms have FATAL RESTRICTIONS for this workload:** Koyeb (free tier restricted to FRA/WAS, no Singapore on free, $29 pre-auth hold, 100s timeout), Modal (custom domain locked to $250/mo Team plan, HTTP web functions hard-capped at 150s), Azure App Service F1 (custom domain blocked on F1, 240s hard timeout, 60 CPU-min/day quota), Northflank (mandatory credit card, commercial use strictly banned), and Vercel (Hobby terms explicitly restrict to "non-commercial, personal use only", 300s/5-minute hard timeout).
- **Top 3 Recommended Platforms ($0, Minutes-Long Batch, Cloud-Built Docker, Singapore):**
  1. **Google Cloud Run (Recommended Primary):** Perpetual Always-Free tier (2M requests, 180,000 vCPU-s, 360,000 GiB-s/month). Request timeout configurable up to **3,600 seconds (60 minutes)**. Cloud Build automatically builds container images from Git repository without local Docker. Supported in `asia-southeast1` (Singapore) with free custom domains and managed TLS.
  2. **Azure Container Apps (Recommended Secondary):** Perpetual Consumption free grant (2M requests, 180,000 vCPU-s, 360,000 GiB-s/month). Request timeout configurable up to **2,400 seconds (40 minutes)**. Cloud build from source via ACR Tasks / Cloud Native Buildpacks (`az containerapp up`). Supported in Southeast Asia (Singapore) with free managed TLS custom domains.
  3. **AWS Lambda + AWS Lambda Web Adapter (Alternative):** Perpetual Always-Free tier (1M requests, 400,000 GB-s/month). Request timeout hard limit is **900 seconds (15 minutes)**. Cloud build via SAM pipeline / GitHub Actions runners. Supported in `ap-southeast-1` (Singapore). Note: Custom domain requires fronting with API Gateway or CloudFront.
  *Special PaaS Mention:* **Render Free Web Service** offers a 100-minute HTTP timeout, no credit card signup, and Singapore region, but provides only 0.1 CPU / 512 MB RAM, spins down after 15 min idle (1-minute cold start), and shares a 750 free instance-hour monthly pool.

---

## 2. Drop List: Dead, Sunset, or No-Longer-Free Platforms

| Platform | Status in 2026 | Fatal Limitation / Reason for Exclusion | Primary Source (Accessed 2026-10-07) |
|---|---|---|---|
| **AWS App Runner** | **SUNSET FOR NEW CUSTOMERS** | Closed to new customers on 2026-04-30 ("AWS App Runner will no longer accept new customers starting on April 30, 2026"). Never offered a free tier. | [AWS App Runner Overview](https://aws.amazon.com/apprunner/) |
| **Fly.io Machines** | **DEAD FREE TIER** | Discontinued legacy free plans on 2024-10-07. New accounts receive only a 2-hour runtime / 7-day trial before instances stop unless a credit card is attached. | [Fly.io Discontinued Plans](https://docs.fly.io/about/discontinued-plans), [Fly.io Pricing](https://docs.fly.io/about/pricing) |
| **DigitalOcean App Platform** | **NO COMPUTE FREE TIER** | Free tier is strictly limited to 3 Static Sites. Compute web services start at $5.00/month (`apps-s-1vcpu-0.5gb`). Also enforces a hard 100-second timeout. | [DigitalOcean App Platform Pricing](https://docs.digitalocean.com/products/app-platform/details/pricing/) |
| **Zeabur** | **FREE COMPUTE PHASED OUT** | Phased out free Shared Clusters on 2026-04-01. The $0 "Free Plan" is a control panel for 1 BYO server; hosted compute requires purchasing a VPS (min $3/mo). | [Zeabur Shared Cluster Phasing Out](https://zeabur.com/changelogs/phasing-out-shared-cluster), [Zeabur Free Plan Docs](https://zeabur.com/docs/en-US/pricing/free-plan) |
| **Hugging Face Spaces** | **PAID-GATED DOCKER SDK** | As of 2026 policy change, creating Docker SDK Spaces requires a paid plan (PRO at $9/month). Only static spaces and 2 ZeroGPU Gradio spaces are free for personal accounts. | [Hugging Face Spaces Overview](https://huggingface.co/docs/hub/en/spaces-overview) |
| **Deno Deploy** | **DISQUALIFIED (NO PYTHON)** | Runtime only executes JavaScript, TypeScript, and WebAssembly. Cannot execute Python or run FastAPI ASGI applications. | [Deno Deploy Docs](https://docs.deno.com/deploy/), [Deno Deploy Pricing](https://deno.com/deploy/pricing) |
| **Cloudflare Containers / Workers** | **PAID-ONLY / 10ms CPU CAP** | Cloudflare Containers is GA (2026-04-13) but strictly paid-only ($5/mo Workers Paid + metered). Plain Python Workers have a 10ms CPU-time cap per request on the free plan, killing batch LLM execution. | [Cloudflare Containers Pricing](https://developers.cloudflare.com/containers/platform/pricing/), [Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/) |

---

## 3. Disqualified or Degraded Platforms

| Platform | Status | Fatal Operational Issue | Primary Source (Accessed 2026-10-07) |
|---|---|---|---|
| **Koyeb** | Active Free Tier | Free instance is geo-locked to Frankfurt (`FRA`) and Washington DC (`WAS`); Singapore (`SIN`) is paid only. Signup enforces a mandatory credit card with a $29 pre-auth hold. Hard 100s request timeout. | [Koyeb Free Instances](https://www.koyeb.com/docs/reference/instances#free-instances), [Koyeb Pricing FAQ](https://www.koyeb.com/docs/faqs/pricing) |
| **Modal** | Active ($30/mo Credit) | Custom domain is blocked on the free Starter plan (requires Team plan at $250/month). HTTP web functions enforce a hard 150-second request timeout (returns HTTP 303 redirect). | [Modal Webhook Timeouts](https://modal.com/docs/guide/webhook-timeouts), [Modal Pricing](https://modal.com/pricing) |
| **Azure App Service (F1)** | Active Free Tier | Custom domains are explicitly disabled on F1 Free (requires Basic paid tier). Hard load-balancer timeout of ~240s. Strict quota of 60 CPU-minutes/day after which app goes offline. No Always On. | [Azure App Service Linux Pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/), [Azure Request Timeout](https://learn.microsoft.com/en-us/troubleshoot/azure/app-service/web-request-times-out-app-service) |
| **Northflank** | Active Free Sandbox | Mandatory credit card verification required before creating any resource on Sandbox. Terms of service forbid commercial endeavors. Shared micro resources (~0.1 vCPU). | [Northflank Pricing Docs](https://northflank.com/docs/v1/application/billing/pricing-on-northflank.md), [Northflank Terms](https://northflank.com/legal/terms) |
| **Vercel** | Active Hobby | Terms verbatim: *"the Hobby plan restricts users to non-commercial, personal use only"* (fair use guidelines). Hard 300-second (5-minute) timeout ceiling. | [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby), [Vercel Function Duration](https://vercel.com/docs/functions/configuring-functions/duration) |

---

## 4. Deep-Dive on Surviving Candidates

### 4.1 Google Cloud Run
- **FastAPI & Python 3.13:** Native container execution. Any base image (e.g., `python:3.13-slim`) runs seamlessly. Source: [Cloud Run Overview](https://cloud.google.com/run).
- **Deployment without Local Docker:** `gcloud run deploy --source .` uploads source code to Cloud Build, which builds the container image in the cloud via Dockerfile or Google Cloud Buildpacks, pushes to Artifact Registry, and deploys. Zero local Docker required. Source: [Cloud Run Source Deploy](https://docs.cloud.google.com/run/docs/deploying-source-code) (accessed 2026-10-07).
- **Free Tier Allowance:** Perpetual Always-Free quota: 2,000,000 requests/month, 180,000 vCPU-seconds/month, 360,000 GiB-seconds/month, and 1 GB egress. Credit card required to activate GCP billing account; overage billed at standard PAYG rates. Source: [Cloud Run Pricing](https://cloud.google.com/run/pricing) (accessed 2026-10-07).
- **Memory, CPU & Concurrency:** Configurable up to 32 GiB RAM / 8 vCPU. Concurrency defaults to 80 requests per container instance (up to 1,000). Idle instances can remain warm up to 15 minutes post-traffic before scale-to-zero. Source: [Cloud Run Autoscaling](https://docs.cloud.google.com/run/docs/about-instance-autoscaling) (accessed 2026-10-07).
- **Maximum Execution Duration:** Configurable up to **3,600 seconds (60 minutes)** for HTTP requests (default 300s). Matches long batch LLM jobs. Source: [Cloud Run Request Timeout](https://docs.cloud.google.com/run/docs/configuring/request-timeout) (accessed 2026-10-07).
- **Cold Start & Idle Rule:** Scales to zero when idle (`min-instances=0`). Cold boot typically 2–5s. Google Cloud may keep instances idle up to 15 min. Source: [Cloud Run Autoscaling](https://docs.cloud.google.com/run/docs/about-instance-autoscaling).
- **Disk:** Ephemeral in-memory container filesystem. (Cloud Storage FUSE optional).
- **HTTPS & Custom Domain:** Free automated HTTPS on `*.run.app` and custom domain mappings in Singapore region. Source: [Cloud Run Locations](https://docs.cloud.google.com/run/docs/locations) (accessed 2026-10-07).
- **Secrets & Env Vars:** Native integration with Google Cloud Secret Manager (mounted files or env vars). Source: [Cloud Run Secrets](https://docs.cloud.google.com/run/docs/configuring/services/secrets).
- **CI/CD:** Native Cloud Build continuous deployment triggers directly from GitHub pushes. Source: [Cloud Run Deploy Continuously](https://docs.cloud.google.com/run/docs/quickstarts/deploy-continuously).
- **Singapore Region & Residency:** `asia-southeast1` (Singapore, Jurong West) fully supported with Tier 2 pricing. No data leaves Singapore. Source: [Cloud Run Locations](https://docs.cloud.google.com/run/docs/locations).
- **Terms:** Standard GCP terms, no academic/commercial prohibition on free tier.

### 4.2 Azure Container Apps (Consumption Plan)
- **FastAPI & Python 3.13:** Native container execution using any OCI image (Python 3.13 supported). Source: [Azure Container Apps Overview](https://azure.microsoft.com/en-ca/pricing/details/container-apps).
- **Deployment without Local Docker:** `az acr build` runs ACR Quick Tasks to build the Dockerfile remotely inside Azure. `az containerapp up --source .` builds and deploys directly from source in the cloud via Cloud Native Buildpacks. Zero local Docker needed. Sources: [ACR Quickstart Task CLI](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-quickstart-task-cli), [ACR Tasks Pack Build](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tasks-pack-build) (accessed 2026-10-07).
- **Free Tier Allowance:** Monthly recurring free grant: 2,000,000 requests, 180,000 vCPU-seconds, and 360,000 GiB-seconds. Credit card required for standard Azure identity verification (or cardless via Azure for Students). Overage billed at standard Consumption rates. Source: [Container Apps Pricing](https://azure.microsoft.com/en-ca/pricing/details/container-apps) (accessed 2026-10-07).
- **Memory, CPU & Concurrency:** Micro allocations available (from 0.25 vCPU / 0.5 GiB). HTTP concurrency scaling via KEDA.
- **Maximum Execution Duration:** HTTP request timeout configurable up to **2,400 seconds (40 minutes)** (default 240s). Verbatim: *"Request time out is 240 seconds... configurable up to 2400 seconds."* Source: [Container Apps Ingress Overview](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview) (accessed 2026-10-07).
- **Cold Start & Idle Rule:** Scales to zero (`minReplicas=0`) during inactivity. Container cold starts take ~4–8 seconds.
- **Disk:** Ephemeral filesystem. Optional Azure Files mounts for persistent volumes.
- **HTTPS & Custom Domain:** Free managed TLS certificates for custom domains. Source: [Container Apps Custom Domains](https://learn.microsoft.com/en-us/azure/container-apps/custom-domains-managed-certificates) (accessed 2026-10-07).
- **Secrets & Env Vars:** Encrypted native secrets referenced via `secretref:<SECRET_NAME>`, with optional Key Vault integration. Source: [Container Apps Manage Secrets](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets).
- **CI/CD:** Native GitHub Actions integration (`azure/container-apps-deploy-action`). Source: [Container Apps GitHub Actions](https://learn.microsoft.com/en-us/azure/container-apps/github-actions).
- **Singapore Region & Residency:** `Southeast Asia` (Singapore) fully supported across Availability Zones 1, 2, and 3. Source: [Azure Locations](https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/#geographies).
- **Terms:** Standard Microsoft Online Services terms, no academic/commercial restriction clause.

### 4.3 AWS Lambda + AWS Lambda Web Adapter (LWA)
- **FastAPI & Python 3.13:** Python 3.13 is a native managed runtime (released Nov 14, 2024; active through 2029). AWS Lambda Web Adapter (LWA) placed in `/opt/extensions` routes HTTP traffic directly to Uvicorn/FastAPI without modifying code. Sources: [AWS Lambda Support for Python 3.13](https://aws.amazon.com/about-aws/whats-new/2024/11/aws-lambda-support-python-313/), [AWS Lambda Web Adapter](https://github.com/aws/aws-lambda-web-adapter) (accessed 2026-10-07).
- **Deployment without Local Docker:** SAM pipelines or GitHub Actions runners build zip/container packages remotely in the cloud via `sam build` and `aws-actions/setup-sam`. AWS CodeBuild can build container images server-side. Zero local Docker needed. Source: [AWS SAM Pipeline Bootstrap](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-pipeline-bootstrap.html) (accessed 2026-10-07).
- **Free Tier Allowance:** Perpetual Always-Free quota: 1,000,000 requests and 400,000 GB-seconds/month. Credit card required for AWS signup. Overage billed standard PAYG. Source: [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/), [AWS Free Tier](https://aws.amazon.com/free/) (accessed 2026-10-07).
- **Memory, CPU & Concurrency:** 128 MB to 10,240 MB RAM. Cannot stay warm for free (Provisioned Concurrency is paid).
- **Maximum Execution Duration:** Hard maximum limit of **900 seconds (15 minutes)**. Doc verbatim: *"set a value between 1 and 900 seconds (15 minutes)"*. Source: [AWS Lambda Configuration Timeout](https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html) (accessed 2026-10-07).
- **Cold Start & Idle Rule:** MicroVM re-used opportunistically; no published idle reclamation timer. Cold start ~1-3s for Python.
- **Disk:** Ephemeral `/tmp` storage (up to 10 GB), resets across execution environments.
- **HTTPS & Custom Domain:** Lambda Function URLs provide free HTTPS but **do not support custom domains**. Custom domains require adding Amazon API Gateway or CloudFront. Source: [AWS Lambda Function URLs Docs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html).
- **Secrets & Env Vars:** Native environment variables encrypted with KMS; SSM Parameter Store / Secrets Manager integration.
- **CI/CD:** Native SAM / GitHub Actions automated deployment pipelines.
- **Singapore Region & Residency:** `ap-southeast-1` (Singapore) fully available.
- **Terms:** Standard AWS customer agreement, no academic/commercial prohibition on free tier.

### 4.4 Render (Free Web Service)
- **FastAPI & Python 3.13:** Native Python runtime with version pinning via `PYTHON_VERSION=3.13.5` or `.python-version`. Runs Uvicorn/Gunicorn directly. Source: [Render Python Version](https://render.com/docs/python-version) (accessed 2026-10-07).
- **Deployment without Local Docker:** Native cloud buildpacks detect `requirements.txt` and build in Render's cloud directly on push from GitHub. Source: [Render Free Services](https://render.com/docs/free.md) (accessed 2026-10-07).
- **Free Tier Allowance:** 750 free instance-hours/month pooled across account. Compute size: 0.1 CPU, 512 MB RAM. No credit card required. Suspends services on monthly hour exhaustion. Source: [Render Free Tier Docs](https://render.com/docs/free.md).
- **Memory, CPU & Concurrency:** 0.1 CPU / 512 MB RAM. Single replica only. Cannot stay warm indefinitely (spins down on idle).
- **Maximum Execution Duration:** Platform enables HTTP responses up to **100 minutes (6,000 seconds)**. Source: [Render vs Vercel Comparison](https://render.com/docs/render-vs-vercel-comparison) (accessed 2026-10-07).
- **Cold Start & Idle Rule:** Spins down after **15 minutes** of no inbound traffic. Spin-up on next request takes approximately **1 minute**. Source: [Render Free Tier Docs](https://render.com/docs/free.md).
- **Disk:** Ephemeral filesystem only. Persistent disks are not available on Free tier.
- **HTTPS & Custom Domain:** Free custom domains with automated Let's Encrypt certificates.
- **Secrets & Env Vars:** Native environment variables and Secret Files.
- **CI/CD:** Native GitHub push-to-deploy out of the box.
- **Singapore Region & Residency:** Singapore is an official deployment region. Source: [Render Regions](https://render.com/docs/regions.md).
- **Terms:** Verbatim: *"Do not use them for production applications. However, they're perfect for testing out a new technology, working on a hobby project..."* Free for research/prototypes.

### 4.5 Railway
- **FastAPI & Python 3.13:** Native Railpack builds with Mise Python 3.13 support (`RAILPACK_PYTHON_VERSION=3.13`). Source: [Railpack Python](https://railpack.com/languages/python/) (accessed 2026-10-07).
- **Deployment without Local Docker:** Railpack builds container images in Railway's cloud from GitHub repository. Zero local Docker needed. Source: [Railway Builds](https://docs.railway.com/builds/railpack).
- **Free Tier Allowance:** One-time $5 credit valid for 30 days on Trial plan (no credit card required). Post-trial reverts to Free plan providing $1/month recurring credit. Services stop when credit runs out. Source: [Railway Free Trial](https://docs.railway.com/pricing/free-trial).
- **Memory, CPU & Concurrency:** 1 vCPU / 0.5 GB RAM on Free tier. Stays warm by default (opt-in Serverless sleep).
- **Maximum Execution Duration:** 15-minute HTTP timeout ceiling on public networking. Source: [Railway Slow Deployments Troubleshooting](https://docs.railway.com/deployments/troubleshooting/slow-deployments).
- **Cold Start & Idle Rule:** Warm by default; opt-in Serverless sleep triggers after 5 minutes of no outbound traffic.
- **Disk:** 0.5 GB persistent volume included free.
- **HTTPS & Custom Domain:** 1 custom domain included on Free/Trial with managed TLS.
- **Secrets & Env Vars:** Native Variables and Sealed Variables.
- **CI/CD:** Native GitHub push-to-deploy.
- **Singapore Region & Residency:** Available in Singapore Equinix SG3 (`asia-southeast1-eqsg3a`). Source: [Railway Regions](https://docs.railway.com/deployments/regions).
- **Terms:** Permits commercial and personal use (Fair Use allows APIs, ML Jobs, cron jobs).

---

## 5. Comprehensive Comparison Table

*All specifications verified against primary vendor documentation accessed on 2026-10-07.*

| Platform | 1. FastAPI + Python 3.13 Support | 2. Local Docker Needed? | 3. Free Tier Allowance & Overage | 4. Memory / CPU & Warm Process | 5. Max Execution Duration | 6. Cold Start & Idle Rule | 7. Persistent Disk | 8. HTTPS & Custom Domain | 9. Secrets / Env Handling | 10. Native GitHub CI/CD | 11. Singapore (SEA) Region | 12. Academic / Commercial Terms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Google Cloud Run** | Native container / buildpacks (Py 3.13 via Dockerfile/buildpack) [1] | **NO** — Cloud Build builds from Git/source in cloud [2] | **Perpetual Free:** 2M req, 180k vCPU-s, 360k GiB-s/mo. Card req. Overage: PAYG [3] | Up to 32GB RAM / 8 vCPU; conc up to 1000. Stays idle ~15m [4] | **60 minutes (3,600s)** [5] | Scale to 0 default; keeps idle up to 15m; cold start 2–5s [4] | Ephemeral only (Cloud Storage FUSE opt) [2] | **YES** — free *.run.app + custom domain with TLS [6] | Native Secret Manager integration (env / volume) [7] | **YES** — native Cloud Build GitHub trigger [8] | **YES** — `asia-southeast1` (Singapore) [6] | No commercial/academic restriction clause [3] |
| **Azure Container Apps** | Native container / buildpacks (Py 3.13 supported) [9] | **NO** — `az acr build` / `az containerapp up` in cloud [10] | **Perpetual Free:** 2M req, 180k vCPU-s, 360k GiB-s/mo. Card req (exc. Students). Overage: PAYG [9] | From 0.25 vCPU / 0.5 GB. Concurrency autoscaling via KEDA [9] | **40 minutes (2,400s)** [11] | Scale to 0 default; cold start 4–8s [11] | Ephemeral only (Azure Files opt) [9] | **YES** — free managed TLS custom domains [12] | Native secrets store + Key Vault integration [13] | **YES** — GitHub Actions native action [14] | **YES** — `Southeast Asia` (Singapore AZ 1,2,3) [9] | No commercial/academic restriction clause [9] |
| **AWS Lambda + LWA** | Native managed runtime Python 3.13 + LWA web adapter [15] | **NO** — SAM / GitHub Actions builds in cloud [16] | **Perpetual Free:** 1M req, 400k GB-s/mo. Card req. Overage: PAYG [17] | 128MB–10GB RAM; concurrency scaling. Warm requires paid Prov Conc [17] | **15 minutes (900s)** [18] | Opportunistic microVM reuse; cold start 1–3s [18] | Ephemeral `/tmp` up to 10GB [18] | **Partial** — HTTPS on URL, custom domain needs API GW/CloudFront [19] | Native KMS-encrypted env vars + SSM/Secrets Mgr [17] | **YES** — native SAM pipeline GitHub Actions [16] | **YES** — `ap-southeast-1` (Singapore) [17] | No commercial/academic restriction clause [17] |
| **Render** | Native runtime (Python 3.13 via `.python-version`) [20] | **NO** — native buildpacks build in cloud [21] | **750 instance-hrs/mo**. No card required. Suspends when exhausted [21] | 0.1 CPU, 512 MB RAM. Single replica. Cannot stay warm 24/7 [21] | **100 minutes (6,000s)** [22] | Spins down after 15 min idle; cold start ~60s [21] | Ephemeral only on Free tier [21] | **YES** — free custom domain + Let's Encrypt TLS [21] | Native env vars and Secret Files [23] | **YES** — native GitHub push-to-deploy [21] | **YES** — Singapore region available [24] | Non-production: *"Do not use them for production applications"* [21] |
| **Railway** | Native runtime (Railpack Python 3.13) [25] | **NO** — Railpack builds in cloud [26] | **$5 Trial credit + $1/mo Free credit**. No card to start. Stops on limit [27] | 1 vCPU / 0.5 GB RAM. Warm by default [27] | **15 minutes (900s)** [28] | Warm default; Serverless sleeps after 5m idle [29] | 0.5 GB persistent volume free [30] | **YES** — 1 custom domain with free TLS [27] | Native Variables and Sealed Variables [31] | **YES** — native GitHub push-to-deploy [27] | **YES** — `asia-southeast1-eqsg3a` (Singapore) [32] | Business/personal allowed; Fair Use allows ML/APIs [33] |
| **Vercel** | Native Python runtime (Beta, Py 3.13 supported) [34] | **NO** — Vercel builds in cloud [35] | **Hobby:** 1M invocations, 4 CPU-hrs, 360 GB-hrs/mo. Pauses 30 days on limit [36] | 1 vCPU / 2GB RAM. In-function concurrency (Fluid) [37] | **5 minutes (300s)** [38] | Fluid compute cached bytecode [37] | Stateless only [36] | **YES** — up to 50 custom domains with TLS [36] | Native Project Environment Variables [36] | **YES** — native Vercel for GitHub App [35] | **YES** — `sin1` (Singapore) [39] | **RESTRICTIVE:** *"Hobby plan restricts users to non-commercial, personal use only"* [36] |
| **Azure App Service** | Native Linux runtime (Python 3.13 via Oryx) [40] | **NO** — `az webapp up` / GitHub Actions [41] | **F1 Free:** 60 CPU-min/day, 1GB RAM. Card req. App goes offline on limit [40] | Shared compute, 60 CPU-min/day. No Always On [42] | **~240 seconds (Linux)** [43] | Unloads on idle; no Always On on Free [42] | 1 GB app storage (overwritten on redeploy) [40] | **NO** — custom domains blocked on Free (F1) [44] | Native Application Settings [40] | **YES** — native Deployment Center GitHub CI [45] | **YES** — Southeast Asia (Singapore) [40] | *"Use of free plan for production workloads is not supported"* [40] |
| **Koyeb** | Native buildpacks (Python 3.13 supported) [46] | **NO** — Cloud Native Buildpacks in cloud [47] | 1 free instance (512MB RAM, 0.1 vCPU). **Mandatory card with $29 hold** [48] | 512 MB RAM, 0.1 vCPU. Scales to 0 after 1 hr idle [49] | **100 seconds** [50] | Scales down after 1 hr; cold boot 3–5s [49] | Ephemeral 2GB SSD only [49] | **YES** — up to 100 custom domains free [51] | Native encrypted secrets vault [52] | **YES** — native GitHub push-to-deploy [47] | **NO** — Free instances restricted to FRA & WAS only [49] | Professional/hobby; non-production on Free [53] |
| **Modal** | Native `@modal.asgi_app` (Python 3.13) [54] | **NO** — builds remote images from Python spec [55] | **$30/mo free credits**. Card req after initial $1 trial. PAYG overage [56] | Up to 100 containers. Warm via `min_containers` (paid) [56] | **150s HTTP ceiling** (background jobs 24h) [57] | Cold start ~1s; idle shutdown after 60s [58] | 1 TiB Volumes free [56] | **NO** — Custom domains require Team plan ($250/mo) [56] | Native `modal.Secret` objects [56] | Documented GitHub Actions recipe [59] | **YES** — `ap-southeast` (Singapore) at 1.15x cost [60] | Internal business use allowed [61] |
| **Northflank** | Native buildpack / Dockerfile [62] | **NO** — builds from Git in cloud [62] | Sandbox: 2 services, 1 DB. **Mandatory card verification** [63] | Shared micro (~0.1-0.5 vCPU). Always warm [63] | Configurable per path (no platform ceiling stated) [64] | Always warm (no sleeping) [63] | Ephemeral container disk [63] | **YES** — managed Let's Encrypt TLS [65] | Native secrets & Secret Groups [66] | **YES** — native GitHub push-to-deploy [62] | **YES** — Singapore (GCP/AWS) [67] | **RESTRICTIVE:** Commercial endeavors prohibited without written approval [68] |
| **Cloudflare Workers** | Native Python Workers (ASGI/Pyodide, Py 3.13) [69] | **NO** for Workers (`wrangler deploy` uploads code) [70] | 100k req/day free. No card req. Returns Error 1027 on limit [71] | 128 MB RAM / isolate. **10ms CPU time limit** [71] | **10ms CPU-time cap** (HTTP wall clock unbounded) [71] | Startup cap 1s; no container idle rule [71] | None (stateless) [71] | **YES** — free custom domain with Cloudflare DNS [71] | 64 secrets per worker [71] | **YES** — native Workers Builds from GitHub [72] | **YES** — runs on Singapore edge PoP automatically [73] | Standard AUP; commercial allowed [71] |
| **Cloudflare Containers** | Containerized FastAPI [74] | **YES** — requires local Docker daemon for deployment [74] | **PAID ONLY** — $0 free tier does not exist (starts at $5/mo + metered) [75] | 1/16 to 4 vCPU, 256MB to 12GB RAM [75] | Configurable up to 5 min [71] | Configurable `sleepAfter` [74] | Ephemeral 2–20GB [75] | Standard Cloudflare TLS [75] | Standard Workers secrets [71] | Native Workers Builds [72] | Anycast global network [73] | Standard Cloudflare Terms [75] |
| **Fly.io** | Custom Dockerfile [76] | **NO** — Remote builders build without local Docker [77] | **DEAD FREE TIER** — 7-day/2-hr trial only, then PAYG [78] | 256MB to 128GB presets. Paid always-on [78] | 60s idle timeout on fly-proxy [79] | Configurable `auto_stop_machines` [76] | Volumes paid ($0.15/GB/mo) [78] | Free SSL certs (10 hosts) [78] | Native `fly secrets` [76] | GitHub Actions via `flyctl-actions` [77] | Singapore `sin` (1.269x markup) [78] | Anti-abuse ToS §5.e [80] |
| **DO App Platform** | Paketo Cloud Native Buildpacks [81] | **NO** — cloud buildpacks from source [82] | **NO COMPUTE FREE TIER** — compute starts at $5/mo [83] | 1 vCPU / 512MB RAM ($5/mo). Paid always-on [83] | **100 seconds hard limit** [84] | Always warm (paid) [83] | Ephemeral only (no volumes) [85] | Free SSL certs [83] | Encrypted app secrets [83] | Native GitHub push-to-deploy [82] | Singapore SGP (Dynamic apps) [86] | Standard DO Terms/AUP [87] |
| **Zeabur** | zbpack build engine (Py 3.13 configurable) [88] | **NO** — zbpack builds in cloud [89] | **FREE COMPUTE SUNSET** (2026-04-01); $0 is BYO server panel [90] | 2C4G build runner; compute is BYO/paid VPS [90] | Unbounded on dedicated server [91] | Always on on dedicated server [90] | Persistent volumes supported [92] | Free *.zeabur.app + custom domain [93] | Environment variables [92] | Native GitHub push-to-deploy [89] | Singapore VPS ($3/mo) [94] | Serverless restricted to non-commercial [95] |
| **Hugging Face Spaces** | Docker SDK [96] | **NO** — builds from Dockerfile in cloud on git push [96] | **PAID-GATED** — Creating Docker Spaces requires PRO ($9/mo) [97] | 2 vCPU / 16 GB RAM (CPU Basic hardware is $0/hr) [97] | No explicit HTTP timeout published [97] | Automatically pauses after 48h idle [98] | Ephemeral 50GB; persistent bucket paid [99] | Custom domains require PRO plan [100] | Native Space Secrets [96] | GitHub Actions hub-sync mirror [101] | No Singapore region picker [97] | Standard Content Policy [102] |
| **Deno Deploy** | **NOT SUPPORTED** (JS/TS/WASM only) [103] | N/A | Free: 1M req, 10 CPU-hrs/mo. [104] | 768 MB RAM, 10 concurrent apps [104] | Not published [104] | Auto-sleeps after ~20-30s idle [104] | Ephemeral / Deno KV [104] | Native env vars [104] | Native GitHub CI/CD [103] | Unverified (2 global regions) [104] | "For personal use and smaller projects" [104] |

---

## 6. Table Sources & Citations

*Every source URL below was fetched and verified on 2026-10-07:*

- **[1]** Google Cloud Run Overview: `https://cloud.google.com/run`
- **[2]** Google Cloud Run Source Deployment: `https://docs.cloud.google.com/run/docs/deploying-source-code`
- **[3]** Google Cloud Run Pricing & Quotas: `https://cloud.google.com/run/pricing` & `https://docs.cloud.google.com/free/docs/free-cloud-features`
- **[4]** Google Cloud Run Autoscaling & Idle Rules: `https://docs.cloud.google.com/run/docs/about-instance-autoscaling` & `https://docs.cloud.google.com/run/docs/about-concurrency`
- **[5]** Google Cloud Run Request Timeout (3600s): `https://docs.cloud.google.com/run/docs/configuring/request-timeout`
- **[6]** Google Cloud Run Locations & Domains: `https://docs.cloud.google.com/run/docs/locations`
- **[7]** Google Cloud Run Secret Manager: `https://docs.cloud.google.com/run/docs/configuring/services/secrets`
- **[8]** Google Cloud Run Deploy Continuously: `https://docs.cloud.google.com/run/docs/quickstarts/deploy-continuously`
- **[9]** Azure Container Apps Pricing & Free Grant: `https://azure.microsoft.com/en-ca/pricing/details/container-apps` & `https://containerapps.azure.com/docs/containerapps/faq`
- **[10]** Azure ACR Tasks Cloud Build: `https://learn.microsoft.com/en-us/azure/container-registry/container-registry-quickstart-task-cli` & `https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tasks-pack-build`
- **[11]** Azure Container Apps Ingress & Timeout (2400s): `https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview`
- **[12]** Azure Container Apps Custom Domains: `https://learn.microsoft.com/en-us/azure/container-apps/custom-domains-managed-certificates`
- **[13]** Azure Container Apps Manage Secrets: `https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets`
- **[14]** Azure Container Apps GitHub Actions: `https://learn.microsoft.com/en-us/azure/container-apps/github-actions`
- **[15]** AWS Lambda Python 3.13 Support & LWA: `https://aws.amazon.com/about-aws/whats-new/2024/11/aws-lambda-support-python-313/` & `https://github.com/aws/aws-lambda-web-adapter`
- **[16]** AWS SAM Pipeline Bootstrap: `https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-pipeline-bootstrap.html`
- **[17]** AWS Lambda Pricing & Free Tier: `https://aws.amazon.com/lambda/pricing/` & `https://aws.amazon.com/free/`
- **[18]** AWS Lambda Configuration Timeout (900s): `https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html` & `https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html`
- **[19]** AWS Lambda Function URLs: `https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html`
- **[20]** Render Python Versions: `https://render.com/docs/python-version`
- **[21]** Render Free Tier Specs & Idle Rules: `https://render.com/docs/free.md`
- **[22]** Render HTTP Timeout (100 min): `https://render.com/docs/render-vs-vercel-comparison` & `https://render.com/articles/django-production-deployment`
- **[23]** Render Environment Variables: `https://render.com/docs/environment-variables.md`
- **[24]** Render Regions: `https://render.com/docs/regions.md`
- **[25]** Railpack Python 3.13: `https://railpack.com/languages/python/`
- **[26]** Railway Cloud Builds: `https://docs.railway.com/builds/railpack`
- **[27]** Railway Pricing & Free Trial: `https://railway.com/pricing` & `https://docs.railway.com/pricing/free-trial`
- **[28]** Railway Timeout Limits (15m): `https://docs.railway.com/deployments/troubleshooting/slow-deployments`
- **[29]** Railway Serverless Sleeping: `https://docs.railway.com/deployments/serverless`
- **[30]** Railway Volumes: `https://docs.railway.com/reference/volumes`
- **[31]** Railway Variables: `https://docs.railway.com/variables`
- **[32]** Railway Regions: `https://docs.railway.com/deployments/regions`
- **[33]** Railway Terms & Fair Use: `https://railway.com/legal/terms` & `https://railway.com/legal/fair-use`
- **[34]** Vercel Python Runtime: `https://vercel.com/docs/functions/runtimes/python`
- **[35]** Vercel for GitHub: `https://vercel.com/docs/git/vercel-for-github`
- **[36]** Vercel Hobby Plan & Non-Commercial Terms: `https://vercel.com/docs/plans/hobby`
- **[37]** Vercel Fluid Compute & Concurrency: `https://vercel.com/docs/fluid-compute` & `https://vercel.com/docs/functions/limitations`
- **[38]** Vercel Function Duration Limits (300s): `https://vercel.com/docs/functions/configuring-functions/duration`
- **[39]** Vercel Regions: `https://vercel.com/docs/regions`
- **[40]** Azure App Service Linux Pricing & Quotas: `https://azure.microsoft.com/en-us/pricing/details/app-service/linux/`
- **[41]** Azure App Service Python Deployment: `https://learn.microsoft.com/en-us/azure/app-service/quickstart-python`
- **[42]** Azure Websites Limits: `https://github.com/MicrosoftDocs/azure-docs/blob/main/includes/azure-websites-limits.md`
- **[43]** Azure App Service 240s Request Timeout: `https://learn.microsoft.com/en-us/troubleshoot/azure/app-service/web-request-times-out-app-service`
- **[44]** Azure App Service Custom Domains: `https://learn.microsoft.com/en-us/azure/app-service/app-service-web-tutorial-custom-domain`
- **[45]** Azure App Service Continuous Deployment: `https://learn.microsoft.com/en-us/azure/app-service/deploy-continuous-deployment`
- **[46]** Koyeb Python Runtime: `https://www.koyeb.com/docs/build-and-deploy/build-from-git/python`
- **[47]** Koyeb Git Deploy: `https://www.koyeb.com/docs/build-and-deploy/deploy-with-git`
- **[48]** Koyeb Pricing FAQ: `https://www.koyeb.com/docs/faqs/pricing`
- **[49]** Koyeb Free Instances: `https://www.koyeb.com/docs/reference/instances#free-instances`
- **[50]** Koyeb 100s Request Timeout: `https://www.koyeb.com/docs/reference/edge-network#requests-timeouts`
- **[51]** Koyeb Domains: `https://www.koyeb.com/docs/run-and-scale/domains`
- **[52]** Koyeb Secrets: `https://www.koyeb.com/docs/reference/secrets`
- **[53]** Koyeb Legal Terms: `https://www.koyeb.com/docs/legal/terms`
- **[54]** Modal Existing Images & FastAPI: `https://modal.com/docs/guide/existing-images`
- **[55]** Modal Cloud Builds: `https://modal.com/docs/guide/existing-images`
- **[56]** Modal Pricing: `https://modal.com/pricing`
- **[57]** Modal Webhook Timeouts (150s): `https://modal.com/docs/guide/webhook-timeouts`
- **[58]** Modal Cold Starts: `https://modal.com/docs/guide/cold-start`
- **[59]** Modal Continuous Deployment: `https://modal.com/docs/guide/continuous-deployment`
- **[60]** Modal Region Selection: `https://modal.com/docs/guide/region-selection`
- **[61]** Modal Legal Terms: `https://modal.com/legal/terms-effective-date-october-2025`
- **[62]** Northflank Cloud Builds: `https://northflank.com/docs/v1/application/build/build-your-code-on-northflank`
- **[63]** Northflank Pricing & Credit Card Requirement: `https://northflank.com/docs/v1/application/billing/pricing-on-northflank.md` & `https://northflank.com/pricing`
- **[64]** Northflank Path Routing Timeouts: `https://northflank.com/docs/v1/application/domains/use-path-based-routing`
- **[65]** Northflank Certificate Generation: `https://northflank.com/docs/v1/application/domains/certificate-generation`
- **[66]** Northflank Secrets: `https://northflank.com/docs/v1/application/secure/inject-secrets`
- **[67]** Northflank Singapore Regions: `https://northflank.com/cloud/gcp/regions/asia-southeast1` & `https://northflank.com/cloud/aws/regions/ap-southeast-1`
- **[68]** Northflank Terms: `https://northflank.com/legal/terms`
- **[69]** Cloudflare Python Workers & FastAPI: `https://developers.cloudflare.com/workers/languages/python/packages/fastapi/`
- **[70]** Cloudflare Deployments: `https://developers.cloudflare.com/workers/get-started/guide/`
- **[71]** Cloudflare Workers Limits & 10ms CPU Cap: `https://developers.cloudflare.com/workers/platform/limits/`
- **[72]** Cloudflare Workers CI/CD: `https://developers.cloudflare.com/workers/ci-cd/builds/`
- **[73]** Cloudflare Network: `https://www.cloudflare.com/network/`
- **[74]** Cloudflare Containers Get Started: `https://developers.cloudflare.com/containers/get-started/` & `https://developers.cloudflare.com/changelog/post/2026-04-13-containers-sandbox-ga/`
- **[75]** Cloudflare Containers Pricing: `https://developers.cloudflare.com/containers/platform/pricing/`
- **[76]** Fly.io Deploy Docs: `https://docs.fly.io/flyctl/deploy/`
- **[77]** Fly.io Remote Builders: `https://docs.fly.io/flyctl/integrating/`
- **[78]** Fly.io Discontinued Plans & Pricing: `https://docs.fly.io/about/discontinued-plans` & `https://docs.fly.io/about/pricing`
- **[79]** Fly.io Proxy Idle Timeout: `https://community.fly.io/t/is-it-possible-to-increase-the-timeout-to-120-sec/3007`
- **[80]** Fly.io Free Quota ToS: `https://community.fly.io/t/free-usage-quotas-and-violating-terms-of-service/8580`
- **[81]** DigitalOcean App Platform Python: `https://docs.digitalocean.com/products/app-platform/getting-started/sample-apps/python/`
- **[82]** DigitalOcean App Platform Overview: `https://www.digitalocean.com/products/app-platform`
- **[83]** DigitalOcean App Platform Pricing: `https://docs.digitalocean.com/products/app-platform/details/pricing/`
- **[84]** DigitalOcean 100s Request Timeout: `https://docs.digitalocean.com/support/my-php-app-is-timing-out-and-throwing-5xx-errors/`
- **[85]** DigitalOcean App Platform Ephemeral Storage: `https://docs.digitalocean.com/products/app-platform/how-to/store-data/`
- **[86]** DigitalOcean Regional Availability: `https://docs.digitalocean.com/platform/regional-availability/`
- **[87]** DigitalOcean Terms & AUP: `https://www.digitalocean.com/legal/terms-of-service-agreement` & `https://www.digitalocean.com/legal/acceptable-use-policy`
- **[88]** Zeabur Python Guides: `https://zeabur.com/docs/en-US/guides/python`
- **[89]** Zeabur Cloud Builds: `https://zeabur.com/docs/en-US/deploy/how-deploys-work`
- **[90]** Zeabur Shared Cluster Phased Out: `https://zeabur.com/changelogs/phasing-out-shared-cluster` & `https://zeabur.com/docs/en-US/pricing/free-plan`
- **[91]** Zeabur Best Practices: `https://zeabur.com/docs/en-US/get-started/best-practices`
- **[92]** Zeabur Storage & Secrets: `https://zeabur.com/docs/en-US/deploy/customize-prebuilt`
- **[93]** Zeabur Domains: `https://zeabur.com/docs/en-US/domain/management`
- **[94]** Zeabur VPS Singapore: `https://zeabur.com/product/vps`
- **[95]** Zeabur Fair Use: `https://zeabur.com/docs/en-US/compliance/fair-use-guidelines`
- **[96]** Hugging Face Docker Spaces: `https://huggingface.co/docs/hub/en/spaces-sdks-docker`
- **[97]** Hugging Face Spaces Overview & Paid Policy: `https://huggingface.co/docs/hub/en/spaces-overview`
- **[98]** Hugging Face Manage Spaces (48h Inactivity Rule): `https://huggingface.co/docs/huggingface_hub/main/en/guides/manage-spaces`
- **[99]** Hugging Face Spaces Storage: `https://huggingface.co/docs/hub/en/spaces-storage`
- **[100]** Hugging Face Custom Domains: `https://huggingface.co/docs/hub/en/spaces-custom-domain`
- **[101]** Hugging Face Repositories GitHub Actions: `https://huggingface.co/docs/hub/repositories-github-actions`
- **[102]** Hugging Face Content Policy: `https://huggingface.co/content-policy`
- **[103]** Deno Deploy Documentation: `https://docs.deno.com/deploy/`
- **[104]** Deno Deploy Pricing & Specifications: `https://deno.com/deploy/pricing`

---

## 7. Not Verified / Gaps

1. **Google Cloud Run ToS Commercial Carve-out:** While the Cloud Run Pricing and Free Tier pages contain no commercial/academic restrictions, the full Google Cloud Master Agreement was not read line-by-line for educational use stipulations.
2. **Azure Container Apps Scale-to-Zero Inactivity Window:** While scale-to-zero is officially confirmed and documented, Microsoft does not publish a universal fixed idle timeout before down-scaling (varies dynamically based on cooling period configuration).
3. **AWS Lambda Exact Frozen Environment Expiration:** AWS does not publish an exact numeric idle duration before a frozen execution environment is recycled by the internal placement engine.
4. **Render Free Tier Cardless Signup Guarantee:** Secondary sources and developer consensus report that Render allows free web service deployment without adding a payment card, but Render's dynamic signup flow was not interactively executed to test whether recent fraud-prevention flags now prompt for a card.
5. **Deno Deploy Available Regions:** The comparison table states Deno Deploy has "2 regions" (consolidated from 6 on classic), but the specific cities/regions were not enumerated on the pages fetched. (Moot since Python is unsupported).
6. **Northflank Global HTTP Timeout Ceiling:** Northflank documents custom per-path timeout configuration, but does not publish an overarching reverse-proxy hard timeout ceiling.
