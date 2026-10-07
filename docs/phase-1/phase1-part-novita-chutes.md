# Phase-1 Evidence: Novita AI + Chutes

All pages fetched **2026-10-06** (access date). Every "current" claim below is from a page fetched today; nothing is from training memory. Quotes are verbatim. Page-level "last updated"/"as of" dates noted where the page displays them. Anything not confirmed on a live page is marked `[UNVERIFIED]` with the reason.

Slug: `novita-chutes`. Companion files: peer subagent reports (Qwen/Z.ai, Baidu/Scaleway, Moonshot/Volcano, DeepInfra/Vercel, SeaLion/Sahabat).

---

## 1. Novita AI (novita.ai)

### Summary table

| Field | Finding (2026-10-06) | Source |
|---|---|---|
| (a) Free model IDs | **None.** No model in the serverless catalog is $0/token | https://novita.ai/models/llm ; https://blogs.novita.ai/free-llm-api-comparison-2026/ |
| (b) Free tier / credits | **$100 promotional credits — Agent Sandbox only, 90 days, by completing a setup survey.** No general model-API signup credit published; referral $10 both sides (cap $500); docs FAQ mentions a $1 credit voucher | https://docs.novita.ai/guides/sandbox-pricing ; https://novita.ai/user/register ; https://blogs.novita.ai/free-llm-api-comparison-2026/ ; https://docs.novita.ai/guides/faq |
| (c) JSON-schema / tools | **Yes** — `response_format: {type: json_schema}` (Structured Outputs) and `tools[].function.parameters` + `strict` function calling | https://docs.novita.ai/api-reference/model-apis-llm-create-chat-completion.md ; https://docs.novita.ai/guides/llm-structured-outputs.md |
| (d) seed / determinism | **Yes** — `seed` accepted, documented as "best effort" deterministic | https://docs.novita.ai/api-reference/model-apis-llm-create-chat-completion.md |
| (e) Context | Per-model, up to 1M (see table below) | https://novita.ai/pricing ; https://novita.ai/models/llm |
| (f) Data use | **Zero Data Retention; not used for model training; no human review of Content "by default"** | https://novita.ai/legal/terms-of-service (§10.2) ; https://novita.ai/legal/privacy-policy |
| (g) Deprecation policy | Public dated retirement notices + replacement model + published migration table; ToS reserves right to remove models anytime | https://novita.ai/docs/changelog/28-09-26 ; https://docs.novita.ai/guides/llm-recommended.md ; https://novita.ai/legal/terms-of-service (§6) |
| (h) OpenAI base URL | `https://api.novita.ai/openai` (chat path `https://api.novita.ai/openai/v1/chat/completions`) | https://docs.novita.ai/llms.txt ; https://docs.novita.ai/guides/llm-api.md |

### (a) Free-model IDs

