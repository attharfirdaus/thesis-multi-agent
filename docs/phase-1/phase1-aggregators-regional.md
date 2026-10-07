# Phase 1 evidence — aggregators & non-US/regional hosts of free hosted open-weight LLMs

Access date for every source below: **2026-10-06** (all pages/models read live today). No recommendations are given; options and evidence only. `[UNVERIFIED]` = not confirmable on a live page today, with the reason stated.

Legend for the fields used per provider: **(a)** free open-weight model IDs today, **(b)** free quota + credit expiry, **(c)** JSON-schema/structured output + tool calling, **(d)** seed/temperature determinism, **(e)** context length, **(f)** data use on the free tier, **(g)** deprecation/versioning policy, **(h)** OpenAI-compatible base URL.

---

## 1. OpenRouter (aggregator, `:free` variants) — special attention item

### (a) Free model IDs available today
Source: `GET https://openrouter.ai/api/v1/models`, filtered to IDs ending `:free`, fetched 2026-10-06. **16 free variants** exist; all are priced `"0"` on prompt and completion (verified: a jq filter for `pricing.prompt != "0"` over the 16 returns nothing). Per-model endpoint = the single sponsoring provider serving the free variant (from `GET /api/v1/models/{id}/endpoints`).

| Free model ID | Free endpoint provider | Context | `structured_outputs` | `tools` | `seed` | expires | Open-weight evidence |
|---|---|---|---|---|---|---|---|
| `apodex/apodex-1.1-mini:free` | Novita | 262,144 | yes | yes | yes | – | not stated on OR page `[UNVERIFIED]` |
| `cohere/north-mini-code:free` | Cohere | 256,000 | – | yes | yes | – | "sparse mixture-of-experts model with 30B total parameters and 3B active" — no weights-release claim `[UNVERIFIED]` |
| `dots-studio/dots-3-note-preview:free` | AtlasCloud | 512,000 | yes | yes | – | **2026-12-31** | "Dots3-Note Preview is an open-weight mixture-of-experts model from Dots Studio" |
| `google/gemma-4-26b-a4b-it:free` | Google AI Studio | 262,144 | – | yes | yes | – | Gemma family, no explicit statement on OR page `[INFERENCE]` |
| `google/gemma-4-31b-it:free` | Google AI Studio | 262,144 | – | yes | yes | – | same `[INFERENCE]` |
| `inclusionai/ling-3.0-flash-sante:free` | Novita | 262,144 | – | yes | yes | – | "mixture-of-experts model from InclusionAI, 5.1B active … 124B total" — no weights-release claim `[UNVERIFIED]` |
| `liquid/lfm-2.5-2.6b:free` | Liquid | 65,536 | yes | yes | yes | – | compact reasoning model; no weights claim on OR page `[UNVERIFIED]` |
| `nvidia/nemotron-3.5-content-safety:free` | Nvidia | 128,000 | – | **no tools** | yes | – | "4B-parameter multimodal guardrail model … fine-tuned from Google Gemma-3-4B" |
| `nvidia/nemotron-3.5-lightning:free` | Nvidia | 1,000,000 | – | yes | yes | – | "open mixture-of-experts model from NVIDIA, 3B active … 30B total" |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | Nvidia | 256,000 | – | yes | yes | – | "30B-A3B open multimodal model" |
| `nvidia/nemotron-3-super-120b-a12b:free` | Nvidia | 262,144 | yes | yes | yes | – | "120B-parameter open hybrid MoE model" |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | Nvidia | 1,000,000 | – | yes | yes | – | "open frontier-reasoning and orchestration model … 55B active / 550B total (MoE)" |
| `poolside/laguna-s-2.1:free` | Poolside | 262,144 | – | yes | – | **2026-10-31** | not stated `[UNVERIFIED]` |
| `poolside/laguna-xs-2.1:free` | Poolside | 262,144 | – | yes | – | **2026-10-31** | not stated `[UNVERIFIED]` |
| `thinkingmachines/inkling:free` | Thinking Machines | 1,048,576 | – | yes | yes | – | "open-weight multimodal mixture-of-experts model … 41B active / 975B total" |
| `thinkingmachines/inkling-small:free` | Thinking Machines | 1,048,576 | – | yes | yes | – | "open-weight multimodal mixture-of-experts … 12B active / 276B total" |

