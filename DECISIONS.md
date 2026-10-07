# DECISIONS — multi-agent LLM evaluation system

Format: `date · decision · options considered · decided by`. Newest first within each phase.
Every provider/model/library fact cited in this project carries a source URL and an access date.

## Open decisions

No model or provider decision remains open. The hosting decisions (O-2, O-3, O-5) were re-taken on 2026-10-07 — see the newest entry — and supersede the 2026-10-06 VM entry below, which is kept as the record of why the VM was chosen and why it was then dropped. What is still open lives in PRD section 14 — the supervisors' metacognitive rubric, the few-shot calibration examples for Bloom levels with no real data, institutional ethics clearance, the validation-subset size, the SUS instrument, and the feedback-text format.

## 2026-10-07 — Architecture reversed: no virtual machine (decided by Atthar)

**Decision.** Deploy on managed services only: the FastAPI + LangGraph API on **Google Cloud Run** (`asia-southeast1`), the database on **Neon PostgreSQL** (Singapore), the frontend on **Vercel Hobby** (Cloudflare Pages as the drop-in alternative), and LLM inference through **Cloudflare Workers AI** (`@cf/google/gemma-4-26b-a4b-it`, per O-1). No VM, no SSH, no OS patching, no reverse proxy, no firewall rules. This supersedes O-2 (Oracle Always Free ARM VM), O-3 (Postgres self-hosted on that VM) and O-5 (frontend served from it).