- The live pricing catalogue shows only paid per-token rates. Novita's own blog states: *"Novita AI's current serverless LLM API catalog does not list a model priced at $0 per token. Its free-tier mechanism is a referral program that gives $10 in credit to both the referrer and the new referred account per successful referral, up to $500 total, spendable against the full serverless catalog."* (https://blogs.novita.ai/free-llm-api-comparison-2026/, published 2026-08-18, `meta-article:modified_time: 2026-09-07`)
- Same claim in that post's comparison row: *"Full serverless LLM API catalog"* is free-tier coverage only via referral credit, and *"no current model in that catalog is offered at $0 per token."*
- Model list check (https://novita.ai/models/llm, fetched today): every listed LLM carries a positive input/output price (e.g. GLM 5.3 Flash $0.15/Mt in, $0.5/Mt out; DeepSeek V4 Flash $0.14/Mt in, $0.28/Mt out). No "free" badge seen on that page.
- **Typical free/open-weight families present today (paid):** DeepSeek (V4.1 Flash, V4 Pro 0813, V4 Flash 0731, V4 Flash, R1 0528, DeepSeek OCR 2), Qwen (Qwen3.8 Flash, Qwen3.5-397B-A17B …), Z.ai GLM (GLM 5.3 Flash/5.3/5.2/5.1/5/4.7/4.7 Flash/4.6/4.5 Air), Moonshot Kimi (K2.7 Code, K2.6, K2.5), MiniMax M3, Tencent Hy3/Hy4 Preview, Xiaomi MiMo V2.6 Flash/Pro, Meta Llama 3.1 8B Instruct, Google Gemma 4 31B/26B, InclusionAI Ling-3.0 Flash (https://novita.ai/models/llm ; https://novita.ai/pricing ; https://docs.novita.ai/guides/llm-recommended.md).

### (b) Free-tier quota / credits

- **Sandbox promotion (headline offer on signup page):** *"Get $100 in Sandbox credits — Sign up and start building instantly. Get $100 in Sandbox credits, valid for 90 days."* (https://novita.ai/user/register)
- Docs scope it explicitly to Sandbox: *"New users can complete a quick account setup survey to receive $100 in promotional credits for eligible Novita Sandbox usage. No credit card is required."* and *"Promotional credits are applied to eligible Novita Sandbox usage first, including CPU, RAM, and billable storage usage where applicable. After credits are used up or expired, continued usage is billed pay-as-you-go per current pricing."* (https://docs.novita.ai/guides/sandbox-pricing)
- Same page: *"Credits may be subject to availability, validity period, usage scope, and quota limits."* → **the 90-day/`$100` figure is confirmed; per-credit expiry mechanics beyond that are `[UNVERIFIED]` (only stated on a page that requires login to inspect voucher status).**
- Sandbox free allowances (not model API): *"Each sandbox includes 20 GB of Ephemeral Storage while running"*; *"Each account includes 60 GB of free Persistent Storage"*, overage $0.00009/GB/h. CPU: 1 vCPU $0.0000098/s; RAM: $0.0000032/GiB/s. (https://docs.novita.ai/guides/sandbox-pricing)
- **Referral credit:** *"a successful referral gives both the referrer and the new referred account $10 in LLM API credits, up to $500 in total credits for a single referrer"*; described as *"referral-gated, not an automatic grant on every new signup"* (https://blogs.novita.ai/free-llm-api-comparison-2026/). Same program described in Novita's 2025 blog: *"both you and your referral will receive $10 in credits"* (https://blogs.novita.ai/earn-500-free-credits-build-faster-with-deepseek-llama-qwen-on-novita-ai/, published 2025-04-22). **Referral-credit expiry is `[UNVERIFIED]` — no live page states it.**
- **$1 voucher:** Novita docs FAQ entry: *"Why did my $1 credit voucher disappear? — Our system automatically revokes vouchers when suspicious registration activity is detected (e.g., malicious sign-ups or multiple accounts from the same device)."* (https://docs.novita.ai/guides/faq.md) → a $1 signup voucher exists in the docs, but **no live page fetched states whether a $1 voucher is granted to every current new account, or its expiry** → `[UNVERIFIED]` amount/eligibility today, plus ToS §4 on revoking free quotas.
- **Rate limits (no "free tier" rate limit exists; limits are account-tier based):** docs define tiers purely by top-up history — T1 *"Monthly top-ups did not exceed $50 in any of the last 3 calendar months"*, T2 ≥$50 ≤$500, T3 ≥$500 ≤$3,000, T4 ≥$3,000 ≤$10,000, T5 ≥$10,000 in one of the last 3 months (https://docs.novita.ai/guides/llm-rate-limits.md). The per-model RPM/TPM table on that page is client-side rendered; **values below were extracted today from the live page** (`window.novitaRemoteData.llmModels`, 206 rows):
  - `deepseek/deepseek-v4.1-flash`: RPM 30 / 100 / 1000 / 3000 / 6000 (T1→T5); TPM 50,000,000 at every tier.
  - RPM T1=30 and T2=100 are uniform across all 206 rows; T3 varies 200–1000, T4 500–3000, T5 1000–6000.
  - TPM varies per model: observed patterns include 2M/6M/50M/50M/50M; 5M/7M/10M/15M/20M; 50M at all tiers.
  - Because the table is JS-rendered, a reader re-verifying without JS sees no numbers on the page (`[UNVERIFIED]` in the sense that the values are not in the static HTML; they are live data from the fetched page today).
- **Startup program (not self-serve):** *"Eligible startups can receive up to $10,000 in credits across Novita AI's Model APIs and Agent Sandbox. The program provides up to $1,000 in credits upfront. The next $5,000 is matched at a 1:1 ratio… For the final $4,000, every two dollars spent earns one dollar in credit. These credits can be redeemed for one year."* Eligibility: *"Venture-backed and Series B or earlier. AI-native product or platform. New Novita user."* (https://startups.novita.ai/)
- Batch inference discount: *"Batch inference is available at an introductory 50% discount on input and output tokens for supported models."* (https://novita.ai/pricing)

### (c) Structured output + tool calling

- `response_format`: *"Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema."* Enum: `text`, `json_object`, `json_schema`. (https://docs.novita.ai/api-reference/model-apis-llm-create-chat-completion.md)
- Tools: *"A list of tools the model may call. Currently, only functions are supported as a tool."* with `function.parameters` *"described as a JSON Schema object"* and `strict`: *"Whether to enable strict schema adherence when generating the function call. If set to true, the model will follow the exact schema defined in the parameters field."* (same page)
- Structured Outputs is model-gated: the supported-model list is JS-rendered on https://docs.novita.ai/guides/llm-structured-outputs.md (page text: *"The following models support `Structured Outputs`"*); the example uses `model = "qwen/qwen3.8-flash"`. **Full supported-ID list is `[UNVERIFIED]` as static text** (needs JS/page data); tool calling is documented per-request without a model allowlist on the same doc page.

### (d) seed + determinism

- *"`seed` — If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result."* (https://docs.novita.ai/api-reference/model-apis-llm-create-chat-completion.md) → accepts `seed`; explicitly "best effort", not a hard determinism guarantee. `temperature` *"between 0 and 2"* default 1 on the same page.

### (e) Context lengths

- Live examples (https://novita.ai/pricing, https://novita.ai/models/llm, fetched today): DeepSeek V4.1 Flash 1M; DeepSeek V4 Pro / V4 Pro 0813 1M; DeepSeek V4 Flash 1M; GLM 5.3 / 5.3 Flash / 5.2 1M; GLM 5.1 200K; GLM 5 198K; GLM 4.7 200K; GLM 4.7 Flash 195K; Kimi K3 1M; Kimi K2.7 Code 256K; Kimi K2.6 256K; Qwen3.8 Flash 977K; Qwen3.5-397B-A17B 262K; MiniMax M3 977K; Llama 3.1 8B Instruct 128K; Gemma 4 31B IT 262K; Ling-3.0 Flash 262K. (Docs recommended-model table uses 1M/262K/128K for the same families: https://docs.novita.ai/guides/llm-recommended.md)

### (f) Data use on the free tier

- **No free tier for model APIs exists**, so no free-tier-specific data clause was found; the governing text is the general ToS/Privacy Policy. Explicit statements:
  - ToS §10.2 (updated 2026-08-05): *"By Default, Novita AI will not use your Content to train our own models or to improve the Services. We will not retain any Content for longer than is necessary to provide the Services to you. We have adopted a "Zero Data Retention" policy, which means that we will not, unless otherwise required by applicable law (or as necessary to provide the Services or technical support to you): (i) log your Content for human review; or (ii) retain your Content beyond the time it takes to generate Output and deliver that Output to you. Notwithstanding the foregoing, you agree that we have the right to apply automated safety screening tools to your Content as we deem appropriate, and that such screening does not constitute retention of your Content for any other purpose."* (https://novita.ai/legal/terms-of-service)
  - Privacy Policy (Effective date: May 13, 2026; Last updated: May 13, 2026): *"The Personal Information will not be used for model training."* and *"This Privacy Policy does not apply to content that we process on behalf of customers while providing services. Our use of that data is governed by our customer agreements covering access to and use of those offerings."* (https://novita.ai/legal/privacy-policy)
  - Qualifier to flag for the thesis: the ToS wording is "**By Default**" and reserves automated safety screening; there is no wording making the guarantee conditional on payment, but also none making it explicitly stronger/weaker on a free tier.
- Trust Center: search index snippet shows *"Retained for 6 months for the purposes of billing, debugging, and security auditing."* → `[UNVERIFIED]`: https://trust.novita.ai/faq returned an empty body when fetched today (JS-only/blank shell); the quoted sentence came from a search-result snippet, not from a live page I could read.
- ToS §4: *"We strictly prohibit users from obtaining multiple free quotas through mass email registration or any other methods."* + revocation of *"all free quotas and discounts"* (https://novita.ai/legal/terms-of-service).

### (g) Deprecation / versioning policy

- Public changelog notice with a fixed cutoff: *"Novita retires the deepseek/deepseek-v4-flash large language model at 16:00 UTC on Oct 9, 2026. Migrate to deepseek/deepseek-v4.1-flash before the cutoff."* Page also says: *"As we release better and more powerful models, we routinely retire older ones."* (https://novita.ai/docs/changelog/28-09-26, titled "Oct 9, 2026 Model Deprecation Notice")
- Docs carry a standing migration table ("Migrating from older models … If you use → Switch to"), e.g. `deepseek/deepseek-r1-0528` → `deepseek/deepseek-v4-pro`. (https://docs.novita.ai/guides/llm-recommended.md)
- Model-access doc on offline models: *"Once a model is offline, no API key can call it … Calls to that model immediately return a "model unavailable" response"* (https://docs.novita.ai/guides/llm-model-access.md).
- Contractual backstop (no notice commitment): ToS §6 — *"Novita AI reserves the right to add, modify, suspend, or remove any Model from the Service at any time … Novita AI shall not be liable for any loss, damage, or disruption arising from the removal or modification of any Model."* (https://novita.ai/legal/terms-of-service)

### (h) OpenAI-compatible base URL

- `OpenAI-Compatible Base URL: https://api.novita.ai/openai` (https://docs.novita.ai/llms.txt); docs: *"simply set your base URL to: api.novita.ai/openai"* and curl `https://api.novita.ai/openai/v1/chat/completions` (https://docs.novita.ai/guides/llm-api.md). Base `https://api.novita.ai` for non-v1 endpoints; auth `Authorization: Bearer <API_KEY>`.

---

## 2. Chutes (chutes.ai)

### Summary table

| Field | Finding (2026-10-06) | Source |
|---|---|---|
| (a) Free model IDs | **None. No free tier at all.** 14 hosted models, all paid per-token | https://chutes.ai/llms.txt ("Live catalog as of Oct 6, 2026: 14 models") ; https://chutes.ai/pricing |
| (b) Free quota / credits | **None current.** Historical 200 req/day Early Access deleted (TEE access removed 2026-02-27; quota for non-TEE until 2026-03-15), replaced by $5 credit or 1 month Base; Chutes: *"No subsidies."* Paid plans: Base $3/mo 300 req/day; Plus $10/mo 2,000 req/day; Pro $20/mo 5,000 req/day | https://chutes.ai/news/community-announcement-february ; https://chutes.ai/news/from-volume-to-value-… ; https://chutes.ai/llms.txt |
| (c) JSON-schema / tools | **Yes** — every LLM in the live catalog advertises `json_mode`, `structured_outputs`, `tools` (+`reasoning`) | https://llm.chutes.ai/v1/models |
| (d) seed / determinism | **Yes** — `seed` in `supported_sampling_parameters` for every catalog LLM; chute default documented *"seed 42"* for one model | https://llm.chutes.ai/v1/models ; https://chutes.ai/docs/models/chutes-deepseek-ai-deepseek-v3-2-tee |
| (e) Context | Per-model 40K → 1.0M (live `context_length`) | https://llm.chutes.ai/v1/models |
| (f) Data use | **Zero content logging for public API inference; not used for model training; only metadata (timestamps, token counts) retained** | https://chutes.ai/privacy ; https://chutes.ai/terms |
| (g) Deprecation policy | No formal policy page; ToS: service/chute changes at any time; catalogue changes announced in news posts; model pages do 404 after removal | https://chutes.ai/terms ; https://chutes.ai/news/community-announcement-february |
| (h) OpenAI base URL | `https://llm.chutes.ai/v1` (management: `https://api.chutes.ai`); key prefix `cpk_` | https://chutes.ai/llms.txt ; https://chutes.ai/docs/guides/starter-guide |

### (a) Free-model IDs

- **None.** The live catalogue (fetched today, no API key required) lists 14 chat/LLM models, each with a positive `pricing.prompt`/`pricing.completion` in USD per token (https://llm.chutes.ai/v1/models). Chutes' own llms.txt: *"Live catalog as of Oct 6, 2026: 14 models."* (https://chutes.ai/llms.txt)
- Catalogue (live, 2026-10-06) with context and price/M tokens:
  - `deepseek-ai/DeepSeek-V3.2-TEE` — 131,072 ctx, $1.00 in / $1.00 out
  - `deepseek-ai/DeepSeek-V4-Flash-0731-TEE` — 1,048,576 ctx, $0.44 / $1.32
  - `google/gemma-4-31B-turbo-TEE` — 131,072 ctx, $0.12 / $0.37 (image in)
  - `zai-org/GLM-5.1-TEE` — 202,752 ctx, $0.98 / $3.08
  - `zai-org/GLM-5.2-TEE` — 1,048,576 ctx, $1.25 / $3.95
  - `moonshotai/Kimi-K2.6-TEE` — 262,144 ctx, $0.50 / $2.85 (image+video in)
  - `moonshotai/Kimi-K3-TEE` — 1,048,576 ctx, $3.00 / $15.00 (image+video in)
  - `Qwen/Qwen3-32B-TEE` — 40,960 ctx, $0.104 / $0.416
  - `Qwen/Qwen3-235B-A22B-Thinking-2507-TEE` — 262,144 ctx, $0.2989 / $1.1957
  - `Qwen/Qwen3.5-397B-A17B-TEE` — 262,144 ctx, $0.45 / $3.00
  - `Qwen/Qwen3.6-27B-TEE` — 262,144 ctx, $0.30 / $2.00
  - `Qwen/Qwen3.8-27B-TEE` — 262,144 ctx, $0.24 / $2.20
  - `unsloth/Mistral-Nemo-Instruct-2407-TEE` — 131,072 ctx, $0.0245 / $0.0978
  - `Nemotron-3-Nano-Omni-30B-TEE` — 131,072 ctx, $0.0245 / $0.0978
  - Open-weight families covered: DeepSeek, Qwen, Z.ai GLM, Moonshot Kimi, Mistral-Nemo, Google Gemma, NVIDIA Nemotron. **No Llama in the current catalogue** (`meta-llama` absent from `GET /v1/models`, fetched today).
- Every catalog entry has `confidential_compute: true` (TEE).

### (b) Free-tier quota / credits

- **There is no free tier today.** Chutes' paid plans are the only bundled allowances: llms.txt (2026-10-06): *"Base: $3/month — 300 bundled requests/day; Plus: $10/month — 2,000 bundled requests/day, 6% off pay-as-you-go rates beyond the quota; Pro: $20/month — 5,000 bundled requests/day, 10% off pay-as-you-go rates beyond the quota; Enterprise: custom pricing"* (https://chutes.ai/llms.txt). Pricing page confirms only the two upper tiers plus PAYG: *"Plus and Pro bundle a daily request quota with a discount on per-token rates"* (https://chutes.ai/pricing).
- **History of the free tier (decisive quotes):**
  - *"In the early days of Chutes (Subnet 64), we introduced an Early Access perk that provided 200 requests per day for free to participating users. … However, the program is no longer sustainable in its current form and will be discontinued."*
  - *"Access to TEE models will be removed for Early Access users. The 200 daily request quota will remain available for all non-TEE models until March 15, at which point the plan will be fully retired."*
  - Transition: *"One month of a Base subscription, or a $5 account credit."*
  - (https://chutes.ai/news/community-announcement-february, dated February 27, 2026)
  - Follow-up: *"~10B tokens/day from a 200 requests/day free quota offered to ~11,000 users. Average cost: ~$6/user/month. Revenue: zero." … "No subsidies. No underwater deals. No abuse vectors."* (https://chutes.ai/news/from-volume-to-value-building-a-sustainable-ai-inference-platform-2, March 20, 2026)
- Subscription safeguard (affects any bundled quota): *"all subscriptions will include a maximum usage allowance equal to 5× the equivalent Pay-As-You-Go value"* and *"the overall monthly benefit will remain capped at 5×"* (https://chutes.ai/news/community-announcement-february).
- Subscription plan rules today: *"Subscriptions are intended for casual, direct usage and not for use in large-scale automated inference, building production applications, or similar high-volume workloads. Acceptable use includes manual interactions and low-volume API usage. Any use cases that require high concurrency, high query volume, or other highly automated usage must use the PAYGO (pay-as-you-go) option."* (https://chutes.ai/terms) → relevant for a thesis artifact that drives the API programmatically.
- **Anonymous path:** llms.txt states requests without a valid Bearer token *"may hit the anonymous rate-limit path (HTTP `429`)"* (https://chutes.ai/llms.txt). **Numeric anonymous allowance is `[UNVERIFIED]` — no live page publishes an RPM/RPD number, and I found no documented per-account inference rate limit for the shared gateway.**
- Payment: *"Pay from a Bittensor wallet in TAO"* (https://chutes.ai/pricing); *"Chutes accepts 25+ payment methods via Stripe … and also takes TAO and Bittensor alpha tokens."* (https://chutes.ai/docs/guides/starter-guide) Connecting a Bittensor wallet is optional: *"Connecting a Bittensor wallet is optional; you do not need one to use the platform."* (same page) → the historical "free quota tied to holding TAO/subnet token" framing is **not** what governs access today (`[UNVERIFIED]` as any current mechanism; no live page ties free access to TAO holdings).

### (c) Structured output + tool calling

- Live catalogue per model flags `supported_features`. Every LLM entry today includes `json_mode`, `structured_outputs`, `tools`, `reasoning` (exception: the two cheapest models, `unsloth/Mistral-Nemo-Instruct-2407-TEE` and `Nemotron-3-Nano-Omni-30B-TEE`, returned only `max_model_len`/`confidential_compute` in the fetched JSON — **their feature arrays were absent in the live payload**, so treat those two as `[UNVERIFIED]` for structured output/tools). (https://llm.chutes.ai/v1/models)
- Docs: *"Chutes supports function calling through its optimized serving templates (vLLM and SGLang), enabling: Structured Data Extraction: Get JSON outputs guaranteed to match a schema…"*, with OpenAI-style `tools` + `tool_choice="auto"` example and `response_format={"type": "json_object"}`. (https://chutes.ai/docs/guides/agents-and-tools)
- DeepSeek-V3.2 model guide: *"Send OpenAI-style tools in your chat completion request via the gateway."* (https://chutes.ai/docs/models/chutes-deepseek-ai-deepseek-v3-2-tee)
- Serving: *"Serving is vLLM-based on the shared OpenAI-compatible gateway, exposing `/v1/chat/completions` and `/v1/completions` (both with streaming) plus `GET /v1/models`."* (DeepSeek-V3.2 guide)

### (d) seed + determinism

- Live catalogue lists `seed` inside `supported_sampling_parameters` for every full-featured LLM entry (alongside `temperature`, `top_p`, `top_k`, `repetition_penalty`, `frequency_penalty`, `presence_penalty`, `stop`). (https://llm.chutes.ai/v1/models)
- Model guide documents an actual default: *"Chute defaults (from the live endpoint definition): `temperature 0.7`, `max_tokens 1024`, `seed 42`, `stream true` on the streaming variant."* (https://chutes.ai/docs/models/chutes-deepseek-ai-deepseek-v3-2-tee) → `seed` is accepted and surfaced; **no page promises bit-identical determinism** (`[UNVERIFIED]` as a determinism guarantee; only parameter support is documented).

### (e) Context lengths

- Live `context_length` / `max_model_len` values per model (2026-10-06): 40,960 (`Qwen3-32B-TEE`); 131,072 (`DeepSeek-V3.2-TEE`, `gemma-4-31B-turbo-TEE`, `Mistral-Nemo-Instruct-2407-TEE`, `Nemotron-3-Nano-Omni-30B-TEE`); 202,752 (`GLM-5.1-TEE`); 262,144 (`Qwen3.5-397B-A17B-TEE`, `Qwen3.6-27B-TEE`, `Qwen3.8-27B-TEE`, `Kimi-K2.6-TEE`, `Qwen3-235B-A22B-Thinking-2507-TEE`); 1,048,576 (`DeepSeek-V4-Flash-0731-TEE`, `GLM-5.2-TEE`, `Kimi-K3-TEE`). (https://llm.chutes.ai/v1/models)
- Starter-guide snapshot (2026-08-17) shows the same order of magnitude; Chutes itself says *"Prices and the catalog move often. Check chutes.ai/pricing before you commit a workload."* (https://chutes.ai/docs/guides/starter-guide)

### (f) Data use on the free tier

- **No free tier exists, so no free-tier-specific clause.** General API guarantee (Privacy Policy, Last updated: 2026-03-16):
  - *"For public LLM inference, we do not log, store, or persist the content of your API requests or responses."*
  - *"We do not log, store, or persist the content of your API requests or responses. In standard API mode our servers may read request data transiently in memory to route and execute a request, but that content is never written to persistent storage. In end-to-end encryption mode, our servers cannot read the content at all."*
  - Collected instead: *"Timestamps, durations, token counts, model identifiers, and stop reasons… Performance metrics… Billing metadata… Short-lived rate-limit counters and operational metrics."*
  - Not collected: *"Prompt text or semantic request content… Model responses or generated artifacts… Conversation history for API usage… Persistent IP-address records tied to invocation content."*
  - (https://chutes.ai/privacy)
- Terms (Last updated: 2026-03-16): *"When you use our API for inference against public models hosted by Chutes, no content from your requests or responses is logged, stored, or persisted."* and *"No Training on Your Data: We do not use your API requests, responses, or application content to train AI models."* (https://chutes.ai/terms)
- Docs FAQ repeats: *"Customer data never used for training"* and *"No persistent storage of request/response data"* (https://chutes.ai/docs/help/faq).
- Caveat to carry into the thesis: *"Private and user-created chutes run arbitrary third-party code that we do not control"* — the guarantee is for public/system models (https://chutes.ai/privacy). Some catalog entries belong to other publishers (e.g. `vonkaiser/*`, `astroboi/*`, `score_test/*` chutes on https://chutes.ai/models), but all 14 LLM entries fetched today are owned by the `chutes` system user.
- Extra: all 14 LLM entries have `confidential_compute: true` (Intel TDX + NVIDIA PPCIE per https://chutes.ai/docs/core-concepts/security-architecture).

### (g) Deprecation / versioning policy

- **No dedicated deprecation/versioning policy page was found** in the 120-page docs corpus or on the legal pages (searched docs corpus and site; the only policy-shaped language is in the ToS).
- ToS: *"Service Changes: We may modify, suspend, or discontinue any part of our service at any time."*; *"Availability: … The Platform is provided on an "as-is" and "as-available" basis."* (https://chutes.ai/terms)
- Precedent of unannounced/per-plan removal: *"Several high-end frontier models will be removed from the Base subscription tier, including: GLM-5, Kimi K2.5, Qwen 3.5, MiniMax M2.5"* (https://chutes.ai/news/community-announcement-february). A currently published docs page for GLM-5 exists in the docs index (https://chutes.ai/docs/models/chutes-zai-org-glm-5-tee) while the corresponding model page now returns *"Model Not Found"* → catalogue pages churn without a versioning contract.
- llms.txt gives stable routing handles instead of pinned versions: `default`, `default:latency`, `modelA,modelB,modelC` failover strings (https://chutes.ai/llms.txt).
- Practical versioning: *"Always read live model IDs … from `GET https://llm.chutes.ai/v1/models` rather than copying them from examples."* (https://chutes.ai/llms.txt)

### (h) OpenAI-compatible base URL

- `base_url = "https://llm.chutes.ai/v1"`, key `cpk_...` sent as `Authorization: Bearer` (https://chutes.ai/llms.txt; https://chutes.ai/docs/guides/starter-guide: *"The API is OpenAI-compatible. Base URL: `llm.chutes.ai/v1`."*).
- Management API: `https://api.chutes.ai` (account, billing, keys, OAuth) (https://chutes.ai/llms.txt).
- Note: `X-API-Key` is **not** a supported inference auth scheme: *"Inference auth is the Bearer token only — `X-API-Key` is not a supported inference auth scheme"* (https://chutes.ai/llms.txt). (Docs for user-created chutes do show `X-API-Key` for `{username}-{chute}.chutes.ai` endpoints: https://chutes.ai/docs/getting-started/running-a-chute — applies to self-deployed chutes, not the shared gateway.)

---

## 3. Side-by-side (as of 2026-10-06)

| | Novita AI | Chutes |
|---|---|---|
| Free model IDs | none | none |
| Free credits | $100 sandbox-only (90 days, survey-gated); $10 referral both sides (cap $500); $1 voucher referenced in FAQ; startup program up to $10k | none (paid plans only: $3/$10/$20 per month with 300/2,000/5,000 requests/day) |
| Free-tier data use | No free tier; general ToS "Zero Data Retention" + "will not use your Content to train our own models" | No free tier; "we do not log, store, or persist the content of your API requests or responses"; "No Training on Your Data" |
| Structured output | `json_schema` (model-gated) | `structured_outputs` feature flag per model |
| Tool calling | `tools[].function.parameters` + `strict` | `tools` feature flag per model; vLLM/SGLang parsers |
| seed | accepted, "best effort" deterministic | accepted (`supported_sampling_parameters`), default 42 on one chute |
| Context | up to 1M | 40K–1M |
| Deprecation | dated notices + replacement models + migration table | no policy page; ToS "at any time"; catalogue churn |
| OpenAI base URL | `https://api.novita.ai/openai` (+`/v1/chat/completions`) | `https://llm.chutes.ai/v1` |
| Cheapest catalog LLM (per M tok, in/out) | DeepSeek OCR 2 $0.03/$0.03; DeepSeek V4 Flash $0.14/$0.28 | Mistral-Nemo-Instruct-2407-TEE / Nemotron-3-Nano-Omni-30B $0.0245/$0.0978 |

---

## 4. Not verified / gaps

1. **Novita: any general model-API signup credit amount today.** Only sources are (i) docs FAQ mentioning a "$1 credit voucher" (https://docs.novita.ai/guides/faq.md) and (ii) Novita's own Aug-2026 blog saying the free mechanism is referral-only. No live page states "every new account receives $X model-API credit". → `[UNVERIFIED]`.
2. **Novita: credit expiry for referral/$1 vouchers.** Not stated on any fetched page (voucher status lives behind login at https://novita.ai/billing). Only the *sandbox* promotion's 90 days is documented.
3. **Novita: RPM/TPM numbers are JS-rendered.** They exist only in `window.novitaRemoteData` on https://docs.novita.ai/guides/llm-rate-limits; I extracted them today with a real browser (values quoted above) but a static reader of the page sees no numbers. If the thesis needs citable static text, this is a re-verification risk.
4. **Novita: full list of models supporting Structured Outputs / function calling** is JS-rendered on https://docs.novita.ai/guides/llm-structured-outputs.md → `[UNVERIFIED]` as static content.
5. **Novita Trust Center retention ("6 months").** https://trust.novita.ai/faq returned an empty JS-only shell when fetched; the sentence came from a search snippet. → `[UNVERIFIED]` on a live readable page.
6. **Chutes: numeric rate limits for the shared gateway / anonymous path.** llms.txt mentions an "anonymous rate-limit path (HTTP 429)" but no RPM/RPD figure is published anywhere I could read (docs FAQ has no rate-limit section; grep of the full docs corpus found only example-code rate limiters). → `[UNVERIFIED]`.
7. **Chutes: pricing inconsistency between pages.** Live `GET https://llm.chutes.ai/v1/models` today shows some prices that differ from the starter guide's 2026-08-17 table (e.g. DeepSeek-V4-Flash-0731: live $0.44/$1.32 vs guide $0.14/$0.28; Kimi-K2.6: live $0.50/$2.85 vs guide $0.58/$3.40; GLM-5.1: live $0.98/$3.08 = guide; Qwen3-32B: live $0.104/$0.416 = guide). Treat the **live `/v1/models` endpoint as authoritative** (Chutes says so itself); the guide is a dated snapshot.
8. **Chutes: determinism guarantee.** `seed` support is documented; identical-output determinism is **not** claimed on any page. → `[UNVERIFIED]` beyond parameter acceptance.
9. **Chutes: the two cheapest models' feature flags.** `unsloth/Mistral-Nemo-Instruct-2407-TEE` and `Nemotron-3-Nano-Omni-30B-TEE` returned no `supported_features`/`supported_sampling_parameters` in the live payload, while the docs llms.txt lists them without feature tags (https://chutes.ai/llms.txt) → structured output/tools/seed support for these two is `[UNVERIFIED]`.
10. **Chutes: deprecation policy.** No page publishes a policy, notice period, or versioning contract → `[UNVERIFIED]`; only ToS "at any time" + observed removals.
11. **Chutes: TAO/subnet-token gating.** The historical "free quota tied to holding a Bittensor subnet token / TAO" is not confirmed anywhere on today's pages; the only TAO references are as a *payment* method (https://chutes.ai/pricing). No live page ties free access to token holding today.
12. **Novita: Llama/Mistral availability.** Llama 3.1 8B Instruct appears in docs/recommended and the catalogue; Mistral-family IDs beyond the listed set were not enumerated (the model library page ships 1,434 lines of listings; only the first 300 lines were inspected). Context/pricing for the tail of the catalogue is `[UNVERIFIED]`.
13. **Free-tier data-use differentiation:** neither provider publishes a *free-tier-specific* data clause; both rely on general terms. If the thesis needs "free tier = trained on / logged", the answer for both is: **no free tier exists**, and general policy says not trained on.
