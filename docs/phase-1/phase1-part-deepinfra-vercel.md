# Phase 1 evidence — DeepInfra & Vercel AI Gateway

All facts below were fetched live on **2026-10-06** (access date). Every "current" claim has a URL and, where decisive, a short verbatim quote. Nothing here is from training memory. `[UNVERIFIED]` marks anything not confirmable on a live page.

Note on page dates: DeepInfra marketing pages show no "last updated" stamp; the Privacy Policy shows "Last modified: August 15th 2026". Vercel docs pages carry a machine-readable `last_updated` field in their `.md` variant, quoted per page.

---

## 1. DeepInfra

### (a) Exact free-model IDs available today

**None. DeepInfra has no free tier today.** No primary page lists free models or a free quota; the pricing page states a card/prepay is mandatory:

> "You have to add a card or pre-pay or you won't be able to use our services. Pre-paid accounts draw down their balance as they go, and invoiced accounts are billed once at the beginning of the following month."
> — https://deepinfra.com/pricing (accessed 2026-10-06)

The catalog is 100% pay-as-you-go. Representative live model IDs and prices from the same page (context / $ per 1M in / $ per 1M out):

| Model ID (as billed) | Context | $/1M in | $/1M out |
|---|---|---|---|
| `deepseek-ai/DeepSeek-V4-Flash-0731` | 1024k | $0.06 ($0.015 cached) | $0.18 |
| `deepseek-ai/DeepSeek-V4-Flash` | 1024k | $0.09 ($0.018 cached) | $0.18 |
| `Qwen/Qwen3.6-35B-A3B` | 256k | $0.10 | $0.95 |
| `Qwen/Qwen3-235B-A22B-Instruct-2507` | 256k | $0.09 | $0.55 |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | 128k | $0.10 | $0.32 |
| `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` | 128k | $0.02 | $0.04 |
| `google/gemma-3-12b-it` | 128k | $0.05 | $0.15 |
| `mistralai/Mistral-Nemo-Instruct-2407` | 128k | $0.019 | $0.03 |
| `microsoft/phi-4` | 16k | $0.07 | $0.14 |

Source: https://deepinfra.com/pricing (accessed 2026-10-06). Also `/models` (accessed 2026-10-06) shows a `show_deprecated` filter, i.e. a catalog with active/past models.

**Historic ~$1.80 / ~$5 signup credit:** no primary DeepInfra page found on 2026-10-06 that promises any signup credit. Third-party aggregators (e.g. free-llm.com, tipwork.cn, aicredits.dev) claim "$5 free credits on signup" / "$5 signup credit + $5/month recurring" — these are **not** confirmed on any DeepInfra-owned page → `[UNVERIFIED]`, and contradicted by the mandatory-card/prepay statement above.

### (b) Free-tier rate/daily quota + credit amount & expiry

- **No free-tier quota exists** (no free tier). 
- Paid account default limit, verbatim:
  > "Every account has a default limit of **200 concurrent requests per model**. If you query two different models simultaneously, you can handle 400 total concurrent requests (200 per model)."
  > Error shape: "You'll receive HTTP **429** with a `Rate limited` message when the limit is exceeded."
  — https://docs.deepinfra.com/account/rate-limits.md (accessed 2026-10-06)
- Pricing page footer repeats the cap: "We limit each account to 200 concurrent requests. If you want more drop us a line" — https://deepinfra.com/pricing (accessed 2026-10-06)
- **Startup program (DeepStart)** — the only "free" mechanism found, and it is not self-serve:
  > "DeepStart ~50,000,000,000 free tokens* … * at DeepSeek V4 Flash prices … **Credits expire 1 year after approval**"
  > Eligibility: "Have raised between 250K and 10M USD", "Founded in the last 2 years"
  — https://deepinfra.com/deepstart (accessed 2026-10-06)

### (c) JSON-schema / structured output + tool/function calling

Both supported on the OpenAI-compatible endpoint.

- Structured output: two modes, `json_object` (schema-free) and `json_schema` (strict). Verbatim: "Enforces a strict output schema using [JSON Schema](https://json-schema.org/). The model is constrained to produce only values that match your schema"; example passes `{"type":"json_schema","json_schema":{"name":"breakthrough","strict":true,"schema":{…}}}`. Docs also warn: "JSON mode can affect model alignment. When forced to produce structured output, some models are more likely to hallucinate values rather than say 'I don't know.'" — https://docs.deepinfra.com/chat/structured-outputs.md (accessed 2026-10-06)
- Tool calling support matrix (verbatim table): Single tool calls ✅, Parallel tool calls "✅ (quality may vary)", `tool_choice: "auto"` ✅, `tool_choice: "none"` ✅, Streaming ✅, Nested calls ❌ — https://docs.deepinfra.com/chat/tool-calling.md (accessed 2026-10-06)
- DeepInfra is the *host* here (not a gateway): models are served on DeepInfra's own H100/A100 infrastructure.

