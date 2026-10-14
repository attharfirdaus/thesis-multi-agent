# Card-free managed PaaS for the FastAPI backend — primary-source survey

**Access date for every source below: 2026-10-14.** Every claim is from the provider's own pricing/FAQ/docs page fetched today. Third-party blogs are never the source for the card column. Items that could not be read from a primary page are marked `[UNVERIFIED]` with the reason.

**Decision rule (from the brief).** A host is acceptable only if (a) no credit card is needed at signup, (b) no credit card is needed to deploy a free service, (c) no pre-authorisation/hold is placed on a card "for verification", (d) no VM/SSH/server administration, (e) the free tier still exists months from now. Backend shape: FastAPI/Uvicorn (ASGI), ~250–400 MB RSS, no ML libs, network I/O to a hosted LLM API and to Neon PostgreSQL in Singapore; a batch of 30–100 submissions, each a few minutes, whole batch 10–60 min; an HTTP request timeout >= 100 s is workable.

---

## 1. Credit-card column first — all candidates

| Provider | Card required at signup? | Card required to deploy a free service? | Pre-auth / hold | Verdict |
|---|---|---|---|---|
| **Render** | **NO** — "No credit card is required." [R1]; "without … entering credit card information" [R1] | **NO** — "All of my services run on free instances. Can I still be billed? *Yes, if you've added a payment method.*" — i.e. a payment method is optional [R2] | None at signup. If you *do* add a card: "A $1 USD transaction is performed as a credit security check … refunded after the transaction completes." [R3] | **PASS — best candidate** |
| **Modal (Starter)** | NO — signup page has no payment field, only "Continue with GitHub / Continue with Google / Continue with SSO" [M1]. No literal "no card" sentence → `[UNVERIFIED]` as a quote | NO on Starter; card only appears on upgrade paths [M2] | None stated | **PASS** (ASGI, 150 s web timeout) |
| **Leapcell (Hobby)** | No card field in signup/pricing/docs; card text is upgrade-only ("We accept all major credit and debit cards" [L1]). No literal "no card" sentence → `[UNVERIFIED]` | NO on Hobby; "$1 USD transaction … as a credit security check" only *after* adding a card [L1] | Only the $1 check after adding a card | **PASS with a hard quota caveat** |
| **Vercel (Hobby)** | **NO** — "The Hobby plan is free"; card entry appears only in Pro upgrade steps [V1] | NO | None stated for Hobby | **PASS, but non-commercial-only terms** |
| **Cloudflare Workers/Containers** | NO for Workers free | Containers: "Available on Workers Paid plan" ($5/mo min) [CF1] | — | FAIL — no Python ASGI on free |
| **Red Hat OpenShift Developer Sandbox** | **NO** — "It is free. There is no credit card required. All you need is a Red Hat account." [RH1] | NO | None stated | FAIL — 30-day trial only |
| **Wispbyte (free)** | **NO** — "512 MB RAM and 1 GB disk for EUR 0. No card, no coins, and you never have to watch an ad to keep it online." [W1] | NO | None stated | FAIL — no HTTPS/custom-domain evidence, Romania-only |
| **Replit (Starter)** | NO card mentioned; "Create apps and publish your first project - all at no cost." [RP1] | NO for the first published app | None stated | FAIL — published link "will automatically go down after 30 days" [RP1] |
| **Hugging Face Spaces** | NO | **YES for anything that runs compute** — "Static Spaces are free for everyone. Gradio and Docker Spaces run on compute and require a paid plan to create: PRO for personal accounts" [H1]; PRO is $9/mo, "Team (via credit card)" [H2] | — | **FAIL — FastAPI needs the Docker SDK, which is PRO-only** |
| **Railway** | **NO** for the trial — "Can I try Railway without a credit card? Yes. … You will receive a one-time grant of $5 to use on resources." [RW1] | NO during the 30-day trial. After it reverts to the $0 Free plan: `[UNVERIFIED]` — Railway never states a card is required for the Free plan, only "Each Railway account needs an active subscription" [RW2] | No hold documented | **FAIL — $1/month credit cannot keep a service online** |
| **PythonAnywhere (Beginner)** | NO card on the free plan (free account flow has no payment step); no explicit "no card" sentence → `[UNVERIFIED]` | NO — "You'll get one web app at your-username.pythonanywhere.com and two consoles with **restricted outbound Internet access**." [P1] | None — no payment instrument in the free flow | **FAIL — outbound allowlist + WSGI-only + 5-min worker kill** |
| **Back4App Containers (free)** | **NO** — "you can spin up your Dockerized software project at no charge (no credit card required)" [B1] | NO — "Yes. Back4app Web Deployment has a Free tier (no credit card required)" [B1] | None stated | **FAIL — free container lives 60 minutes** |
| **Clever Cloud** | **NO** — "When you sign up you will get free credits to give Clever Cloud a try with no payment card required." [CC1] | NO while credits last | None stated | **FAIL — no permanent free tier; nano 1 vCPU/512 MB = €6/mo** |
| **Northflank** | **Effectively YES** — "all users must add a payment method to start creating resources on Northflank, regardless of plan selection." [N1] | **YES** — same sentence | Not stated | **FAIL — card mandatory even on the free tier** |
| **Zeabur** | **NO** — "No credit card required — just sign up and start deploying." [Z1] | **YES in practice** — "Shared clusters have been deprecated. **New projects can no longer be created on shared clusters**" [Z2]; free plan has no runtime compute, only "Manageable own servers: 1" [Z3] | `[UNVERIFIED]` | **FAIL — needs a purchased Zeabur server (VPS/root)** |
| **Koyeb** | **YES** — "You'll need a valid payment method and must subscribe to one of our paid plans to get started."; "We require a credit card to prevent fraud and abuse." [K1] | **YES** — no cardless path for new signups | **YES, $29** — "We verify the card you enter by placing a $29 pre-authorization hold and immediately canceling it." [K1] | **FAIL — card + paid plan mandatory** |
| **Fly.io** | **YES after trial** — "You don't need a credit card to start the trial. After the trial ends, you'll need to add a credit card" [F1]; "All organizations (except for Linked Organizations) require a credit card on file." [F1] | YES outside the trial | Trial only; card mandatory after | **FAIL — "Is there a free tier? **No.** New organizations don't have a free tier or a monthly free usage allowance."** [F1] |
| **Scalingo** | NO at account creation, **but the trial requires a payment method** — "To use your free trial, you must configure your billing profile and add a valid payment method." [S1] (marketing page contradicts: "30 days free trial, no credit card required" [S2] → conflict unresolved) | **YES** — same sentence [S1] | "when you enter a card, we only verify the card" [S3] | **FAIL — 30-day trial, billing starts automatically after** |
| **Qoddi** | Card required before **any** resource — "A credit or debit card is required to verify your account, **even when you host only free static sites**. Prepaid cards are not accepted." [Q1] | **YES** — "requires the verification of a valid form of payment before any resource can be created" [Q2] | **YES, $1** — "a $1 charge will appear on your account, this is only a pre-authorization" [Q2] | **FAIL — card + pre-auth hold; no free app tier** |
| **Alwaysdata (free)** | NO — "Sign up for free and without purchase obligation right now!" [A1] | NO | None stated | FAIL — Python is WSGI-only, 256 MB RAM |
| **Zerops** | Card/credits required — "Enter your desired top-up amount (minimum $10 VAT excl.)" [ZR1] | YES for services ("Services in Zerops require computing resources that are billed separately from your project core") [ZR1] | Not stated | FAIL — no free compute |
| **Sevalla / Kinsta app hosting** | **YES** — "When you sign up to Sevalla, the first thing you need to do is enter your payment method and billing details, and then click Complete setup." [SV1] | YES; only static hosting is free [SV2] | Not stated | FAIL |
| **IBM Cloud Code Engine** | YES — "you're asked to provide credit card information for identity verification" [IB1] | YES | Not stated | FAIL |
| **Google Cloud Run** | YES — "you must provide a credit card … during the sign up" + "$0.00 and $1.00 USD" pending transaction [G1] | YES (owner's card already rejected: `OR_MIVEM_02`) | YES | FAIL |
| **Azure Container Apps** | YES — "a credit card or a debit card (non-prepaid)" + "one-dollar … verification hold" [AZ1] | YES | YES | FAIL |
| **Oracle Cloud Always Free** | YES — "Oracle may periodically check the validity of your card, resulting in a temporary "authorization" hold." [O1] | YES | YES | FAIL (also VM-shaped) |
| **SAP BTP** | No card for the trial | Free tier needs a commercial contract — "The free tier model for SAP BTP is a commercial model that can be accessed by signing up for an SAP BTP Enterprise Agreement … or Pay-As-You-Go" [SA1] | — | FAIL — trial ends at 90 days |
| **Hostman, WSO2 Choreo, Patr Cloud, Netlify functions** | — | — | — | FAIL — no free backend/app tier, or self-hosted closed beta, or 60 s function cap |

### Dead or discontinued (say it plainly)

| Host | Status |
|---|---|
| **Glitch** | Dead. "We'll be ending web hosting for your apps on Glitch on July 8, 2025." [GL1] Hosting ended; the domain now belongs to an unrelated sports product ("Glitch is a sports technology product operated by Otaku Labs Inc." [GL2]) |
| **Cyclic.sh** | Dead. "Cyclic is Shutting Down" [CY1] |
| **Adaptable.io** | Dead pool — company stage "Deadpooled" in the Tracxn company profile [AD1] |
| **Deta Space** | Dead — https://deta.space/ returns HTTP 530 (fetched 2026-10-14); deta.sh no longer resolves; "Space is unfortunately sunsetting" [DS1] |
| **Genezio** | Dead as a PaaS — pricing page now reads "The enterprise AI visibility platform" [GN1] |
| **Koyeb as a free host** | Alive as a company (joining Mistral AI) but "New users will only be able to sign up for those [Pro+] plans." [K2] |

---

## 2. What the card-free survivors actually give you

| | **Render (Free)** | **Modal (Starter)** | **Leapcell (Hobby)** | **Vercel (Hobby)** |
|---|---|---|---|---|
| RAM / CPU | "0.1 CPU / 512 MB RAM" [R4]; free plan id `free` [R3] | Not published per-container on the pricing page; $30/month of compute credit, "100 containers + 10 GPU concurrency" [M2] | "3 vCPUs, 4GB RAM" per project cap, serverless duration quota below [L1] | Serverless only: "Active CPU 4 CPU-hrs", "Provisioned Memory 360 GB-hrs" [V1] |
| Instance hours / compute quota | "Render grants **750 Free instance hours** to each workspace per calendar month"; "If you consume all of your Free instance hours during a given month, Render **suspends** all of your Free web services until the start of the next month." [R5] 750 h > a 31-day month (744 h) → one always-on service fits `[INFERENCE: arithmetic]` | "$30 / month free credits", monthly recurring [M2] | "Serverless Duration **3 GB-hours / month** included" [L1] | Monthly allowances above; "if you exceed your usage limits on the Hobby plan, you will have to wait until 30 days have passed before you can use the feature again." [V1] |
| Bandwidth / egress | Hobby: "5 GB included per month (then $0.15 per GB)" [R3]. Service-initiated traffic (LLM API calls, external DB) counts [R6] | "1 TiB / month free network egress" [M2] | "Data Transfer 2 GB / month included"; "Max Payload Size 100 MB" [L1] | "Fast Data Transfer First 100 GB"; "Fast Origin Transfer First 10 GB" [V1] |
| Build minutes | "Standard build pipeline \| 500 mins per month (then $5 per 1K mins)" [R3] | "Build Execution 60 Min / month included"; "Max Build Duration 10 Minutes" [L1] | Builds up to 45 min per deployment [V1] |
| Idle / sleep rule | "Render **spins down** a Free web service that goes 15 minutes without receiving any inbound traffic. This includes both HTTP requests and WebSocket messages from existing connections." Cold start "about one minute" [R5] | Scale-to-zero is intrinsic to the model; keep-warm not documented on pricing | "Invocation Timeout 900 Seconds" [L1]; serverless idle semantics | Serverless only; no always-on process on Hobby [V1] |
| **Max HTTP request duration** | **6000 s (100 min)** — "Render allows responses to take up to 100 minutes for HTTP requests." [R7] | **150 s** — "All Web Function types (modal.fastapi_endpoint, modal.asgi_app, modal.wsgi_app, and modal.web_server) have a maximum HTTP request timeout of 150 seconds enforced." [M3] | **900 s** — "Request Timeout … Free 15 min" [L4] | **300 s** — "Maximum duration \| 300s (5 minutes) default and max" [V2] |
| Does the idle rule kill an in-flight request? | No documented cap other than the 100-min response limit; the spin-down timer is defined on "receiving any inbound traffic", so a live request keeps it awake. Separately, "Render might restart a Free web service at any time." [R5] Whether such a restart aborts an in-flight request is `[UNVERIFIED]` | No idle-kill documented; the 150 s cap is the binding limit, and long work is the documented pattern to move to background Functions (`.spawn()`) [M3] | No idle-kill documented | Requests end at 300 s; nothing to kill |
| FastAPI / ASGI support | Native: language "Python 3", start "`uvicorn main:app --host 0.0.0.0 --port $PORT`" [R8]; **uv.lock recognised** — "Render automatically adds uv to your Python service's runtime if your project's root directory includes a `uv.lock` file." [R9]; Docker images also deployable [R4] | Native Python only: "For ASGI apps, you can create a function decorated with `@modal.asgi_app`" [M4] | Native containers; FastAPI quickstart: build "`pip install -r requirements.txt`", start "`uvicorn app:app --host 0.0.0.0 --port 8080`" [L2] | Native ASGI: "Use the Python runtime to run ASGI … applications on Vercel."; "Define dependencies in pyproject.toml (with or without a uv.lock)" [V3] |
| Singapore / SEA region | **YES** — "Oregon, USA / Ohio, USA / Virginia, USA / Frankfurt, Germany / **Singapore**" [R10] | Closest is "ap-southeast" (`ap-south` routing); no Singapore literal; region selection costs 1.15x–1.75x [M5] | `[UNVERIFIED]` — "Deploy in US, Asia and other regions", no region page [L1] | **YES** — "sin1 \| ap-southeast-1 \| Singapore" [V4] |
| HTTPS + custom domain on free tier | YES — 2 custom domains included, "Automatic TLS ✓"; free services support "Custom domains, Managed TLS certificates" [R3][R5] | **NO** — "Custom domains \| Not included" [M2]; only `*.modal.run` | YES — "Custom Domain with Free TLS"; Let's Encrypt [L5] | YES — domains per project 50, "HTTPS Certificates \| Included" [V1] |
| Secrets / env vars, GitHub deploys | "Environment variables & secret files ✓"; native GitHub auto-deploys [R3][R4] | "Secrets \| Unlimited" [M2]; deploys via `modal deploy` CLI, GitHub integration not documented | "variables are encrypted and private"; "Every push to the linked branch automatically triggers a build and deploy." [L6] | Env vars 1000/env, 64 KB total for Python projects; GitHub CI/CD included, but Hobby cannot link org-owned repos [V1] |
| What happens when the free limit is exceeded | Instance hours: "Render **suspends** all of your Free web services until the start of the next month." Bandwidth: "If you haven't added a payment method, Render instead suspends all of your Free services for the remainder of the month." Builds: "Render instead disables all new builds for your workspace for the remainder of the month" [R5]. Also: "Render **may suspend** a Free web service that initiates an uncommonly high volume of traffic over the public internet" — examples listed are "Accessing an external database" and "Invoking external APIs" [R5] | `[UNVERIFIED]` — post-credit-exhaustion behaviour not documented on the pages read | "We will response you a 429 status code and exception message." [L1] | "you will have to wait until 30 days have passed before you can use the feature again." [V1] |

### Near-misses worth a line (documented reasons they lose)

- **Back4App Containers** — card-free, Docker-first, 0.25 CPU / 256 MB / 100 GB transfer, but: "On the free plan the URL and the container live **60 minutes** from the moment the deploy starts" [B2]; USA region only [B1]. A 60-minute batch could *just* fit, but the app cannot exist between demonstrations.
- **PythonAnywhere** — card-free, but free accounts get "restricted outbound Internet access" [P1], ASGI is "an experimental feature" [P3], and "we set a 5-minute timeout on all web workers. If they can't respond to a request in under that time, they're assumed to have accidentally hung, and are restarted." [P2] No Docker. Neon over TCP:5432 is not reachable from a free account (`[INFERENCE]` from the restricted-outbound statement; no primary page enumerates the allowlist for free accounts).
- **Hugging Face Spaces** — free CPU Basic is generous (2 vCPU / 16 GB / 50 GB disk), but FastAPI requires the Docker SDK, and "Gradio and Docker Spaces run on compute and require a paid plan to create: PRO" [H1]. Even if paid, "If your Space needs to make any network requests, you can make requests through the standard HTTP and HTTPS ports (80 and 443) along with port 8080. **Any requests going to other ports will be blocked.**" [H3] — Neon (5432/TCP) is blocked.
- **Deno Deploy** — JS/TS runtime only; no Python/FastAPI path documented [D1]. Also pauses at free quota. `[UNVERIFIED]`: exact Deno free-tier wording was not transcribed here beyond the language failure.
- **Northflank** — genuinely generous free tier ("no sleeping" per its pricing copy) but blocked by the mandatory payment method [N1].
- **Railway** — card-free trial, PostgreSQL/regions fine (Singapore: "asia-southeast1-eqsg3a" [RW3]), native uv/FastAPI detection [RW4], 900 s request timeout [RW5] — but the recurring $1/month credit cannot fund 24/7 compute `[INFERENCE: arithmetic]`.
- **Zeabur** — cardless signup, but free projects can no longer be created on shared clusters [Z2]; deploying needs a purchased monthly server [Z3].
- **Clever Cloud** — the best *technical* fit of the failures: native uv mode ("Native uv deployment activates when … a `uv.lock` file exists at the root of your project" [CC2]), Singapore in the infrastructure list [CC3], but no permanent free tier — free credits only [CC1].

---

## 3. Genuinely usable card-free for THIS backend

Criteria applied: card-free (verified), ASGI, free tier that persists, >= 100 s requests, no in-flight kill by an idle rule, TCP egress to Neon Singapore (not just 80/443).

1. **Render — Free web service.** The only candidate that is card-free, permanent, always-on-capable (750 instance h/month), Singapore-region, HTTPS + 2 custom domains, native Python with `uv.lock` support or the existing `backend/Dockerfile`.
   **Blocking limitations, named:** (a) "Render **may suspend** a Free web service that initiates an uncommonly high volume of traffic over the public internet", with "Accessing an external database" and "Invoking external APIs" given as examples [R5] — this is exactly this app's traffic pattern, and it is a *documented* suspension risk; (b) 0.1 CPU / 512 MB RAM is at the bottom edge of the 250–400 MB budget; (c) 15-minute idle spin-down, ~1-minute cold start, and "Render might restart a Free web service at any time" [R5]; (d) 5 GB/month egress shared with service-initiated traffic (the LLM API calls) [R3][R6]; (e) no persistent disk on free — sessions/documents must live in Neon, not on the filesystem.
2. **Modal (Starter) — as a second host or the batch executor.** Native `@modal.asgi_app`, $30/month recurring credit, no card field at signup, 1 TiB egress, unlimited secrets.
   **Blocking limitations:** 150 s enforced HTTP request timeout [M3] — the batch must be split per submission or moved to background Functions with `.spawn()` + polling; **no custom domain on free** ("Custom domains \| Not included") [M2]; no Singapore literal (nearest `ap-southeast`) [M5]; post-credit-exhaustion behaviour undocumented `[UNVERIFIED]`.
3. **Leapcell (Hobby) — usable only as a light demo.** FastAPI quickstart, 900 s request timeout, free custom domain + TLS.
   **Blocking limitation:** "Serverless Duration 3 GB-hours / month included" [L1] — a 400 MB service running the 60-minute batch burns roughly 0.4 GB-h per batch, so the month's allowance is a handful of batches at most `[INFERENCE: arithmetic]`; persistent servers are Plus-only. Card-free status rests on absence of a card field rather than an explicit sentence `[UNVERIFIED]`.
4. **Vercel (Hobby) — usable for the API surface only, and probably disallowed by its own terms.** Native ASGI Python, `sin1` Singapore, 300 s max request, 100 GB transfer.
   **Blocking limitations:** "the Hobby plan restricts users to **non-commercial, personal use only**." [V1] — a thesis prototype for an institution is a terms question the owner must decide, not a technical one; 300 s cap [V2]; no always-on process, so a 10–60-minute batch must be decomposed; it is a serverless platform, not a PaaS (the sibling report `local://cardfree-serverless.md` covers that class in depth).

Everything else on the candidate list is either dead, no longer free, trial-only, or has a card in the path.

**Practical shape of the answer:** deploy the FastAPI backend as a Render Free web service in the Singapore region (status quo Docker or native + `uv.lock`), accept the 15-minute spin-down and accept that Render reserves the right to suspend a free service for heavy service-initiated traffic; keep Neon as the database (Render's own free Postgres "expire 30 days after creation" [R5] — do not use it for the demo); keep Modal Starter configured as the fallback runner if Render suspends or the 512 MB / 0.1 CPU instance proves too small.

---

## 4. Not verified / gaps

1. **Render request timeout provenance.** "100 minutes" appears on `render.com/docs/render-vs-heroku-comparison` [R7], not on the web-services or limits pages. The binding number for the load balancer may differ; no throttling/idle-timeout value is published in the free-tier doc. `[UNVERIFIED]`
2. **Render native uv support vs Dockerfile.** uv.lock detection is documented [R9]; whether the *build* uses `uv sync` and whether `pyproject.toml` alone (no lock) works is not stated. The existing `backend/Dockerfile` is the deterministic path.
3. **Whether a Render forced restart aborts an in-flight request.** Not stated. `[UNVERIFIED]`
4. **Modal card-free.** No primary sentence says "no credit card"; the evidence is the absence of any payment field on `modal.com/signup`. `[UNVERIFIED]` — worth one manual check with the owner's browser before committing.
5. **Modal Starter per-container RAM/CPU** and post-credit-exhaustion behaviour: not published on the pricing page. `[UNVERIFIED]`
6. **Leapcell card-free** (same absence-of-evidence issue) and its region list — no region page exists; Singapore presence unconfirmed. `[UNVERIFIED]`
7. **Vercel Hobby card-free** — no literal sentence; card entry is shown only in Pro upgrade steps. `[UNVERIFIED]`
8. **PythonAnywhere free-tier outbound allowlist** — no primary page enumerates which hosts a free account may reach, so "an arbitrary LLM API host is reachable" and "Neon 5432 is blocked" are inferences from "restricted outbound Internet access" [P1], not quotes. `[UNVERIFIED]`
9. **PythonAnywhere free-plan ASGI pricing** — "We have not worked out the long-term pricing for ASGI sites … We're 99.9% certain that there will be a way to host them in a free plan, though!" [P4] — not a commitment. `[UNVERIFIED]`
10. **Deno Deploy** — only the language failure was confirmed; the 2026 free-tier numbers and pause behaviour were not transcribed from Deno's own page in this pass. `[UNVERIFIED]`
11. **Back4App** — HTTP request timeout and build-minute quota are not published; the 60-minute lifetime is documented but its exact interaction with a request already in flight is not. `[UNVERIFIED]`
12. **Clever Cloud** — the size and validity period of the signup free credits are not stated on the pages read, so "how many months of demo" cannot be bounded. `[UNVERIFIED]`
13. **Scalingo** — direct contradiction between `doc.scalingo.com` ("you must … add a valid payment method") [S1] and the marketing page ("no credit card required") [S2]; unresolved. `[UNVERIFIED]`
14. **Wispbyte** — JS-only rendering left the fair-use text unavailable; HTTPS/custom-domain and request timeout unverified. `[UNVERIFIED]`
15. **Neon connectivity from Modal/Leapcell/Vercel** — none of these pages document arbitrary outbound TCP, so reachability of Neon's Singapore Postgres is an inference from the platform model, not a quote. `[UNVERIFIED]`
16. **Longevity.** Every free tier here can change without notice; the Render storefront could not be checked from the owner's network today. Nothing in this report is a guarantee that these terms hold at demonstration time months from now.
17. **Source-provenance caveat.** Rows marked [R*], [H*], [F*], [N1], [V1] and the dead-host table were re-fetched and quoted by me directly today; the remaining rows rest on primary pages fetched by delegated researchers this same day and are quoted verbatim from those fetches, without an independent second read.

---

## Sources (all accessed 2026-10-14)

- [R1] https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026 — "No credit card is required."
- [R2] https://render.com/docs/faq — "All of my services run on free instances. Can I still be billed? Yes, if you've added a payment method."
- [R3] https://render.com/pricing
- [R4] https://render.com/docs/web-services and https://render.com/docs/compute-plans
- [R5] https://render.com/docs/free
- [R6] https://render.com/docs/outbound-bandwidth
- [R7] https://render.com/docs/render-vs-heroku-comparison — "Render allows responses to take up to 100 minutes for HTTP requests."
- [R8] https://render.com/docs/deploy-fastapi
- [R9] https://render.com/docs/uv-version
- [R10] https://render.com/docs/regions
- [M1] https://modal.com/signup · [M2] https://modal.com/pricing · [M3] https://modal.com/docs/guide/webhook-timeouts · [M4] https://modal.com/docs/guide/webhooks · [M5] https://modal.com/docs/guide/region-selection
- [L1] https://leapcell.io/pricing · [L2] https://docs.leapcell.io/examples/python/fastapi · [L4] https://docs.leapcell.io/limit · [L5] https://docs.leapcell.io/service/domain · [L6] https://docs.leapcell.io/overview
- [V1] https://vercel.com/docs/plans/hobby · [V2] https://vercel.com/docs/limits · [V3] https://vercel.com/docs/functions/runtimes/python · [V4] https://vercel.com/docs/regions
- [H1] https://huggingface.co/docs/hub/spaces-overview · [H2] https://huggingface.co/pricing · [H3] https://huggingface.co/docs/hub/spaces-overview (Networking)
- [N1] https://northflank.com/docs/v1/application/billing/pricing-on-northflank
- [F1] https://fly.io/docs/about/pricing/
- [K1] https://www.koyeb.com/docs/faqs/pricing · [K2] https://www.koyeb.com/blog/koyeb-is-joining-mistral-ai-to-build-the-future-of-ai-infrastructure
- [RW1] https://railway.com/pricing · [RW2] https://docs.railway.com/pricing/plans · [RW3] https://docs.railway.com/deployments/regions · [RW4] https://railpack.com/languages/python · [RW5] https://docs.railway.com/networking/public-networking/specs-and-limits
- [Z1] https://zeabur.com/docs/en-US/pricing/free-plan · [Z2] https://zeabur.com/docs/en-US/server/shared-cluster · [Z3] https://zeabur.com/pricing
- [B1] https://www.back4app.com/pricing/container-as-a-service · [B2] https://www.back4app.com/blog/deploy-python-fastapi-dockerfile-database
- [CC1] https://www.clever.cloud/pricing/ · [CC2] https://www.clever.cloud/developers/doc/deploy/applications/python/uv/ · [CC3] https://www.clever.cloud/infrastructure/
- [P1] https://www.pythonanywhere.com/pricing/ · [P2] https://help.pythonanywhere.com/pages/AsyncInWebApps/ · [P3] https://help.pythonanywhere.com/pages/ASGI/ · [P4] https://help.pythonanywhere.com/pages/ASGI/
- [S1] https://doc.scalingo.com/platform/getting-started/free-trial · [S2] https://scalingo.com/runtimes/python-hosting · [S3] https://scalingo.com/pricing
- [Q1] https://qoddi.com/pricing/ · [Q2] https://devcenter.qoddi.com/qoddi-account-verification-procedure/
- [RH1] https://developers.redhat.com/developer-sandbox/FAQ · [W1] https://wispbyte.com/ · [RP1] https://docs.replit.com/billing/plans/starter-plan
- [A1] https://www.alwaysdata.com/en/register/ · [ZR1] https://docs.zerops.io/company/payment · [SV1] https://docs.sevalla.com/ · [SV2] https://sevalla.com/pricing/
- [IB1] https://cloud.ibm.com/docs/account?topic=account-accounts · [G1] https://docs.cloud.google.com/free/docs/free-cloud-features · [AZ1] https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account · [O1] https://www.oracle.com/cloud/free/ · [SA1] https://www.sap.com/products/technology-platform/trial.html
- [CF1] https://developers.cloudflare.com/containers/
- [D1] https://docs.deno.com/deploy/
- Dead: [GL1] https://blog.glitch.com/post/changes-are-coming-to-glitch · [GL2] https://www.tryglitch.com/support · [CY1] https://www.cyclic.sh/posts/cyclic-is-shutting-down · [AD1] https://platform.tracxn.com/a/d/company/58487618e4b048552752e744/adaptable · [DS1] https://x.com/detahq/status/1830605654920466888 · [GN1] https://genezio.com/pricing/
- Sibling report on non-PaaS/serverless hosts: `local://cardfree-serverless.md`
