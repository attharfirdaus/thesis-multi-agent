# Phase-1 Evidence: AI Singapore SEA-LION + Sahabat-AI

Access date for every URL below: **2026-10-06** (all pages fetched live on that date).
Scope: evidence only, no recommendations. Anything not confirmed on a live page is marked **[UNVERIFIED]**.

Method notes / source quirks observed today:
- `docs.sea-lion.ai` is a GitBook site; each page also exists as `.md` (used here) and exposes `llms.txt`. Its built-in `ask=` query endpoint did **not** answer (returned the plain page / HTTP 500), so no docs-Q&A results are relied on.
- `playground.sea-lion.ai` is login-gated (Google OAuth); the free-API **model list is only visible per API key** via `GET /v1/models`, which requires auth. Unauthenticated call today returns 401: `{"error":{"message":"Authentication Error, No api key passed in.","type":"auth_error","param":"None","code":"401"}}` (https://api.sea-lion.ai/v1/models).
- `sahabat-ai.com` is a JavaScript-only Svelte SPA (plain fetch produced no text); content below was read by rendering it in Chromium. `chat.sahabat-ai.com` is a Flutter web app behind login/Firebase.
- `platform.publicai.co` docs are JS-rendered; pages below were read in Chromium (each page shows `Last modified on October 6, 2026`).
- `build.nvidia.com/models.md` (NVIDIA NIM catalog index) contains **no** SEA-LION, Sahabat-AI, or any AI Singapore entry today (grep over the full 205-line index: 0 hits).

---

# PROVIDER A — AI Singapore SEA-LION (`sea-lion.ai`)

Steward: AI Singapore (AISG), "a national research programme funded by the National Research Foundation, Singapore and hosted by the National University of Singapore" — verbatim from https://sea-lion.ai/terms-of-use/ (page states "Last updated on 19th November 2024"). Country of origin shown for the hosted SEA-LION models on the PublicAI gateway is **Singapore** (https://platform.publicai.co/models).

## (a) Model IDs available today

### Model families on Hugging Face `aisingapore` (87 models; org verified)
Source: https://sea-lion.ai/models (page modified 2026-09-21; table footer: "Updated as of 26 May 2026 – V4 Generation") and https://huggingface.co/aisingapore

| Family / version | Model IDs (HF `aisingapore/...`) | Params | Context |
|---|---|---|---|
| v4.8 MOE (Nemotron), released Sep 2026 | `Nemotron-SEA-LION-v4.8-120B-A12B`, `Nemotron-SEA-LION-v4.8-30B-A3B` (+ `-Base`, `-GGUF`, `-FP8`, `-NVFP4`) | 120B / 30B | 262K (models page); docs: "**Context Length:** 8K (Base model), 256K" |
| v4.5 (Gemma) | `Gemma-SEA-LION-v4.5-E2B-IT` | 2.3B eff (5.1B w/ embeddings) | 128k |
| v4.5 (Qwen) | `Qwen-SEA-LION-v4.5-27B-IT`, `Qwen-SEA-LION-v4.5-27B-IT-SpecDecoder` | 27B | 262k |
| v4 (Gemma) | `Gemma-SEA-LION-v4-27B-IT`, `-VL`, `Gemma-SEA-LION-v4-4B-VL` | 27B / 4B | 128k |
| v4 (Qwen) | `Qwen-SEA-LION-v4-32B-IT`, `Qwen-SEA-LION-v4-4B-VL`, `Qwen-SEA-LION-v4-8B-VL` | 32B / 4B / 8B | 128k (32B), 256k (VL) |
| v4 (Apertus) | `Apertus-SEA-LION-v4-8B-IT` | 8B | 65k |
| v3.5 (Llama) | `Llama-SEA-LION-v3.5-8B-R`, `Llama-SEA-LION-v3.5-70B-R` | 8B / 70B | 128K |
| v3 (Llama/Gemma) | `Llama-SEA-LION-v3-8B(-IT)`, `Llama-SEA-LION-v3-70B(-IT)`, `Gemma-SEA-LION-v3-9B(-IT)` | 8B/70B/9B | 128K (Llama v3), 8192 (Gemma v3 9B) |
| v2 | `Llama-SEA-LION-v2-8B(-IT)` | 8B | 8192 |
| Safety / embedding | `Qwen-SEA-Guard-4B-040226`, `Qwen-SEA-Guard-8B-040226`, `Llama-SEA-Guard-8B-040226`, `Gemma-SEA-Guard-12B-040226`, `SEA-LION-ModernBERT-Embedding-600M`, `SEA-LION-E5-Embedding-600M` | — | 128k (guards), 8k / 512 (embedding) |

Context values: https://sea-lion.ai/models and per-model docs, e.g. https://docs.sea-lion.ai/models/sea-lion-v4.8/nemotron-sea-lion-v4.8, https://docs.sea-lion.ai/models/sea-lion-v4.5/qwen-sea-lion-v4.5 ("**Context length:** 262k"), https://docs.sea-lion.ai/models/sea-lion-v3/gemma-sea-lion-v3-9b ("**Context Length**: 8192"), https://docs.sea-lion.ai/models/sea-lion-v2 ("* **Context Length**: 8192").

### Model IDs confirmed callable on first-party free API (`https://api.sea-lion.ai/v1`)
Documented by example only (no public list endpoint without a key):
- `aisingapore/Qwen-SEA-LION-v4.5-27B-IT` — instruct + tool calling (https://docs.sea-lion.ai/guides/inferencing/api)
- `aisingapore/Llama-SEA-LION-v3.5-70B-R` — reasoning (same page)
- `aisingapore/Gemma-SEA-LION-v4-27B-IT`, `aisingapore/Llama-SEA-LION-v3-70B-IT` (same page, tool-calling guide)
- `aisingapore/SEA-Guard`, `aisingapore/SEA-LION-ModernBERT-Embedding-600M` (same page)
- `aisingapore/Gemma-SEA-LION-v3-9B-IT` (https://github.com/aisingapore/sealion-notebooks/blob/main/SEA_LION_Trial_API_Key.ipynb)
- Full set per key: `curl 'https://api.sea-lion.ai/v1/models' -H 'Authorization: Bearer YOUR_API_KEY'` (same API page). **[UNVERIFIED]** which additional IDs (e.g. v4.8) that endpoint returns today — requires a key.

### Model IDs served by third parties (all confirmed on HF API today)

| Where | Models | Evidence |
|---|---|---|
| HF Inference Providers → `featherless-ai` | `aisingapore/Llama-SEA-LION-v3-70B-IT`, `Llama-SEA-LION-v3-8B-IT`, `Gemma-SEA-LION-v3-9B-IT`, `Llama-SEA-LION-v3.5-8B-R`, `Llama-SEA-LION-v2-8B-IT`, `Gemma-SEA-LION-v4-27B-IT` | `?expand=inferenceProviderMapping` on each model API record, e.g. `{"featherless-ai":{"status":"live",...}}`; model `inference: warm` |
| HF Inference Providers → `publicai` | `aisingapore/Gemma-SEA-LION-v4-27B-IT`, `aisingapore/Qwen-SEA-LION-v4-32B-IT` | same API expansion; https://huggingface.co/models?inference_provider=publicai (4 models total today) |
| Cloudflare Workers AI | `@cf/aisingapore/gemma-sea-lion-v4-27b-it` only | https://developers.cloudflare.com/workers-ai/models/gemma-sea-lion-v4-27b-it/ ; https://docs.sea-lion.ai/guides/inferencing/cloudflare |
| PublicAI Gateway (utility) | `aisingapore/Gemma-SEA-LION-v4-27B-IT`, `aisingapore/Qwen-SEA-LION-v4-32B-IT` | https://platform.publicai.co/models |
| Google Vertex AI Model Garden / AWS Bedrock Custom Model Import / AWS SageMaker / vLLM self-host / Ollama | customer-deployed (you pay the cloud), guide: https://docs.sea-lion.ai/guides/inferencing |
| **NVIDIA NIM / build.nvidia.com** | **NOT hosted** — zero SEA-LION entries in https://build.nvidia.com/models.md | grep of full catalog index, 2026-10-06 |

## (b) Free tier: rate/daily quota, credit amount & expiry

**First-party SEA-LION API** — https://docs.sea-lion.ai/guides/inferencing/api ("Rate Limits" section):
> "As of 04 Jun 2026, our rate limits is set to **10 requests per minute per user**."

https://docs.sea-lion.ai/overview/readme/faq (section "API access and rate limits"):
> "Our free APIs are intended for proof-of-concept (POC) development and are rate-limited (10 requests per minute). They are not designed for production workloads."
> "We are not able to raise the limits on the free POC tier."

Other first-party constraints: "Only 1 API key is allowed to be created per user." (API page). Key is called a "Create New Trial API Key" in the Playground Key Manager.
- **No daily request quota, token quota, credit amount, or key expiry period is published anywhere in the docs** → **[UNVERIFIED]**. The FAQ only implies expiry is possible: "My API key expired, or I am hitting timeouts. What should I do?" (no lifetime stated). Playground itself is login-gated (https://playground.sea-lion.ai/), so the Key Manager screen could not be read.

**Cloudflare Workers AI (Gemma-SEA-LION-v4-27B-IT)** — https://developers.cloudflare.com/workers-ai/platform/pricing/ (page "Last updated Oct 1, 2026"):
> "Our free allocation allows anyone to use a total of **10,000 Neurons per day at no charge**. To use more than 10,000 Neurons per day, you need to sign up for the Workers Paid plan."
> "All limits reset daily at 00:00 UTC."
Model rate for `@cf/aisingapore/gemma-sea-lion-v4-27b-it`: "$0.351 per M input tokens, $0.555 per M output tokens" (= 31,876 / 50,488 neurons per M tokens) — same pricing page and model page.

**PublicAI Gateway (a non-profit utility hosting 2 SEA-LION models)** — https://platform.publicai.co/docs (rendered):
> "Every new user account receives **$2 of free starter credit**, used for API calls at the listed per-token prices."
Free tier limits — https://platform.publicai.co/plans (rendered; page footer "Last modified on October 6, 2026"):
> "Free | **100 requests/minute** | Default when you create an API key"
SEA-LION pricing there — https://platform.publicai.co/models: `aisingapore/Gemma-SEA-LION-v4-27B-IT` 128K "$0.20 / $0.40 per 1M tokens" (Country of Origin: Singapore); `aisingapore/Qwen-SEA-LION-v4-32B-IT` 128K "$0.25 / $0.50 per 1M tokens".

**Hugging Face Inference Providers (router)** — https://huggingface.co/docs/inference-providers/pricing:
> "| Free Users | **$0.10, subject to change** | Inference Providers |"
> "| PRO Users | $2.00 | All Hugging Face compute services |"
Credits are monthly; pay-as-you-go after that. Hosting SEA-LION this way means paying Featherless AI and/or Public AI rates with a $0.10/month free allowance.

**Featherless AI (host of 6 SEA-LION models) has no free plan** — https://featherless.ai/pricing: plans are "Chat $25/month", "Developer $50/credits per month", "Business Custom". Data line on that page: "Prompts stored | Never".

## (c) Structured output / tool calling support

| Endpoint | Tool/function calling | JSON-schema structured output |
|---|---|---|
| `api.sea-lion.ai` | **Yes, model-dependent** (documented with worked examples): Qwen-SEA-LION-v4.5-27B-IT supports native function calling (`tools`, `tool_choice:"auto"`, `finish_reason=="tool_calls"`); Llama-SEA-LION-v3-70B-IT "Fully supports OpenAI-style tool calling"; Gemma-SEA-LION-v4-27B-IT ignores `tools` unless `tool_choice` is forced, else text-parsed ```tool_code blocks; Llama-SEA-LION-v3.5-70B-R "Reasoning model **without** tool calling capability". Quotes/examples: https://docs.sea-lion.ai/guides/inferencing/api and https://docs.sea-lion.ai/guides/tool_calling | **Not documented** → **[UNVERIFIED]**. Model-level claim only: Gemma-SEA-LION-v4-27B "inherits Gemma 3's ... Advanced function calling and structured outputs" (https://docs.sea-lion.ai/models/sea-lion-v4/gemma-sea-lion-v4-27b) |
| Cloudflare Workers AI | **Not documented** — the model's parameter list has no `tools`/`tool_choice` (params: prompt, lora, response_format, raw, stream, max_tokens, temperature, top_p, top_k, seed, repetition/frequency/presence penalty). https://developers.cloudflare.com/workers-ai/models/gemma-sea-lion-v4-27b-it/ | `response_format` object exists (details not enumerated on page) |
| PublicAI Gateway | Not documented per model: "Inference parameters (temperature, top_p, max_tokens, etc.) vary by model." https://platform.publicai.co/models → **[UNVERIFIED]** | ditto |
| HF router (Featherless/PublicAI) | Same model-dependent behavior; no provider-specific statement → **[UNVERIFIED]** | ditto |

## (d) `seed` + temperature determinism

- **First-party API: `seed` is not documented** in any SEA-LION doc page (full-text grep of all 51 doc pages from https://docs.sea-lion.ai/llms.txt found no API `seed` parameter) → **[UNVERIFIED]**. `temperature` is used in examples (e.g. `"temperature": 0`) but no determinism guarantee is stated.
- Note the API is vLLM-fronted (docs use vLLM-only knobs such as `chat_template_kwargs`, and warn about response **caching**: "your API responses might have been cached ... set the `no-cache` flag to `true`").
- **Cloudflare Workers AI: yes, documented** — `seed` integer, min 1, max 9999999999, "**Random seed for reproducibility of the generation.**" plus `temperature` (min 0, max 5, default 0.6) on https://developers.cloudflare.com/workers-ai/models/gemma-sea-lion-v4-27b-it/
- PublicAI / Featherless: no `seed`/determinism statement found → **[UNVERIFIED]**.

## (e) Context length

See table in (a). Headline numbers today: Nemotron v4.8 = 262,144 tokens (docs; models page says 262K); Qwen v4.5 27B = 262k; Qwen v4 VL = 256k; Gemma v4/v4.5 27B and Llama v3/v3.5 = 128k; Gemma v4 4B-VL = 128k; Apertus v4 8B = 65k; Gemma v3 9B and SEA-LION v2 = 8192; modernBERT embedding = 8k, E5 embedding = 512.
Cloudflare-hosted Gemma-SEA-LION-v4-27B-IT shows "Context Window 128,000 tokens".

## (f) DATA-USE on the free/hosted tiers (verbatim)

**First-party SEA-LION API** — governed by https://sea-lion.ai/terms-of-use/ ("Last updated on 19th November 2024"):
> "You retain ownership of the Content. **We may use the Content to provide, maintain, develop and improve our Services**, comply with applicable law, enforce our terms and policies and keep our Services safe."
> "You hereby irrevocably and unconditionally agree that **we may monitor your use of the Services** to ensure the quality of the Service, Service improvement (where required) and compliance with the Terms."

https://sea-lion.ai/privacy-policy/ ("Last updated on 19th November 2024") — logging and retention:
> "1.4 Log Data ... This Log Data includes information such as your IP address, browser type, operating system, the referring web page, pages visited, location, your mobile carrier, device information (including device and application IDs), **search terms**, and cookie information."
> "**2.1** ... any information you provide on our platform(s) ... **may remain even after you terminate your account.** We urge you to consider the sensitivity of any information you input into these services."
> "**3.2 Deletion of Your Personal Data** You can request your account deletion..." (deletion is request-based; no storage duration given)
The docs state usage is subject to those two pages: "Usage of the SEA-LION API is subject to our Terms of Use and Privacy Policy" (https://docs.sea-lion.ai/guides/inferencing/api).
Verdict language (no training statement either way): SEA-LION ToU/PP **do not** contain a sentence promising "we will not train on your prompts", and they do not explicitly say they train on them; they grant a service-improvement use right plus monitoring. No retention period is published → **[UNVERIFIED]** for any retention window. Hosting region of `api.sea-lion.ai` is not documented → **[UNVERIFIED]**.

**Cloudflare Workers AI** — https://developers.cloudflare.com/workers-ai/platform/data-usage/ (page "Last updated Apr 21, 2026"):
> "Your inputs (e.g., text prompts, image submissions, audio files, etc.), outputs ..., embeddings, and training data constitute Customer Content."
> "Cloudflare does not make your Customer Content available to any other Cloudflare customer."
> "**Cloudflare does not use your Customer Content to (1) train any AI models made available on Workers AI or (2) improve any Cloudflare or third-party services, and would not do so unless we received your explicit consent.**"
> "Cloudflare processes certain customer data in order to provide the Workers AI service, subject to our Privacy Policy ...". Model license caveat on same page: "The models constitute Third-Party Services and may be subject to open source or other license terms ... Be sure to review the license terms applicable to each model".

**PublicAI Inference Utility (Metagov Inc., US 501(c)(3))** — https://publicai.co/tc (Terms & Privacy):
> "**1.5 Third-Party Providers** ... Your Prompt will be processed via a subprocessor ... We do not control providers' retention, training, or other uses once data is sent to them."
> "**Academic Research Partnerships** ... **We provide raw database copies that may include usernames, emails, and conversation content** ... We require researchers to sign data use agreements ... We require deletion of all raw data after the research project concludes." (opt-out path: delete chats / email support@publicai.co)
> "**2.5** ... We temporarily retain technical logs ... These logs are stored for **no longer than 90 days**."
> "**2.9** ... What we DON'T currently offer: Formal Data Processing Agreements (DPAs) ... **Localized data storage outside the US** ... Organizations or individuals requiring formal GDPR compliance documentation should not use our Service."
> "**2.11 Security Measures** ... Current limitations: **No encryption at rest** (planned when OpenWebUI supports it)"
Marketing claim on https://publicai.co/utility (Sep 2, 2025): "**Privacy-first.** By default, user prompts and outputs are not used for training or shared." (this is the utility's own statement; the opt-in "Data Flywheel" is consent-gated).

**HF Inference Providers / Featherless**: Featherless pricing page states "Prompts stored: Never" (https://featherless.ai/pricing); HF itself states it passes through provider costs and hosts no model weights for routed calls — no prompt-retention sentence found on the HF pricing page → provider terms govern (**[UNVERIFIED]** for the exact HF-router retention wording).

## (g) Deprecation / versioning policy for models

**No published deprecation, sunset, or model-versioning policy was found** on any live SEA-LION page today (full-text grep of all 51 pages listed in https://docs.sea-lion.ai/llms.txt for `deprecat|sunset|retire|EOL|end of life|archive`: 0 relevant hits). Evidence of practice only: versioned doc pages are kept for v1 → v2 → v3 → v3.5 → v4 → v4.5 → v4.8, each with a release date, and the API is described as POC-only. → **[UNVERIFIED]** (no policy page exists as of 2026-10-06).

## (h) OpenAI-compatible base URLs (exact)

| Host | Base URL | Evidence |
|---|---|---|
| AI Singapore first-party | `https://api.sea-lion.ai/v1` (chat completions: `https://api.sea-lion.ai/v1/chat/completions`; embeddings: `/v1/embeddings`; models: `/v1/models`) | https://docs.sea-lion.ai/guides/inferencing/api — "SEA-LION's API endpoints for chat are compatible with OpenAI's API and libraries." |
| Cloudflare Workers AI | `https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1` (model id `@cf/aisingapore/gemma-sea-lion-v4-27b-it`) | https://developers.cloudflare.com/workers-ai/models/gemma-sea-lion-v4-27b-it/ and https://docs.sea-lion.ai/guides/inferencing/cloudflare |
| PublicAI Gateway | `https://api.publicai.co/v1` (requires `User-Agent` header) | https://platform.publicai.co/docs (confirmed live: `/v1/models` returns 401 JSON without auth) |
| Hugging Face Inference Providers router | `https://router.huggingface.co/v1` | https://huggingface.co/docs/inference-providers/index ("drop-in OpenAI replacement", `base_url="https://router.huggingface.co/v1"`) |
| NVIDIA NIM | n/a — SEA-LION not in catalog (`https://integrate.api.nvidia.com/v1` is NVIDIA's base but has no SEA-LION model) | https://build.nvidia.com/llms.txt + https://build.nvidia.com/models.md |
| Vertex AI / Bedrock Custom Model Import | customer-deployed endpoints (Bedrock import documented only for `us-east-1` and `us-west-2` at time of writing) | https://docs.sea-lion.ai/guides/inferencing/vertex_ai , .../amazon_bedrock |

## Licenses per SEA-LION model (verbatim where decisive)

| Model | License (HF metadata today) | Docs page says |
|---|---|---|
| `Nemotron-SEA-LION-v4.8-120B-A12B` / `-30B-A3B` | `license: mit` (HF README front-matter: "license: mit"; card body: "**License:** [MIT](https://mit-license.org/)") | docs page says "**License:** [Other](https://huggingface.co/aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B-Base/blob/main/NOTICE.md)" → **contradiction between docs and HF card, recorded as-is** |
| `Qwen-SEA-LION-v4.5-27B-IT` | HF `cardData.license: mit` **with** `license_link: https://huggingface.co/Qwen/Qwen3.6-27B/blob/main/LICENSE` | docs page: "**License:** [Apache-2.0](https://github.com/QwenLM/Qwen3.6/blob/main/LICENSE)" → contradiction recorded |
| `Qwen-SEA-LION-v4-32B-IT` | `license: mit` | — |
| `Gemma-SEA-LION-v4-27B-IT` | `license: gemma` | "**License:** [Gemma Terms of Use](https://ai.google.dev/gemma/terms)" |
| `Gemma-SEA-LION-v4.5-E2B-IT` | `cardData.license: mit` + `license_link: https://ai.google.dev/gemma/docs/gemma_4_license` | — |
| `Llama-SEA-LION-v3.5-8B-R` / `-70B-R` | `license: llama3.1` | — |
| `Apertus-SEA-LION-v4-8B-IT` | `license: mit` | docs: "**License:** Apache-2.0" |

AISG's FAQ-level statement (https://docs.sea-lion.ai/overview/readme/faq):
> "**Is SEA-LION free to use? Can I use it commercially?** Yes. SEA-LION is open-source and free to use, including for commercial purposes. You can download and self-host the models from Hugging Face, or access them through cloud platform partners."

Base-license restrictions that ride along with the non-permissive families (quoted today):
- Gemma Terms of Use (https://ai.google.dev/gemma/terms) — "Section 3: DISTRIBUTION AND RESTRICTIONS 3.1 Distribution and Redistribution You may reproduce or Distribute copies of Gemma or Model Derivatives if you meet all of the following conditions: You must include the use restrictions referenced in Section 3.2 as an enforceable provision in any agreement (e.g., license agreement, terms of use, etc.) ... All Distributions (other than through a Hosted Service) must be accompanied by a 'Notice' text file ..."; Section 3.2 requires compliance with the "Gemma Prohibited Use Policy at ai.google.dev/gemma/prohibited_use_policy ... which is hereby incorporated by reference into this Agreement".
- Llama 3.1 Community License — "2. Additional Commercial Terms. If, on the Llama 3.1 version release date, the monthly active users of the products or services made available by or for Licensee ... is greater than 700 million monthly active users in the preceding calendar month, you must request a license from Meta, which Meta may grant to you in its sole discretion ..." (https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/LICENSE; the HF copy at huggingface.co/meta-llama/Llama-3.1-70B-Instruct is gated — HTTP 401 without login).

## Quick SEA-LION summary table

| Host | Free? | Rate limit / credit | Data-use verdict | OpenAI base URL |
|---|---|---|---|---|
| `api.sea-lion.ai` | Yes (POC tier) | 10 RPM/user; 1 key per user; no published daily quota, credits, or expiry | ToU: AISG "may use the Content to provide, maintain, develop and improve our Services"; "we may monitor your use of the Services". No training promise, no retention period, no region documented | `https://api.sea-lion.ai/v1` |
| Cloudflare Workers AI (Gemma-SEA-LION-v4-27B-IT) | Yes | 10,000 Neurons/day free (resets 00:00 UTC); then $0.011/1k Neurons | "Cloudflare does not use your Customer Content to (1) train any AI models ... or (2) improve any ... services"; third-party model licenses still apply | `https://api.cloudflare.com/client/v4/accounts/{id}/ai/v1` |
| PublicAI Gateway (Gemma-SEA-LION-v4-27B-IT, Qwen-SEA-LION-v4-32B-IT) | Yes, limited | Free tier 100 RPM; **$2** starter credit, then pay-as-you-go | Not used for training by default (opt-in flywheel); raw logs incl. usernames/emails/chats shared with vetted academic researchers; logs ≤90 days; no encryption at rest; no localised non-US storage | `https://api.publicai.co/v1` |
| HF Inference Providers → featherless-ai / publicai | Only via HF credits ($0.10/mo free acct; $2 PRO) or paid provider plan | Featherless has no free plan ($25/$50 per month) | Featherless: "Prompts stored: Never" | `https://router.huggingface.co/v1` |
| NVIDIA NIM | n/a — not hosted | — | — | — |

---

# PROVIDER B — Sahabat-AI (Indosat Ooredoo Hutchison + GoTo)

Steward: ecosystem "co-initiated and co-developed by ... PT Indosat Tbk ("Indosat Ooredoo Hutchison" or "IOH")", with GoTo and AI Singapore as partners (https://sahabat-ai.com/documents/Sahabat-AI-Responsible-Use-Guide-v7.pdf, "Version April 2025"). Country: Indonesia.

## (a) Model IDs available today (Hugging Face; weights only)

HF org page: `https://huggingface.co/sahabat-ai` **307-redirects to** `https://huggingface.co/Sahabat-AI` (org name "Sahabat-AI", company, 99 followers). Models mirrored under two orgs, `Sahabat-AI/…` and `GoToCompany/…`:

| Model ID | Base / type | Context | License tag |
|---|---|---|---|
| `Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT` (= `GoToCompany/Llama-Sahabat-AI-v2-70B-IT`) | Llama 3.1 70B CPT + IT, released 2025-05-30 | "The model has a context length of 128k" (model card) | `llama3.1` |
| `Sahabat-AI/gemma2-9b-cpt-sahabatai-v1-instruct` | Gemma-2 9B CPT | "context length of 8192" | `gemma` (Gemma Community License) |
| `Sahabat-AI/gemma2-9b-cpt-sahabatai-v1-base` | Gemma-2 9B CPT base | 8192 | `gemma` |
| `Sahabat-AI/llama3-8b-cpt-sahabatai-v1-instruct` | Llama-3 8B CPT | "context length of 8192" | `llama3` (Llama3 Community License) |
| `Sahabat-AI/llama3-8b-cpt-sahabatai-v1-base` | Llama-3 8B CPT base | 8192 | `llama3` |

Languages on the card front-matter: `en, id, jv, su, bbc (Batak Toba), ban (Balinese)` for v2-70B. The 70B model card stack: "Co-initiated by: PT GoTo Gojek Tokopedia Tbk, Indosat Ooredoo Hutchison — Developed by: PT GoTo Gojek Tokopedia Tbk, AI Singapore".
(Also on the Hub from third parties, not official: many community GGUF quants, e.g. `mradermacher/SahabatAI-Lion-9B-TIES-v1-Instruct-GGUF`.)

## (b) Free tier: rate/daily quota, credit amount & expiry

**There is NO public hosted free API for Sahabat-AI.** Findings:
- `sahabat-ai.com` "Untuk Developers" section offers only HF download + contribution channels — no API key, no endpoint, no quota: rendered page text (2026-10-06) shows "Sahabat-AI 70B … Lisensi Open-Source … HuggingFace" and contact `support@sahabat-ai.com`.
- Probed hosts today: `https://api.sahabat-ai.com/v1/models` → **404**; `https://api.sahabat-ai.com/v1/chat/completions` → **404**; `https://api.sahabat-ai.id/v1/models` → connection failure; `https://llm.sahabat-ai.com/v1/models` → connection failure; `https://chat.sahabat-ai.com/v1/models` → **404**.
- `https://chat.sahabat-ai.com` is the consumer chat app (Flutter web + Firebase), not a documented developer API; login-gated, so no API docs/terms could be read.
- The only third-party serverless host found for these weights is **HF Inference Providers → featherless-ai**, which maps `Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT` (`status: live`) — but Featherless has no free plan (https://featherless.ai/pricing: $25/mo chat, $50/mo credit plans). The 8B/9B v1 models have **no** `inferenceProviderMapping` at all (checked `?expand=inferenceProviderMapping`: `{}`).
- **FriendliAI** lists `Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT` but only as "Dedicated Endpoints" / "Container" — no serverless free tier (https://friendli.ai/models/Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT).
- Not in NVIDIA NIM catalog (grep of https://build.nvidia.com/models.md: 0 hits) and not on Cloudflare Workers AI or the PublicAI gateway catalogs.
- A third-party directory claims a "hosted API" (https://recatools.com/ai-directory/sahabat-ai/, page dated 30 Sep 2026) — **no primary source found to substantiate it** → treat as **[UNVERIFIED]**; the primary site documents no API.

So: **weights-only for developers; the only Sahabat-AI-hosted service is the first-party chat app** (sahabat-ai.com / GoPay app), plus paid third-party hosts. Also, unrelated "GPU Merdeka credit coupons" exist for researchers ("Kupon Kredit GPU Merdeka … kirim proposal Anda dan dapatkan kupon kreditnya sekarang" — sahabat-ai.com, rendered; application via Google Form) but these are GPU compute coupons, not a model API.

## (c) Structured output / tool calling

No Sahabat-AI API exists to test, and no model card for any Sahabat-AI model documents tool/function calling or JSON-schema output. The v2-70B card documents only plain Transformers generation, and mentions tool calling nowhere. → **[UNVERIFIED]** / not offered.
(Comparable point of reference only: the Responsible Use Guide discusses tool-call safeguards generically — "If the usecase involves tool calling, it is important to protect what is passed to the agent tool" — which describes deployment advice, not an API feature.)

## (d) `seed` + temperature determinism

Not documented for any Sahabat-AI hosted service (none exists) and not asserted on any model card (v1 cards list `temperature`/`max_new_tokens` only). → **[UNVERIFIED]**.

## (e) Context length

- `Llama-Sahabat-AI-v2-70B-IT`: **128k** ("The model has a context length of 128k", model card).
- `gemma2-9b-cpt-sahabatai-v1-instruct/base`, `llama3-8b-cpt-sahabatai-v1-instruct/base`: **8192** ("The model has a context length of 8192"); the cards note a benchmark caveat: "VLLM caps the context size at 4096 tokens while HuggingFace was set to 8192 tokens."

## (f) DATA-USE

**Weights**: no data-use restriction beyond the base licenses (see below); the Responsible Use Guide is guidance, not a data-processing policy.
**First-party chat service (chat.sahabat-ai.com / sahabat-ai.com)**: **no privacy notice or data-use policy was found today.** The site's only policy document linked from the page is the Cookie Notice (https://sahabat-ai.com/documents/Sahabat-AI-Cookie-Policy-v2.pdf, "effective on 2 June 2025"), which says:
> "We only use cookies that are strictly necessary for the operation or functionality of the Service." (only `sID` 1-day and `rID` 30-day first-party cookies; contact `support@sahabat-ai.com`)
`https://chat.sahabat-ai.com/privacy` → 404; `.../terms` → 404; `sahabat-ai.com/robots.txt` and `/sitemap.xml` → 404. Whether prompts sent to the chat app are logged, retained, trained on, or human-reviewed is therefore **unstated on any live page** → **[UNVERIFIED]**. (PT Indosat is named as the controller in the Cookie Notice.)
The Responsible Use Guide sets the *model-level* expectation on privacy only as advice to deployers — verbatim: "AI systems must ensure robust privacy and data protection mechanisms throughout their lifecycle ... such as Indonesia's Law No. 27 Year 2022 on Personal Data Protection ..." and "Sahabat-AI is provided 'as is'. Indosat Ooredoo Hutchison do not represent or warrant that the reliability, timeliness, quality, suitability, availability, accuracy, completeness, or security of Sahabat-AI will fulfil users' needs and expectations."

## (g) Deprecation / versioning policy

No deprecation or versioning policy published. Versioning in practice is by model name (v1 = 8B/9B, v2 = 70B, May 2025). → **[UNVERIFIED]**.

## (h) OpenAI-compatible base URL

**None.** No OpenAI-compatible endpoint is documented or reachable for Sahabat-AI (probes in (b): 404 / no host). The chat app is a web UI, and third-party serving (Featherless via HF router `https://router.huggingface.co/v1`, FriendliAI dedicated endpoints) is not an OpenAI-compatible *Sahabat-AI* host under the provider's control.

## Licensing (verbatim, per model family)

- `Llama-Sahabat-AI-v2-70B-IT`: card front-matter `license: llama3.1`; card body: "**License:** [Llama 3.1 Community License](https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct/blob/main/LICENSE)". Restriction quote (official Meta repo): "2. Additional Commercial Terms. If, on the Llama 3.1 version release date, the monthly active users of the products or services made available by or for Licensee ... is greater than **700 million monthly active users** in the preceding calendar month, you must request a license from Meta ..." (https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/LICENSE). Note: the HF copy of that LICENSE is gated (HTTP 401 without login) — verified today.
- v1 Llama-3 8B models: "**License:** [Llama3 Community License](https://huggingface.co/meta-llama/Meta-Llama-3-8B/blob/main/LICENSE)" (`license: llama3`); the Llama 3 Community License contains the same 700M-MAU clause: "2. Additional Commercial Terms. If, on the Meta Llama 3 version release date, the monthly active users ... is greater than 700 million monthly active users ..." (https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3/LICENSE).
- v1 Gemma-2 9B models: "**License:** [Gemma Community License](https://ai.google.dev/gemma/terms)" (`license: gemma`); Gemma terms require the Section 3.2 use restrictions to be flowed down and include the Prohibited Use Policy by reference (quotes in the SEA-LION section above).
- The site renders the 70B model's license as "**Lisensi Open-Source**" (sahabat-ai.com, rendered) — i.e. marketing shorthand, while the underlying Hub license is Llama 3.1 Community License (not OSI-listed).
- Training-data licensing statement on v1 cards: "special care was taken to ensure that the datasets used had commercially permissive licenses through verification with the original data source."

## Indonesian-language focus (documented)

- Site: "Sahabat-AI adalah sebuah koleksi Large Language Models (LLMs) open-source yang dirancang khusus untuk Bahasa Indonesia dan bahasa daerah" and "Sahabat-'Sahabat' sejati Anda yang fasih berbahasa Indonesia, Sunda, Jawa, Bali, dan Batak" (sahabat-ai.com, rendered 2026-10-06).
- Press release (GoTo, 02 June 2025): "The latest Sahabat-AI model can now operate across **five local languages: Bahasa Indonesia, Javanese, Sundanese, Balinese and Bataknese** in addition to a number of international languages." (https://www.gotocompany.com/en/news/press/sahabat-ai-gets-smarter-indosat-and-goto-launch-new-70-billion-parameter-model-with-multilingual-chat-service)
- Model card languages: `en, id, jv, su, bbc, ban`.

## Hosting region / country (documented)

- GoTo press release, 02 June 2025: "All data and GPU infrastructure used to serve the model are stored within Indonesian territory or on users' own servers, ensuring compliance with national data regulations."; Indosat runs it on "GPU Merdeka, our sovereign AI cloud", "deployed by Indosat's Lintasarta".
- Site (rendered): "Data yang Disimpan Secara Lokal — Semua data Anda tetap berada di Indonesia" and "GPU Merdeka adalah layanan cloud AI berdaulat yang didukung oleh NVIDIA ... Dengan hosting dalam negeri dan dikelola oleh profesional TI Indonesia".
- Marketing-Interactive (3 Jun 2025): "Built on GPU Merdeka, which was developed by Indosat's Lintasarta, the model is trained and served entirely within Indonesia." (trade press, corroborating)

## Quick Sahabat-AI summary

| Field | Finding |
|---|---|
| Free hosted API | **None. Weights-only** (plus first-party chat app). No documented endpoint; `api.sahabat-ai.com` 404s |
| Models | `Llama-Sahabat-AI-v2-70B-IT` (128k), `gemma2-9b-cpt-sahabatai-v1-*` (8192), `llama3-8b-cpt-sahabatai-v1-*` (8192) — HF orgs `Sahabat-AI` + `GoToCompany` |
| Quota / credit | n/a (no API). GPU Merdeka *compute* credit coupons exist for approved proposal applicants (not a model API) |
| Structured output / tools | Not documented → [UNVERIFIED] |
| Seed | Not documented → [UNVERIFIED] |
| License | Llama 3.1 / Llama 3 Community (700M-MAU clause) and Gemma Terms (flow-down + Prohibited Use Policy) |
| Data-use on chat app | **No privacy/data-use policy published** (only a cookie notice listing 2 strictly-necessary cookies) → [UNVERIFIED] |
| OpenAI base URL | None |
| Region | Indonesia (GPU Merdeka / Lintasarta, in-country); "All data and GPU infrastructure used to serve the model are stored within Indonesian territory" |

---

# Not verified / gaps

1. **Free SEA-LION API model list** — only visible with a key (`GET /v1/models` → 401 today); which v4.8/v4.5/v3 models are actually served, and whether the list differs per key, is **[UNVERIFIED]**. Documented examples only.
2. **SEA-LION trial-key credits/expiry/daily cap** — not published in docs or FAQ; Playground Key Manager is Google-login-gated. Only the 10 RPM figure is published. **[UNVERIFIED]**.
3. **`seed` on `api.sea-lion.ai`** — undocumented. Untestable without a key (auth is checked before body parsing: 401). **[UNVERIFIED]**. Documented only on Cloudflare's host of the same model family.
4. **JSON-schema (`response_format`/structured outputs) on `api.sea-lion.ai`** — undocumented; only a model-level claim for Gemma-SEA-LION-v4-27B. **[UNVERIFIED]**.
5. **SEA-LION deprecation/versioning policy** — no policy page exists (full-text grep of all 51 doc pages). **[UNVERIFIED]**.
6. **Hosting region of `api.sea-lion.ai`** — not stated in ToU/PP/docs. **[UNVERIFIED]**. (Third-party hosts: Cloudflare = global edge; PublicAI = "no localised data storage outside the US"; Bedrock import guide lists only us-east-1/us-west-2.)
7. **License contradictions recorded as-is** (no resolution attempted): Nemotron v4.8 — HF `license: mit` vs docs "License: Other (NOTICE.md)"; Qwen v4.5 27B — HF `mit` (+ Qwen license link) vs docs "Apache-2.0"; Apertus v4 8B — HF `mit` vs docs "Apache-2.0". Meta Llama LICENSE text is unreadable on HF without login (401); quoted from Meta's official GitHub repo instead.
8. **Sahabat-AI chat-app privacy/data-use** — no privacy notice, ToS, or retention statement is published on sahabat-ai.com or chat.sahabat-ai.com (404s on /privacy, /terms; site exposes only a cookie notice). Prompt logging/retention/training in the chat service is **[UNVERIFIED]**. A claim of a "hosted API" from an aggregator (recatools.com, 30 Sep 2026) could not be confirmed on any primary page.
9. **Sahabat-AI v1 model card data section** is descriptive prose (training data provenance, "commercially permissive licenses" claim) with no data-use policy for hosted inference. **[UNVERIFIED]** beyond the wording quoted.
10. **PublicAI docs** were read via browser rendering because the docs are JS-only; their `Last modified on October 6, 2026` stamp is quoted from the rendered footer.
11. Not investigated (out of assigned scope): exact Vertex AI / Bedrock / SageMaker pricing and regions beyond the modelled countries.