### (d) Seed + temperature determinism

`seed` **is** an accepted API parameter, but determinism is **explicitly disclaimed**. From the live OpenAPI schema of `POST /v1/chat/completions`:

> `seed` (integer|null) — "Seed for random number generator. If not provided, a random seed is used. **Determinism is not guaranteed.**"
> — https://api.deepinfra.com/openapi.json (fetched 2026-10-06); rendered identically in the API reference page https://docs.deepinfra.com/api-reference/chat-completions/openai-chat-completions

`temperature` is supported (0–2, default 1) and documented as "lower values … will make the output more focused and deterministic" — https://docs.deepinfra.com/chat/overview (accessed 2026-10-06).

### (e) Context length

Per model, not account-wide. Examples (https://deepinfra.com/pricing, accessed 2026-10-06): `DeepSeek-V4-Flash(-0731)` 1024k; `Qwen3.6-*`/`Qwen3.5-*` 256k; `Llama-4-Scout-17B-16E` 320k; `Llama-3.3-70B-Instruct-Turbo` 128k; `gemma-3-12b-it` 128k; `Qwen2.5-72B-Instruct` 32k; `phi-4` 16k. Max output default: "If explicitly set to None it will be the model's max context length minus input length or 65536, whichever is smaller" (OpenAPI, accessed 2026-10-06).

### (f) DATA-USE — store/log/train/human review

No free-vs-paid distinction (there is no free tier); the policy is account-wide.

> "We will not store, sell, or train using this data unless we have your explicit consent."
> — DeepInfra Privacy Policy, "Last modified: August 15th 2026", section "Data submitted to and returned by our inference Service" — https://deepinfra.com/privacy (accessed 2026-10-06)

> "We do not use data you submit to our APIs for training models, except when using Google or Anthropic models, where the receiving company's training policy applies."
> "We do not log the content of your requests. We log only metadata useful for debugging: request ID, cost, sampling parameters."
> — https://docs.deepinfra.com/account/data-privacy (accessed 2026-10-06)

Other verbatim points from that page: "**Input data is not stored to disk** during inference — it exists only in memory while the request is being processed"; "**We do not share your data with third parties** (except Google/Anthropic model exceptions)"; "When using the Google model, Google logs prompts and responses for a limited period solely to detect violations of their Prohibited Use Policy."; note a caveat for the batch path: "When using our bulk inference APIs … we may need to store data for a longer period, potentially on disk in encrypted form."

Contract-level, from the ToS:

> "Provider will not sell Customer Data, and will not use Customer Data to train, fine-tune, or otherwise improve any model, except as necessary to provide the Services (e.g., fine-tuning a model for Customer's use). Provider will not retain, store, or log any Customer Data submitted to or generated by the Services beyond the period strictly necessary to process and return the applicable request…"
> — https://deepinfra.com/terms (accessed 2026-10-06)

Homepage marketing echo: "With our zero retention policy your inputs, your outputs, and your user data stay private." — https://deepinfra.com/ (accessed 2026-10-06). The catalog exposes `ZDR` badges per model (e.g. `deepseek-ai/DeepSeek-V4-Flash-0731` "ZDR", `moonshotai/Kimi-K3` "ZDR Cache retention").

Human review: not mentioned anywhere on the pages read → `[UNVERIFIED]` (no statement either way).

### (g) Deprecation / versioning policy for models

No formal published policy page. Evidence of the mechanism exists as product UI strings on the live models page:

> `deprecated_warning`: "Due to low usage this model will be deprecated on {{date}}. Your inference requests are still working. Please update your code to use another model."
> `replaced_warning`: "Due to low usage this model has been replaced by {{replaced_by}}. Your inference requests are still working but they are redirected. Please update your code to use another model."
> `show_deprecated`: "show deprecated"; `deprecated`: "Deprecated"; `col_retired`: "Replaced"
> — https://deepinfra.com/models (fetched 2026-10-06, i18n strings in page payload)

Versioning is also first-class in the API: the `model` parameter accepts "Model name, or `MODEL_NAME:VERSION`, or `deploy_id:DEPLOY_ID`" — https://docs.deepinfra.com/chat/overview (accessed 2026-10-06). Model IDs themselves are dated snapshots (e.g. `DeepSeek-V4-Flash-0731`, `DeepSeek-V4-Pro-0813`).

### (h) OpenAI-compatible base URL

```
https://api.deepinfra.com/v1/openai
```
Verbatim: "The only changes you need to make from your existing OpenAI code: 1. Set `base_url` to `https://api.deepinfra.com/v1/openai` 2. Set `api_key` to your DeepInfra token 3. Set `model` to a model from our catalog" — https://docs.deepinfra.com/chat/overview (accessed 2026-10-06). Chat route: `https://api.deepinfra.com/v1/openai/chat/completions`. Caveat on the same page: "We may not be 100% compatible with all OpenAI parameters."

---

## 2. Vercel AI Gateway

### (a) Which models are free / free-tier-eligible today

The docs page describing eligibility: https://vercel.com/docs/ai-gateway/pricing (`last_updated: 2026-09-08`, accessed 2026-10-06):

> "The free tier includes a subset of models, not the full catalog. To see which models you can use with free credits, browse the Free Tier models." (link resolves to `/ai-gateway/models?freeTier=true`)

**Method + caveat:** the `/ai-gateway/models` page's embedded payload carries a boolean `availableToFreeTier` per model entry. The `?freeTier=true` query string does **not** filter server-side (the same 417 markers appear with and without it), so the flag was extracted directly: **233 of 417 catalog entries are `availableToFreeTier: true`, corresponding to 223 unique model IDs**. The public API `GET https://ai-gateway.vercel.sh/v1/models` returned 411 models and does **not** expose a free-tier field at all. Counts from the two sources therefore differ; the flag only exists in the browsable page payload.

Free-tier-eligible **open-weight** IDs observed (subset, `availableToFreeTier:true`; context window from `GET /v1/models`, fetched 2026-10-06):

| Free-tier model ID | Context | zdr | no_training |
|---|---|---|---|
| `meta/llama-3.3-70b` | 128k | all | all |
| `meta/llama-3.1-8b` | 128k | some | some |
| `meta/llama-3.1-70b` | — | — | — |
| `meta/llama-4-maverick` | 128k | all | all |
| `deepseek/deepseek-r1` | 128k | all | all |
| `deepseek/deepseek-v3.1` | 163.8k | — | — |
| `deepseek/deepseek-v3.1-terminus` | 131k | — | — |
| `deepseek/deepseek-v4-flash` | 1000k | some | some |
| `deepseek/deepseek-v4-flash-vision-exp` | — | — | — |
| `deepseek/deepseek-v4.1-flash-fast` | — | — | — |
| `openai/gpt-oss-20b` | 131k | some | some |
| `openai/gpt-oss-safeguard-20b` | — | — | — |
| `zai/glm-4.5-air` | 128k | none | none |
| `zai/glm-4.7-flash` | — | — | — |
| `mistral/mistral-small` | 262k | all | all |
| `mistral/mistral-nemo` | — | — | — |
| `mistral/ministral-8b`, `mistral/ministral-14b` | — | — | — |
| `alibaba/qwen3-coder` | 262k | some | some |
| `alibaba/qwen3-coder-30b-a3b`, `qwen3-coder-next` | 262k / 256k | — | — |
| `alibaba/qwen-3-14b` | 40.96k | — | — |
| `alibaba/qwen-3-32b` | 128k | — | — |
| `moonshotai/kimi-k2-thinking` | 216k | all | all |
| `moonshotai/kimi-k2.5` | — | — | — |
| `nvidia/nemotron-3-super-120b-a12b` | 256k | all | all |
| `nvidia/nemotron-3-nano-30b-a3b` | — | — | — |
| `google/gemma-4-26b-a4b-it` | — | — | — |
| `minimax/minimax-m2.1` | — | — | — |
| `meta/muse-spark-1.1/1.2/1.3`, `meta/muse-glimmer-30b` | — | — | — |

The same flag also marks many closed-weight models (e.g. `anthropic/claude-opus-4.5`, `openai/gpt-5-mini`, `spacexai/grok-4.5`, `google/gemini-3.8-flash`). So on today's page payload the free tier is **not** limited to open weights. Reproduction: fetch `https://vercel.com/ai-gateway/models` and, in the embedded Next.js payload, read `availableToFreeTier` per model entry — 233 `true` of 417 entries (223 unique IDs), 2026-10-06.

### (b) Free credits: amount, expiry, rate limits

Amount, from the live pricing table (rendered HTML; the `.md` variant omits this table):

> Free tier → **"Monthly credit | $5/month included"**; Paid tier → "Pay as you go with purchased credits"
> — https://vercel.com/docs/ai-gateway/pricing (accessed 2026-10-06)

Expiry / mechanics, verbatim from the same page:

> "Your free credits start when you make your first AI Gateway request."
> "Once you purchase credits, your account transitions to the paid tier and the monthly free credit no longer applies."
> "Free tier requests are also rate limited per model, with lower limits than the paid tier. If you exceed a limit, AI Gateway returns a `429` error and you can retry after a short wait."

Purchased-credit expiry, verbatim from the FAQ (https://vercel.com/docs/ai-gateway/faq, `last_updated: 2026-09-13`):

> "**Do AI Gateway Credits expire?** Yes. Purchased credits expire one year after purchase, as stated in the purchase flow."

Is the free credit an expiring trial? Verbatim:

> "**Is the free tier a time-limited trial?** No. The free tier is a monthly included credit, not an expiring trial."

Payment method may be required before free credits work — FAQ error table:

> "`403` with `customer_verification_required` — The team must add a valid payment method before using free credits — Add a payment method from the link in the error response"

Rate-limit numbers for the free tier are deliberately **not published**: "Limits can change, so this page describes behavior rather than fixed numbers. To confirm the current limit for a model, contact Vercel from your dashboard's **Support** entry." (https://vercel.com/docs/ai-gateway/rate-limits, `last_updated: 2026-09-08`). Paid tier: "AI Gateway does not rate limit paid-tier requests." → free-tier per-model 429 ceiling is `[UNVERIFIED]` numerically.

**Stale-source conflict, flagged:** the GA blog from 2025-08-21 (https://vercel.com/blog/ai-gateway-is-now-generally-available, accessed 2026-10-06) says "$5 of credits every 30 days", "We don't restrict access to premium models", and "Vercel doesn't place any rate limits on your queries". The current docs (2026-09) supersede the last two: free tier is a *subset* of models with *lower per-model limits*. The $5/month figure is consistent across both.

### (c) Structured output + tool/function calling

Both documented and demonstrated on the gateway.

- Structured output via AI SDK (`Output.object` + Zod):
  `const { output } = await generateText({ model: 'anthropic/claude-sonnet-5', output: Output.object({ schema: z.object({…}) }), prompt: '…' });`
  — https://vercel.com/docs/ai-gateway/sdks-and-apis/ai-sdk (accessed 2026-10-06)
- Dedicated reference pages exist per API format: `/docs/ai-gateway/sdks-and-apis/openai-chat-completions/structured-outputs`, `/responses/structured-outputs`, `/anthropic-messages-api/structured-outputs`, `/openresponses/structured-outputs` (all listed in https://vercel.com/docs/sitemap.md, accessed 2026-10-06; the `.md` variants of some sub-pages 404 — JS/HTML only).
- Tool calling: `tools: { getWeather: tool({ inputSchema: z.object({…}), execute }) }` with `stopWhen: isStepCount(5)` — same AI SDK page. Caveat quoted on that page: "Without it the request stops as soon as the tool runs, finishing with `finishReason: 'tool-calls'` and an empty `text`."
- Catalog capability flags (from `GET https://ai-gateway.vercel.sh/v1/models`, fetched 2026-10-06): 253 of 411 models tagged `tool-use`; 228 tagged `structured-output`. Example per-model `supported_parameters` for `openai/gpt-oss-120b` includes `response_format`, `structured_outputs`; for `meta/llama-3.3-70b` it lists only `max_tokens, temperature, stop, tools, tool_choice, reasoning, include_reasoning` (no `response_format`).

### (d) Seed + temperature determinism

- `temperature`: present in the gateway catalog's `supported_parameters` for many models; also accepted as a standard Chat Completions field. Documented as a per-model capability, no gateway-level determinism statement.
- `seed`: **not listed in `supported_parameters` for any of the 411 models** in `GET https://ai-gateway.vercel.sh/v1/models` (checked programmatically, 2026-10-06), and **no AI Gateway doc page read mentions `seed` or determinism**. The underlying AI SDK does document it: "`seed?` (`number`): The seed (integer) to use for random sampling. If set and supported by the model, calls will generate deterministic results." — https://ai-sdk.dev/docs/reference/ai-sdk-core/generate-text.md (accessed 2026-10-06), and the AI Gateway provider page (https://ai-sdk.dev/providers/ai-sdk-providers/ai-gateway.md) does **not** mention seed.
- Verdict: whether AI Gateway forwards `seed` to upstream providers, and whether any free-tier model returns deterministic output, is `[UNVERIFIED]` — no live primary source confirms it. Not empirically testable here (no API key/credit balance available).

### (e) Context length

Per model, exposed in the catalog. Examples from `GET https://ai-gateway.vercel.sh/v1/models` (fetched 2026-10-06): `deepseek/deepseek-v4-flash` 1,000,000 (max_tokens 384,000); `alibaba/qwen3-coder-plus` 1,000,000; `alibaba/qwen3-235b` 262,144; `mistral/mistral-small` 262,144; `nvidia/nemotron-3-super-120b-a12b` 256,000; `moonshotai/kimi-k2-thinking` 216,144; `meta/llama-3.3-70b` 128,000; `openai/gpt-oss-20b` 131,072; `zai/glm-4.5-air` 128,000.

### (f) DATA-USE — store/log/train/human review (free vs paid)

Vercel-side, verbatim FAQ answers (https://vercel.com/docs/ai-gateway/faq, `last_updated: 2026-09-13`):

> "**Does Vercel train on my prompts or store my data?** No. Vercel does not train on your prompts, and AI Gateway itself does not retain prompt or response content: it is deleted once the request completes."

> "**What does AI Gateway log about my requests?** AI Gateway does not log the prompts or responses in your requests. That content is not retained after the request completes. What AI Gateway records is each request's metadata… routing attempt details are kept for 30 days…"

> "Vercel's own retention policy does not constrain providers, so enable these controls when you need a guarantee that covers the whole path."

ZDR page (https://vercel.com/docs/ai-gateway/security-and-compliance/zdr, `last_updated: 2026-09-22`):

> "AI Gateway has a ZDR policy and does not retain prompts, outputs, or sensitive data. User data is immediately and permanently deleted after requests are completed."
> "Zero data retention (ZDR) is available for Pro and Enterprise users on AI Gateway."
> "By default, AI Gateway does not route based on the data retention policy of providers." / "If we do not know a provider's ZDR stance or have not yet established an agreement with them, they are treated as not being ZDR-compliant."

Prompt-training control (https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training, `last_updated: 2026-09-10`):

> "No training on prompt data is available to all AI Gateway users at no extra charge."
> "If we do not know a provider's training data stance or have not yet established an agreement with them, we assume that they train on your data. If disallow prompt training is enabled on a request, it will not be routed through that provider."

Free vs paid reading: the Vercel-side retention behaviour is tier-independent (no tier-specific wording found), and `disallowPromptTraining: true` is available to all users at no cost (usable on the free tier), but **ZDR is Pro/Enterprise only** — so a free-tier (Hobby) user cannot enforce provider-side zero retention, only no-training routing. Per-model catalog flags `zdr` / `no_training` (`all` / `some` / `none`) indicate which providers qualify. Human review of prompt data by Vercel is not mentioned → `[UNVERIFIED]` (no statement either way).

### (g) Deprecation / versioning policy for models

`[UNVERIFIED]` — no AI Gateway model deprecation/lifecycle policy page exists in the docs sitemap or in the AI Gateway section of https://vercel.com/docs/sitemap.md (searched 2026-10-06 for "deprecat", "retire", "sunset", "lifecycle": only unrelated platform pages matched). What *is* published is catalog freshness:

> "Every model entry in `GET /v1/models` carries its provider release date in `released`"
> — https://vercel.com/docs/ai-gateway/faq (accessed 2026-10-06)

Model-ID stability, notice periods, or removal guarantees are not documented anywhere found. The gateway does maintain dated/versioned slugs (e.g. `alibaba/qwen3.8-max-0902`, `deepseek/deepseek-v4-flash-0731`, `-fast` suffix convention documented in the FAQ).

### (h) OpenAI-compatible base URL

```
https://ai-gateway.vercel.sh/v1
```
Verbatim from the docs' own code samples: `const client = new OpenAI({ apiKey: …, baseURL: 'https://ai-gateway.vercel.sh/v1' })` and `curl https://ai-gateway.vercel.sh/v1/chat/completions` — https://vercel.com/docs/ai-gateway/security-and-compliance/zdr and https://vercel.com/docs/ai-gateway/rate-limits and https://vercel.com/docs/ai-gateway (all accessed 2026-10-06). Anthropic Messages API base is `https://ai-gateway.vercel.sh` (no `/v1`). Catalog endpoint: `GET https://ai-gateway.vercel.sh/v1/models` (no auth required, verified 2026-10-06).

---

## 3. Side-by-side summary

| Field | DeepInfra | Vercel AI Gateway |
|---|---|---|
| (a) Free models today | **None** — no free tier; card/prepay mandatory | **223 unique free-tier-eligible model IDs** (233/417 catalog entries) incl. `meta/llama-3.3-70b`, `deepseek/deepseek-v4-flash`, `openai/gpt-oss-20b`, `zai/glm-4.5-air`, `mistral/mistral-small` |
| (b) Free quota/credit | No free credit on any primary page; paid default 200 concurrent/model. DeepStart: 50B tokens, **"Credits expire 1 year after approval"** | **$5/month included**; starts at first request; ends permanently after first credit purchase; purchased credits **expire 1 year**; per-model 429, numbers unpublished |
| (c) JSON schema + tools | ✅ `json_schema` strict + `json_object`; ✅ tools (nested ❌) | ✅ `Output.object`/Zod + 4 API-format docs; ✅ tools; catalog: 228 structured-output, 253 tool-use |
| (d) `seed` | Accepted; schema says **"Determinism is not guaranteed."** | Not in any model's `supported_parameters`; undocumented → `[UNVERIFIED]` |
| (e) Context | Per model 16k–1024k | Per model up to 1000k |
| (f) Data use | "will not store, sell, or train using this data unless we have your explicit consent"; "We do not log the content of your requests" | "AI Gateway itself does not retain prompt or response content: it is deleted once the request completes"; no training; ZDR = Pro/Enterprise only, no-training routing = all tiers |
| (g) Deprecation policy | No policy page; UI states a deprecation date + "Replaced by" redirect; `MODEL:VERSION` param | No policy page found → `[UNVERIFIED]`; catalog exposes `released` dates |
| (h) OpenAI base URL | `https://api.deepinfra.com/v1/openai` | `https://ai-gateway.vercel.sh/v1` |

---

## 4. Not verified / gaps

1. **DeepInfra signup credit (~$1.80 / $5):** claimed by several aggregators; **no DeepInfra-owned page** on 2026-10-06 states any signup or recurring free credit. Treat as `[UNVERIFIED]`; the pricing page's mandatory-card/prepay wording points the other way.
2. **DeepInfra free-tier data-use split:** impossible to verify because no free tier exists; the policy is account-wide.
3. **DeepInfra human review of prompts:** no statement found (docs say content is not logged; no mention of human review) → `[UNVERIFIED]`.
4. **DeepInfra formal model deprecation policy:** only in-product strings found (`deprecated_warning`, `replaced_warning`), no policy page with notice periods.
5. **Vercel free-tier rate-limit numbers:** explicitly undocumented ("contact Vercel from your dashboard's Support entry") → `[UNVERIFIED]`.
6. **Vercel monthly-credit rollover:** unstated whether unused free monthly credit carries over; not documented → `[UNVERIFIED]`.
7. **Vercel `seed` pass-through:** not listed for any model in the catalog API, and no docs mention; whether the OpenAI-compatible surface transparently forwards `seed` upstream is `[UNVERIFIED]`. Not empirically testable here (no API key/credit balance in this environment).
8. **Vercel model-deprecation policy:** no AI Gateway lifecycle/deprecation page found in the sitemap (searched 2026-10-06) → `[UNVERIFIED]`.
9. **Vercel free-tier model list source mismatch:** the `availableToFreeTier` flag only exists in the `/ai-gateway/models` page payload (233/417 entries); `GET /v1/models` (411 models) has no such field, and the `?freeTier=true` query param does not filter server-side. Counts differ between the page and the API.
10. **Vercel free-tier eligibility expansion:** the 2025 GA blog said "We don't restrict access to premium models", but the 2026-09 docs say the free tier is "a subset of models". The extracted flag currently marks many closed-weight models as free-tier eligible — direction of travel is inconsistent between sources; flagged rather than resolved.
11. **Some Vercel doc sub-pages are JS-only:** `.md` variants for `sdks-and-apis/openai-chat-completions*` and `sdks-and-apis/ai-sdk` details returned 404 on direct fetch; content was confirmed from the parent pages and the rendered HTML instead.
