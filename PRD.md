# PRD — Multi-Agent LLM Evaluation System for AI-Permitted Assignments

Oct 6, 2026 · @Atthar

## 1. Overview

This web application is the design artefact of Atthar's ITB master's thesis: a multi-agent LLM system that evaluates the cognitive and metacognitive depth of students' analyses of AI output in AI-permitted assignments. It lets a lecturer upload submissions, run the agent pipeline, review evidence-backed scores, and correct them.

The thesis follows Design Science Research Methodology (DSRM), so the app has two jobs: be usable by lecturers (demonstration) and produce traceable data for evaluation against expert raters.

Problem. When students may use AI, the final answer no longer shows how deeply the student thought. Lecturers need to see whether the student critically analysed, verified, and reflected on AI output, and grading that by hand at class scale is slow and inconsistent.

Thesis title: *Pengembangan Sistem Multi-Agent LLM untuk Evaluasi Kedalaman Kognitif dan Metakognitif Mahasiswa pada AI-Permitted Assignment*. Supervisors: Prof. Dr. Ir. Jaka Sembiring, M.Eng. and Dr. Fetty Fitriyanti Lubis, S.T., M.T.

This PRD is written for a coding agent. Where it says "decision reserved for Atthar", the agent must stop, report options, and wait.

## 2. Goals, non-goals, success criteria

The MVP succeeds when a lecturer with no technical background can evaluate a full class batch end-to-end without help, and every score in the result can be traced back to quoted evidence and the agent that produced it.

Goals:

- Evaluate each submission on two dimensions only: cognitive (Bloom's Taxonomy level) and metacognitive (self-monitoring and reflection indicators).
- Show every score with its evidence: the quoted passage, the agent, the model, and the rationale.
- Let the lecturer accept, override, or comment on any score, and keep both the system score and the human score.
- Export results in a form usable for the thesis evaluation (Quadratic Weighted Kappa, Cohen's Kappa, Spearman correlation are computed outside the app).
- Run at zero recurring cost on free tiers.

Non-goals for the MVP:

- Affective dimension and learning-outcome scoring (dropped from thesis scope).
- Auto-assigning final grades or pushing grades to an LMS.
- Training or fine-tuning any model inside the app. The app loads no weights and trains nothing; every model is called over a hosted API.
- Student-facing features. Students never log in.
- Plagiarism or AI-text detection.

Success criteria (to be confirmed with the supervisors):

- A lecturer completes upload → run → review → export for one batch in a single session, without documentation.
- 100% of displayed scores link to at least one evidence quote from the submission.
- The pipeline is reproducible: same input, same config, same model version → same stored output, or the variance is logged.
- Usability is measured with a standard instrument during DSRM demonstration. Which instrument (e.g. SUS) is an open question.

## 3. Users and roles

The lecturer is the only end-user role. The app is multi-tenant: any lecturer who wants to use it creates an account and works with their own assignments, independent of other lecturers. There is no built-in comparison between lecturers inside the app. The two-lecturer agreement check needed for thesis validation is a separate, manual process run outside the app (see section 12).

| Role | Who | What they do | Technical comfort |
| --- | --- | --- | --- |
| Lecturer | Any course lecturer who creates an account | Creates assignments, uploads submissions, runs evaluation, reviews and overrides system scores, exports results. Sees only their own assignments | Low to medium. Uses LMS and spreadsheets, not developer tools |
| Admin / researcher | Atthar | Manages users, rubric and prompt versions, model config, views run logs, exports research datasets | High |

UI language defaults to Bahasa Indonesia, with English as a toggle. Submissions are mostly in Bahasa Indonesia, possibly mixed with English technical terms.

## 4. Core user flows

The main flow is four screens long: create assignment, upload, wait, review. Anything else is secondary.

Lecturer: evaluate a batch

1. Log in and land on the dashboard listing their own assignments.
2. Create an assignment: title, course, the assignment prompt given to students, and rubric (pre-filled default rubric; editable).
3. Upload submissions: drag-and-drop multiple PDF/DOCX files, or a ZIP. The app extracts text and shows a preview list with detected student identifiers.
4. Confirm and click one primary button: "Evaluate". A progress view shows per-submission status (queued, running, done, failed) and keeps working if the lecturer closes the tab.
5. Review the results table: one row per student, cognitive level, metacognitive score, a confidence flag, review status.
6. Open one submission: the student text on the left with highlighted evidence, scores, the AI's explanation, and generated feedback text on the right. Accept, override (with a short reason), or comment.
7. Export the batch to XLSX/CSV.

Admin: research operations

1. Manage users; version the rubric, prompts, and model configuration; every run records which versions it used.
2. Run the same batch in single-agent baseline mode or multi-agent mode (see section 12).
3. Export a research dataset for the manual two-lecturer agreement study used in thesis validation (section 12).

## 5. Functional requirements

P0 items make up the MVP the thesis demonstration needs; P1 items support validation; P2 items are deferred.

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-01 | Email/password login with two roles: lecturer and admin. Lecturers sign up freely; the app is multi-tenant, one lecturer's assignments are never visible to another | P0 |
| FR-02 | Assignment CRUD: title, course, assignment prompt, rubric reference | P0 |
| FR-03 | Batch upload of PDF, DOCX, TXT and ZIP; text extraction; per-file error reporting without failing the batch | P0 |
| FR-04 | Data minimisation and pseudonymisation on ingest: student identifiers are removed from the text rather than merely relabelled (name, NIM, email, phone, and anything found in headers, footers, filenames, document metadata, tables or the text itself); the mapping is held in a separate owner-only table; and the exact payload sent to any provider is re-checked at the provider client, which blocks the call and flags the submission for review if an identifier is present | P0 |
| FR-05 | Segment each submission into AI output vs student analysis. Auto-segment, then let the lecturer correct the boundary | P0 |
| FR-06 | Asynchronous evaluation jobs with per-submission status, retry on failure, and resumable runs | P0 |
| FR-07 | Cognitive score: Bloom level per student analysis, from the cognitive agent (LLM with mandatory few-shot calibration, section 6), with the evidence span and a rationale | P0 |
| FR-08 | Metacognitive score: per-indicator presence and strength, each with quoted evidence and rationale | P0 |
| FR-09 | Results table with sort, filter by level, and a "needs review" flag for low-confidence or agent-disagreement cases | P0 |
| FR-10 | Submission detail view: highlighted evidence linked to each score | P0 |
| FR-11 | Lecturer override per score with required short reason; system score is kept, never overwritten | P0 |
| FR-12 | Export results to XLSX and CSV | P0 |
| FR-13 | Every run stores rubric version, prompt versions, model names and versions, parameters, and timestamps | P0 |
| FR-14 | Explainable AI: each score is shown with a plain-language explanation of why the model reached it. Every dimension carries the evidence span plus a short rationale from the agent that produced it (cognitive, metacognitive, or synthesis); a token-attribution method such as attention weights or integrated gradients may still be added later (open question, section 14) | P0 |
| FR-15 | Single-agent baseline mode on the same batch for comparison: one LLM call over the full rubric covering both dimensions, same model, same rubric version | P1 |
| FR-16 | Research export: system scores (per mode) and lecturer overrides per submission, in a format that can be joined offline with the separately collected two-lecturer rating sheet, plus run metadata | P1 |
| FR-17 | Rubric editor with versioning | P1 |
| FR-18 | Bahasa Indonesia / English UI toggle | P1 |
| FR-19 | Per-student feedback text, generated by the synthesis agent, editable by the lecturer before export | P0 |
| FR-20 | LMS integration | P2 |

FR-05 is a hard dependency. If the AI output and the student's own analysis cannot be separated reliably, both scores are measured on the wrong text. The coding agent must inspect the archived submissions' structure before building the segmenter.

## 6. Multi-agent architecture

A LangGraph state graph runs per submission: preprocess, then a cognitive and a metacognitive agent in parallel, then synthesis, then a rule-based evidence check before anything is saved. This split is a starting proposal and must match the architecture described in Bab III.

&#91;embedded content: system architecture · 4 pipeline steps\]

The cognitive agent and the metacognitive agent are both LLM-based now, and stay as two separate agents rather than one merged call. The split preserves the per-dimension specialisation claim (Gap 4) and keeps each dimension's prompt, evidence and rationale independently auditable in AgentTrace. The synthesis agent is LLM-based too. Orchestration itself stays rule-based: routing in the state graph is a rule, not a model call.

This reopens the tautology risk that the original IndoBERT design existed to avoid: an LLM is now judging work that was partly produced by analysing another LLM's output. The mitigation is not optional. It is mandatory few-shot calibration of every LLM agent against the supervisor-approved rubric, with the calibration examples stored as versioned PromptVersion rows and cited in the thesis, so the round trip (student → AI output → student's analysis → this system's judgement) is interrogated rather than assumed away.

Graph rules:

- Shared state is a typed Pydantic model: submission text segments, rubric version, each agent's output, flags, errors.
- Each agent returns structured JSON validated against its schema; invalid output is retried, then marked failed.
- If a quote fails the evidence check, synthesis retries once with the failure reason; if it fails again, the score is saved with a "needs review" flag.
- State is checkpointed in Postgres, so an interrupted run resumes at the last completed step.
- Only sanitised text ever leaves the machine: preprocess removes identifiers before they are stored, and the single provider client re-checks each outgoing payload and refuses to send if it detects one, flagging the submission for review instead. Submission files, filenames, document metadata, images and the pseudonymisation mapping are never sent.
- In single-agent baseline mode (section 12), steps 2a to 3 are replaced by one LLM call over the full rubric; steps 1 and 4 stay the same.

## 7. LLM model selection (resolved 2026-10-06; full log in `DECISIONS.md`)

### Selection (2026-10-06)

| Role | Model | Why |
| --- | --- | --- |
| Orchestrator | No LLM — rule-based routing in LangGraph | Routing was never model-dependent; an LLM planner would spend free-tier quota on a step a rule already decides |
| Cognitive agent | Cloudflare Workers AI `@cf/google/gemma-4-26b-a4b-it` | Best current Bahasa Indonesia evidence among free open-weight routes (SEA-HELM, Sep 2026: Gemma 4 31B 79.75), 256k context, native function calling, largest free token budget (~1.1M input tokens/day inside 10,000 Neurons/day) |
| Metacognitive agent | same model | Same criteria, plus the daily quota must absorb the 3–5 run-to-run variance requirement (section 11) |
| Synthesis agent | same model | Same criteria; 256k context holds rubric + all agent outputs + generated feedback |

Alternative recorded but not configured: Groq `openai/gpt-oss-120b` (strict constrained-decoding JSON, "never produces invalid JSON"). Weighted lower on Bahasa Indonesia evidence (SEA-HELM 72.28 versus 79.75) and on free quota (200K tokens/day cannot absorb the 3–5 reproducibility runs), and its own two live pages contradict each other on free-tier limits.

One provider only, and its published data-use position is explicit: Cloudflare states it does not use Customer Content to train AI models or to improve Cloudflare or third-party services. Pseudonymised student text therefore reaches one third party with one data-use policy. Evidence, sources and access dates: `docs/phase-1/`.

Training ban as a configuration constraint (O-6, 2026-10-06): no route whose free tier may train on or human-review prompt content may be configured, now or in a later swap. That rules out OpenRouter's free endpoints, the Google AI Studio free tier, Mistral Free mode, and the BytePlus/Volcano reward programs, whatever their capability. Any provider change re-verifies the no-training stance from the provider's own page, records the source and date in `DECISIONS.md`, and re-checks structured output and context length against the new endpoint.

### How this was decided

The coding agent did not pick or hard-code any LLM. Its first task was a research report on free, open-weight models per agent role, evaluated against the criteria table below with a source and an access date per claim; Atthar chose from that report on 2026-10-06. Model names live only in config, never in code.

Local inference is ruled out: every LLM call goes to a free hosted provider. The thesis draft names Llama 3.1 via Ollama, which is obsolete on both counts — local inference is out, and the free hosts no longer serve Llama (Groq moved Llama 3.1/3.3 to Enterprise, Together AI removed its free Llama endpoints, GitHub Models was retired 2026-07-30). Bab III must be updated.

Scope of the research:

- Open-weight LLMs offered free by hosted inference providers, accessed by API. No local inference.
- The cognitive dimension was originally scoped to an IndoBERT classifier; that scope is superseded — no usable checkpoint and no labelled dataset exist (section 7a).
- Check current sources at the time of research (model cards, provider pricing pages, license texts). Do not rely on memory for versions, limits, or licenses; cite the page for every claim.

Evaluation criteria per candidate:

| Criterion | Why it matters here |
| --- | --- |
| License terms for research and deployment | The thesis artefact is published and demonstrated |
| Bahasa Indonesia capability, with evidence (benchmark or documented training data) | Submissions are in Indonesian |
| Reliable structured output (JSON schema) and tool calling | Agents exchange typed state through LangGraph |
| Context length | One submission plus rubric plus instructions must fit |
| Data use on the free tier: whether prompts are logged, retained, or used for training | Pseudonymised student text is sent to the provider |
| Free-tier limits (rate, daily quota) and model deprecation policy | Whether a full batch runs at zero cost, and whether the same model is still available at the defense |
| Determinism controls (temperature, seed) | Reproducibility of thesis results |

Deliverable, then stop:

1. A comparison table of candidates against the criteria above, with source links.
2. A short recommendation per agent role (orchestrator, cognitive agent, metacognitive agent, synthesis agent), with one alternative each.
3. An explicit privacy note per provider: its stated retention and training-use policy for free-tier requests, with the source link.
4. Done 2026-10-06; the report is archived in `docs/phase-1/`. Model names live only in config, never in code.

Because student text leaves the institution, providers whose free tier may train on submitted data are excluded unless Atthar decides otherwise. The thesis privacy argument shifts from local inference to pseudonymisation plus provider selection by data policy. Free hosted models can also be withdrawn; the report must say how each provider handles deprecation, since results need to be reproducible until the defense.

For now, build against a free open-source hosted LLM, chosen from the research report above. Atthar may later migrate to an internal ITB-hosted LLM, which is not accessible yet; the LLM provider interface (one config-driven client, section 8) exists specifically so that move needs no code change, only a config update and re-verification of structured-output and context-length behaviour against the new endpoint.

## 7a. IndoBERT: pretrained base vs. fine-tuned classifier — **SUPERSEDED 2026-10-06 (kept as the record of why IndoBERT was evaluated and ruled out)**

A fine-tuned IndoBERT is not a ready-made download. IndoBERT itself (e.g. indobenchmark/indobert-base-p1 or indolem/indobert-base-uncased on Hugging Face) is an open-weight, pretrained Indonesian language model, free to use. But it is pretrained for general language understanding, not for classifying Bloom's Taxonomy levels; out of the box it has no notion of "Remember" vs. "Analyze". Turning it into the cognitive classifier FR-07 needs means fine-tuning: attaching a classification head and training it on examples of student analysis text labelled with the correct Bloom level.

This is a separate ML pipeline, not something the web app produces:

1. Label a sample of the archived submissions with Bloom levels, by the same rubric the lecturer UI uses, so training labels and runtime labels agree.
2. Fine-tune the pretrained IndoBERT checkpoint on those labels (a standard Hugging Face Trainer workflow).
3. Evaluate the fine-tuned model's own accuracy and agreement before it is trusted as FR-07's classifier.
4. Export and load the resulting checkpoint into the backend; the backend only does inference, never training.

Labelling this sample is Atthar's work, not the coding agent's: the agent should not invent Bloom labels for real student text. That constraint still applies to the few-shot calibration examples the cognitive agent now needs. **Decision (2026-10-06): neither option. Fine-tuning is dropped — outcome below.**

### Outcome: why IndoBERT was ruled out (2026-10-06)

Atthar reversed the original plan. Both halves are data-size problems, not tuning problems:

1. **Not enough labelled examples.** Only on the order of tens of archived submissions exist, and the higher-order Bloom levels are likely to have zero or near-zero examples. A classifier cannot predict a class it never saw in training, so a Bloom head trained on this sample would fail the upper levels by construction. More epochs, augmentation, or a larger encoder do not produce an absent class.
2. **No ready-made substitute exists.** Phase 1 checked the Hugging Face Hub both for a fine-tuned Indonesian Bloom classifier and, separately, for any public dataset of labelled student answers in any language. Five community Indonesian Bloom checkpoints exist, none provenance-clear (reported accuracy 0.49–0.58; most carry no model card, no license and no documented training data). The strongest published result (Baharuddin & Naufal, JISEBI 9(2):253-263, 2023, 97% accuracy) released its dataset but not its weights. No public dataset of labelled student analysis text with Bloom levels was found anywhere, in Indonesian or otherwise. Sources: `docs/phase-1/phase1-indobert-checkpoints.md`.

**Consequence.** FR-07 is served by a cognitive agent (LLM, mandatory few-shot calibration) under the same rules as the metacognitive agent, per section 6. No model weights are loaded in the backend, so the backend carries no inference framework and no GPU requirement.

## 8. Tech stack and deployment

Stack: a Next.js frontend on Vercel, a Python FastAPI backend running LangGraph **on the owner's machine**, and managed Postgres on Neon. LangGraph is fixed by the thesis. Hosting was settled on 2026-10-14 (O-2/O-3/O-5 in `DECISIONS.md`): every provider that would host the API requires a credit card whose verification fails, so the API runs locally — natively or in Docker — and is exposed at a public HTTPS URL through a Cloudflare Quick Tunnel when it must be shown remotely. No virtual machine, no server administration, no card. The one hard rule this arrangement introduces: the API must connect as `thesis_app`, never as the Neon owner role, which carries `BYPASSRLS` and would silently disable every tenancy policy.

| Layer | Proposal | Reason |
| --- | --- | --- |
| Frontend | Next.js (App Router, TypeScript), Tailwind CSS, shadcn/ui | Fast to build a clean, accessible UI; Atthar already works in this stack |
| Frontend hosting | Vercel Hobby (git-push deploy, zero configuration) in front of the Cloud Run API; Cloudflare Pages is the drop-in alternative | Vercel needs no adapter or build changes. Caveat to own: Hobby is "non-commercial personal use only" and its definition reaches "a paid employee or consultant writing the code" — if that clause becomes a problem, Cloudflare Pages carries no such restriction. No student text reaches either host: the browser calls the API directly (section 11) |
| Backend API | FastAPI (Python) | Same language as LangGraph and the analysis scripts |
| Agent orchestration | LangGraph, with a Postgres checkpointer | Thesis decision: explicit state graph, resumable runs, inspectable state per step |
| Cognitive agent | Same hosted LLM as the other agents, few-shot calibrated (sections 6, 7, 7a) | One model, one provider, one data-use policy across all dimensions; no local weights, so nothing to load, quantise or keep resident |
| LLM access | One OpenAI-compatible client interface; provider and model set in config | Switch between hosted free providers without code changes |
| Database + auth | Neon PostgreSQL (Singapore) as the only managed service; auth implemented in the FastAPI app; **no file storage at all** (decision O-3, 2026-10-07) | Neon scales to zero in 5 minutes and wakes automatically on the next query, so no manual unpause before a demo; it documents a PgBouncer transaction-mode pooler, and the app connects through it with `prepare_threshold=None` so prepared statements do not break across pooled backends. Auth stays in-app so the identity mapping never sits in a third-party database. Uploaded documents are never stored: they are parsed in memory and discarded |
| Background jobs | Postgres-backed job table. A batch is decomposed so each submission is evaluated by its own backend invocation rather than one enormous request | Locally there is no request timeout to design around, but the decomposition still earns its keep: a crash, a closed laptop or a restart mid-batch must not lose the run. LangGraph state is checkpointed in Postgres, so a re-triggered submission resumes at its last completed step. No queue service, no worker process, no Redis |
| Backend hosting | The API runs **locally** on the owner's machine (`scripts/dev.sh`, or the same image in Docker), against Neon; a **Cloudflare Quick Tunnel** publishes it at a public HTTPS URL when a remote demonstration is needed (decision O-2, 2026-10-14) | Every managed host requires a card whose verification fails, so local is the only free option left. Costs, measured rather than assumed: the machine must be on; a Quick Tunnel URL changes per restart and Cloudflare documents them as development-only; and the tunnel makes the browser requests cross-site, which requires `COOKIE_SAMESITE=none` with `COOKIE_SECURE=true` — with `lax`, signup succeeds and the very next request is 401 (A/B verified on the live Vercel page) |
| Local development | Python venv from a lockfile (uv) for the backend, npm for the frontend, and PostgreSQL 18 installed natively (Homebrew on macOS — the same major as Neon); `scripts/dev.sh` starts all three. Docker is optional | The stack now runs where it is developed, so there is no cloud/development split to keep honest. The `backend/Dockerfile` is still the production artefact and is built by CI; `docker build backend/` gives image parity locally when it matters |

Requirements on the setup:

- One documented command starts the full stack locally (a script that starts PostgreSQL, the API and the web app). No container runtime is needed on the development machine; Render builds the production image from the repository.
- All secrets in environment variables; a `.env.example` documents every variable, and production secrets are stored in Render's environment-variable settings as secrets, never in the repository.
- CI on GitHub Actions: lint, type check, unit tests on push.
- Free-tier limits (RAM, sleep/cold start, storage, request quotas) must be checked on the providers' current pages and recorded in the repo README with the date checked. This PRD does not state them because they change. (Render, Neon and Vercel checked 2026-10-14; findings in `docs/phase-2/cardfree-paas.md` and `docs/phase-2/arch-data-layer.md`.)

A simpler alternative is a single Python app (FastAPI serving the frontend, or a Gradio/Streamlit UI). It deploys to one host but gives less control over a lecturer-friendly UI. Keep the two-tier proposal unless free backend hosting proves unworkable.

## 9. UI/UX and design system

The interface should feel like a plain, calm academic tool: one primary action per screen, ITB blue as the only brand colour, and no agent jargon shown to lecturers.

UX principles:

- One primary button per screen (Create, Upload, Evaluate, Export). Secondary actions are text links or a menu.
- Plain-language labels in Bahasa Indonesia: "Tingkat Kognitif", "Indikator Metakognitif", "Perlu Ditinjau". No terms like agent, node, token, or prompt in the lecturer UI; those live in the admin area.
- Every score is clickable and jumps to its highlighted evidence in the student text.
- Long work never blocks the screen. Evaluation runs in the background with visible progress and survives a closed tab.
- Destructive actions (delete assignment, re-run batch) need confirmation.
- Empty states explain the next step in one sentence.
- Desktop-first (lecturers review on laptops); usable on tablet; mobile shows read-only results.
- Accessibility: WCAG 2.1 AA contrast, keyboard navigation, visible focus states.

Screens: Login, Dashboard (assignment list), Assignment setup, Upload and preview, Run progress, Results table, Submission detail (split view), Export, Rater queue, Admin settings.

Visual design:

| Token | Value | Use |
| --- | --- | --- |
| `primary` | A deep institutional blue chosen for the project (no exact ITB hex required); suggested starting point \`#1E3A8A\` | Primary buttons, active nav, links, headers |
| `primary-foreground` | White | Text on primary |
| `background` | White / very light neutral gray | Page background |
| `surface` | Light tint of primary | Selected rows, info panels |
| `text` | Near-black neutral | Body text |
| Status colours | Green (done), amber (needs review), red (failed) | Status badges only, always paired with a text label |

Typography: one sans-serif family, base size 16 px, generous line height for reading student text. Layout: left sidebar navigation, max content width for reading panes. No ITB logo is used anywhere in the app; a plain text wordmark identifies the product.

## 10. Data model

System scores, lecturer overrides are stored as separate records against the same submission and dimension, never merged, so agreement can be computed later.

| Entity | Key fields | Notes |
| --- | --- | --- |
| User | id, email, name, role | Roles: lecturer, admin |
| Assignment | id, owner\_id, title, course, prompt\_text, rubric\_version\_id | One lecturer owns it |
| Submission | id, assignment\_id, pseudonym, ai\_output\_text, student\_analysis\_text, segmentation\_status | Pseudonym only; no real name here. **No uploaded file, no filename and no unredacted text is stored** — documents are parsed in memory, redacted, and discarded. Only the two redacted segments persist, because scores and evidence offsets point at them |
| StudentIdentity | submission\_id, real\_identifier | Separate table, row-level access for the owner only |
| RubricVersion | id, version, dimensions, levels, indicators, descriptors | Immutable once used in a run |
| PromptVersion | id, agent\_name, version, template | Immutable once used in a run |
| Run | id, assignment\_id, mode (single-agent / multi-agent), model\_config, rubric\_version\_id, prompt\_version\_ids, started\_at, finished\_at, status | Full config snapshot |
| AgentTrace | id, run\_id, submission\_id, agent\_name, input\_ref, output\_json, latency\_ms, error | One row per agent step, for debugging and the thesis |
| SystemScore | id, run\_id, submission\_id, dimension, indicator (nullable), level, confidence, rationale, explanation\_type | Output of the pipeline |
| Evidence | id, system\_score\_id, start\_offset, end\_offset, quote | Spans into student\_analysis\_text |
| LecturerReview | id, system\_score\_id, action (accept / override), new\_level, reason, reviewed\_at | System score kept unchanged |
| Feedback | id, submission\_id, generated\_text, edited\_text, edited\_by, exported\_at | Generated by the synthesis agent; lecturer may edit before export |
| Job | id, run\_id, submission\_id, status, attempts, last\_error | Postgres-backed queue |

The exact level scales for both dimensions come from the thesis rubric (Bab II/III) and are stored as data in RubricVersion, not hard-coded.

## 11. Non-functional requirements

Privacy and reproducibility outrank speed: this is a research artefact handling student work.

- Nothing about a submitted document is kept: no uploaded file, no filename, no document metadata and no unredacted text. The file is parsed in memory, identifiers are removed, and the original bytes are discarded when the request ends (architecture decision, 2026-10-07). Only the redacted segments that scores and their evidence point at are stored.
- Privacy and data minimisation: identifiers are removed on ingest (FR-04) and the mapping never leaves the database; data handling consistent with Indonesia's Personal Data Protection Law (UU PDP, UU No. 27 Tahun 2022). All LLM calls go to a hosted provider, so the app tells lecturers that pseudonymised text is processed by a third party, and only providers selected under section 7's data-use criterion are configured.
- What leaves, and what never does: only the text segment the calling agent needs — the student's analysis text for the cognitive and metacognitive agents, plus the AI-output segment for synthesis. Never sent: the submission file, its filename, document metadata, images, the pseudonymisation mapping, or any identifier. An identifier found inside the analysis text is deleted rather than replaced with a stable per-student code, so the provider cannot link two submissions from the same student, and no submission reference is included in the payload.
- No-training rule (O-6, 2026-10-06): no route whose free tier may train on or human-review prompt content may be configured, now or in a future swap. A provider change re-verifies that stance from the provider's own page and records the source and date in `DECISIONS.md` before it is configured.
- Enforcement: the provider client is the only egress point for submission text; it re-checks each payload and blocks the call instead of sending a detected identifier.
- Access control: lecturers see only their own assignments, enforced in the database (row-level security), not only in the UI.
- Reproducibility: temperature and seed set from config; every run snapshots model, prompt and rubric versions; re-running an old run uses its stored snapshot; if the hosted model is no longer available, the run is flagged rather than silently switched to another model. Because every dimension is now produced by a sampled LLM, no dimension is exempt from run-to-run variance: each dimension is run 3–5 times per submission and reported as mean ± SD alongside the single-agent baseline comparison, with the spread stored per run. Provider `seed` is best-effort on every free route evaluated, so reproducibility is documented by measurement, not assumed.
- Reliability: a failed submission never fails the batch; jobs retry with backoff; rate-limit errors from free providers are handled by queuing, not crashing.
- Performance: target batch duration is set after the model choice, based on measured throughput on the chosen host. The UI must stay responsive during runs.
- Cost: zero recurring cost. Any feature that requires a paid tier is flagged to Atthar before it is built.
- Observability: structured logs per agent step (AgentTrace); an admin page lists failed jobs with their error.
- Maintainability: typed interfaces between agents (Pydantic models), unit tests for each agent with fixture submissions, no model names or provider URLs in code.

## 12. Research instrumentation

The app itself is single-rater: each lecturer uses it independently. The thesis's own validation (two lecturers rating the same subset) is a separate, manual process run outside the app by Atthar as researcher, using the app's research export.

Single-agent baseline mode (FR-15). The supervisor asked for a clear justification of multi-agent over single-agent. The app should run one LLM call with the full rubric on the same batch, same model, same rubric version, and store it as a separate Run. This gives a like-for-like comparison inside the same artefact instead of an argument from literature alone. Since 2026-10-06 both modes run on the same LLM for every dimension, so the baseline needs no separate path for the cognitive dimension — and the multi-agent justification must rest on consistency, per-dimension auditability and error localisation rather than on raw accuracy, given that D1/D2/J3 suggest single-agent few-shot can match or beat multi-agent on accuracy alone.

Agreement data. The research export (FR-16) gives system level (per mode) and the owning lecturer's override per submission and dimension. Atthar joins this offline with the two-lecturer rating sheet collected manually (above). Statistics (Quadratic Weighted Kappa, Cohen's Kappa, Spearman correlation, Wilcoxon signed-rank) are computed offline in Python notebooks, not in the app, so the analysis stays transparent and citable.

Manual two-lecturer validation (outside the app). Atthar recruits two lecturers, gives them the same rubric, and collects their ratings on a shared subset through a separate form or spreadsheet, not through the app. Their agreement is computed with Krippendorff's alpha (target > 0.80, from the thesis SLR) or weighted kappa. Disagreements are resolved by discussion to consensus, forming the reference labels the system is compared against. Lecturer overrides recorded inside the app are reported separately and never used as reference labels, since they are made after seeing system output.

Traceability. AgentTrace rows let any thesis claim about agent behaviour be backed by a stored example.

Data constraint. Only archived submissions from a previous semester are available before the defense. The app must work fully on an imported archive; live classroom use is a later phase.

## 13. Milestones and rules for the coding agent

Build in six gated phases; each phase ends with a demo to Atthar and does not start the next until he approves.

1. Research and decisions. Model research report (section 7), free-tier check (section 8), inspection of the archived submissions' structure, and confirmation of whether a fine-tuned IndoBERT classifier already exists or must be trained (section 7a). Gate: Atthar picks models, hosting, and the IndoBERT path.
2. Skeleton. Repo, local environment (uv + npm + Homebrew PostgreSQL; Docker optional for image parity), auth with roles, database schema, CI, the database on Neon, and the frontend on Vercel. Gate: login works — locally, and through the Quick Tunnel when the app is shared with someone else.
3. Ingestion. Upload, text extraction, identifier detection and removal (headers, footers, filenames, document metadata, tables, in-text), segmentation with manual correction, and the provider-client egress check. Gate: all archived submissions import cleanly with no identifier left in the text that would be sent to a provider.
4. Agent pipeline. LangGraph graph, cognitive agent (LLM, few-shot calibrated), metacognitive agent, synthesis agent (rationale, explanation, feedback text), job queue, traces. Gate: one batch evaluates end-to-end with evidence and an explanation per score.
5. Lecturer UI. Results table, submission detail with evidence and plain-language explanation, feedback text editor, override, export. Gate: a walkthrough with one lecturer, no help given.
6. Research features. Single-agent baseline, research export. Gate: export loads into the analysis notebook.

Working rules:

- Ask before choosing anything this PRD marks as reserved: models, hosting provider, final rubric content, the few-shot calibration plan.
- The metacognitive indicator set is fixed for now to G1's four SRL codes (elaborasi, organisasi, orientasi, evaluasi); treat it as the working rubric, store it as data (RubricVersion), and flag it clearly as interim pending the supervisors' guideline. Never invent levels, indicators, or thresholds beyond this.
- Do not add features outside this PRD without asking.
- Keep a `DECISIONS.md` log: date, decision, options considered, who decided.
- Verify library versions and provider limits from official docs at the time of use; record the source and date.

## 14. Open questions

- [ ] Rubric and rater guideline from the supervisors, to replace the interim G1 (Fan et al., 2025) four-code SRL scheme used as a placeholder for the metacognitive dimension.
- [ ] Few-shot calibration for the cognitive agent: who writes the example for a Bloom level that has zero real examples in the archived data, and how is that synthetic example validated so it does not bias the agent toward one phrasing? (Replaces the IndoBERT labelling question; the approach is mandatory per section 6, so the examples gate phase 4.)
- [ ] Size of the two-lecturer validation subset and how disagreements are resolved (discussion to consensus, or a tie-break rule) — this governs the manual process in section 12, not the app itself.
- [ ] Multi-agent justification now that both modes use the same kind of model: the argument has to lean on consistency, per-dimension auditability and error localisation rather than raw accuracy, because D1/D2/J3 suggest single-agent few-shot can match or beat multi-agent on accuracy alone (section 12).
- [ ] Confirm SUS (or another named instrument) for the DSRM usability demonstration, and whether it uses the same two lecturers as the validation study.
- [ ] Institutional ethics clearance or student consent for sending the analysis text itself — identifiers removed and the minimum segment only — to a hosted LLM provider. This is a question for the supervisors, not for the app. The system-side rule is already fixed: O-6 (no provider that trains on or human-reviews prompts) and O-7 (no identifying data leaves; only the segment an agent needs; enforced at the provider client).
- [ ] What token-attribution method, if any, should back the explanation shown for a cognitive score beyond the evidence span (e.g. attention weights, integrated gradients, or SHAP, which Atthar already has experience with)? No source for this in the SLR; flagged as needing its own literature check. With an LLM cognitive agent the evidence span plus the agent's rationale is the explanation by default, since the hosted APIs expose no attention weights.
- [ ] Format and length for the generated per-student feedback text, and whether the lecturer can regenerate it.