**Why the reversal (Atthar's reason).** A VM carries ongoing administration — SSH, OS updates, firewall, TLS renewal, monitoring — that is disproportionate for a thesis prototype whose subject is the multi-agent pipeline, not server operations. Explicit instruction: do not reintroduce a VM without a concrete technical blocker.

**Why the VM is not technically required** (verified 2026-10-07; evidence in `docs/phase-2/arch-*.md`):

1. **The reason the VM was chosen disappeared.** It was chosen on 2026-10-06 because the backend loaded an IndoBERT checkpoint and needed ≈1.3–2.0 GB resident, and because a batch run needed a process that would not be recycled. O-4 removed the model on the same day; the backend now holds no weights, no torch and no GPU requirement.
2. **LangGraph in library mode needs no long-lived server.** Its own docs require long-lived API + queue-worker containers only for the managed Agent Server; the checkpointed library path runs inside any process and resumes from a `thread_id`. Their serverless warning is scoped to the Agent Server binary, not to the library.
3. **It writes nothing to disk.** Checked directly: no temp files, no subprocesses, no in-process background tasks in `backend/app`. Uploads are parsed in memory.
4. **The batch shape fits a request.** Cloud Run allows a request up to 60 minutes, and a batch is decomposed so each submission is an independently retried invocation, with LangGraph state checkpointed in Postgres — which is the resumability the PRD already required, without a worker host or a queue service.

**What the VM bought, and why it is not needed.** Control, no cold start, and a single vendor. Control is not a requirement — nothing in the PRD needs a fixed outbound IP, a persistent disk or a cron daemon. A cold start of a few seconds is invisible for a lecturer-initiated batch. Vendor count rises from one to three, which is the tradeoff Atthar accepted in exchange for near-zero operational work.

**Constraints accepted with this architecture:**

- Neon suspends compute after 5 minutes idle and wakes automatically on the next query — no manual unpause before a demonstration, unlike the alternative that pauses for a week and needs an operator.
- Neon's pooler runs PgBouncer in **transaction mode**, so server-side prepared statements had to be disabled: `prepare_threshold=None` on the connection pool (`backend/app/db.py`). Tenant context already used `SET LOCAL` (never plain `SET`), which is what makes pooled connections safe for the row-level-security design.
- The compute host and the database host now process student documents during extraction and redaction, before anything is sent to an LLM. Both were checked against the fixed rule that no provider may train on content: Cloud Run and Neon both pass (`docs/phase-2/arch-privacy-topology.md`).
- **Documents are never persisted.** Migration `0002_no_raw_document_storage.sql` drops `file_ref` and `raw_text`; only the redacted segments survive, because scores and evidence offsets point at them. No object storage exists in this architecture.
- Vercel Hobby is excluded from Vercel's DPA and its terms permit training on free-tier content — acceptable only because the frontend never receives student text (the browser calls the API directly). If the clause or the data stance becomes a problem, Cloudflare Pages is the drop-in replacement.

**Residual risks, recorded rather than hidden:** (a) Vercel Hobby's "non-commercial personal use only" clause; (b) `StudentIdentity.real_identifier` still lives in the managed database — the privacy review recommends keeping the identity mapping outside any managed database, which is a change to FR-04 and needs Atthar's decision; (c) the Cloudflare Workers AI key is a production secret and must live in Secret Manager.

**Local development is unchanged:** uv + npm + Homebrew PostgreSQL, started by `scripts/dev.sh`. The development machine still has no container runtime; Cloud Build builds the production image in the cloud.

## 2026-10-07 — Phase 2 start: environment, versions and the local stack

### Decided

- **No containers on the development machine** (Atthar). Local development is uv + npm + Homebrew PostgreSQL, started by `scripts/dev.sh`, with no Compose file. [Partially superseded 2026-10-07: production now runs a container image, but Cloud Build builds it in the cloud, so the development machine still needs no container runtime.] PRD §8, §13 updated accordingly.
- **Pins verified 2026-10-07** (PyPI/npm/registry metadata and project release schedules; full table with sources in `docs/phase-2/phase2-version-pins.md`): Python **3.13** (LangGraph 1.2.14 declares 3.10–3.13 only, so 3.14 would put the orchestration library outside its declared support), Node **24 LTS**, Next.js **16.3.8**, React 19.2.8, Tailwind **4.3.3**, shadcn CLI **4.21.2**, FastAPI **0.142.2**, Uvicorn 0.54.0, Pydantic **2.13.5**, psycopg **3.3.6** `[binary]`, PostgreSQL **18.6**, uv **0.12.23**.
- **Boring-pin rule:** releases published hours before retrieval are skipped in favour of the previous patch (Next 16.4.0 → 16.3.8; shadcn 4.21.3 → 4.21.2), while routine patch bumps are taken (LangGraph 1.2.14, psycopg 3.3.6). Rationale: a regression in the toolchain costs thesis days; one patch of soak costs nothing.
- **TypeScript stays 5.x** (create-next-app resolved `^5`). TypeScript 7 is the native Go compiler rewrite and does not expose the JS compiler API, which non-Next tooling still consumes.
- **Region: Singapore** for everything that offers a choice. [Superseded 2026-10-07 for the Oracle reasoning: the tenancy's permanent home region no longer applies. Cloud Run runs in `asia-southeast1` and Neon is provisioned in a Singapore region.]
- **Hostname:** [superseded 2026-10-07 — Cloud Run provides an HTTPS `*.run.app` URL with a managed certificate, so no DuckDNS name and no reverse proxy are needed.]
- **Dependencies are installed when the phase that uses them starts**: LangGraph and psycopg's checkpointer are *pinned now* but not installed until phase 4, so the phase-2 lockfile stays small.

### Schema and auth decisions (implemented)

- **Two database roles.** `thesis_migrator` owns the schema; `thesis_app` is what the API connects as. A table owner bypasses RLS unless `FORCE` is set (set), and a superuser bypasses it regardless — hence a plain non-superuser runtime role.
- **One uniform tenant policy.** Every tenant table carries `owner_id` and one policy compares it with `app.current_user_id()`, set per transaction by `SET LOCAL`. Denormalising `owner_id` onto leaf tables was chosen over multi-level join policies: uniform, auditable, and no recursive policy evaluation.
- **`users` and `sessions` are deliberately not row-level-secured.** Resolving a session token to a user happens before any tenant context exists; both tables are reachable only through the auth code path. Every other table is covered.
- **Row factories are set per cursor, never on the connection.** Pooled connections are shared, and mutating `conn.row_factory` leaked a dict factory into a later request — caught by the RLS test, not by review.
- **Session and CSRF cookies**: session is httpOnly, CSRF is readable and echoed in `X-CSRF-Token` (double submit), both SameSite=Lax, `Secure` off locally and on in production, no `Domain` unless set.
- **Login throttling is in-process** (5 attempts / 15 min per IP+email). One process, one host: a Postgres-backed limiter is the upgrade path if the app ever runs multiple workers.
- **The frontend fetches in the browser, never in a server component**, so no hosting provider processes student text (keeps O-5 and O-7 consistent). The API error strings are mapped to Indonesian in the client; message codes arrive with the language toggle (FR-18).

### Verified on 2026-10-07 (local)

- PostgreSQL 18.6 running locally; `scripts/bootstrap_db.sh` creates roles and both databases; `0001_init.sql` applies.
- `ruff check` clean, `mypy app` clean, **10/10 backend tests pass**, including DB-enforced tenant isolation (a lecturer cannot read or write another's rows) and no-context-means-no-rows.
- Frontend `eslint`, `tsc --noEmit` and `next build` clean.
- Real browser walkthrough: signup → dashboard (name shown), logout → login → dashboard, wrong password → inline Indonesian error, session cookie httpOnly, CSRF cookie JS-readable.

### Note on phase-1 access dates

Phase-1 pages were fetched late in the evening of 2026-10-06 local (UTC+7); a few provider pages carry their own `last_updated` stamp of 2026-10-07 because the fetch crossed local midnight. Phase-1 evidence files are dated 2026-10-06; phase-2 research is dated 2026-10-07.

## 2026-10-06 — Phase 1 gate, part 2: hosting, frontend and the privacy rules (decided by Atthar)

### O-2 resolved — backend host: Oracle Cloud Always Free ARM VM

- **Decision:** 2 OCPU / 12 GB RAM / 200 GB block volume, always-on, Singapore region; systemd services; Caddy reverse proxy for TLS; Docker optional, not required.
- **Options considered:** Render free, Koyeb free, Railway free (all 512 MB class), Google Cloud Run, Hugging Face Spaces, Oracle Always Free.
- **Why:** no cold start, no invocation or credit cap, no egress bill, and no third party inside the student-data path. The 512 MB class became technically possible again after O-4 removed the model weights, but adds 0.1 CPU and idle spin-downs for no benefit once a VM is in the design. Limits verified 2026-10-06: `docs/phase-1/phase1-hosting-free-tiers.md`.
- **Risks accepted and to manage:** OCI may reclaim an A1 instance when CPU, network and memory all stay below the 20th percentile over a 7-day window — the workload must keep the instance visibly active; OS patching, database backups (`pg_dump`) and certificate renewal are ours; signup requires a card for identity verification (no charge unless upgraded).

### O-3 resolved — PostgreSQL self-hosted on the same VM (agent's choice, per Atthar's instruction)

- **Decision:** PostgreSQL on the Oracle VM, auth inside the FastAPI app, submission files on the VM block volume. Documented fallback: Supabase (Postgres + Auth + Storage).
- **Options considered:** Supabase free, Neon free, Oracle Autonomous DB (the three on the open list), plus self-hosting on the VM.
- **Why:** (1) Oracle Autonomous DB cannot back the LangGraph checkpointer — LangGraph ships savers for Postgres and SQLite only (verified 2026-10-06), so the Oracle option is ruled out technically, not by preference; (2) `StudentIdentity.real_identifier` is the highest-harm table in the system and must not sit in a third-party free database; (3) both managed free tiers add a demo-day failure mode (Supabase pauses after 7 days of low activity and needs a manual unpause; Neon scales to zero after 5 minutes) and neither covers auth and file storage without a second service; (4) the VM already exists under O-2, so this removes dependencies rather than adding them.
- **Cost accepted:** auth is ours to get right — argon2id hashing, httpOnly/Secure/SameSite cookies, CSRF protection on state-changing requests, login rate limiting, and row-level security enforced in Postgres, not only in the UI. If that proves too risky in phase 2, Supabase is the fallback with the same SQL schema.

### O-5 resolved — frontend served from the same Oracle VM (agent's choice, per Atthar's instruction)

- **Decision:** Next.js `output: 'standalone'` behind Caddy on the same VM as the backend. Managed fallback if that proves heavy: Azure Static Web Apps Free.
- **Research:** 12 candidates against SSR support, limits, idle behaviour, TLS, free-tier clauses, privacy and logs, every row sourced and dated → `docs/phase-1/phase1-frontend-hosting.md`.
- **Why not a provider:** Vercel Hobby is the only free tier whose written terms are a genuine risk — "Hobby teams are restricted to non-commercial personal use only", and its definition of commercial reaches "a paid employee or consultant writing the code". Cloudflare Workers Free caps CPU at 10 ms per invocation while Cloudflare's own docs say SSR "typically use[s] 10-20 ms" (Error 1102); Netlify Free is a 300-credit hard cap (~15 GB bandwidth) and may delete a project "without notice"; Render Free is 512 MB / 0.1 CPU with a 15-minute spin-down; Deno Deploy shuts idle apps down after ~20–30 seconds; Firebase Spark cannot serve SSR at all; GitHub Pages is static-only and bans SaaS use. The VM has no clause, no cold start and no cap.
- **Why it also satisfies O-7:** with the frontend on the same host, server-side rendering reads student text over localhost, so no frontend provider ever processes it. On any managed host that would have required client-side fetching as a workaround.

### O-6 resolved — no provider that trains on prompts

- **Decision:** a route whose free tier may train on or human-review prompt content may never be configured. The chosen provider satisfies this: Cloudflare states it "does not use your Customer Content to (1) train any AI models made available on Workers AI or (2) improve any Cloudflare or third-party services".
- **Consequence:** OpenRouter's free endpoints, the Google AI Studio free tier, Mistral Free mode and the BytePlus/Volcano reward programs are permanently excluded, whatever their capability. Any future swap re-verifies the stance from the provider's own page and records the source and date here.
- **Also accepted:** the chosen model is on Cloudflare's free list today, but Cloudflare publishes no deprecation policy — so the run records its model version, and a withdrawn model flags the run rather than silently re-pointing it (PRD §11).

### O-7 resolved — no identifying data leaves; minimum necessary segment only

- **Decision:** send only the text segment the calling agent needs, with identifiers removed. A provider never receives data that can identify a student. Still the supervisors' call: institutional ethics clearance (PRD §14).
- **Design consequences, now in PRD §5 (FR-04), §6 and §11:**
  1. **Minimisation, not relabelling, on the egress path.** An identifier found inside the analysis text is deleted, not replaced with a stable per-student code, so a provider cannot link two submissions from the same student. Internal storage keeps the FR-04 mapping for review and linkage; that mapping never leaves the VM.
  2. **No submission reference in the payload.** Correlation lives in AgentTrace locally.
  3. **Defence in depth.** Ingest filters first; the provider client — the single egress point — re-checks each payload and blocks the call instead of sending a detected identifier, flagging the submission for review.
  4. **Files and images are never sent.** Screenshots are extracted to text locally first.
  5. **Never sent:** the submission file, filename, document metadata, images, the AI-output segment to an agent that does not need it, the pseudonymisation mapping, or any identifier.
- **Residual risk, stated rather than hidden:** text that is not an identifier can still be quasi-identifying (a distinctive anecdote, a rare combination of course and cohort). Minimisation reduces this; it does not eliminate it, which is why the ethics clearance question stays open with the supervisors.

## 2026-10-06 — Phase 1 gate: O-4 reversed, O-1 resolved (decided by Atthar)

### O-4 reversed — IndoBERT fine-tuning dropped

- **Options considered:** (a) label archived submissions with Bloom levels, fine-tune an IndoBERT base, evaluate, then load the checkpoint into the backend (PRD §7a); (b) stub the cognitive agent with the keyword baseline (Baseline 1 in the SLR metric sheet) and swap in the real classifier later.
- **Decision: neither.** The cognitive dimension is served by an LLM cognitive agent with few-shot prompting — the same approach as the metacognitive agent — as a separate agent, not merged into one call.
- **Why (Atthar's reason):** only tens of archived submissions exist, and the higher-order Bloom levels likely have zero or near-zero examples; a classifier cannot predict a class it never saw in training. This is a data-size problem, not something more tuning fixes.
- **Supported by the phase-1 evidence:** no provenance-clear fine-tuned Indonesian Bloom classifier exists publicly (5 community checkpoints, reported accuracy 0.49–0.58, most with no model card, no license and no documented training data); the strongest published result (Baharuddin & Naufal, JISEBI 9(2):253-263, 2023, 97%) released its dataset but not its weights; and no public dataset of labelled student analysis text with Bloom levels was found in any language, not only Indonesian. See `docs/phase-1/phase1-indobert-checkpoints.md`.
- **Consequence:** no model weights and no inference framework in the backend; the RAM floor drops (see the updated PRD §8 row). PRD §2, §5 (FR-07/FR-14/FR-15), §6, §7, §7a (superseded, kept as the record), §8, §11, §12, §13, §14 updated the same day. The old IndoBERT labelling question in §14 is replaced by the few-shot calibration question (below), and the token-attribution question now applies to LLM-produced cognitive scores.

### O-1 resolved — one model, one provider, per role

| Role | Model | Decided by |
| --- | --- | --- |
| Orchestrator | No LLM — LangGraph routing is rule-based | agent recommendation, accepted by Atthar |
| Cognitive agent | Cloudflare Workers AI `@cf/google/gemma-4-26b-a4b-it` | agent recommendation, accepted by Atthar |
| Metacognitive agent | same model | same |
| Synthesis agent | same model | same |

- **Why this model:** best Bahasa Indonesia evidence among free open-weight routes (SEA-HELM, Sep 2026 — Gemma 4 31B **79.75**, Qwen 3.6 **77.96**, SEA-LION v4.5 27B **76.51**, gpt-oss-120b **72.28**); 256k context; native function calling; the largest free token budget of the candidates (~1.10M input tokens/day inside Cloudflare's 10,000 Neurons/day), which is what has to absorb the new 3–5 run-to-run variance requirement; and Cloudflare's published position that it does not use Customer Content to train AI models or to improve Cloudflare or third-party services. One provider means one data-use policy for all pseudonymised student text.
- **Cognitive agent defaults to the same model, per instruction:** nothing in the criteria table justifies a second provider. The runner-up, Groq `openai/gpt-oss-120b`, wins on structured output (constrained decoding — "Never errors or produces invalid JSON") but loses on Bahasa Indonesia evidence (72.28 vs 79.75) and on free quota (200K tokens/day cannot absorb 3–5 cognitive runs × ~30 submissions plus the other agents), and Groq's own two live pages contradict each other on its free limits. Recorded as the alternative; not configured.
- **Accepted residual risk:** Cloudflare's JSON Mode is hint-level — "Workers AI can't guarantee that the model responds according to the requested JSON Schema". Mitigated by schema validation, retry, and the existing "needs review" flag (PRD §6); to be measured when phase 4 runs. A single-model design also means one outage hits every dimension — the config-driven client (PRD §8) is what makes a swap a config change.
- **Sources:** `docs/phase-1/phase1-providers-primary.md`, `phase1-aggregators-regional.md`, `phase1-indo-llm-capability.md` (all fetched 2026-10-06).
- **New open question recorded (PRD §14):** who writes the few-shot example for a Bloom level with zero real examples, and how that synthetic example is validated so it does not bias the agent toward one phrasing. Also recorded: the multi-agent justification must now argue consistency and auditability, not raw accuracy (D1/D2/J3).

## Phase 1 — Research and decisions (2026-10-06)

- **2026-10-06 · Interim metacognitive rubric fixed to G1's four SRL codes (elaborasi, organisasi, orientasi, evaluasi), stored as data (RubricVersion), flagged interim pending the supervisors' guideline · no alternative adopted; supervisors' rubric not yet received · decided by PRD §13 working rule (Atthar previously).**
- **2026-10-06 · No LLM, no hosting provider, no IndoBERT checkpoint chosen by the agent in phase 1 · options only · reserved for Atthar. (Partly superseded the same day: O-1 and O-4 were then decided by Atthar — see the gate entry above. O-2/O-3/O-5/O-6/O-7 remain open.)** PRD §7/§8/§7a.
- **2026-10-06 · All phase-1 provider limits, licences and models treated as facts only when read from a primary page on 2026-10-06; claims that could not be verified on a live page are recorded as `[UNVERIFIED]` with the reason · decided by agent, per PRD §13 ("verify … record the source and date").** Evidence archived in `docs/phase-1/` (16 files).
- **2026-10-06 · Local inference stays ruled out (PRD §7); no exception taken for Hugging Face Spaces self-hosted inference.**
- **2026-10-06 · Phase-1 submission corpus = the 4 AI-output submissions in the repo root (`Tugas 1–4 … .pdf`, MRTI semester 2). 5 further own submissions (Tugas 5–8, Tugas Akhir) contain no AI output at all and were read as structure evidence only. Other students' variants do not exist locally yet · consequence: FR-05 design is deferred until real variants exist · stated by Atthar, recorded by agent.**
- **2026-10-06 · AI evidence files written to `docs/phase-1/` (research only, no application code) · decided by agent.**

## Findings that constrain later phases (not choices)

- Groq no longer serves Llama on the free tier (Enterprise/"ContactSales"; deprecation page records Llama 3.1 8B + 3.3 70B shutdown 2026-08-16). GitHub Models retired entirely 2026-07-30. Together AI free Llama endpoints removed 2025-11-13 / 2026-03-06. → Any thesis text naming "Llama 3.1 via Ollama" (PRD §7) is obsolete on both counts (local inference ruled out; free hosted Llama gone at those providers).
- Hugging Face free accounts can no longer create Gradio or Docker Spaces (HTTP 402; PRO $9/month required) → the PRD §8 "Hugging Face Spaces free" backend option is dead as written.
- Render free = 512 MB RAM / 0.1 CPU. **Updated 2026-10-06 after O-4:** with no model weights in the backend (no torch, no transformers), the resident floor drops from ≈1.3–2.0 GB to an estimated ≈250–400 MB, so the 512 MB-class hosts (Render, Koyeb, Railway) are no longer ruled out on RAM — the remaining costs are 0.1 CPU and idle spin-downs, and the estimate must be confirmed by measurement in phase 2. Docker was never the blocker on any host: none requires it for a native Python service.
- No fine-tuned IndoBERT Bloom classifier with clean provenance exists publicly (5 community checkpoints, 0.49–0.58 accuracy, mostly no card/license/dataset), and no public dataset of labelled student-analysis Bloom data exists in any language. **Superseded as a plan (O-4, 2026-10-06):** the labelling pass is not needed because there is no fine-tuning — but the same constraint carries over to the cognitive agent's few-shot examples, which Atthar must author or validate rather than the agent inventing them (PRD §14).
- Free-tier data policy is the binding constraint, not capability: the strongest Indonesian numbers today belong to general models (Gemma 4 31B 79.75, Qwen 3.6 77.96 on SEA-HELM Sep 2026), while several free routes (Gemini free tier, OpenRouter free endpoints, Mistral free mode, Volcano/BytePlus rewards) train on or human-review prompt content.

## Verification log

| Date | Verified | Source |
| --- | --- | --- |
| 2026-10-06 | Free-tier limits, licences, model IDs and data-use terms for 23 providers + 43 models | see `docs/phase-1/*.md`, every claim URL-cited |
| 2026-10-06 | Free-tier hosting limits: Vercel, Render, HF Spaces, Koyeb, Fly.io, Railway, PythonAnywhere, Oracle, Cloud Run, Azure, Supabase, Neon | `docs/phase-1/phase1-hosting-free-tiers.md` |
| 2026-10-06 | Frontend hosting for Next.js App Router on 12 free candidates (limits, idle behaviour, free-tier clauses, privacy, logs) | `docs/phase-1/phase1-frontend-hosting.md` |
| 2026-10-06 | LangGraph checkpoint savers: Postgres and SQLite only — Oracle Autonomous DB cannot back the checkpointer | [docs.langchain.com — checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers) |
| 2026-10-06 | Vercel Hobby fair-use clause: "non-commercial personal use only", including "a paid employee or consultant writing the code" | [vercel.com/docs/limits/fair-use-guidelines](https://vercel.com/docs/limits/fair-use-guidelines) |