Also free: the router slug `openrouter/free` — "automatically selects a free model at random from the available free models" and "filters for models that support the features your request needs, such as image understanding, tool calling, and structured outputs" (https://openrouter.ai/docs/guides/routing/routers/free, 2026-10-06).

Discrepancy to flag: several third-party posts (e.g. buldrr.com, remoteopenclaw.com, updated mid-2026) claim "29 free models". The live models API returns 16 `:free` entries today. Secondary sources only; treat as stale.

OpenRouter exposes **no open-weights flag** in the models API — a public feature request asks exactly for one: "OpenRouter already offers a simple, one-click toggle at Settings → Privacy that restricts all routing to Zero Data Retention (ZDR) endpoints only. I would love an equivalent toggle that restricts routing to open-weight models only." (https://github.com/OpenRouterTeam/docs/issues/2, 2026-10-06).

### (b) Free quota, credit expiry
Source: https://openrouter.ai/docs/api_reference/limits (2026-10-06) and https://openrouter.ai/docs/faq (2026-10-06).

> "If you have purchased at least 10 credits, your free model rate limit will be 1000 requests per day. Otherwise, you will be rate limited to 50 free model API requests per day."

Rate-limit table on the limits page: credits purchased < 10 → 20 requests/min, 50 requests/day; ≥ 10 → 20 requests/min, 1000 requests/day. Two documented nuances: "To absorb rounding and top-up fees, the higher daily ceiling is granted starting one credit below the table's threshold (currently 9 credits)"; and "Making additional accounts or API keys will not affect your rate limits, as we govern capacity globally."

Live per-account counter is exposed: `GET /api/v1/key` → `free_model_daily_requests: {used, limit, remaining}`, and `is_free_tier`.

New-user credit: FAQ says only "All new users receive a small free allowance to test out OpenRouter." — **amount not stated** `[UNVERIFIED]`. Credit expiry: "Per our terms, we reserve the right to expire unused credits after one year of purchase." (FAQ). Terms also state Promo Credits "are non-refundable and non-exchangeable" (https://openrouter.ai/terms §4.3, 2026-10-06).

### (c) Structured output + tool calling
Supported per endpoint, not per model. 4 of the 16 free models advertise `structured_outputs`: apodex-1.1-mini, dots-3-note-preview, lfm-2.5-2.6b, nemotron-3-super-120b-a12b (live `/endpoints` call, 2026-10-06). 15 of 16 advertise `tools` (nemotron-3.5-content-safety does not). Wire format: `response_format: {type: "json_schema", json_schema: {name, strict, schema}}` (https://openrouter.ai/docs/guides/features/structured-outputs, 2026-10-06). Doc caveat:

> "Enforcement varies by provider: some guarantee schema-conforming output, while others translate your schema into their own structured-output format or treat it as a strong hint, so exact compliance is not guaranteed on every endpoint."

Pin routing with `provider.require_parameters: true` to only hit endpoints that support the params.

### (d) Seed / temperature determinism
`seed` and `temperature` are listed in `supported_parameters` per model (see table). Docs (https://openrouter.ai/docs/api_reference/parameters, 2026-10-06):

> "If specified, the inferencing will sample deterministically, such that repeated requests with the same seed and parameters should return the same result. Determinism is not guaranteed for some models."

Also: "When a sampling parameter is absent from your request, OpenRouter omits it upstream rather than substituting a hardcoded value" — i.e. provider defaults apply.

### (e) Context length
Per-endpoint, shown in the table above: 65,536 (`lfm-2.5-2.6b`) up to 1,048,576 (`inkling`, `inkling-small`, `nemotron-3.5-lightning`, `nemotron-3-ultra`).

### (f) Data use on the free tier — key finding
OpenRouter itself, by default: "OpenRouter does not store your prompts or responses, *unless* you opt in to one or both of the following … **Private Input & Output Logging** … Off by default. Enable it in your Observability settings … **OpenRouter Use of Inputs/Outputs:** Allow OpenRouter to use your prompt and completion data to improve the product. In exchange, you receive a 1% discount … Off by default." (https://openrouter.ai/docs/guides/privacy/data-collection, 2026-10-06)

Account-level training control (this is the documented trade-off; there is no per-model `:free` toggle):

> "On your account settings page, you can set whether you would like to allow routing to providers that may train on your data (according to their own policies). **There are separate settings for paid and free models.** … If you opt out of training in your account settings, OpenRouter will not route to providers that train."
> — https://openrouter.ai/docs/guides/privacy/provider-logging, 2026-10-06

And: "Providers that do log, or where we have been unable to confirm their policy, will not be routed to unless the model training toggle is switched on in the privacy settings tab." (FAQ, 2026-10-06)

Provider-side flags for the exact endpoints serving the 16 free variants (live `GET https://openrouter.ai/api/frontend/v1/all-providers`, 2026-10-06; `retainsPrompts`/`retentionDays`/`training`):

| Free endpoint provider | Paths served (free variants) | Retains prompts | Retention | May train on prompts |
|---|---|---|---|---|
| NovitaAI | apodex-1.1-mini, ling-3.0-flash-sante | no → "Zero retention" | – | no |
| AtlasCloud | dots-3-note-preview | yes | unknown period | no |
| Cohere | north-mini-code | yes | 30 days | no |
| Google AI Studio | gemma-4-26b-a4b, gemma-4-31b | yes | 55 days | no |
| Liquid | lfm-2.5-2.6b | yes | unknown period | **yes** |
| Nvidia | 5 Nemotron free variants | yes | unknown period | **yes** |
| Poolside | laguna-s-2.1, laguna-xs-2.1 | yes | unknown period | no |
| Thinking Machines | inkling, inkling-small | yes | unknown period | **yes** |

So on the free tier: 9 of the 16 free variants are served by providers flagged "may train" (Liquid, Nvidia, Thinking Machines) unless the account opts out — and opting out removes those endpoints from routing.

Conservative fallback rule: "If OpenRouter is not able to establish or ascertain a clear policy for a provider or endpoint, we take a conservative stance and assume that the endpoint both retains and trains on data and mark it as such." (https://openrouter.ai/docs/guides/features/zdr, 2026-10-06)

**ZDR + free models**: enforcing Zero Data Retention is mutually exclusive with today's free list. `GET https://openrouter.ai/api/v1/endpoints/zdr` (2026-10-06) returns 0 endpoints whose model name ends with "(free)"; the ZDR provider list (AkashML, Cerebras, DeepInfra, Novita, Liquid, Google, Scaleway-like EU names are not listed, etc.) does not include the free-variant endpoints above.

Terms language putting the burden on the user: "Some Models may store or train on your Inputs for improving their own large language models and may allow you to opt-out of model training, as described in their Model Terms. Where possible, OpenRouter has opted out of model training with the Models it uses. OpenRouter strives to accurately represent the status of prompt logging and training for each Model on our Site. However, OpenRouter is not liable for errors or misrepresentations made in any Model Terms." (https://openrouter.ai/terms §6.1, 2026-10-06)

### (g) Deprecation / versioning
- Model level: each model carries an `expiration_date`; 3 of the 16 free variants carry one (laguna-s-2.1 and laguna-xs-2.1 → 2026-10-31; dots-3-note-preview → 2026-12-31).
- API level: "The OpenRouter API has a single stable version, `v1` … There are no version headers and no date-based version pinning." Non-breaking changes ship without notice; breaking changes are human-reviewed, changelogged, with migration notes. "Model availability is separate from API versioning: models are added and removed by providers independently." (https://openrouter.ai/docs/api_reference/versioning, 2026-10-06)

### (h) OpenAI-compatible base URL
`https://openrouter.ai/api/v1` — "drop-in replacement for OpenAI" (`/chat/completions`, `/completions`); https://openrouter.ai/docs/faq and https://openrouter.ai/docs/quickstart (2026-10-06).

Region/hosting: OpenRouter is a routing layer; inference happens at the upstream provider, no region pinning on the free tier. EU/US in-region routing exists only for paid plans: "On the Business and Enterprise plans, OpenRouter supports in-region routing in the EU and US … send a request to `https://eu.openrouter.ai` or `https://us.openrouter.ai`" (https://openrouter.ai/docs/guides/privacy/provider-logging, 2026-10-06).

---

## 2. Hugging Face Inference Providers

### (a) Free open-weight models today
HF's free tier is **credit-based, not model-gated**: the monthly credit applies to routed requests to any of the "200+ models from leading AI inference providers" (https://huggingface.co/docs/inference-providers/pricing, 2026-10-06). There is no published list of "free models"; the free credit is spent against whatever model you call. The OpenAI-compatible chat endpoint example uses `openai/gpt-oss-120b`; recommended chat models listed include Qwen/Qwen3-*, deepseek-ai/DeepSeek-R1, zai-org/GLM-4.5, meta-llama/Llama-3.1-8B-Instruct, openai/gpt-oss-120b (https://huggingface.co/docs/inference-providers/tasks/chat-completion, 2026-10-06). Note the two billing modes: routed requests consume credits; custom provider keys do not ("Monthly Credits: ❌ No - Credits don't apply", pricing page).

### (b) Free quota, expiry
> "Every Hugging Face user receives monthly credits to experiment with Inference Providers: Free Users — $0.10, subject to change — Inference Providers; PRO Users — $2.00; Team or Enterprise Organizations — $2.00 per seat." — https://huggingface.co/docs/inference-providers/pricing (2026-10-06)

Credits are "credited every month and applied automatically before any pay-as-you-go usage is billed"; whether unused credit rolls over is not stated `[UNVERIFIED]`. No request-per-minute/day figure is published: the old rate-limits page (https://huggingface.co/docs/inference-providers/rate-limits) **redirects to the pricing page today** (verified 2026-10-06), so no RPM/RPD number could be cited. After the credit is exhausted: "All users can continue using the API after exhausting their monthly credits by purchasing additional credits."

### (c) Structured output + tool calling
Yes, both. `response_format` accepts `json_schema` (with `schema` and `strict`) and `json_object`; `tools`/`tool_choice`/`tool_prompt` are documented request fields (https://huggingface.co/docs/inference-providers/tasks/chat-completion, 2026-10-06). Worked example uses `client.beta.chat.completions.parse(...)` against `https://router.huggingface.co/cerebras/v1` and states "Both approaches guarantee that your response will match the specified schema" (https://huggingface.co/docs/inference-providers/guides/structured-output, 2026-10-06). The guide also warns: "Structured outputs are a good use case for selecting a specific provider and model because you want to avoid incompatibility issues between the model, provider and the schema."

### (d) Seed / temperature
`seed` (integer) and `temperature` (0–2) are documented chat-completion request fields. The doc gives no determinism statement for `seed` `[UNVERIFIED]`; the API spec lists it bare.

### (e) Context length
Model-dependent; not documented per provider in the chat-completion page `[UNVERIFIED]` — must be read off individual model cards.

### (f) Data use on the free tier
No free-tier-specific training clause was found for HF Inference Providers (searched HF docs and terms, 2026-10-06). What exists is a platform-level statement, identical for free and paid:

> "Hugging Face does not store any user data for training purposes. We do not store the request body or response when routing requests through Hugging Face. Logs are kept for debugging purposes for up to 30 days, but no user data or tokens are stored."
> — https://huggingface.co/docs/inference-providers/security, 2026-10-06

The same page pushes data policy down to the upstream: "For more information on how your data is handled, please refer to the Data Security Policies of each provider." The Inference Services Supplemental Terms (Effective April 28, 2025; https://cdn-media.huggingface.co/landing/assets/Supplemental+Terms+-+Inference+Services.pdf, fetched 2026-10-06) contain no free-tier data-use clause; they state that HF processes data under the HF DPA and that limited analytics via PostHog are stored in the EU.

Routing choice therefore determines the actual data policy: providers in the HF catalogue include EU hosts (Scaleway, OVHcloud AI Endpoints) and non-EU hosts (Together, Fireworks, DeepInfra, Novita, Groq, Cerebras, Baseten, Cohere, Z.ai, Public AI …) — https://huggingface.co/docs/inference-providers/index (2026-10-06).

### (g) Deprecation / versioning
No published model-deprecation or versioning policy found in the Inference Providers docs or the Supplemental Terms `[UNVERIFIED]` — the terms describe service term/fees only, and model availability is per provider.

### (h) OpenAI-compatible base URL
`https://router.huggingface.co/v1` (OpenAI-compatible; "drop-in replacement for the OpenAI chat completions API"), with per-provider variants such as `https://router.huggingface.co/cerebras/v1`. Model IDs support policy suffixes `:fastest`, `:cheapest`, `:preferred`, or `:<provider>` (https://huggingface.co/docs/inference-providers/index, 2026-10-06). Auth: HF token with `inference.serverless.write`.

Region/hosting: HF Inc. (US) as the billing/router party; inference executed by the third-party provider chosen. No published region guarantee for free/routed requests `[UNVERIFIED]`.

---

## 3. Alibaba Cloud Model Studio (Bailian) / DashScope — Qwen free quota

Three deployment scopes exist: International, Global, China. **Free quota is granted only in the Singapore region**, only to models with service deployment scope "International".

### (a) Free model IDs today

| Family | Free-quota (1,000,000-token) IDs confirmed live |
|---|---|
| Qwen-Max | `qwen3.8-max`, `qwen3.8-max-0902`, `qwen3.7-max`, `qwen3.7-max-2026-06-08`, `qwen3.7-max-2026-05-20`, `qwen3.7-max-preview` |
| Qwen-Plus | `qwen3.7-plus`, `qwen3.7-plus-2026-05-26` (and other dated snapshots) |
| Qwen-Flash | `qwen3.7-flash`, `qwen3.7-flash-2026-07-15`, `qwen3.8-flash` |
| Qwen-Coder | `qwen3-coder-plus` (= `qwen3-coder-plus-2025-09-23`), `qwen3-coder-flash` (= `qwen3-coder-flash-2025-07-28`) |
| Qwen open-source, hosted | `qwen3.8-2.4t-a95b`, `qwen3.8-27b`; plus Qwen3.8/3.6/3.5/Qwen3/Qwen3-Coder "open-source" tables with free-quota columns |

Eligibility, verbatim: "Only models in the Singapore region with the service deployment scope set to International are eligible for a free quota. Models in other regions or with different service scopes are not eligible for a free quota." — https://www.alibabacloud.com/help/en/model-studio/new-free-quota (accessed 2026-10-06; page "Last Updated: Sep 22, 2026"). Pricing table: https://www.alibabacloud.com/help/en/model-studio/model-pricing (accessed 2026-10-06; "Last Updated: Sep 28, 2026").

### (b) Quota, expiry, rate limits
- **1,000,000 tokens per model**, input+output combined, independent per model: "Each model (such as qwen-plus, qwen3.6-plus, or qwen3.6-plus-2026-04-02) has its own independent free quota (typically 1,000,000 tokens). Quota cannot be merged or transferred across models."
- **90-day validity**: "The free quota is valid for 90 days, starting from the date you activate Alibaba Cloud Model Studio, the model is released, or your model request is approved (whichever is later)."
- Snapshot and mainline versions are separate quotas: "A snapshot version with a date suffix … and the latest version without a date suffix … are treated as two independent models, each with its own free quota."
- Free quota covers real-time invocation only (not batch, fine-tuning, deployment, OSS). Separate OAuth-style free quota: "OAuth authentication provides an independent free quota for model inference (2,000 calls per day)."
- Rate limits are account-level RPM/TPM aggregated across RAM users/workspaces/API keys; flagship models use dynamic TPM tiers by monthly spend (e.g. Singapore `qwen3.8-max` baseline 2,000,000 TPM, scaling to 5M/10M). Dated snapshots get lower RPM (e.g. `qwen3.7-max` 600 RPM/1M TPM vs snapshots 60 RPM).
Sources: new-free-quota, https://www.alibabacloud.com/help/en/model-studio/rate-limit, https://www.alibabacloud.com/help/en/model-studio/quota-management (2026-10-06).

### (c) Structured output + tools
- Two modes: JSON Object `{"type":"json_object"}` ("Most Qwen models") and **JSON Schema** `{"type":"json_schema",...,"strict":true}` — limited, verbatim: "Qwen3.7-Plus series, Qwen3.7-Flash series, Qwen3.7-Max series, Qwen3.8-Max series, and Qwen3.8-Flash series models." (https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output, 2026-10-06)
- Function calling: "Supported by all general-purpose models." (https://www.alibabacloud.com/help/en/model-studio/qwen-function-calling, 2026-10-06)

### (d) Seed / determinism
API accepts `seed`. Verbatim: "If you pass the same `seed` value in a call and other parameters remain unchanged, the model returns the same result **as much as possible**." → not documented as a hard guarantee. (https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-dashscope, 2026-10-06; "Last Updated: Sep 28, 2026")

### (e) Context
`qwen3.8-max`, `qwen3.8-max-0902`, `qwen3.8-flash`, `qwen3.7-plus`, `qwen3.7-flash`, `qwen3.7-max`: 1M; `qwen-long`: 10M; Qwen3.5 open-source: 256k. (https://www.alibabacloud.com/help/en/model-studio/text-generation-model, 2026-10-06)

### (f) Data use on the free tier
No free-vs-paid distinction in the data statement; it is global: "Alibaba Cloud Model Studio does not use customer business data to develop or improve models without explicit consent." (https://www.alibabacloud.com/help/en/model-studio/qwen-and-wan-training-data-disclosure, 2026-10-06) and "Alibaba Cloud protects data privacy and will never use your data for model training. All data transmitted when building applications or training models is encrypted." (https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio, 2026-10-06). Privacy notice: https://www.alibabacloud.com/help/en/model-studio/privacy-notice (SOC 2 noted). Free-tier-specific wording `[UNVERIFIED]` — no contrary carve-out found.

### (g) Deprecation / versioning
"For snapshot models, which are identified by a specific date in their name …, we issue a sunset notice 30 days before the official sunset date. For mainline models … we issue a sunset notice 3 months before." After notice, QPM/TPM "for retiring models will gradually decrease"; at retirement "API calls to the retired model will fail." (https://www.alibabacloud.com/help/en/model-studio/model-depreciation, 2026-10-06; "Last Updated: Sep 28, 2026")

### (h) OpenAI-compatible base URL
- International/Singapore: `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1`
- China (Beijing): `https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`
- Region variants also documented: `cn-hongkong`, `ap-northeast-1` (Tokyo), `eu-central-1` (Frankfurt), `us-east-1`.
- Legacy domains `https://dashscope-intl.aliyuncs.com` (International) and `https://dashscope.aliyuncs.com` (Beijing) still appear in the migration guidance, but the printed `/compatible-mode/v1` suffix for those legacy domains was not found on a live page today → `[UNVERIFIED]`.
Sources: https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio, https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-dashscope (2026-10-06).

Region/hosting for the free quota: **Singapore (ap-southeast-1)** only.

---

## 4. Z.ai / Zhipu AI (GLM)

Two platforms: international **Z.ai** (JINGSHENG HENGXING TECHNOLOGY PTE.LTD, Singapore) and China **BigModel** (bigmodel.cn). Keys are not shared.

### (a) Free model IDs today
Z.ai (international) pricing page, all four price columns "Free": `GLM-4.7-Flash` (text, 200K), `GLM-4.5-Flash` (text, 200K), `GLM-4.6V-Flash` (vision, 128K, "Free, Native Function Call Support"). Verbatim pricing rows: "| GLM-4.7-Flash | Free | Free | Free | Free |". GLM-4.7 guide: "Positioning: Lightweight, Completely Free".
BigModel (China) `免费` rows: `GLM-4.7-Flash` (200K), `GLM-4-Flash-250414` (128K), `GLM-Z1-Flash` (128K), `GLM-4.6V-Flash` (vision), `GLM-4V-Flash` (vision, 4K), `GLM-4.1V-Thinking-Flash` (vision, 64K), `CogView-3-Flash` (image), `CogVideoX-Flash` (video).
Sources: https://docs.z.ai/guides/overview/pricing, https://docs.z.ai/guides/overview/overview, https://docs.z.ai/guides/llm/glm-4.7, https://docs.bigmodel.cn/cn/guide/start/pricing (2026-10-06).

### (b) Quota, credit expiry, rate limits
- Z.ai: Flash models listed at $0 permanently; no token quota, no expiry stated. Whether the free tier is permanent `[UNVERIFIED]`.
- BigModel: new-user trial credit 平台体验金, verbatim: "除非在赠送时对有效期另有约定，通常平台体验金的使用有效期为自发放之日起 30 天" ("unless otherwise agreed at grant time, the trial credit is normally valid for 30 days from the date of issue"); non-withdrawable/transferable.
- Rate limits: BigModel documents concurrency-based limits only ("速率限制主要体现在：并发请求数限制…"), actual per-model numbers behind login → `[UNVERIFIED]`. Z.ai's rate-limit doc redirects to the JS-only app page `https://z.ai/manage-apikey/rate-limits` (no readable numbers) → `[UNVERIFIED]`.
Sources: https://docs.bigmodel.cn/cn/terms/service-agreement, https://docs.bigmodel.cn/cn/api/rate-limit, https://docs.z.ai/guides/overview/concept-param, https://z.ai/manage-apikey/rate-limits (2026-10-06).

### (c) Structured output + tools
JSON Object mode only: `response_format: {"type":"json_object"}`; schema validation is client-side. Both OpenAPI specs have enum `["text","json_object"]` and **0 matches for `json_schema`** (https://docs.z.ai/openapi.json, https://docs.bigmodel.cn/openapi/openapi-en.json, 2026-10-06). Function calling supported (`tools`; `tool_choice` "only supports `auto`"). (https://docs.z.ai/guides/capabilities/function-calling, 2026-10-06)

### (d) Seed / determinism
**No `seed` parameter**: 0 matches for `"seed"` in both OpenAPI specs; core-parameters reference lists only `do_sample`, `temperature`, `top_p`, `max_tokens`, `stream`, `thinking`, `reasoning_effort`. Determinism is via greedy decoding: "Set to `false` when you need reproducible, deterministic output." (https://docs.z.ai/guides/overview/concept-param, 2026-10-06)

### (e) Context
GLM-4.7-Flash 200K (max output 128K); GLM-4.5-Flash 200K (max 96K); GLM-4.6V-Flash 128K (max 32K); GLM-4-Flash-250414 128K; GLM-Z1-Flash 128K. (https://docs.z.ai/guides/overview/overview, https://docs.bigmodel.cn/cn/guide/start/pricing, 2026-10-06)

### (f) Data use — decisive ambiguity
- Individual users, Z.ai **reserves training rights** (§IV.3.a): "For individual users, we reserve the right to process any User Content to improve our existing Services and/or to develop new products and services … You hereby explicitly authorize and consent to our: (i) utilization and storage of User Content that does not constitute personal data for the purpose of developing and improving our machine learning and artificial intelligence technologies".
- API developers/enterprises, no training without opt-in (§IV.7): "For enterprises and developers using API Services, we will not use your User Content for developing or improving Services unless you explicitly agree to such use."
- API DPA: "The Company do not store any of the content the Customer or its End Users provide or generate while using our Services."
- Residual ambiguity: the free Flash models are reached with an API key, but §IV.7 names only "enterprises and developers"; a free API key is not explicitly assigned to either bucket on a live page. (https://docs.z.ai/legal-agreement/terms-of-use, "Last Update: April 14, 2026"; https://docs.z.ai/legal-agreement/privacy-policy, "Last Update: September 29, 2025"; both 2026-10-06)
- BigModel (China): "就您的数据，除为您提供服务所必需外，智谱不会进行任何未获授权的使用及披露"; storage "仅…最小必要范围内…且会进行必要的匿名化和加密处理"; privacy policy permits **anonymized** data use including "使用匿名数据进行机器学习或模型算法训练". Storage in mainland China: "目前我们不会跨境传输或存储您的个人信息". (https://docs.bigmodel.cn/cn/terms/service-agreement, https://docs.bigmodel.cn/cn/terms/privacy-policy, 最新版本生效日期 2025-05-20; 2026-10-06)

### (g) Deprecation / versioning
Not found on any live page today → `[UNVERIFIED]`. Neither docs index (https://docs.z.ai/llms.txt, https://docs.bigmodel.cn/llms.txt, 2026-10-06) lists a model-lifecycle page.

### (h) OpenAI-compatible base URL
- Z.ai international: `https://api.z.ai/api/paas/v4/`
- BigModel China: `https://open.bigmodel.cn/api/paas/v4/`
(https://docs.z.ai/guides/overview/quick-start, https://docs.bigmodel.cn/cn/guide/develop/openai/introduction, 2026-10-06)

Region/hosting: Z.ai international operates from Singapore; BigModel is hosted in mainland China with an explicit no-cross-border-transfer statement (quote above).

---

## 5. Baidu Qianfan (百度千帆)

Docs are Chinese-only (Gatsby SPAs; content read from the page's own `page-data.json` on `bce.bdstatic.com`). `intl.cloud.baidu.com` carries marketing only.

### (a) Free model IDs today
Authoritative page 新用户免费额度 (`Imi2rpirg`, page self-date **2025-11-17**, https://cloud.baidu.com/doc/qianfan/s/Imi2rpirg) lists **17 models × 1,000,000 free Tokens, 有效期 3个月**: ERNIE-4.5-Turbo-128K/32K/VL, ERNIE-X1-Turbo-32K, DeepSeek-R1, DeepSeek-R1-250528, DeepSeek-V3-250324, DeepSeek-V3.1-250821, DeepSeek-V3.1-Think-250821, Kimi-K2-Instruct, Qwen3-235B-A22B-Instruct-2507, Qwen3-30B-A3B-Instruct-2507, Qwen3-Coder-30B-A3B-Instruct, Qwen3-Coder-480B-A35B-Instruct, bge-large-en, bge-large-zh, qianfan-sug-8k.

**That page is stale.** Cross-checked against the live model list (`rmh4stp0j`, self-date **2026-09-16**) and the shutdown notice (`zmrykcisj`, 2026-07-24): only `ernie-4.5-turbo-128k`, `ernie-4.5-turbo-32k`, `ernie-4.5-turbo-vl`, `bge-large-en/zh` remain in the catalogue; ERNIE-X1-Turbo-32K, qianfan-sug-8k, the DeepSeek-R1/V3/V3.1 batch, Kimi-K2-Instruct and the Qwen3 (2025) batch are retired or absent. Which IDs currently receive free Tokens is `[UNVERIFIED]`. The historic "permanently free" ERNIE-Speed/Lite/Tiny tier is gone (listed as retired in the 2026-06-30/07-28 notice) — aggregator claims to the contrary are outdated.

### (b) Quota, expiry, rate limits
Verbatim from `Imi2rpirg`: "新用户免费额度仅支持抵扣预置模型服务在线推理（调用）消耗的Tokens，不支持抵扣批量推理（调用）消耗的Tokens。" and the grant table: **1,000,000 Tokens per model, 有效期 3个月**. No cash credit value published (aggregator "50元" claim not confirmed).
Per-model default flow control (live list `rmh4stp0j`, 2026-09-16): `ernie-4.5-turbo-128k` and `ernie-4.5-turbo-32k` 5000 RPM / 400,000 TPM; `ernie-4.5-turbo-vl` 1000 RPM / 200,000 TPM; `deepseek-v4-pro`/`v4.1-flash` and `glm-5.2`/`5.3` 60 RPM / 1,000,000 TPM; `ernie-5.0/5.1`, `qwen3.5-*` 60 RPM / 150,000–250,000 TPM. Response headers expose `X-Ratelimit-Limit-Requests`/`-Input-Tokens`/`-Output-Tokens`. Whether free Tokens carry extra limits `[UNVERIFIED]`.

### (c) Structured output + tools
`POST https://qianfan.baidubce.com/v2/chat/completions` accepts `response_format.type` ∈ {`json_object`, `text`, `json_schema`} (schema inline); doc note: "(2) 不支持以下模型：ERNIE X1 Turbo系列". `tools` + `tool_choice` (`none`/`auto`/`required`/named function) + `parallel_tool_calls` (default true). No legacy `functions`. (https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb, 2026-10-06)

### (d) Seed / determinism
`seed` accepted (0–2147483647). Verbatim: "如果指定，系统将尽最大努力进行确定性采样，以便使用相同seed和参数的重复请求返回相同的结果" — best-effort only. Not supported on ERNIE X1 Turbo series, Qwen2.5, Qianfan-Agent-Intent. (same API doc, 2026-10-06)

### (e) Context
ERNIE 4.5 Turbo 32k/128k → 32k/128k (max out 12288); ERNIE 4.5 Turbo VL → 128k (16,384); ERNIE 5.0/5.1 → 128k; DeepSeek-V4 / V4.1-flash → 1M; Qwen3.5 family → 256k; GLM-5.2/5.3 → 1M; Kimi-K2.6 → 256k. (live list, 2026-09-16)

### (f) Data use on the free tier
No free-tier-specific clause found. General user agreement (§5.1(6), effective 2026-01-09, https://cloud.baidu.com/doc/qianfan/s/Cmh4stmpy): "除执行您的服务要求外，我们不进行任何未获授权的使用及披露。为免疑义，我们不会使用您的输入和模型输出数据、上传的知识文档、数据集进行训练，也不会将您的数据集与任何第三方共享。" But §13.2 authorizes use "应用于服务性能优化、系统故障排查及风险控制管理等" and §4.11 authorizes compliance review "包括但不限于对输入和输出进行审查". The trial agreement 大模型技术体验服务协议 §1.3 (`jmh4stmn3`, 2025-10-29) allows Baidu to process data "在为您提供本合同所述服务及优化本合同所述服务效果的范围内". Whether free Tokens fall under that trial agreement is not stated → `[UNVERIFIED]`. Privacy policy §8 (2026-04-23): user owns business data; no unauthorized access. (all 2026-10-06)

### (g) Deprecation / versioning
模型版本升级及退役机制 (`zmh4stou3`, self-date **2026-09-24**): preview models "滚动升级不会提前通知用户"; undated mainline models roll with "提前1~2周发送通知"; dated versions "生命周期一般为3~6个月"; retirement announced "以短信、站内信等方式". Live list tags models "（即将下线）". (2026-10-06)

### (h) OpenAI-compatible base URL
Verbatim: "兼容 OpenAI 接口协议的Base URL：`https://qianfan.baidubce.com/v2`" (完整路径 `https://qianfan.baidubce.com/v2/chat/completions`); Anthropic-compatible base `https://qianfan.baidubce.com/anthropic`. (https://cloud.baidu.com/doc/qianfan/s/Smoghsq3g, self-date 2026-09-30, 2026-10-06)

Region/hosting: mainland China (Baidu Cloud); no cross-region option found.

---

## 6. Scaleway Generative APIs (Serverless)

### (a) Free models today
Credit-based, not model-gated: the free tier applies across the Serverless catalogue. Live catalogue (`supported-models`, self-date 2026-08-14) includes `glm-5.2`, `deepseek-v4-flash-0731`, `qwen3.8-27b`, `qwen3.6-35b-a3b`, `qwen3.5-397b-a17b`, `qwen3-235b-a22b-instruct-2507`, `qwen3-coder-30b-a3b-instruct`, `gemma-4-26b-a4b-it`, `gpt-oss-120b`, `llama-3.3-70b-instruct`, `mistral-medium-3.5-128b`, `mistral-small-3.2-24b-instruct-2506`, `pixtral-12b-2409`, `whisper-large-v3`, `bge-multilingual-gemma2`, `qwen3-embedding-8b`. (2026-10-06)

### (b) Quota, expiry, rate limits
Verbatim (pricing page, https://www.scaleway.com/en/pricing/model-as-a-service/, 2026-10-06): "Try out new models with our free tier: 1 million tokens and 60 minutes of audio transcription." FAQ: "The Free Tier allows you to process, without incurring any costs, up to: - 1,000,000 tokens for models billed by tokens - 60 minutes of audio transcription for models billed by audio minutes" and "The Free Tier is applied to the most expensive tokens first. The minimum billing unit is 1,000 tokens." Signup page: "Get started with **€100 free credit** when you create a **Business** account." Expiry not stated anywhere → `[UNVERIFIED]` (conditions of the €100 credit also unstated).
Rate limits (https://www.scaleway.com/en/docs/generative-apis/reference-content/rate-limits/, self-date 2026-04-24): per-model 200k–2,000k tokens/min (e.g. `glm-5.2` 200k → 1,000k), 300 req/min (600 with validated identity), 100 concurrent requests, 1800 audio sec/min (3600 validated). "Base limits apply if you registered a valid payment method."
Stale text to flag: the signup page FAQ still says "This service is totally free while in beta. Once in general availability stage, Generative APIs will be with a 'pay-as-you-go' pricing" — contradicts the current free-tier + per-token pricing on the same page.

### (c) Structured output + tools
Verbatim: "This mode enforces a strict schema format... Supports complex types and validation mechanisms as per the JSON schema specification, including nested schemas composition (`anyOf`, `allOf`, `oneOf` etc), `$ref`, `all` types, and regular expressions." Plus legacy `json_object`. "All LLMs in the Scaleway library support **Structured outputs** and **JSON mode**." Function calling: "All the [chat models] ... hosted by Scaleway support function calling." Only `function` tools (no `custom` tools); "Meta models do not support parallel tool calls." Unsupported params: `user`, `store`, `metadata`, `prompt_cache_key`, `web_search_options`. (https://www.scaleway.com/en/docs/generative-apis/how-to/use-structured-outputs/, https://www.scaleway.com/en/docs/generative-apis/how-to/use-function-calling/, 2026-10-06)

### (d) Seed / determinism
From the official OpenAPI schema (https://www.scaleway.com/en/developers/api/generative-apis/v1/schema.yml, 2026-10-06), verbatim: "Value which controls the randomness of the output to ensure determinism. When using the same seed value along with identical input and parameters, you should receive the same model response each time. This holds true even when temperature is set above 0. Note that fully deterministic output is not guaranteed over long periods of time (such as several months), as the inference model may be updated and optimized." Temperature: "does not affect request reproducibility (only affected by the `seed` parameter)".

### (e) Context
`glm-5.2` 256k (1M capable, preview-capped), `deepseek-v4-flash-0731` 256k (1M capable), `qwen3.8-27b` 256k, `qwen3.6-35b-a3b` 256k, `qwen3.5-397b-a17b` 250k, `gemma-4-26b-a4b-it` 256k, `gpt-oss-120b` 128k, `llama-3.3-70b-instruct` 100k, `mistral-medium-3.5-128b` 180k (1M capable), `pixtral-12b-2409` 128k. Max output is capped per model (e.g. 32k for qwen3.6/3.8/gpt-oss; 16k for qwen3.5-397b) and "you cannot increase the maximum number of output tokens beyond the limits for each model". (supported-models page, 2026-08-14)

### (f) Data use — strongest EU position of this group
Verbatim (https://www.scaleway.com/en/docs/generative-apis/reference-content/data-privacy/, self-date validation **2025-10-03**, 2026-10-06): "By default we apply a Zero Data Retention Policy, collecting only data required to provide the service reliably and securely." / "We do not collect, read, reuse, or analyze the content of your inputs, prompts, or outputs generated by the API. The only exception being when your traffic harms our service operations or your resource availability such as generating abnormal errors - like HTTP 500 errors - or may represent malicious activity. In this case, we may store temporarily the corresponding HTTP request content to identify and fix root cause issues or any security vulnerability." / "Your data is not used for training, retraining, or improving the base models." / "Your personal data may be stored in the following region: Paris, France." / "As a European company, Scaleway's AI services are not subject to extraterritorial laws such as the American Cloud Act." Exception data "stored for up to two weeks"; anonymized usage data up to 6 months. No free-tier carve-out — the policy does not distinguish paid vs free.

### (g) Deprecation / versioning
Verbatim (https://www.scaleway.com/en/docs/generative-apis/reference-content/model-lifecycle/, self-date 2026-04-24): "We guarantee support for new models in `Active` status for at least 8 months starting from their regional launch. Customers will receive a 3-month notice before any model is marked as End-of-Life (EOL)." Preview: "at least 1 month ... 1-month notice". Deprecated models keep working to their EOL date; traffic may be auto-redirected to a replacement. Live EOL dates include `pixtral-12b-2409` and `qwen3-coder-30b-a3b-instruct` 2026-10-01, `gemma-3-27b-it` 2026-08-01.

### (h) OpenAI-compatible base URL
`https://api.scaleway.ai/v1` (Quickstart, self-date 2026-04-16, 2026-10-06).

Region/hosting: **Paris, France** (OPCORE datacenter; API region `fr-par`) — FAQ: "All *Serverless models* are currently hosted in a secure data center located in Paris, France, operated by OPCORE ... we will continue to guarantee that *Serverless models* accessible through `api.scaleway.ai` remain hosted in Europe."

---

## 7. DeepInfra

### (a) Free models today
**None. DeepInfra has no free tier today.** No primary page lists free models or free quota; the pricing page requires payment up front:

> "You have to add a card or pre-pay or you won't be able to use our services. Pre-paid accounts draw down their balance as they go, and invoiced accounts are billed once at the beginning of the following month."
> — https://deepinfra.com/pricing (2026-10-06)

Catalog is 100% pay-as-you-go. Representative live IDs / context / $ per 1M in / out: `deepseek-ai/DeepSeek-V4-Flash-0731` 1024k $0.06/$0.18; `deepseek-ai/DeepSeek-V4-Flash` 1024k $0.09/$0.18; `Qwen/Qwen3.6-35B-A3B` 256k $0.10/$0.95; `Qwen/Qwen3-235B-A22B-Instruct-2507` 256k $0.09/$0.55; `meta-llama/Llama-3.3-70B-Instruct-Turbo` 128k $0.10/$0.32; `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` 128k $0.02/$0.04; `google/gemma-3-12b-it` 128k $0.05/$0.15; `microsoft/phi-4` 16k $0.07/$0.14 (all https://deepinfra.com/pricing, 2026-10-06).

Historic "~$1.80 / $5 signup credit": no DeepInfra-owned page states any signup credit today; aggregator claims are contradicted by the mandatory-card wording → `[UNVERIFIED]`.

### (b) Quota, credit expiry, rate limits
No free quota exists. Paid default: "Every account has a default limit of **200 concurrent requests per model**. If you query two different models simultaneously, you can handle 400 total concurrent requests (200 per model)." Excess → HTTP 429 `Rate limited` (https://docs.deepinfra.com/account/rate-limits, 2026-10-06).
The only free mechanism found is not self-serve — DeepStart: "DeepStart ~50,000,000,000 free tokens* … * at DeepSeek V4 Flash prices … **Credits expire 1 year after approval**"; eligibility "Have raised between 250K and 10M USD" and "Founded in the last 2 years" (https://deepinfra.com/deepstart, 2026-10-06).

### (c) Structured output + tools
Both: `json_object` and `json_schema` ("Enforces a strict output schema using JSON Schema…"), example uses `{"type":"json_schema","json_schema":{"name":…,"strict":true,"schema":{…}}}`; doc warning: "JSON mode can affect model alignment. When forced to produce structured output, some models are more likely to hallucinate values rather than say 'I don't know.'" Tool-calling matrix: single ✅, parallel "✅ (quality may vary)", `tool_choice` auto/none ✅, streaming ✅, nested calls ❌. (https://docs.deepinfra.com/chat/structured-outputs, https://docs.deepinfra.com/chat/tool-calling, 2026-10-06)

### (d) Seed / determinism
`seed` accepted, determinism explicitly disclaimed — live OpenAPI: "Seed for random number generator. If not provided, a random seed is used. **Determinism is not guaranteed.**" (https://api.deepinfra.com/openapi.json, 2026-10-06)

### (e) Context
Per model: 16k (`phi-4`) to 1024k (`DeepSeek-V4-Flash*`); `Llama-3.3-70B` 128k. Max output default: "the model's max context length minus input length or 65536, whichever is smaller" (OpenAPI, 2026-10-06).

### (f) Data use
> "We will not store, sell, or train using this data unless we have your explicit consent." — https://deepinfra.com/privacy, "Last modified: August 15th 2026" (2026-10-06)
> "We do not use data you submit to our APIs for training models, except when using Google or Anthropic models, where the receiving company's training policy applies." / "We do not log the content of your requests. We log only metadata useful for debugging: request ID, cost, sampling parameters." / "**Input data is not stored to disk** during inference — it exists only in memory while the request is being processed" — https://docs.deepinfra.com/account/data-privacy (2026-10-06)
Contract: "Provider will not sell Customer Data, and will not use Customer Data to train, fine-tune, or otherwise improve any model, except as necessary to provide the Services… Provider will not retain, store, or log any Customer Data submitted to or generated by the Services beyond the period strictly necessary to process and return the applicable request…" — https://deepinfra.com/terms (2026-10-06). Catalog exposes per-model `ZDR` badges. Human review: no statement either way → `[UNVERIFIED]`.

### (g) Deprecation / versioning
No policy page. Mechanism visible as product strings: "Due to low usage this model will be deprecated on {{date}}. Your inference requests are still working." / "Due to low usage this model has been replaced by {{replaced_by}}… they are redirected." (https://deepinfra.com/models payload, 2026-10-06). API versioning is first-class: `model` accepts "`MODEL_NAME:VERSION`, or `deploy_id:DEPLOY_ID`" (https://docs.deepinfra.com/chat/overview, 2026-10-06).

### (h) OpenAI-compatible base URL
`https://api.deepinfra.com/v1/openai` — "The only changes you need to make from your existing OpenAI code: 1. Set `base_url` … 3. Set `model` to a model from our catalog"; caveat "We may not be 100% compatible with all OpenAI parameters." (https://docs.deepinfra.com/chat/overview, 2026-10-06)

---

## 8. Vercel AI Gateway

### (a) Free models today
Docs: "The free tier includes a subset of models, not the full catalog. To see which models you can use with free credits, browse the Free Tier models." (https://vercel.com/docs/ai-gateway/pricing, `last_updated: 2026-09-08`, 2026-10-06)
Extraction method + caveat: the `/ai-gateway/models` page payload carries `availableToFreeTier` per entry — **233 of 417 entries are true (223 unique IDs)**; `?freeTier=true` does not filter server-side, and `GET https://ai-gateway.vercel.sh/v1/models` (411 models, fetched 2026-10-06) exposes **no** free-tier field. Free-tier-eligible open-weight IDs observed (subset): `meta/llama-3.3-70b`, `meta/llama-3.1-8b`, `meta/llama-3.1-70b`, `meta/llama-4-maverick`, `deepseek/deepseek-r1`, `deepseek/deepseek-v3.1`, `deepseek/deepseek-v3.1-terminus`, `deepseek/deepseek-v4-flash`, `openai/gpt-oss-20b`, `openai/gpt-oss-safeguard-20b`, `zai/glm-4.5-air`, `zai/glm-4.7-flash`, `mistral/mistral-small`, `mistral/mistral-nemo`, `mistral/ministral-8b`, `mistral/ministral-14b`, `alibaba/qwen3-coder`, `alibaba/qwen3-coder-30b-a3b`, `alibaba/qwen-3-14b`, `alibaba/qwen-3-32b`, `moonshotai/kimi-k2-thinking`, `moonshotai/kimi-k2.5`, `nvidia/nemotron-3-super-120b-a12b`, `nvidia/nemotron-3-nano-30b-a3b`, `google/gemma-4-26b-a4b-it`, `minimax/minimax-m2.1`. The same flag also marks closed-weight models (e.g. `anthropic/claude-opus-4.5`, `openai/gpt-5-mini`) → today's free tier is **not** limited to open weights.

### (b) Free credits, expiry, rate limits
> "Monthly credit | $5/month included" — https://vercel.com/docs/ai-gateway/pricing (2026-10-06)
> "Your free credits start when you make your first AI Gateway request." / "Once you purchase credits, your account transitions to the paid tier and the monthly free credit no longer applies." / "Free tier requests are also rate limited per model, with lower limits than the paid tier. If you exceed a limit, AI Gateway returns a `429` error…"
> "**Do AI Gateway Credits expire?** Yes. Purchased credits expire one year after purchase…" / "**Is the free tier a time-limited trial?** No. The free tier is a monthly included credit, not an expiring trial." — https://vercel.com/docs/ai-gateway/faq (`last_updated: 2026-09-13`, 2026-10-06)
Payment method may be required: FAQ error table lists "`403` with `customer_verification_required` — The team must add a valid payment method before using free credits". Free-tier numeric limits are deliberately unpublished: "Limits can change, so this page describes behavior rather than fixed numbers." (https://vercel.com/docs/ai-gateway/rate-limits, `last_updated: 2026-09-08`) → numeric ceiling `[UNVERIFIED]`.
Stale source flagged: the GA blog (2025-08-21) says "We don't restrict access to premium models" and "Vercel doesn't place any rate limits on your queries" — both superseded by the 2026-09 docs.

### (c) Structured output + tools
Structured output via AI SDK `Output.object({schema: z.object({…})})`; per-format reference pages exist for OpenAI Chat Completions, Responses, Anthropic Messages, OpenResponses. Tools: `tools: { … tool({inputSchema, execute}) }` with `stopWhen: isStepCount(5)`; caveat "Without it the request stops as soon as the tool runs, finishing with `finishReason: 'tool-calls'` and an empty `text`." Catalog flags: 228/411 `structured-output`, 253/411 `tool-use`; `openai/gpt-oss-120b` lists `response_format`,`structured_outputs`, while `meta/llama-3.3-70b` lists only `max_tokens, temperature, stop, tools, tool_choice, reasoning, include_reasoning`. (https://vercel.com/docs/ai-gateway/sdks-and-apis/ai-sdk + `GET https://ai-gateway.vercel.sh/v1/models`, 2026-10-06)

### (d) Seed / determinism
`seed` is **not** present in `supported_parameters` for any of the 411 catalog models, and no AI Gateway page read mentions seed/determinism `[UNVERIFIED]`. The underlying AI SDK documents "If set and supported by the model, calls will generate deterministic results." (https://ai-sdk.dev/docs/reference/ai-sdk-core/generate-text, 2026-10-06).

### (e) Context
Per model up to 1,000,000 (`deepseek/deepseek-v4-flash` 1M/max_tokens 384k; `alibaba/qwen3-coder-plus` 1M; `alibaba/qwen3-235b` 262,144; `mistral/mistral-small` 262,144; `nvidia/nemotron-3-super-120b-a12b` 256,000; `moonshotai/kimi-k2-thinking` 216,144; `meta/llama-3.3-70b` 128,000; `openai/gpt-oss-20b` 131,072). (catalog API, 2026-10-06)

### (f) Data use
> "**Does Vercel train on my prompts or store my data?** No. Vercel does not train on your prompts, and AI Gateway itself does not retain prompt or response content: it is deleted once the request completes." / "AI Gateway does not log the prompts or responses in your requests… routing attempt details are kept for 30 days" / "Vercel's own retention policy does not constrain providers, so enable these controls when you need a guarantee that covers the whole path." — https://vercel.com/docs/ai-gateway/faq (`last_updated: 2026-09-13`, 2026-10-06)
> "AI Gateway has a ZDR policy and does not retain prompts, outputs, or sensitive data. User data is immediately and permanently deleted after requests are completed." / "Zero data retention (ZDR) is available for **Pro and Enterprise users** on AI Gateway." / "If we do not know a provider's ZDR stance or have not yet established an agreement with them, they are treated as not being ZDR-compliant." — https://vercel.com/docs/ai-gateway/security-and-compliance/zdr (`last_updated: 2026-09-22`, 2026-10-06)
> "No training on prompt data is available to **all** AI Gateway users at no extra charge." / "If we do not know a provider's training data stance … we assume that they train on your data. If disallow prompt training is enabled on a request, it will not be routed through that provider." — https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training (`last_updated: 2026-09-10`, 2026-10-06)
Net effect: Vercel-side retention is tier-independent; `disallowPromptTraining` is available on the free tier; **provider-side ZDR enforcement is Pro/Enterprise only**. Catalog per-model `zdr`/`no_training` flags are `all`/`some`/`none`. Human review by Vercel: not mentioned → `[UNVERIFIED]`.

### (g) Deprecation / versioning
`[UNVERIFIED]` — no AI Gateway lifecycle/deprecation page exists in https://vercel.com/docs/sitemap.md (searched "deprecat/retire/sunset/lifecycle", 2026-10-06). Published instead: "Every model entry in `GET /v1/models` carries its provider release date in `released`" (FAQ). Dated slugs exist (`alibaba/qwen3.8-max-0902`, `deepseek/deepseek-v4-flash-0731`).

### (h) OpenAI-compatible base URL
`https://ai-gateway.vercel.sh/v1` (code samples: `new OpenAI({baseURL: 'https://ai-gateway.vercel.sh/v1'})`, `curl …/v1/chat/completions`); Anthropic Messages base `https://ai-gateway.vercel.sh` (no `/v1`); catalog `GET https://ai-gateway.vercel.sh/v1/models` (no auth required, verified 2026-10-06).

---

## 9. Novita AI

### (a) Free models today — **none**
The live catalogue prices every model above $0 per token; no free-tier models. Novita's own blog: "Novita AI's current serverless LLM API catalog does not list a model priced at $0 per token. Its free-tier mechanism is a referral program…" (https://blogs.novita.ai/free-llm-api-comparison-2026, published 2026-08-18, `meta-article:modified_time: 2026-09-07`). Catalogue checked live: https://novita.ai/models/llm, https://novita.ai/pricing (2026-10-06) — e.g. GLM 5.3 Flash $0.15/$0.50 per M, DeepSeek V4 Flash $0.14/$0.28 per M. Paid open-weight families present include DeepSeek V4.x, Qwen3.8, GLM 5.x, Kimi K2.x/K3, MiniMax M3, Llama 3.1 8B Instruct, Gemma 4, Ling-3.0 Flash.

### (b) Credits, expiry, rate limits
- Sandbox promotion only: "New users can complete a quick account setup survey to receive $100 in promotional credits for **eligible Novita Sandbox usage**. No credit card is required." / "Promotional credits are applied to eligible Novita Sandbox usage first…" (https://docs.novita.ai/guides/sandbox-pricing, 2026-10-06). Signup banner: "$100 in Sandbox credits, valid for 90 days" (https://novita.ai/user/register).
- Referral: "$10 in LLM API credits, up to $500 in total credits for a single referrer" (blog, 2026-10-06); expiry `[UNVERIFIED]`.
- A "$1 credit voucher" is referenced in docs FAQ ("Why did my $1 credit voucher disappear?") — eligibility/expiry today `[UNVERIFIED]` (https://docs.novita.ai/guides/faq, 2026-10-06).
- Rate limits are top-up-tier based (T1–T5, T1 = "Monthly top-ups did not exceed $50 in any of the last 3 calendar months"). The per-model RPM/TPM table is JS-rendered (`window.novitaRemoteData`, 206 rows); values extracted live today: T1 RPM 30 / T2 100 uniform across all rows; T3 200–1,000; T4 500–3,000; T5 1,000–6,000; TPM varies 2M–50M by model. A static reader of https://docs.novita.ai/guides/llm-rate-limits sees no numbers.
- Startup program up to $10k, "Venture-backed and Series B or earlier", not self-serve (https://startups.novita.ai/, 2026-10-06). Batch inference at "introductory 50% discount".

### (c) Structured output + tools
"Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema." Enum: `text`, `json_object`, `json_schema`. Tools: "only functions are supported as a tool", `function.parameters` as JSON Schema, `strict` "the model will follow the exact schema defined in the parameters field". (https://docs.novita.ai/api-reference/model-apis-llm-create-chat-completion, 2026-10-06) Structured Outputs is model-gated; the supported-model list is JS-rendered → full ID list `[UNVERIFIED]`.

### (d) Seed / determinism
"`seed` — If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result." (same API reference, 2026-10-06) — best effort, not guaranteed.

### (e) Context
Per model up to 1M: DeepSeek V4.1 Flash / V4 Pro / V4 Flash 1M; GLM 5.3 / 5.3 Flash / 5.2 1M; Kimi K3 1M; Qwen3.8 Flash 977K; MiniMax M3 977K; Kimi K2.7 Code 256K; Llama 3.1 8B 128K. (https://novita.ai/pricing, 2026-10-06)

### (f) Data use
No free tier exists, so no free-tier clause; general terms apply:
> ToS §10.2 (updated 2026-08-05): "By Default, Novita AI will not use your Content to train our own models or to improve the Services. We will not retain any Content for longer than is necessary to provide the Services to you. We have adopted a "Zero Data Retention" policy, which means that we will not… (i) log your Content for human review; or (ii) retain your Content beyond the time it takes to generate Output… Notwithstanding the foregoing, you agree that we have the right to apply automated safety screening tools to your Content as we deem appropriate…"
> Privacy Policy (effective/updated 2026-05-13): "The Personal Information will not be used for model training."
(https://novita.ai/legal/terms-of-service, https://novita.ai/legal/privacy-policy, 2026-10-06)
Trust Center snippet "Retained for 6 months for the purposes of billing, debugging, and security auditing." came from a search snippet only — https://trust.novita.ai/faq returned an empty JS shell → `[UNVERIFIED]`.

### (g) Deprecation / versioning
Dated public retirement notices with migration targets: "Novita retires the deepseek/deepseek-v4-flash large language model at 16:00 UTC on Oct 9, 2026. Migrate to deepseek/deepseek-v4.1-flash before the cutoff." (https://novita.ai/docs/changelog/28-09-26, 2026-10-06). Docs carry a standing migration table ("If you use → Switch to", https://docs.novita.ai/guides/llm-recommended, 2026-10-06). Contractual backstop with no notice commitment: ToS §6 "Novita AI reserves the right to add, modify, suspend, or remove any Model from the Service at any time".

### (h) OpenAI-compatible base URL
`https://api.novita.ai/openai` (chat: `https://api.novita.ai/openai/v1/chat/completions`), `Authorization: Bearer <API_KEY>` (https://docs.novita.ai/llms.txt, https://docs.novita.ai/guides/llm-api, 2026-10-06).

Region/hosting: not documented on the pages read `[UNVERIFIED]`.

---

## 10. Chutes (chutes.ai)

### (a) Free models today — **none**
Live catalogue (no key needed) lists 14 chat/LLM models, all with positive per-token prices; Chutes' own llms.txt: "Live catalog as of Oct 6, 2026: 14 models." (https://llm.chutes.ai/v1/models, https://chutes.ai/llms.txt, 2026-10-06). Models: `deepseek-ai/DeepSeek-V3.2-TEE` (131,072 ctx, $1.00/$1.00), `deepseek-ai/DeepSeek-V4-Flash-0731-TEE` (1,048,576, $0.44/$1.32), `google/gemma-4-31B-turbo-TEE` (131,072, $0.12/$0.37), `zai-org/GLM-5.1-TEE` (202,752, $0.98/$3.08), `zai-org/GLM-5.2-TEE` (1,048,576, $1.25/$3.95), `moonshotai/Kimi-K2.6-TEE` (262,144, $0.50/$2.85), `moonshotai/Kimi-K3-TEE` (1,048,576, $3.00/$15.00), `Qwen/Qwen3-32B-TEE` (40,960, $0.104/$0.416), `Qwen/Qwen3-235B-A22B-Thinking-2507-TEE` (262,144, $0.2989/$1.1957), `Qwen/Qwen3.5-397B-A17B-TEE` (262,144, $0.45/$3.00), `Qwen/Qwen3.6-27B-TEE`, `Qwen/Qwen3.8-27B-TEE` (both 262,144), `unsloth/Mistral-Nemo-Instruct-2407-TEE` (131,072, $0.0245/$0.0978), `Nemotron-3-Nano-Omni-30B-TEE` (131,072, $0.0245/$0.0978). No Llama in the current catalogue. All entries `confidential_compute: true` (TEE).

### (b) Quota / credits — free tier retired
> "In the early days of Chutes (Subnet 64), we introduced an Early Access perk that provided 200 requests per day for free to participating users… However, the program is no longer sustainable in its current form and will be discontinued." / "Access to TEE models will be removed for Early Access users. The 200 daily request quota will remain available for all non-TEE models until March 15, at which point the plan will be fully retired." / transition offer "One month of a Base subscription, or a $5 account credit." — https://chutes.ai/news/community-announcement-february (2026-02-27, 2026-10-06)
> "~10B tokens/day from a 200 requests/day free quota offered to ~11,000 users. Average cost: ~$6/user/month. Revenue: zero." / "No subsidies." — https://chutes.ai/news/from-volume-to-value-building-a-sustainable-ai-inference-platform-2 (2026-03-20)
Current paid plans: "Base: $3/month — 300 bundled requests/day; Plus: $10/month — 2,000 bundled requests/day…; Pro: $20/month — 5,000 bundled requests/day" (https://chutes.ai/llms.txt, 2026-10-06). Subscriptions also carry "a maximum usage allowance equal to 5× the equivalent Pay-As-You-Go value" and are "not for use in large-scale automated inference, building production applications" (https://chutes.ai/terms, 2026-10-06) — relevant if a thesis app calls programmatically. Anonymous Bearer-less requests "may hit the anonymous rate-limit path (HTTP `429`)" (llms.txt); numeric anonymous allowance `[UNVERIFIED]`. TAO appears only as a payment method today, not a gating mechanism `[UNVERIFIED]` for any current TAO-holding benefit.

### (c) Structured output + tools
Live per-model flags include `json_mode`, `structured_outputs`, `tools`, `reasoning` for every full catalogue entry (exception: `unsloth/Mistral-Nemo-Instruct-2407-TEE` and `Nemotron-3-Nano-Omni-30B-TEE` returned no feature arrays in the live payload → `[UNVERIFIED]`). Docs: "Chutes supports function calling through its optimized serving templates (vLLM and SGLang)… Get JSON outputs guaranteed to match a schema…" (https://chutes.ai/docs/guides/agents-and-tools, 2026-10-06)

### (d) Seed / determinism
`seed` is listed in `supported_sampling_parameters` for every full entry; one model guide documents "Chute defaults … `seed 42`". No page promises identical outputs → determinism `[UNVERIFIED]`; only parameter support is documented. (https://llm.chutes.ai/v1/models, https://chutes.ai/docs/models/chutes-deepseek-ai-deepseek-v3-2-tee, 2026-10-06)

### (e) Context
40,960 → 1,048,576 per model (see list in (a)). Chutes' own caution: "Prices and the catalog move often. Check chutes.ai/pricing before you commit a workload." (https://chutes.ai/docs/guides/starter-guide, 2026-10-06)

### (f) Data use
No free tier, so no free-tier clause. General API guarantees:
> Privacy Policy (last updated 2026-03-16): "For public LLM inference, we do not log, store, or persist the content of your API requests or responses." / "In standard API mode our servers may read request data transiently in memory to route and execute a request, but that content is never written to persistent storage." / Collected instead: "Timestamps, durations, token counts, model identifiers, and stop reasons…"
> Terms (last updated 2026-03-16): "When you use our API for inference against public models hosted by Chutes, no content from your requests or responses is logged, stored, or persisted." / "No Training on Your Data: We do not use your API requests, responses, or application content to train AI models."
(https://chutes.ai/privacy, https://chutes.ai/terms, 2026-10-06) Caveat: "Private and user-created chutes run arbitrary third-party code that we do not control" — the guarantee covers public/system models.

### (g) Deprecation / versioning
No policy page found in the docs corpus or legal pages → `[UNVERIFIED]`. ToS: "We may modify, suspend, or discontinue any part of our service at any time." Observed churn without contract: "Several high-end frontier models will be removed from the Base subscription tier, including: GLM-5, Kimi K2.5, Qwen 3.5, MiniMax M2.5" (news, 2026-02-27); a docs page for `chutes-zai-org-glm-5-tee` exists while the model page returns "Model Not Found". llms.txt advises: "Always read live model IDs … from `GET https://llm.chutes.ai/v1/models` rather than copying them from examples."

### (h) OpenAI-compatible base URL
`https://llm.chutes.ai/v1` (management API `https://api.chutes.ai`; key prefix `cpk_`, "Inference auth is the Bearer token only — `X-API-Key` is not a supported inference auth scheme"). (https://chutes.ai/llms.txt, https://chutes.ai/docs/guides/starter-guide, 2026-10-06)

Region/hosting: not documented on the pages read `[UNVERIFIED]`; serving described as TEE (Intel TDX + NVIDIA PPCIE) per https://chutes.ai/docs/core-concepts/security-architecture (2026-10-06).

---

## 11. AI Singapore SEA-LION

Steward: AI Singapore (AISG), "a national research programme funded by the National Research Foundation, Singapore and hosted by the National University of Singapore" (https://sea-lion.ai/terms-of-use/, "Last updated on 19th November 2024", 2026-10-06).

### (a) Models available today
87 models in the `aisingapore` HF org. Family/version table (https://sea-lion.ai/models, modified 2026-09-21; https://huggingface.co/aisingapore, 2026-10-06):
- v4.8 Nemotron, released Sep 2026: `Nemotron-SEA-LION-v4.8-120B-A12B`, `-30B-A3B` (+ `-Base`, `-GGUF`, `-FP8`, `-NVFP4`) — 262K ctx (docs: "8K (Base model), 256K").
- v4.5: `Gemma-SEA-LION-v4.5-E2B-IT` (128k), `Qwen-SEA-LION-v4.5-27B-IT` (+`-SpecDecoder`) (262k).
- v4: `Gemma-SEA-LION-v4-27B-IT`, `-VL`, `Gemma-SEA-LION-v4-4B-VL` (128k), `Qwen-SEA-LION-v4-32B-IT` (128k), `Qwen-SEA-LION-v4-4B-VL`, `Qwen-SEA-LION-v4-8B-VL` (256k), `Apertus-SEA-LION-v4-8B-IT` (65k).
- v3.5: `Llama-SEA-LION-v3.5-8B-R`, `-70B-R` (128K). v3: `Llama-SEA-LION-v3-8B(-IT)`, `-70B(-IT)` (128K), `Gemma-SEA-LION-v3-9B(-IT)` (8192). v2: `Llama-SEA-LION-v2-8B(-IT)` (8192).
- Safety/embedding: `Qwen-SEA-Guard-4B/8B`, `Llama-SEA-Guard-8B`, `Gemma-SEA-Guard-12B`, `SEA-LION-ModernBERT-Embedding-600M`, `SEA-LION-E5-Embedding-600M`.

IDs confirmed callable on the first-party free API (`https://api.sea-lion.ai/v1`) are documented by example only: `aisingapore/Qwen-SEA-LION-v4.5-27B-IT`, `aisingapore/Llama-SEA-LION-v3.5-70B-R`, `aisingapore/Gemma-SEA-LION-v4-27B-IT`, `aisingapore/Llama-SEA-LION-v3-70B-IT`, `aisingapore/Gemma-SEA-LION-v3-9B-IT`, `aisingapore/SEA-Guard`, `aisingapore/SEA-LION-ModernBERT-Embedding-600M` (https://docs.sea-lion.ai/guides/inferencing/api, 2026-10-06). The full list requires a key: `GET https://api.sea-lion.ai/v1/models` returns 401 unauthenticated (`{"error":{"message":"Authentication Error, No api key passed in.",...}}`) → which v4.8/v4.5 IDs are actually served today is `[UNVERIFIED]`.

Third-party hosts (confirmed via HF `?expand=inferenceProviderMapping`, 2026-10-06): featherless-ai serves 6 SEA-LION models (`Llama-SEA-LION-v3-70B-IT`, `v3-8B-IT`, `Gemma-SEA-LION-v3-9B-IT`, `Llama-SEA-LION-v3.5-8B-R`, `Llama-SEA-LION-v2-8B-IT`, `Gemma-SEA-LION-v4-27B-IT`); publicai serves 2 (`Gemma-SEA-LION-v4-27B-IT`, `Qwen-SEA-LION-v4-32B-IT`); Cloudflare Workers AI serves 1 (`@cf/aisingapore/gemma-sea-lion-v4-27b-it`). **NVIDIA NIM: not hosted** (0 SEA-LION entries in https://build.nvidia.com/models.md, 2026-10-06).

### (b) Free quota / credits
> "As of 04 Jun 2026, our rate limits is set to **10 requests per minute per user**." / "Only 1 API key is allowed to be created per user." / "Our free APIs are intended for proof-of-concept (POC) development and are rate-limited (10 requests per minute). They are not designed for production workloads." / "We are not able to raise the limits on the free POC tier."
(https://docs.sea-lion.ai/guides/inferencing/api; https://docs.sea-lion.ai/overview/readme/faq, 2026-10-06)
No daily quota, token quota, credit amount or key lifetime is published → `[UNVERIFIED]`; the FAQ only asks "My API key expired, or I am hitting timeouts. What should I do?" without stating a lifetime.
Other free hosts: Cloudflare Workers AI — "Our free allocation allows anyone to use a total of **10,000 Neurons per day at no charge**… All limits reset daily at 00:00 UTC." (https://developers.cloudflare.com/workers-ai/platform/pricing/, "Last updated Oct 1, 2026"); model rate $0.351/$0.555 per M tokens. PublicAI Gateway — "Every new user account receives **$2 of free starter credit**"; free tier "**100 requests/minute**" (https://platform.publicai.co/docs, https://platform.publicai.co/plans, footer "Last modified on October 6, 2026"); SEA-LION pricing there $0.20/$0.40 and $0.25/$0.50 per M tokens, "Country of Origin: Singapore". HF router route uses the HF free credit ($0.10/month) and Featherless has no free plan ("Chat $25/month", https://featherless.ai/pricing).

### (c) Structured output + tools
Tool calling: yes, model-dependent and documented with examples — Qwen-SEA-LION-v4.5-27B-IT supports native function calling (`tools`, `tool_choice:"auto"`, `finish_reason=="tool_calls"`); Llama-SEA-LION-v3-70B-IT "Fully supports OpenAI-style tool calling"; Gemma-SEA-LION-v4-27B-IT ignores `tools` unless `tool_choice` is forced (else text-parsed ```tool_code blocks); Llama-SEA-LION-v3.5-70B-R is "Reasoning model **without** tool calling capability" (https://docs.sea-lion.ai/guides/inferencing/api, https://docs.sea-lion.ai/guides/tool_calling, 2026-10-06). JSON-schema/`response_format` structured output on `api.sea-lion.ai`: **not documented** → `[UNVERIFIED]`. Cloudflare's model page lists `response_format` among params but no `tools`/`tool_choice`.

### (d) Seed / determinism
`seed` is not documented on any SEA-LION doc page (full-text grep of all 51 pages listed in https://docs.sea-lion.ai/llms.txt → no API `seed` parameter) → `[UNVERIFIED]`. Docs warn about response caching ("your API responses might have been cached ... set the `no-cache` flag to `true`"). Cloudflare's host documents `seed` (integer, min 1, max 9999999999): "**Random seed for reproducibility of the generation.**" (https://developers.cloudflare.com/workers-ai/models/gemma-sea-lion-v4-27b-it/, 2026-10-06).

### (e) Context
262,144 (Nemotron v4.8); 262k (Qwen v4.5 27B); 256k (Qwen v4 VL); 128k (Gemma v4/v4.5 27B, Llama v3/v3.5); 65k (Apertus v4 8B); 8192 (Gemma v3 9B, SEA-LION v2); embeddings 8k / 512. (https://sea-lion.ai/models + per-model docs pages, 2026-10-06)

### (f) Data use on the free tier
> ToU: "You retain ownership of the Content. **We may use the Content to provide, maintain, develop and improve our Services**, comply with applicable law, enforce our terms and policies and keep our Services safe." / "You hereby irrevocably and unconditionally agree that **we may monitor your use of the Services** to ensure the quality of the Service, Service improvement (where required) and compliance with the Terms." — https://sea-lion.ai/terms-of-use/ (Last updated 19 Nov 2024, 2026-10-06)
> Privacy Policy: "1.4 Log Data ... This Log Data includes information such as your IP address, browser type, ... **search terms**, and cookie information." / "2.1 ... any information you provide on our platform(s) ... **may remain even after you terminate your account.**" — https://sea-lion.ai/privacy-policy/ (Last updated 19 Nov 2024, 2026-10-06)
No sentence promises "we will not train on your prompts", and none says they do; no retention period and no hosting region for `api.sea-lion.ai` are published → `[UNVERIFIED]` for retention window and region.
Other hosts: Cloudflare — "**Cloudflare does not use your Customer Content to (1) train any AI models made available on Workers AI or (2) improve any Cloudflare or third-party services, and would not do so unless we received your explicit consent.**" (https://developers.cloudflare.com/workers-ai/platform/data-usage/, "Last updated Apr 21, 2026"). PublicAI — "We provide raw database copies that may include usernames, emails, and conversation content" to academic researchers; logs "stored for **no longer than 90 days**"; "No encryption at rest"; "**Localized data storage outside the US**" not offered; "Organizations or individuals requiring formal GDPR compliance documentation should not use our Service." (https://publicai.co/tc, 2026-10-06). Featherless: "Prompts stored | Never" (https://featherless.ai/pricing, 2026-10-06).

### (g) Deprecation / versioning
No policy page exists — full-text grep of all 51 doc pages for `deprecat|sunset|retire|EOL|end of life|archive` returned no relevant hits → `[UNVERIFIED]` (2026-10-06).

### (h) OpenAI-compatible base URLs
| Host | Base URL |
|---|---|
| AI Singapore first-party | `https://api.sea-lion.ai/v1` — "SEA-LION's API endpoints for chat are compatible with OpenAI's API and libraries." |
| Cloudflare Workers AI | `https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1` |
| PublicAI Gateway | `https://api.publicai.co/v1` (requires `User-Agent` header) |
| HF Inference Providers router | `https://router.huggingface.co/v1` |
| NVIDIA NIM | n/a (not hosted) |
(all 2026-10-06)

Licenses (HF metadata vs docs, contradictions recorded unresolved): `Nemotron-SEA-LION-v4.8-*` HF `mit` vs docs "License: Other (NOTICE.md)"; `Qwen-SEA-LION-v4.5-27B-IT` HF `mit` (+Qwen license link) vs docs "Apache-2.0"; `Apertus-SEA-LION-v4-8B-IT` HF `mit` vs docs "Apache-2.0"; `Gemma-SEA-LION-v4-27B-IT` `gemma` (Gemma Terms of Use, §3.1 flow-down + §3.2 Prohibited Use Policy); `Llama-SEA-LION-v3.5-*` `llama3.1` (700M-MAU clause). AISG FAQ: "Yes. SEA-LION is open-source and free to use, including for commercial purposes." (https://docs.sea-lion.ai/overview/readme/faq, 2026-10-06)

Region: AISG is Singapore-based; PublicAI shows "Country of Origin Singapore" for the hosted SEA-LION models. `api.sea-lion.ai` hosting region is not documented `[UNVERIFIED]`.

---

## 12. Sahabat-AI (Indosat Ooredoo Hutchison + GoTo)

Steward quote: ecosystem "co-initiated and co-developed by ... PT Indosat Tbk ("Indosat Ooredoo Hutchison" or "IOH")", with GoTo and AI Singapore as partners (https://sahabat-ai.com/documents/Sahabat-AI-Responsible-Use-Guide-v7.pdf, "Version April 2025", 2026-10-06).

### (a) Models today — weights only
HF org `Sahabat-AI` (https://huggingface.co/sahabat-ai redirects there), models mirrored under `Sahabat-AI/...` and `GoToCompany/...`:
| Model ID | Base | Context | License tag |
|---|---|---|---|
| `Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT` (= `GoToCompany/…`) | Llama 3.1 70B CPT + IT, released 2025-05-30 | 128k ("The model has a context length of 128k") | `llama3.1` |
| `Sahabat-AI/gemma2-9b-cpt-sahabatai-v1-instruct` / `-base` | Gemma-2 9B CPT | 8192 | `gemma` |
| `Sahabat-AI/llama3-8b-cpt-sahabatai-v1-instruct` / `-base` | Llama-3 8B CPT | 8192 | `llama3` |
Card languages: `en, id, jv, su, bbc (Batak Toba), ban (Balinese)`.

### (b) Free hosted API — **none**
`sahabat-ai.com` "Untuk Developers" offers only HF download + contact (`support@sahabat-ai.com`) — no API key, endpoint or quota. Host probes today: `https://api.sahabat-ai.com/v1/models` → 404; `…/v1/chat/completions` → 404; `https://api.sahabat-ai.id/v1/models` → connection failure; `https://llm.sahabat-ai.com/v1/models` → connection failure; `https://chat.sahabat-ai.com/v1/models` → 404. Only first-party consumer surface is the chat app `chat.sahabat-ai.com` (Flutter web + Firebase, login-gated). Only third-party serverless host found: HF Inference Providers → featherless-ai maps `Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT` (`status: live`), and Featherless has no free plan; the v1 8B/9B models have `inferenceProviderMapping: {}` (no provider). FriendliAI lists the 70B model as "Dedicated Endpoints"/"Container" only. Not in the NVIDIA NIM catalog, Cloudflare Workers AI, or PublicAI catalogs. An aggregator claim of a hosted API (recatools.com, page dated 30 Sep 2026) could not be substantiated on any primary page → `[UNVERIFIED]`. "Kupon Kredit GPU Merdeka" coupons exist for approved research proposals, but these are GPU compute coupons, not a model API. (all 2026-10-06)

### (c) Structured output / tools — **not documented**, no API exists `[UNVERIFIED]`. Model cards document plain Transformers generation only.

### (d) Seed / determinism — not documented for any hosted service; v1 cards list only `temperature`/`max_new_tokens` → `[UNVERIFIED]`.

### (e) Context — 128k (`Llama-Sahabat-AI-v2-70B-IT`); 8192 (v1 Gemma-2 9B and Llama-3 8B). Cards note a benchmark caveat: "VLLM caps the context size at 4096 tokens while HuggingFace was set to 8192 tokens."

### (f) Data use
Weights: no data-use restriction beyond base licenses. First-party chat service: **no privacy notice or data-use policy found** — `chat.sahabat-ai.com/privacy` → 404, `…/terms` → 404; the only policy document on the site is the Cookie Notice (https://sahabat-ai.com/documents/Sahabat-AI-Cookie-Policy-v2.pdf, "effective on 2 June 2025"): "We only use cookies that are strictly necessary for the operation or functionality of the Service." Whether prompts to the chat app are logged, retained, trained on, or human-reviewed is unstated → `[UNVERIFIED]`. The Responsible Use Guide sets model-level expectations for deployers only: "AI systems must ensure robust privacy and data protection mechanisms throughout their lifecycle ... such as Indonesia's Law No. 27 Year 2022 on Personal Data Protection".

### (g) Deprecation / versioning — none published; versioning by model name only (v1 = 8B/9B, v2 = 70B, May 2025) → `[UNVERIFIED]`.

### (h) OpenAI-compatible base URL — **none** (no endpoint exists; third-party serving via HF router `https://router.huggingface.co/v1` or FriendliAI dedicated endpoints is not a Sahabat-AI-operated host).

### Region / hosting — Indonesia, documented
> GoTo press release, 02 June 2025: "All data and GPU infrastructure used to serve the model are stored within Indonesian territory or on users' own servers, ensuring compliance with national data regulations." Indosat runs it on "GPU Merdeka, our sovereign AI cloud", "deployed by Indosat's Lintasarta". (https://www.gotocompany.com/en/news/press/sahabat-ai-gets-smarter-indosat-and-goto-launch-new-70-billion-parameter-model-with-multilingual-chat-service, 2026-10-06)
Site (rendered): "Data yang Disimpan Secara Lokal — Semua data Anda tetap berada di Indonesia".

### Indonesian-language focus (documented)
Site: "Sahabat-AI adalah sebuah koleksi Large Language Models (LLMs) open-source yang dirancang khusus untuk Bahasa Indonesia dan bahasa daerah"; GoTo press: "can now operate across **five local languages: Bahasa Indonesia, Javanese, Sundanese, Balinese and Bataknese** in addition to a number of international languages." Site renders the 70B license as "**Lisensi Open-Source**" (marketing shorthand — the Hub license is the Llama 3.1 Community License, which contains the 700M-MAU clause).

---

## 13. Moonshot AI / Kimi (Kimi Open Platform)

Contracting entity: "Moonshot AI PTE. LTD.", Singapore law (https://platform.kimi.ai/docs/agreement/modeluse, page "Last Updated: July 30th, 2026", 2026-10-06). Doc host `platform.moonshot.ai` **301-redirects to** `platform.kimi.ai` (verified via HTTP headers today).

### (a) Free models today — **none**
> "The Kimi API Open Platform uses pay-as-you-go billing with no subscription plan." — https://platform.kimi.ai/docs/guide/product-plans (2026-10-06)
Available (paid) models (https://platform.kimi.ai/docs/models, 2026-10-06): `kimi-k3` (1M ctx, "2.8 trillion parameters, native visual understanding"), `kimi-k2.7-code` / `kimi-k2.7-code-highspeed` (256k), `kimi-k2.6` (256k, text+image+video). Prices: kimi-k3 $3.00/M in, $15.00/M out; kimi-k2.x $0.95/M in, $4.00/M out (https://platform.kimi.ai/docs/pricing/chat).

### (b) Entry cost, credits, rate limits
> "To prevent abuse, you need to recharge at least \$1 to start using, and when your cumulative recharge reaches \$5, you will receive a \$5 voucher." — https://platform.kimi.ai/docs/pricing/limits (2026-10-06)
Tier0 (the $1 entry tier): concurrency 1, RMB 3 RPM, TPM 500,000, TPD 1,500,000, web-search QPS 1; Tier1 ($10) → RPM 100, TPM 2M, unlimited TPD; Tier5 ($3,000) → RPM 300/TPM 5M. "Vouchers do not count towards the cumulative recharge total." New-user vouchers exist but are restricted: "Kimi K3 requires available balance in your account; vouchers granted from new-user verification cannot be used for Kimi K3." (https://platform.kimi.ai/docs/guide/open-code, 2026-10-06). **Voucher amount/expiry `[UNVERIFIED]`** — no live page states the signup voucher value; the ¥15/$1 trial credit could not be confirmed anywhere live. Billing split: "Account usage is now deducted at a uniform ratio of 50% cash and 50% vouchers."

### (c) Structured output + tools
`response_format`: `json_object` and `json_schema` with `strict: true` and an "MFJS (Moonshot Flavored JSON Schema)" profile. Model caveats: "`kimi-k3` reliably supports Structured Output, including nested objects, arrays, and `anyOf`." / "`kimi-k2.6` occasionally behaves unstably with complex schemas; for example, `$ref` may return a Markdown code block". Tools: `tools` + `tool_choice`, but "`tool_choice: "required"` is supported only by `kimi-k3`; kimi-k2.6 and kimi-k2.7-code do not support `required` and return an error if it is passed". (https://platform.kimi.ai/docs/guide/response_format, https://platform.kimi.ai/docs/api/models-overview, 2026-10-06)

### (d) Seed / determinism
**No `seed` parameter exists** — full-text scan of the complete docs bundle (https://platform.kimi.ai/docs/llms-full.txt, 772 KB, fetched today) returns zero occurrences of `seed`. Sampling knobs are locked: `kimi-k3` and `kimi-k2.7-code` fix `temperature` at 1.0, `top_p` at 0.95, `n`=1; "**Fixed** means the parameter cannot be modified: passing any other value returns an error, so do not pass it explicitly." → API-level reproducibility is not offered. (https://platform.kimi.ai/docs/api/models-overview, 2026-10-06)

### (e) Context
`kimi-k3` 1,048,576; `kimi-k2.7-code`, `-highspeed`, `kimi-k2.6` 262,144. (https://platform.kimi.ai/docs/pricing/chat, 2026-10-06)

### (f) Data use
> ToS §4 (Last Updated July 30th, 2026): "We may use Content to provide, maintain, develop, support, and improve the Services... Customer who requires restrictions on the use of Customer Content for training or improving Moonshot AI models may contact Moonshot AI to discuss available enterprise arrangements or separate written agreements. **Unless otherwise expressly agreed in writing, Customer Content may be used for the foregoing purposes.**" — https://platform.kimi.ai/docs/agreement/modeluse
> ZDR page: "By default, the Kimi Open Platform does not use **enterprise** customer data to train models." / "ZDR is available on request to enterprise customers." — https://platform.kimi.ai/docs/guide/zero-data-retention
> Privacy policy: "To Improve and Develop Our Services: … This includes training and refining our underlying technology, such as machine learning models and algorithms." — https://platform.kimi.ai/docs/agreement/userprivacy
(all 2026-10-06). No free-tier clause exists because there is no free tier.

### (g) Deprecation / versioning
No policy document; dated notices in the model list: `kimi-k2.5` "officially discontinued on **August 31, 2026**"; `moonshot-v1` series **August 31, 2026**; `kimi-k2` series **May 25, 2026**; `kimi-latest` **January 28, 2026**; `kimi-thinking-preview` **November 11, 2025**. **No minimum advance-notice period is documented** → `[UNVERIFIED]`. (https://platform.kimi.ai/docs/models, 2026-10-06)

### (h) OpenAI-compatible base URL
`https://api.moonshot.ai/v1` (`/chat/completions`); Anthropic-format base `https://api.moonshot.ai/anthropic`. "API Keys from `platform.kimi.ai` and `platform.kimi.com` are completely independent." (https://platform.kimi.ai/docs/api/overview, 2026-10-06)

Region/hosting: Singapore entity (contracting party); `platform.kimi.ai` vs `platform.kimi.com` keys isolated, "Global edition" launched May 2025. The China platform (`platform.moonshot.cn` / `api.moonshot.cn`) exists only indirectly (Moonshot email domain `moonshot.cn`); its current status/quotas/data policy `[UNVERIFIED]` (not fetched).

---

## 14. ByteDance Volcano Engine — Ark (mainland-China site; Chinese-only docs)

Retrieval note: `www.volcengine.com/docs/...` is JS-only; content was read from the site's own docs API (`https://docs.volcengine.com/api/doc/getDocDetail?type=online&LibraryCode=ark&DocumentCode=<code>`), which returns the same `MDContent` the page renders. Doc "UpdatedTime" stamps are quoted per page.

### (a) Free model IDs
Free quota is per model, for accounts that have **not** activated the model service (https://www.volcengine.com/docs/ark/free-inference-quota, UpdatedTime 2026-08-24, 2026-10-06). From the product page table (https://www.volcengine.com/product/ark, 2026-10-06) — **500,000 tokens (50万) free per model**: text `Doubao-Seed-2.1-pro`, `Doubao-Seed-2.1-turbo`, `Doubao-Seed-Evolving`, `Doubao-Seed-Character`; embeddings `Doubao-embedding-vision`; plus image/voice/web-search allowances (Seedream 5.0-lite 50 images, 4.5/4.0 200 images; TTS 5,000 chars; ASR 20 hours; web plugin 20,000 calls/month). **Hosted open-weight models (DeepSeek-V4.x, GLM-5.x, Qwen, Llama) are NOT in the free-quota table** → no documented free quota for them on the CN site `[UNVERIFIED]`.
Meaning of "free": "每个模型提供一定额度的免费调用量，免费额度消耗完后可在开通管理页中开通模型，并继续付费使用" (https://www.volcengine.com/docs/ark/activation-management, UpdatedTime 2026-09-30).

### (b) Quota mechanics, expiry, rate limits
> "免费额度仅适用于抵扣 **按 token 后付费产生的在线推理费用**，不能抵扣使用各类插件、知识库等产生的费用。" / "免费推理额度，不同模型分别计算，主账号下共享" / "免费推理额度，基础模型和精调后模型共享" (https://www.volcengine.com/docs/ark/free-inference-quota, 2026-10-06)
Batch inference and fine-tuning cannot consume the free quota; cache storage fees are not offset. 安心体验模式 (Free Tokens Only): "您调用推理 API 时仅消耗平台赠送的 50w token 免费额度，接近免费额度后服务将暂停，避免产生额外费用"; eligibility = account "未开通过模型服务"; "**once disabled it cannot be re-enabled**" (https://www.volcengine.com/docs/ark/free-tokens-only-mode, UpdatedTime 2026-09-30).
**Expiry of the 500k inference quota `[UNVERIFIED]`** — no validity period is stated on either page. (The "有效期 2 年" figure belongs to the separate Managed Agents welcome pack: https://www.volcengine.com/docs/ark/model-service-pricing.)
Alternative free-token source — 协作奖励计划 (Data Collaboration Rewards): "调用已获授权的推理接入点，每日将采集每个模型不超过500万tokens的推理数据，并于次日发放有效期为30天的等量免费资源包" (https://www.volcengine.com/docs/ark/collaboration-reward-program, UpdatedTime 2026-09-21) — i.e. up to 5M tokens/day of free resource packs in exchange for daily collection of your inference data.
Per-model rate limits (https://www.volcengine.com/docs/ark/model-list, UpdatedTime 2026-09-28): e.g. `doubao-seed-2-1-pro-260915` max RPM 500 / TPM 1,000,000; `doubao-seed-2-1-lite-260915` max RPM 30,000 / TPM 5,000,000.

### (c) Structured output + tools
`response_format` ∈ {`text`, `json_object`, `json_schema` (with `strict`)} — **beta**: "该能力尚在 beta 阶段，受资源与平台负载影响，服务可用性可能随访问情况产生波动，请谨慎在生产环境使用。" Not supported with TPM 保障包 (https://www.volcengine.com/docs/ark/structured-output-beta, UpdatedTime 2026-09-22). Function calling: `tools` (`tools.function.name/description/parameters/strict`) (https://www.volcengine.com/docs/ark/function-calling, UpdatedTime 2026-09-22; chat API doc UpdatedTime 2026-09-24).

### (d) Seed / determinism
**No `seed` parameter** — the Chat API parameter reference contains no `seed` field and no "seed" string except in model names. Determinism is only described for `top_p`: "取值越大生成的随机性越高，取值越低生成的确定性越高。" `temperature` default 1.0, `top_p` default 0.7, with model-specific pins (some seed-2.0 models pin `top_p` to 0.95 and ignore manual values). (https://www.volcengine.com/docs/ark/chat-api, 2026-10-06)

### (e) Context
`doubao-seed-evolving`, `doubao-seed-2-1-pro-260915`, `-lite-260915` 1024k; `doubao-seed-2-1-pro-260628`/`-turbo-260628` 256k; `deepseek-v4-1-flash-260910` 1024k; `glm-5-3-flash-260828` 1024k. (model list, 2026-09-28)

### (f) Data use — the decisive free/paid mechanic
> 豆包模型服务协议 §四 (UpdatedTime 2026-09-18): "4.1 除非您单独同意，本服务将不使用您提交给服务或使用服务输出的内容训练、重新训练或改进基础模型。您单独同意的情况包括：4.1.1 同意火山引擎的《数据授权使用协议》；或 4.1.2 参与火山引擎协作奖励计划…" / "4.2 为履行法定合规要求，火山引擎有权采取技术手段对您使用本服务的行为及信息进行审查，包括但不限于…自动化过滤审核…" — https://www.volcengine.com/docs/ark/doubao-model-service-agreement
i.e. default = no training; opting into the Data Authorization Agreement **or** the rewards program turns training ON — and the rewards program is exactly how the extra free daily tokens are obtained.
> 数据授权使用协议: "2.1 授权目的：…开发机器学习、人工智能相关技术和模型的优化、开发、使用、学术理论研究及发表等目的。" / "2.3 授权期限：… **授权期限为 永久**。" — https://www.volcengine.com/docs/ark/volcengine-data-authorization-agreement (2026-10-06)
Rewards-program safety claims: "无授权不采集：当您从未授权、撤回授权，或者本计划终止时，您的数据不会被采集"; withdrawal is possible at any time. Retention window on the CN site: not found in text (security whitepaper is a PDF/images only) → `[UNVERIFIED]`.

### (g) Deprecation / versioning
> "当某个模型确定下线计划时，我们会通过短信、站内信等方式发布通知，请及时关注。" (https://www.volcengine.com/docs/ark/model-deprecation-notice, UpdatedTime 2026-09-30)
Explicit per-batch lifecycle: 第十批 — 启动&通知 2026-09-22 10:00 (UTC+8), EOM (模型停止新购) 2026-09-24 10:00, EOS (模型服务下线) **2026-11-24 14:00**, with an early EOS **2026-10-22 14:00** for `doubao-seed-2-0-lite-260215` and `-mini-260215`; unmigrated endpoints auto-migrated or shut down. Models already flagged `即将下线` include `doubao-seed-2-0-pro-260215`, `deepseek-v4-pro-260425`.

### (h) OpenAI-compatible base URL
> "数据面 API：https://ark.cn\-beijing.volces.com/api/v3" / "管控面 API：https://ark.cn\-beijing.volcengineapi.com/" — https://www.volcengine.com/docs/ark/base-url-and-authentication (UpdatedTime 2026-06-23, 2026-10-06). Auth `Authorization: Bearer $ARK_API_KEY`; the Coding Plan uses a different base URL (warned in the same doc).

Region/hosting: mainland China (Beijing endpoint); CN docs Chinese-only.

---

## 15. BytePlus ModelArk (ByteDance international, `byteplus.com`)

Same Ark stack, overseas regions and English docs.

### (a)/(b) Free quota
> "Get started with **500,000 free tokens for every Large Language Model** and 2,000,000 free tokens for every vision model. Enterprise customers can unlock even greater value with our exclusive partnership program, receiving 5 million tokens…" — https://www.byteplus.com/en/product/modelark (2026-10-06)
Free-LLM list (500k each): `Dola-Seed-2.0-lite`, `-mini`, `-pro`, `-Code`, `ByteDance-Seed-1.8`, `Skylark-pro`, **`DeepSeek-V4-pro`**, **`DeepSeek-V4-flash`**, **`DeepSeek-V3.2`**, `ByteDance-Seed-1.6`, `-flash` — i.e. on the international platform open-weight DeepSeek models *do* carry 500k free tokens, unlike the CN site. Free Tokens Only mode: "calls to the inference API consume only the 500k free tokens granted by the platform. When the free quota is nearly exhausted, the service will be automatically paused" (https://docs.byteplus.com/en/docs/ModelArk/free-tokens-only-mode). T&C: "with a value of 500,000 (Five Hundred Thousand) tokens per Model"; "This offer is redeemable only once per BytePlus account."; "The Free-Token Package may have a validity period, which can be viewed in the…" → validity `[UNVERIFIED]`. Promotion: "Each model can enjoy a 50% discount on usage of up to 1 billion tokens. The 50% discount will apply for 14 days (336 hours)." Rewards alternative: "Ongoing Benefit: Enjoy 5,000,000 tokens free every day!" with daily packages capped at that day's consumption of the enrolled model. (all 2026-10-06)

### (c)/(d) Structured output + tools; seed
`response_format` with `json_schema`/`strict` and `tools` are in the Chat API parameter list (https://docs.byteplus.com/en/docs/ModelArk/chat-api, 2026-10-06); model list flags "Tool use"/"Structured output" plus per-model Max RPM/TPM. **No `seed` parameter** (checked the full parameter reference) → seed-based reproducibility not offered.

### (e) Context
`dola-seed-2-1-turbo-260628` 256K; `seed-2-0-lite-260428` 256K; 1024K-class models include `deepseek-v4-1-flash`, `glm-5-3-flash` (model list, 2026-10-06).

### (f) Data use
> "Without the customer's prior authorization, BytePlus ModelArk will neither interfere with the data processing nor use Customer Data for its own model training." / "BytePlus ModelArk service may store your Customer Data for content safety purposes; **input and output triggered by the filter are retained for 180 days in Malaysia.**" / Data centers: "Malaysia, Indonesia, and/or the EU/EEA" — https://docs.byteplus.com/en/docs/ModelArk/BytePlus_ModelArk_Data_Processing (Published Time Tue, 28 Jul 2026, 2026-10-06)
Rewards program overrides this by opt-in: "The Input and Output submitted or generated through your selected Campaign endpoints within the Daily Maximum Token Amount limit (the 'Authorized Data') **will be permanently used to provide, maintain, develop or improve our model services or the underlying technologies**…"; withdrawal: "the right and license you grant hereunder should continue in effect after such withdrawal or termination." (https://docs.byteplus.com/en/docs/ModelArk/collaboration-reward-program, 2026-10-06)

### (g) Deprecation / versioning
> "Notifications will be issued at least 30 calendar days before the model is officially deactivated." — https://docs.byteplus.com/en/docs/ModelArk/1350667 (Last Updated September 10, 2026, 2026-10-06)
Timetable: First Notification Date → Deprecation Date → Deactivation Date; 4th batch 2026-09-08 → 2026-09-15 → **2026-11-11**; "starting from the First Notification Date, quotas for deprecated models will be gradually reduced."

### (h) OpenAI-compatible base URL
> "Data plane API: `https://ark.ap-southeast.bytepluses.com/api/v3`" — https://docs.byteplus.com/en/docs/ModelArk/1298459 (2026-10-06)

Region/hosting: "Malaysia, Indonesia, and/or the EU/EEA" (data-processing doc quote above); content-safety-filtered I/O retained 180 days **in Malaysia**.

---

## Closing table — one row per provider (all data fetched 2026-10-06)

| Provider | Free open-weight models today | Free quota | Data use on the free tier | JSON-schema structured output | Tool calling | `seed` | OpenAI-compatible base URL | Region / hosting |
|---|---|---|---|---|---|---|---|---|
| **OpenRouter** (§1) | 16 `:free` variants (gemma-4 ×2, nemotron ×5, inkling ×2, lfm-2.5, dots-3, apodex-1.1, ling-3.0, north-mini-code, laguna ×2) + `openrouter/free` router | 20 RPM; 50 req/day, or 1,000 req/day once ≥10 credits purchased (higher ceiling applied from 9) | OpenRouter itself no prompt storage by default (two opt-ins); per-endpoint provider flags decide: 9/16 free variants served by providers flagged **may train** (Liquid, Nvidia, Thinking Machines). Account setting "allow routing to providers that may train" is **separate for free vs paid models**; opting out removes those endpoints. **0 of the 16 free endpoints are ZDR-eligible** | Yes on 4 of 16 free models (`apodex-1.1-mini`, `dots-3-note-preview`, `lfm-2.5-2.6b`, `nemotron-3-super-120b-a12b`); `response_format.json_schema` | Yes on 15 of 16 (not `nemotron-3.5-content-safety`) | Yes on 13 of 16, documented best-effort ("Determinism is not guaranteed for some models") | `https://openrouter.ai/api/v1` | Routing layer; inference at upstream provider. EU/US in-region routing only on Business/Enterprise plans (`eu.openrouter.ai`, `us.openrouter.ai`) |
| **HF Inference Providers** (§2) | Credit-based, no model gating (200+ routed models) | $0.10/month (free accounts), $2.00 PRO/seat; monthly reset; purchased credits 1-year expiry on Vercel-style terms ≠ HF (HF: not stated) | "Hugging Face does not store any user data for training purposes. We do not store the request body or response when routing requests through Hugging Face. Logs are kept for debugging purposes for up to 30 days"; upstream provider policies govern | Yes — `response_format` `json_schema`/`json_object`; "Both approaches guarantee that your response will match the specified schema" | Yes (`tools`, `tool_choice`, `tool_prompt`) | `seed` accepted; determinism not documented | `https://router.huggingface.co/v1` (per-provider: `…/cerebras/v1`) | HF Inc. (US) as router/billing; execution at partner incl. EU hosts (Scaleway, OVHcloud) and non-EU hosts |
| **Alibaba Model Studio** (§3) | Qwen free-quota IDs (mostly not open-weight): `qwen3.8-max`, `qwen3.8-flash`, `qwen3.7-plus/max/flash` (+ dated snapshots), `qwen3-coder-plus/flash`, hosted open-source `qwen3.8-2.4t-a95b`, `qwen3.8-27b` | 1,000,000 tokens **per model** (in+out combined), 90-day validity; Singapore/international scope only; OAuth path 2,000 calls/day | "does not use customer business data to develop or improve models without explicit consent"; "will never use your data for model training" — no free-tier carve-out found | Yes, limited set: "Qwen3.7-Plus/Flash/Max, Qwen3.8-Max/Flash series"; `json_object` on most models | Yes — "Supported by all general-purpose models." | `seed` accepted; "returns the same result **as much as possible**" | Intl `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1`; CN `…cn-beijing…compatible-mode/v1` (legacy dashscope paths `[UNVERIFIED]`) | Singapore (free quota) / Beijing; also HK, Tokyo, Frankfurt, US-Virginia endpoints documented |
| **Z.ai / Zhipu GLM** (§4) | Z.ai: `GLM-4.7-Flash`, `GLM-4.5-Flash`, `GLM-4.6V-Flash`. BigModel: same + `GLM-4-Flash-250414`, `GLM-Z1-Flash`, `GLM-4V-Flash`, `GLM-4.1V-Thinking-Flash`, `CogView-3-Flash`, `CogVideoX-Flash` | Z.ai: listed permanently $0, no quota/expiry stated. BigModel: new-user trial credit, "normally valid for 30 days" | Z.ai §IV.7 (API/devs): "we will not use your User Content for developing or improving Services unless you explicitly agree"; DPA: "do not store any of the content"; **but** §IV.3.a (individual users) explicitly authorizes training → free-key bucket ambiguous. BigModel: no unauthorized use; anonymized data may be used for "机器学习或模型算法训练"; storage stays in mainland China, "目前我们不会跨境传输或存储您的个人信息" | **No `json_schema`** — `json_object` only (0 matches in both OpenAPI specs) | Yes (`tools`; `tool_choice` "only supports `auto`") | **No `seed`** parameter in either spec; determinism via `do_sample=false` | Z.ai `https://api.z.ai/api/paas/v4/`; BigModel `https://open.bigmodel.cn/api/paas/v4/` | Z.ai = Singapore entity; BigModel = mainland China (no cross-border transfer) |
| **Baidu Qianfan** (§5) | Free-quota page (stale, 2025-11-17) lists 17 model IDs; only `ernie-4.5-turbo-128k/-32k/-vl` + `bge-large-en/zh` still in the live catalogue | 1,000,000 tokens/model, 开户后 3 months, online inference only; per-model RPM/TPM (ernie-4.5-turbo-128k 5000 RPM / 400k TPM) | "我们不会使用您的输入和模型输出数据、上传的知识文档、数据集进行训练" (§5.1(6)) but §13.2 authorizes "服务性能优化、系统故障排查及风险控制管理" and §4.11 compliance review "包括但不限于对输入和输出进行审查"; trial agreement allows processing "在…及优化本合同所述服务效果的范围内" → which agreement covers free tokens `[UNVERIFIED]` | Yes — `response_format` {`json_object`,`text`,`json_schema`} (not ERNIE X1 Turbo) | Yes — `tools`, `tool_choice`, `parallel_tool_calls` | `seed` accepted, "尽最大努力进行确定性采样" (best effort) | `https://qianfan.baidubce.com/v2` (Anthropic-compat `…/anthropic`) | Mainland China |
| **Scaleway Generative APIs** (§6) | Credit applies across Serverless catalogue: `glm-5.2`, `deepseek-v4-flash-0731`, `qwen3.8-27b`, `qwen3.6-35b-a3b`, `qwen3.5-397b-a17b`, `gemma-4-26b-a4b-it`, `gpt-oss-120b`, `llama-3.3-70b-instruct`, `mistral-medium-3.5-128b`, `mistral-small-3.2-24b`, `pixtral-12b`, `qwen3-235b-a22b-instruct-2507`, `qwen3-coder-30b-a3b`, `whisper-large-v3`, embeddings | "1 million tokens and 60 minutes of audio transcription"; €100 credit for Business accounts; expiry not stated | "By default we apply a Zero Data Retention Policy" / "We do not collect, read, reuse, or analyze the content of your inputs, prompts, or outputs" (narrow exception: service-harming traffic, ≤2 weeks) / "Your data is not used for training, retraining, or improving the base models." No free-tier carve-out | Yes — strict `json_schema` ("nested schemas … `anyOf`, `allOf`, `oneOf`, `$ref`, regex") + legacy `json_object`; "All LLMs in the Scaleway library support Structured outputs" | Yes — "All the [chat models] … hosted by Scaleway support function calling" (Meta models: no parallel tool calls) | Yes — "same seed … same model response each time … even when temperature is set above 0"; long-term determinism not guaranteed | `https://api.scaleway.ai/v1` | **Paris, France** (OPCORE; region `fr-par`); "not subject to extraterritorial laws such as the American Cloud Act" |
| **DeepInfra** (§7) | **None — no free tier**; card/prepay mandatory | No free credit; DeepStart (not self-serve) 50B tokens, "Credits expire 1 year after approval"; paid 200 concurrent requests/model | "will not store, sell, or train using this data unless we have your explicit consent"; "We do not log the content of your requests"; "Input data is not stored to disk during inference" | Yes — strict `json_schema` (+ `json_object`) | Yes (single/parallel/streaming; nested calls ❌) | Yes but "Determinism is not guaranteed." | `https://api.deepinfra.com/v1/openai` | Not stated on pages read `[UNVERIFIED]` |
| **Vercel AI Gateway** (§8) | ~223 free-tier-eligible model IDs (233/417 catalogue entries, incl. closed-weight ones) — e.g. `meta/llama-3.3-70b`, `deepseek/deepseek-v4-flash`, `openai/gpt-oss-20b`, `zai/glm-4.5-air`, `mistral/mistral-small`, `nvidia/nemotron-3-super-120b-a12b`, `google/gemma-4-26b-a4b-it` | $5/month included, starts at first request, ends permanently after the first credit purchase; purchased credits expire 1 year; per-model 429s, numbers unpublished | "Vercel does not train on your prompts, and AI Gateway itself does not retain prompt or response content: it is deleted once the request completes." / "AI Gateway does not log the prompts or responses"; **ZDR = Pro/Enterprise only**; "No training on prompt data is available to all AI Gateway users at no extra charge" | Yes — `Output.object`/Zod; 228/411 models tagged structured-output | Yes — 253/411 models tagged tool-use | Not in any model's `supported_parameters`; undocumented `[UNVERIFIED]` | `https://ai-gateway.vercel.sh/v1` | Vercel (US); upstream provider unconstrained by Vercel's retention policy |
| **Novita AI** (§9) | **None** — no $0/token model; "does not list a model priced at $0 per token" | $100 credits **Sandbox-only**, 90 days, survey-gated; $10 referral both sides (cap $500); $1 voucher referenced in FAQ; startup program ≤$10k | No free tier; ToS §10.2 "By Default, Novita AI will not use your Content to train our own models… We have adopted a "Zero Data Retention" policy" (automated safety screening reserved); "The Personal Information will not be used for model training." | Yes — `response_format.json_schema` (model-gated) | Yes — `tools[].function.parameters` + `strict` | Yes — "best effort to sample deterministically" | `https://api.novita.ai/openai` | Not documented on pages read `[UNVERIFIED]` |
| **Chutes** (§10) | **None** — 14 paid models (DeepSeek/Qwen/GLM/Kimi/Mistral-Nemo/Gemma-4/Nemotron), no Llama | **Free tier retired**: 200 req/day Early Access ended (TEE access removed 2026-02-27; non-TEE quota until 2026-03-15) → "$5 credit or 1 month Base"; "No subsidies." Paid: $3/$10/$20 per month (300/2,000/5,000 req/day). Anonymous Bearer-less path exists, numbers `[UNVERIFIED]` | No free tier; "For public LLM inference, we do not log, store, or persist the content of your API requests or responses"; "No Training on Your Data" | Yes — `structured_outputs` flag on every full catalogue entry | Yes — `tools` flag; vLLM/SGLang parsers | Yes (`supported_sampling_parameters`; one chute default `seed 42`); determinism not promised | `https://llm.chutes.ai/v1` | Not documented `[UNVERIFIED]`; all catalogue entries TEE (`confidential_compute: true`) |
| **AI Singapore SEA-LION** (§11) | First-party free API: `Qwen-SEA-LION-v4.5-27B-IT`, `Llama-SEA-LION-v3.5-70B-R`, `Gemma-SEA-LION-v4-27B-IT`, `Llama-SEA-LION-v3-70B-IT`, `Gemma-SEA-LION-v3-9B-IT`, `SEA-Guard`, `SEA-LION-ModernBERT-Embedding-600M` (documented examples; full list needs a key) | "our rate limits is set to **10 requests per minute per user**" (as of 04 Jun 2026), 1 key/user, POC only; no daily quota/credit/expiry published. Cloudflare host: 10,000 Neurons/day free; PublicAI host: $2 starter credit, free tier 100 RPM | ToU: "We may use the Content to provide, maintain, develop and improve our Services"; "we may monitor your use of the Services"; no no-training promise, no retention period, no region stated. Cloudflare host: "does not use your Customer Content to (1) train any AI models … or (2) improve any … services". PublicAI host: raw logs incl. usernames/emails/chats shared with academic researchers; logs ≤90 days; no encryption at rest; no non-US localised storage | **Not documented** on `api.sea-lion.ai` → `[UNVERIFIED]` (Cloudflare host lists `response_format`) | Yes, model-dependent (Qwen v4.5-27B native tool calls; Llama v3-70B "Fully supports OpenAI-style tool calling"; Gemma v4-27B text-parsed unless forced; `-R` models none) | Not documented on the first-party API; Cloudflare host documents `seed` "for reproducibility" | `https://api.sea-lion.ai/v1` (Cloudflare `…/accounts/{id}/ai/v1`; PublicAI `https://api.publicai.co/v1`; HF `https://router.huggingface.co/v1`) | AISG Singapore; `api.sea-lion.ai` region not documented `[UNVERIFIED]`; PublicAI "Country of Origin Singapore" |
| **Sahabat-AI** (§12) | **No hosted API — weights only** (`Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT` 128k; `gemma2-9b-cpt-sahabatai-v1-*` and `llama3-8b-cpt-sahabatai-v1-*` 8192) | None (no API). GPU Merdeka compute coupons exist for approved research proposals | Weights: base licenses only. Chat app: **no privacy notice or ToS published** (only a cookie notice) → prompt logging/retention/training `[UNVERIFIED]` | Not documented `[UNVERIFIED]` | Not documented `[UNVERIFIED]` | Not documented `[UNVERIFIED]` | **None** (third-party only: HF router, FriendliAI dedicated) | **Indonesia** — "All data and GPU infrastructure used to serve the model are stored within Indonesian territory"; GPU Merdeka / Lintasarta |
| **Moonshot / Kimi** (§13) | **None** — "pay-as-you-go billing with no subscription plan" | $1 minimum recharge to start; "$5 voucher" at $5 cumulative recharge; Tier0 RPM 3 / TPM 500k / TPD 1.5M / concurrency 1; signup-voucher amount+expiry `[UNVERIFIED]` | "**Unless otherwise expressly agreed in writing, Customer Content may be used for the foregoing purposes**" (develop/support/improve); ZDR "available on request to enterprise customers"; "does not use **enterprise** customer data to train models" | Yes — `json_schema` with `strict` + MFJS profile (kimi-k3 most reliable; k2.6 unstable with `$ref`) | Yes (`tools`; `tool_choice:"required"` only on kimi-k3) | **No `seed`** (0 hits in 772 KB docs bundle); `temperature` fixed 1.0, `top_p` 0.95 on current models | `https://api.moonshot.ai/v1` (Anthropic `…/anthropic`) | Moonshot AI PTE. LTD. (Singapore); `platform.kimi.ai` vs `platform.kimi.com` keys isolated; China platform not verified |
| **Volcano Engine Ark (CN)** (§14) | Free quota only for Doubao/Seedream/voice/embedding models (`Doubao-Seed-2.1-pro`, `-turbo`, `Seed-Evolving`, `Seed-Character`, `Doubao-embedding-vision`) — **no free quota documented for hosted DeepSeek/GLM/Qwen/Llama** | 500,000 tokens **per model**, unactivated accounts, session-shared under main account; expiry `[UNVERIFIED]`; Free Tokens Only mode auto-pauses at exhaustion; rewards program = "每日将采集每个模型不超过500万tokens的推理数据，并于次日发放有效期为30天的等量免费资源包" | §4.1 "除非您单独同意，本服务将不使用您提交给服务或使用服务输出的内容训练、重新训练或改进基础模型" — opting into the 数据授权使用协议 ("授权期限为 永久") **or** the rewards program turns training on; §4.2 allows automated content review | Yes (beta) — `json_schema`/`json_object`; not with TPM package | Yes — `tools.function` | **No `seed`** in the Chat API reference | `https://ark.cn-beijing.volces.com/api/v3` | Mainland China (Beijing); docs Chinese-only |
| **BytePlus ModelArk (intl)** (§15) | 500k free tokens per LLM incl. `DeepSeek-V4-pro`, `DeepSeek-V4-flash`, `DeepSeek-V3.2`, plus `Dola-Seed-2.0-*`, `ByteDance-Seed-1.6/1.8`, `Skylark-pro`; 2M per vision model | "500,000 free tokens for every Large Language Model"; "redeemable only once per BytePlus account"; validity `[UNVERIFIED]`; Free Tokens Only mode pauses at exhaustion; promo 50% off up to 1B tokens for 14 days; rewards "5,000,000 tokens free every day" | "Without the customer's prior authorization, BytePlus ModelArk will neither interfere with the data processing nor use Customer Data for its own model training"; content-safety-filtered I/O "retained for 180 days in Malaysia"; rewards opt-in grants a permanent licence over captured data | Yes (`json_schema`, `strict`) | Yes | **No `seed`** in the parameter reference | `https://ark.ap-southeast.bytepluses.com/api/v3` | "Malaysia, Indonesia, and/or the EU/EEA"; filtered content retained in Malaysia |

---

## Not verified / gaps (consolidated)

1. **OpenRouter** — exact labels of the account-level privacy toggles could not be read: `https://openrouter.ai/settings/privacy` redirects to sign-in (`https://openrouter.ai/sign-in?redirect_url=…`). What is documented is the rule ("There are separate settings for paid and free models") and its consequence. New-user "small free allowance" amount is not stated anywhere live. Aggregator claims of ~29 free models conflict with the 16 returned by the models API today.
2. **HF Inference Providers** — no published RPM/RPD limits: `/docs/inference-providers/rate-limits` **redirects to the pricing page today**; no rollover rule for the $0.10 monthly credit; no model-deprecation policy page found; per-model context lengths are not in the chat-completion reference.
3. **Z.ai / BigModel** — free-tier rate/concurrency numbers are behind a JS-only page/login; no `json_schema`; no `seed`; no deprecation policy page; whether a free API key is governed by the individual-user training clause or the API-developer clause is not resolved on any live page.
4. **Baidu Qianfan** — the free-quota page (2025-11-17) predates the 2026-06-30/07-28 model shutdowns, so the current free ID set is `[UNVERIFIED]`; which agreement covers free tokens is unstated; docs Chinese-only.
5. **Scaleway** — free-tier expiry and €100-credit conditions unstated; signup-page FAQ still contains stale "totally free while in beta" copy contradicting the current pricing.
6. **DeepInfra** — no free tier at all today; the widely cited signup credit is contradicted by the mandatory card/prepay wording; no deprecation policy page; human review of prompts unstated.
7. **Vercel AI Gateway** — free-tier rate numbers unpublished by design; `seed` absent from every model's `supported_parameters` and untested (no key); no deprecation policy page; the `availableToFreeTier` flag exists only in the models page payload (233/417), not in `GET /v1/models` (411), and `?freeTier=true` does not filter server-side; the 2025 GA blog contradicts the 2026 docs on premium-model access and rate limits.
8. **Novita AI** — no model-API free tier; general signup-credit amount and referral/voucher expiry unstated; RPM/TPM table and the Structured-Outputs model list are JS-rendered (values captured from the live page today, not present in static HTML); Trust Center "6 months" retention seen only in a search snippet.
9. **Chutes** — free tier explicitly retired (quotes in §10); numeric rate limits for the shared/anonymous path unpublished; no deprecation policy page; determinism not promised; two cheapest models expose no feature flags; live `/v1/models` prices differ from the dated starter guide (live endpoint treated as authoritative).
10. **SEA-LION** — free-API model list requires a key (401 today); trial-key credits/expiry/daily cap unpublished; `seed` and JSON-schema undocumented and untestable without a key; no deprecation policy page; `api.sea-lion.ai` hosting region unstated; license metadata contradictions (HF `mit` vs docs "Other"/"Apache-2.0") recorded unresolved.
11. **Sahabat-AI** — no hosted free API exists (probed hosts 404 / unreachable); chat-app data use has no published policy; an aggregator's "hosted API" claim is unsubstantiated on any primary page.
12. **Moonshot / Kimi** — no free tier; signup voucher amount/expiry unverified; China platform (`platform.moonshot.cn`) not verified; no documented deprecation notice window.
13. **Volcano Ark CN** — 500k free-quota expiry unstated; no free quota documented for hosted open-weight (DeepSeek/GLM/Qwen/Llama) models on the CN site; retention window unverified (whitepaper is PDF/image-only); docs Chinese-only and JS-only (read via the site's own docs API).
14. **BytePlus ModelArk** — free-token validity period unstated; docs JS-only (read via rendering proxy).
15. **Cross-cutting:** none of the 15 providers publishes a *free-tier-specific* data-use clause except where a free mechanism is itself the data bargain (OpenRouter's training toggle for providers that may train; Volcano Ark's and BytePlus's rewards programs). Where "free" exists, check the *opt-in* that produces it.
