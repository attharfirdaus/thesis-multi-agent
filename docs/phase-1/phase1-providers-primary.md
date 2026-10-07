# Phase 1 — Free hosted inference for open-weight LLMs (primary providers)

Access date for every citation: **2026-10-06**. Every number below is quoted from the provider's own page fetched today. Version/limit/price/licence facts are never taken from memory. Items the provider does not publish are marked `[UNVERIFIED]` with the reason. No recommendations, no selection: options and evidence only.

Scope notes
- "Free" is used as: (a) a provider-run tier with no payment method, or (b) models priced $0.00/1M tokens. Both kinds are reported separately per provider, because they are not the same thing.
- Bahasa Indonesia capability is listed only where the fetched page itself documents it. Cross-provider Indonesian benchmark evidence is the separate `ModelIndoCapability` slice of this phase.
- The app's single config-driven OpenAI-compatible client (PRD §8) makes item 8 (base URL) load-bearing.

---

## 1. Groq (GroqCloud)

Sources fetched: https://console.groq.com/docs/rate-limits , https://console.groq.com/docs/models , https://console.groq.com/docs/structured-outputs , https://console.groq.com/docs/tool-use , https://console.groq.com/docs/deprecations , https://console.groq.com/docs/openai , https://console.groq.com/docs/billing-faqs , https://console.groq.com/docs/legal/services-agreement , https://console.groq.com/docs/legal/customer-data-processing-addendum , https://groq.com/privacy-policy — all accessed 2026-10-06.

### 1.1 Open-weight models usable at $0
A Free tier exists and is defined by the absence of a payment method: on downgrading, "Your account returns to Free tier rate limits and restrictions" (billing-faqs). The Services Agreement §5.1 allows fee-free designation: "Certain Cloud Services and AI Model Services may be designated as fee-free or otherwise available without triggering a payment for a limited time or based on usage limits."

Models listed in the rate-limit table (i.e. reachable without a paid upgrade):

| Model ID | Family / licence | Context | Max completion |
| --- | --- | --- | --- |
| `openai/gpt-oss-120b` | OpenAI gpt-oss, open weight | 131,072 | 65,536 |
| `openai/gpt-oss-20b` | OpenAI gpt-oss, open weight | 131,072 | 65,536 |
| `openai/gpt-oss-safeguard-20b` | OpenAI gpt-oss (safety) | 131,072 | 65,536 |
| `qwen/qwen3.8-27b` | Alibaba Qwen3.8, open weight | 131,072 | 16,384 |
| `meta-llama/llama-prompt-guard-2-22m` / `-86m` | Meta (classifier, not a chat model) | 512 | 512 |
| `whisper-large-v3`, `whisper-large-v3-turbo` | audio (ASR), not LLM | – | – |
| `minimaxai/minimax-m2.7` | preview, "ContactSales" rate limits | 196,608 | 131,072 |

Llama-family status (models page vs deprecation page — the two disagree, both quoted):
- Models page still lists `llama-3.1-8b-instant` (131,072 ctx, max completion 131,072) and `llama-3.3-70b-versatile` (131,072 ctx, 32,768 max completion) as Production, but with price and rate limits "ContactSales" and an "Enterprise" tag — i.e. not part of the free/developer plan.
- The deprecation page says the opposite about availability: "August 16, 2026: llama-3.1-8b-instant and llama-3.3-70b-versatile … on June 17, 2026, we emailed users to announce the deprecation … Shutdown date 08/16/26". Same page: Llama 4 Scout 17B and Llama 4 Maverick 17B shut down 07/17/26 and 03/09/26.
- Net: as of 2026-10-06 no Llama model is documented as usable at $0 on Groq, and the deprecation page says the 3.1/3.3 IDs are past shutdown while the models page still displays them. **Contradiction between two live Groq pages — flagged, not resolved.**
- Llama 3.1 8B / 3.3 70B / 3.2 small / Llama 4 were all retired on this platform over 2025–2026 (deprecation page history), so pinning the thesis to a Llama ID on Groq carries visible risk.

### 1.2 Free-tier limits
Published table on the rate-limits page (page header says these are the values for the listed model IDs):

| Model ID | RPM | RPD | TPM | TPD |
| --- | --- | --- | --- | --- |
| `openai/gpt-oss-120b` | 30 | 1,000 | 8K | 200K |
| `openai/gpt-oss-20b` | 30 | 1,000 | 8K | 200K |
| `openai/gpt-oss-safeguard-20b` | 3 | 1,000 | 2K | 200K |
| `qwen/qwen3.8-27b` | 30 | 1,000 | 8K | 200K |

The same page then says: "Need higher rate limits? Upgrade to Developer plan … **Note that the limits shown below are the base limits for the Developer plan**" — while the models page's "RATE LIMITS (DEVELOPER PLAN)" column gives `openai/gpt-oss-120b` = **250K TPM / 1K RPM**. Two live Groq pages attach different numbers to "Developer plan", so the free-tier attribution of the 30 RPM / 1K RPD / 8K TPM / 200K TPD row is `[UNVERIFIED]`: the page also states "You can view the current, exact rate limits for your organization on the limits page in your account settings" (login required, not fetchable). No concurrent-request limit, no monthly free quota, no credit-expiry rule is published for the Free tier. Also published: "Rate limits apply at the organization level, not individual users"; "Cached tokens do not count towards your rate limits"; exceeding returns `429` with `retry-after`.

### 1.3 Structured output and tool calling
Structured Outputs, verbatim: strict mode "uses **constrained decoding** to guarantee that the output will always match your schema exactly … **Never errors or produces invalid JSON**"; "All fields must be `required` and objects must set `additionalProperties: false`". Strict mode supported by `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`. Best-effort (`strict: false`, default) additionally on `openai/gpt-oss-safeguard-20b`, and "may produce valid JSON that does not match your schema". Hard limitation quoted: "**Streaming and tool use are not currently supported with Structured Outputs.**" JSON Object Mode remains available for all other models.

Tool use: "**All models hosted on Groq support tool use**." Per-model table: `gpt-oss-20b`/`gpt-oss-120b` local+remote tools yes, **parallel tool use No**; `qwen/qwen3.8-27b` parallel yes; `llama-3.3-70b-versatile` and `llama-3.1-8b-instant` parallel yes (both listed as deprecated elsewhere).

### 1.4 Determinism
`seed` (API reference, chat completions): "If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same `seed` and parameters should return the same result. **Determinism is not guaranteed**, and you should refer to the `system_fingerprint` response parameter to monitor changes in the backend."
`temperature`: "If you set a `temperature` value of 0, it will be converted to `1e-8`" (OpenAI-compatibility page). Unsupported request fields that 400: `logprobs`, `logit_bias`, `top_logprobs`, `messages[].name`, `N` must be 1.

### 1.5 Context length (free models)
131,072 for gpt-oss-120b / gpt-oss-20b / gpt-oss-safeguard-20b / qwen3.8-27b; 196,608 for minimax-m2.7. Max completion: 65,536 (gpt-oss), 16,384 (qwen3.8-27b).

### 1.6 Data use — free tier
Groq's public privacy policy explicitly does **not** cover API content: "This Policy does **not** apply to the information that we process as a 'data processor' on behalf of customers ('Customer Data') of our business offerings such as GroqCloud … Our processing of Customer Data … is governed by our Groq Services Agreement and Data Processing Addendum." The operative sentence is in the Services Agreement §4.2 (Last Modified: June 22, 2026): "**Groq does not access, use, store, or retain Inputs or Outputs except as necessary to provide the Cloud Services, in accordance with the Customer's permission or instruction, comply with applicable law, ensure the reliable operation of the Cloud Services, or confirm Customer's compliance with the AUP. … For clarity, Groq is not permitted to use Inputs or Outputs for training or fine-tuning any AI Model Services or other models, unless explicitly granted permission or instructed by Customer.**" §4.2 also offers an opt-in "zero data retention setting" for eligible customers. DPA (Effective October 15, 2025) §10: on termination, deletion of Personal Data "as soon as reasonably practicable and within a maximum period of 180 days". No separate retention/training text exists for the Free tier; the Agreement governs "fee-free" services (§5.1), so the same clause applies. Not found on any Groq page: a numeric retention window for normal API operation. Groq ToS §14.2 caps liability for services "provided free of charge" at $5,000.

### 1.7 Deprecation policy
Deprecation doc: production models — "we will provide a clear migration path and recommended replacement model"; preview models — "may be discontinued at short notice with limited advance warning"; process = email notification + docs update + transition period + optional automatic upgrade to the replacement, then errors on the old ID. No minimum notice period is published; the Services Agreement §4.4 only promises "commercially reasonable efforts to provide Customer with reasonable prior notice". Observed practice on the same page: Llama 3.1 8B / Llama 3.3 70B announced 2026-06-17, shut down 2026-08-16 (≈2 months); `qwen/qwen3.6-27b` shut down 2026-09-14; Llama 4 Scout/Maverick ≈1 month. Version pinning: model IDs are version-bearing (e.g. `llama-3.3-70b-versatile`); no stability guarantee is documented for IDs, and one historical case explicitly moved behaviour under an unchanged ID ("requests … will automatically upgrade to their respective 3.3 versions").

### 1.8 API shape
OpenAI-compatible: `base_url="https://api.groq.com/openai/v1"` (openai doc). Caveats listed above (temperature 0 → 1e-8; unsupported fields; `N`=1; `seed` best-effort). Native SDKs also exist.

---

## 2. Cerebras Cloud (Cerebras Inference)

Sources fetched: https://inference-docs.cerebras.ai/support/rate-limits , https://inference-docs.cerebras.ai/models/overview , https://inference-docs.cerebras.ai/models/openai-oss , https://inference-docs.cerebras.ai/models/qwen-3.8-27b , https://inference-docs.cerebras.ai/capabilities/structured-outputs , https://inference-docs.cerebras.ai/capabilities/tool-use , https://inference-docs.cerebras.ai/api-reference/chat-completions , https://inference-docs.cerebras.ai/resources/openai , https://inference-docs.cerebras.ai/support/deprecation , https://inference-docs.cerebras.ai/support/preview-releases , https://inference-docs.cerebras.ai/quickstart , https://www.cerebras.ai/pricing , https://www.cerebras.ai/privacy-policy , https://www.cerebras.ai/terms-of-service — all accessed 2026-10-06.

### 2.1 Open-weight models usable at $0
There is **no permanently free tier**. Verbatim FAQ on the rate-limits page: "**Is there a permanently free tier?** No. The Free Trial is time- and credit-bounded: $5 in credits that expire 30 days after they're granted. Once your credits are used up or expire, you need to purchase credits (Pay as You Go) to keep using Shared Inference. Cerebras doesn't currently offer a no-cost tier that renews automatically or a per-model always-free allowance." The Free Trial requires "adding a verified payment method"; without one "Playground and API access remain inactive". Pricing page repeats: "Add a valid payment method to receive a one-time $5 promotional credit. The credit expires 30 days after activation."

Models on the Free Trial (= the whole Shared Inference catalog, currently 2 models):

| Model ID | Parameters | Context (free / paid) | Max output (free / paid) |
| --- | --- | --- | --- |
| `gpt-oss-120b` | 120B (OpenAI open weight) | 65k / 131k | 32k / 40k |
| `qwen-3.8-27b` | 27B (Qwen, open weight) | 64k (65,536) / 128k (131,072) | 32,768 / 40,960 |

Llama-family: none. Deprecations page shows `llama3.1-8b` and `llama-3.3-70b` retired 2026-05-27 and 2026-02-16; Gemma 4 31B withdrawn from Shared Inference 2026-09-03 (Dedicated only).

### 2.2 Free-trial limits
| Model | RPM | Uncached TPM | Total TPM | TPH | TPD |
| --- | --- | --- | --- | --- | --- |
| `gpt-oss-120b` | 5 | 30K | 90K | 1M | 1M |
| `qwen-3.8-27b` | 5 | 30K | 90K | 1M | 1M |

Dual-bucket model: "every organization has both an uncached token limit and a total token limit"; Total TPM default = 3× uncached TPM; cached tokens do not count toward uncached TPM. Token-bucket replenishment, not fixed windows. `max_completion_tokens` is counted against quota up front. `qwen-3.8-27b` image limit on free tier: 2 images/request, 10 MiB payload. No concurrent-request limit published. Credit expiry: 30 days (above); no monthly renewal. Arithmetic (mine, from the pricing page's `gpt-oss-120b` rates $0.35/M input, $0.75/M output): $5 one-time credit ≈ 14.3M input-only tokens, or ≈ 4.5M output-only tokens.

### 2.3 Structured output and tool calling
Structured Outputs table: `qwen-3.8-27b` and `gpt-oss-120b` support Text, JSON object, JSON Schema, and `strict: true` on Shared Inference. Strict mode = constrained decoding; "you must set `additionalProperties: false`. This is required for every object in your schema." Limits: 5,000 counted schema characters; nesting depth 10; 500 object properties; 500 enum values; root must be an `object`; root unions unsupported. Tool calling: `qwen-3.8-27b` and `gpt-oss-120b` — `tool_choice` `none|auto|required|named`, strict mode yes, parallel calls yes, multi-turn yes. Important cross-feature constraint: "Support for combining `tools` and `response_format` is model-dependent … **`gpt-oss-120b` rejects requests containing both fields.**"

### 2.4 Determinism
`seed`: "If specified, the system will make a best effort to sample deterministically so repeated requests with the same `seed` and parameters return the same result. **Determinism is not guaranteed.**" Responses carry `system_fingerprint`. Sampling controls advertised for both free models.

### 2.5 Context length
See 2.1. Free-tier context is **half** the paid context on both models (65k vs 131k; 64k vs 128k) — relevant if one submission + rubric + instructions must fit.

### 2.6 Data use — free tier
Privacy policy §6 (Effective August 27, 2024): "**We do not retain inputs and outputs associated with our training, inference and chatbot Services. We delete logs associated with our training, inference and chatbot Services when they are no longer necessary to provide services to you.**" Terms of Use "Data Usage and Privacy": Cerebras keeps only "the right to use Service Content to provide the Service to you, comply with applicable law and enforce these Terms. **For clarity, the foregoing does not grant Cerebras the right to use Service Content for the purpose of training or fine-tuning models.**" "Usage Data" (diagnostics/telemetry) explicitly "excludes User Content and Outputs". No free-trial-specific carve-out is published; the policy text is identical for trial and paid. Caveats reported as-is: (a) the privacy policy is dated 2024-08-27, older than the current trial terms; (b) retention is bounded only by "no longer necessary", with no numeric window.

### 2.7 Deprecation policy
Dedicated deprecations page: a dated list of removals with recommended replacements (e.g. 2026-09-03: "`gemma-4-31b` is no longer available with Cerebras Shared Inference"), and no published minimum notice window — the Gemma removal was posted on its effective date. Preview Releases policy distinguishes Private Preview / Public Preview / GA and promises stable, versioned interfaces at GA, but states no model-retirement notice period. Partial pinning guarantee from the model catalog: "We are committed to serving the original weights for existing model IDs without modification. We do not alter model architectures via pruning on our hosted portfolio."

### 2.8 API shape
OpenAI-compatible: `base_url="https://api.cerebras.ai/v1"`. Differences documented: `n` only 1; `service_tier` unavailable on Shared Inference; `prediction` unavailable for `qwen-3.8-27b`; image inputs must be base64 data URIs (no external https URLs); for `gpt-oss-120b` both `system` and `developer` roles are elevated to developer-level instructions, so "the same prompt may yield different behavior here compared to OpenAI".

---

## 3. Google AI Studio / Gemini API — Gemma free tier

Sources fetched: https://ai.google.dev/gemini-api/docs/pricing , https://ai.google.dev/gemini-api/docs/rate-limits , https://ai.google.dev/gemini-api/docs/models , https://ai.google.dev/gemini-api/terms , https://ai.google.dev/api/generate-content , https://ai.google.dev/gemini-api/docs/openai , https://ai.google.dev/gemini-api/docs/deprecations , https://ai.google.dev/gemini-api/docs/structured-output , https://ai.google.dev/gemini-api/docs/function-calling , https://ai.google.dev/gemma/docs , https://ai.google.dev/gemma/docs/core — all accessed 2026-10-06. (pricing page footer: "Last updated 2026-10-06"; models page "Last updated 2026-10-06"; rate-limits page "Last updated 2026-09-02"; Gemma overview "Last updated 2026-04-02".)

### 3.1 Open-weight models usable at $0
Pricing page contains a Gemma section: "## [Gemma 4](/gemma/docs/core/model_card_4) Our lightweight, state of the art, open model…" with the table row `Input price — Free Tier: Free of charge; Paid Tier: Not available`, same for Output and Context caching, and `Used to improve our products — Free Tier: Yes; Paid Tier: No`. So Gemma 4 is offered **only** on the free tier in the Gemini API. Google AI Studio itself is also free: "Google AI Studio usage is free of charge in all available regions" (pricing page notes).
Gemma 4 family per the Gemma overview: "Small Sizes: 2B and 4B effective parameter models … Dense: A powerful 31B parameter dense model … Mixture-of-Experts: A highly efficient 26B MoE model … Unified: A 12B parameter encoder free model"; open weights, "permit responsible commercial use".
Gap flagged: the Gemini API **Models page does not list any Gemma model**, and `https://ai.google.dev/gemini-api/docs/models/gemma-4-31b-it` returns HTTP 404. So the exact Gemma model ID / endpoint callable through `generativelanguage.googleapis.com` could not be confirmed today → `[UNVERIFIED]` (Gemma appears only in the pricing table, not in the model catalog page). Llama-family: not offered by Google at all.

### 3.2 Free-tier limits
Not published. The rate-limits page states limits "can be viewed in Google AI Studio" and links `https://aistudio.google.com/rate-limit` (login required), dimensions RPM / TPM / RPD, "Rate limits are applied per project, not per API key. Requests per day (RPD) quotas reset at midnight Pacific time", and "**Specified rate limits are not guaranteed and actual capacity may vary**". It also warns "Rate limits are more restricted for experimental and preview models". The free-tier RPM/TPM/RPD numbers themselves are therefore `[UNVERIFIED]` — Google removed the published per-model free-tier table; no monthly free quota, concurrency limit, or credit-expiry concept exists for the free tier (there is nothing to expire). Tool pricing on free tier is published separately: Google Search grounding "500 RPD free (limit shared for Flash and Flash-Lite). Not available for Pro."

### 3.3 Structured output and tool calling
Docs describe these as capabilities of "Gemini models". Structured outputs: "You can configure Gemini models to generate responses that adhere to a provided JSON Schema" (response mime type + response schema). Function calling: "Function calling lets you connect models to external tools and APIs." A grep of both pages found **no occurrence of "Gemma"** → whether Gemma supports JSON-schema output or function calling through the Gemini API is `[UNVERIFIED]` (not documented on either capability page). Gemma's own documentation does claim function calling for the open weights: "**Enhanced Coding & Agentic Capabilities:** … built-in function-calling support" (Gemma 4 overview, linking `/gemma/docs/capabilities/text/function-calling-gemma4`) — that is a property of the open-weight model, not a statement about the Gemini API endpoint.

### 3.4 Determinism
`GenerationConfig.seed`, verbatim from the API reference: "`seed` `integer` … Optional. Seed used in decoding. **If not set, the request uses a randomly generated seed.**" `temperature` is a standard field of the same config. No further nondeterminism caveat for seeds is published on the generation-config reference.

### 3.5 Context length
Gemma 4 overview: "**Increased Context Window:** Small models feature a 128K context window, while the medium models support 256K." Per-size mapping (E2B/E4B/12B/26B A4B/31B → 128K vs 256K) is not stated granularly on the fetched page. Gemini API context for Gemma is `[UNVERIFIED]` (no Gemma model page).

### 3.6 Data use — free tier (highest-stakes finding)
Gemini API Additional Terms of Service, Effective March 23, 2026, section "Unpaid Services" → "How Google Uses Your Data", verbatim: "When you use Unpaid Services, including, for example, Google AI Studio and the unpaid quota on Gemini API, **Google uses the content you submit to the Services and any generated responses to provide, improve, and develop Google products and services and machine learning technologies**…" and: "**To help with quality and improve our products, human reviewers may read, annotate, and process your API input and output.** Google takes steps to protect your privacy as part of this process. This includes disconnecting this data from your Google Account, API key, and Cloud project before reviewers see or annotate it. **Do not submit sensitive, confidential, or personal information to the Unpaid Services.**" The pricing page mirrors this in a column: free tier "Used to improve our products: Yes"; paid tier "No". Consequence for this thesis: pseudonymised student analysis text on the Gemini free tier is used for product improvement and is subject to human review. No retention window is stated. (For projects in the EEA/CH/UK the paid-service data rules apply even to free quota — not applicable to an Indonesian deployment but quoted for completeness.)

### 3.7 Deprecation policy
Deprecations page (Last updated 2026-10-06) tracks release and shutdown dates per model. Published notice rules (models page, "Model version name patterns"): preview models "will be deprecated with **at least 2 weeks notice**"; the `-latest` alias gets "a **2-week notice** … before the version behind latest is changed"; "**Stable** … Points to a specific stable model. Stable models usually don't change." Experimental models: "availability of model endpoints is subject to change". Concrete example of long lead time on the deprecations page: `gemini-3.1-flash-lite` shutdown 2027-05-07 (≈12 months). No Gemma row exists on the deprecations page → Gemma retirement timing is `[UNVERIFIED]`.

### 3.8 API shape
OpenAI-compatible endpoint exists for Gemini models: `base_url="https://generativelanguage.googleapis.com/v1beta/openai/"` (openai doc, "What changed? Just three lines!"). Whether Gemma is callable through that endpoint is `[UNVERIFIED]` (Gemma is absent from the API model catalog). Native REST/SDK path: `generateContent` with `GenerationConfig`.

---

## 4. GitHub Models

Source fetched: https://docs.github.com/en/github-models (the older `use-github-models/prototyping-with-ai-models` and `about-github-models` URLs both resolve to this page) — accessed 2026-10-06.

### 4.1–4.8
**Service retired — no options exist.** Verbatim, in full: "**GitHub Models has been retired.** As of **July 30, 2026**, GitHub Models has been fully retired. The playground, model catalog, inference API, and bring your own key (BYOK) are no longer available to any customer." The page points to Azure AI Foundry and GitHub Copilot as alternatives (both outside this task's scope — Azure AI Foundry is a paid catalogue, GitHub Copilot is not an open-weight inference API for this app).
Consequently: models at $0 = none; free-tier limits = n/a; structured output / tool calling / determinism / context = `[UNVERIFIED]` and moot; data-use policy = `[UNVERIFIED]` (the retired service's terms were not re-served; not fetched today); deprecation policy = n/a (the whole service was retired); SDK base URL = n/a. Any 2025-era GitHub Models note in the thesis draft is obsolete as of 2026-07-30.

---

## 5. Mistral — La Plateforme free mode ("Free")

Sources fetched: https://mistral.ai/pricing/ , https://docs.mistral.ai/admin/billing-usage/subscriptions , https://docs.mistral.ai/admin/billing-usage/usage-limits , https://docs.mistral.ai/models , https://docs.mistral.ai/resources/known-limitations , https://docs.mistral.ai/studio/conversations/structured-output , https://docs.mistral.ai/studio/conversations/function-calling , https://docs.mistral.ai/inference/sampling , https://docs.mistral.ai/api/ , https://docs.mistral.ai/inference/model-lifecycle , https://docs.mistral.ai/resources/migration-guides , https://help.mistral.ai/en/articles/347617-do-you-use-my-user-data-to-train-your-artificial-intelligence-models , https://help.mistral.ai/en/articles/455207-can-i-opt-out-of-my-input-or-output-data-being-used-for-training — all accessed 2026-10-06.

### 5.1 Open-weight models usable at $0
There is no model-level $0 pricing; there is a plan-level included allowance. Mistral's pricing page Free plan advertises: "**$10 /mo in API credits**", "Test Mistral models in Studio", "Limited messages and web searches". Docs confirm the mechanism: "**Free mode** lets you create API keys and use included monthly usage within the limits shown on the Limits page" (usage-limits); "Free mode is the default state for new accounts" (subscriptions); usage "is shared across Studio, the API, and Vibe Code".
Open-weight models listed on the models page (licence as printed on that page):
- `mistral-large-4-0` — "Open", state-of-the-art multimodal
- `mistral-large-3-25-12` — Apache 2.0
- `mistral-small-4-0-26-03` — Apache 2.0
- `ministral-3-14b-25-12`, `ministral-3-8b-25-12`, `ministral-3-3b-25-12` — Apache 2.0
- `mistral-medium-3-5-26-04` — "Modified MIT"
- `voxtral-small-25-07`, `voxtral-mini-transcribe-realtime-26-02`, `shieldstral-1-0` — Apache 2.0
- third-party open weight: `zai-glm-5-3` (Z.ai)
Also free-of-charge by policy: Labs models — "Are free of charge. Allow silent updates at any time. **Don't support data collection opt-out.** Aren't recommended for production use."
Llama-family: none — and the migration guide maps away from it ("Llama 3 8B Instruct → Mistral 7B Instruct"; "self-hosted Llama" migration section warns about tokenizer/prompt-format differences).
Indonesian relevance: no Mistral page fetched today documents Indonesian coverage. The only language-specific note found is archival: `mistral-saba-2502` (retired 9/30/2025) → `[UNVERIFIED]` for Mistral's current Indonesian capability on these pages.

### 5.2 Free-mode limits
Not published. Verbatim: "API rate limits … are shown in Admin Panel → API → Limits" (usage-limits); "Completion rate limits are listed per model and include: Tokens per minute … Requests per second". Model-level RPM/RPD/TPM values for Free mode are therefore `[UNVERIFIED]` — no public page states them. Related published limits: rate limits "apply per organization" and exceedance returns `429`; "Batch processing does not count against real-time rate limits"; Org/Workspace monthly spending limits exist and "If the Organization reaches its monthly spending limit, API access can be suspended". Credit expiry: the Free-plan allowance is described as monthly included usage (resets per billing period) — no explicit expiry sentence found → `[UNVERIFIED]` on forfeiture rules.

### 5.3 Structured output and tool calling
Mistral offers two modes and recommends one: "Use JSON mode when more flexibility … **Custom structured outputs are more reliable and are recommended whenever possible.**" Custom mode = user schema in `response_format`; JSON mode = `response_format: {"type":"json_object"}`. Known limitations page: with JSON mode "the model always returns valid JSON. You must include 'JSON' in the system or user prompt. Otherwise the model may produce an infinite whitespace stream." and "**JSON mode does not guarantee adherence to a specific schema. Use function calling for structured outputs.**" Function calling: supported-model list on the function-calling page (Mistral Large 3, Mistral Medium 3.5, Mistral Small 3.2, Mistral Small Creative, Ministral 3 14B/8B/3B, Devstral 2, Devstral Small 2, Voxtral Small, Codestral, Magistral Medium/Small 1.2) — note this list is the page's own "non-exhaustive list" and does **not** mention Mistral Large 4 or Mistral Small 4 (page appears older than the model list). Limits: "Maximum number of tools per request: 128"; "Parallel function calls are supported but may return calls in any order"; `tool_choice: "any"` "does not guarantee which tool is selected". OpenAI-compatible tool schema: "Yes. We support the same tool/function calling schema as OpenAI."

### 5.4 Determinism
`random_seed`, verbatim from the API reference: "The seed to use for random sampling. **If set, different calls will generate deterministic results.**" Sampling docs add the standard caveat about temperature: "even with greedy sampling at `temperature=0`, **slight variances** can sometimes occur due to hardware differences and rounding errors … This effect becomes especially evident during long completions … where a single differing token can create an entirely new sequence."

### 5.5 Context length
From the known-limitations table: Mistral Large 3 **256k**, Mistral Medium 3.5 **256k**, Mistral Medium 3.1 128k, Mistral Small 4 **256k**, Codestral 128k, Devstral 2 256k, Magistral Medium 1.2 128k, Ministral 3 (3B/8B/14B) **256k**, Mistral Nemo 12B 128k. "Requests exceeding the model's context window return a `400 Bad Request` error." Mistral Large 4 / Small 4 context not in that table → `[UNVERIFIED]` for Large 4 specifically (Small 4 = 256k).

### 5.6 Data use — free tier
Help-centre article on Mistral Studio: "## Free mode — As stated during subscription, **we may use your data (input and output) to train our artificial intelligence models.** You have the right to opt out of this program at any time" (link to the opt-out article). The opt-out procedure: "In the Admin panel, open the **Privacy** menu … Under the `Anonymous improvement data` section, disable the toggle to prevent API calls and related data from being used to improve Mistral's services", and "**Vibe and API opt-out toggles are separate.**" Contradiction to flag: the public pricing page's plan table shows a "Model training" row where the **Free** column appears empty while Pro/Education/Team/Enterprise show "Opt-out" — the help article nonetheless documents an API opt-out for Studio/API generally. Both pages are Mistral-owned; the discrepancy is reported, not resolved. Labs models are worse: no opt-out at all (model-lifecycle page). Mistral serves the API "from EU data centers by default"; uploaded files "are retained for 30 days unless deleted earlier".

### 5.7 Deprecation policy
Model lifecycle policy, verbatim table: Labs **1 month** notice, Public Preview **1 month**, General Availability **6 months**, Third-party models **1 month**; "Deprecation is announced as soon as a replacement model is available. … Once retired, requests to its identifiers fail with a `404` error." Stability: GA models "Receive **no silent updates**" and "Are supported until retirement"; only GA models get aliases `-latest` / `-major`; model IDs are `model-name-major-minor` and "For precise control, pin your deployment to a specific major.minor version identifier" (warning: "using an alias may expose you to silent updates in model behavior and pricing").

### 5.8 API shape
OpenAI-compatible: the migration guide states "The Mistral Chat Completions API follows the same request structure as OpenAI"; "## Use the OpenAI-compatible base URL — If your application uses an OpenAI-compatible client (LangChain, LlamaIndex, or any other third-party library), point it at the Mistral API by changing only the base URL and model name", `base_url="https://api.mistral.ai/v1"`. Native SDK method names differ (`client.chat.complete`, `client.chat.stream`).

---

## 6. Cloudflare Workers AI (free daily allocation)

Sources fetched: https://developers.cloudflare.com/workers-ai/platform/pricing/ (Last updated Oct 1, 2026), https://developers.cloudflare.com/workers-ai/platform/limits/ (Last updated Sep 17, 2026), https://developers.cloudflare.com/workers-ai/platform/data-usage/ (Last updated Apr 21, 2026), https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/ (Last updated Sep 18, 2026), https://developers.cloudflare.com/workers-ai/features/json-mode/ (Last updated Sep 14, 2026), https://developers.cloudflare.com/workers-ai/features/function-calling/ (Last updated Apr 21, 2026), https://developers.cloudflare.com/workers-ai/models/ , https://developers.cloudflare.com/workers-ai/models/gpt-oss-120b/ , https://developers.cloudflare.com/workers-ai/models/gpt-oss-20b/ , https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/ , https://developers.cloudflare.com/workers-ai/models/llama-3.1-8b-instruct-fp8/ , https://developers.cloudflare.com/workers-ai/models/llama-3.3-70b-instruct-fp8-fast/ , https://developers.cloudflare.com/workers-ai/changelog/ — all accessed 2026-10-06.

### 6.1 Open-weight models usable at $0
Mechanism, verbatim: "Our free allocation allows anyone to use a total of **10,000 Neurons per day** at no charge. To use more than 10,000 Neurons per day, you need to sign up for the Workers Paid plan. … All limits reset daily at 00:00 UTC. If you exceed any one of the above limits, further operations will fail with an error." Paid-only exceptions are named explicitly: "Some models require a paid billing method. This applies to `@cf/moonshotai/kimi-k2.6`, `@cf/moonshotai/kimi-k2.7-code`, `@cf/zai-org/glm-5.2`, `@cf/zai-org/glm-5.3`, `@cf/zai-org/glm-5.3-flash`, `@cf/deepseek-ai/deepseek-v4-flash-0731`, and `@cf/deepseek-ai/deepseek-v4-pro-0813`." Everything else in the LLM pricing table is reachable from the free allocation. Relevant open-weight models at $0 (model page details cited individually):

| Model ID | Context | Function calling | Free-tier budget (my arithmetic from the pricing page's neuron rates) |
| --- | --- | --- | --- |
| `@cf/openai/gpt-oss-120b` | 128,000 | Yes (page) | 31,818 neurons/M input → ≈0.31M input tokens/day |
| `@cf/openai/gpt-oss-20b` | 128,000 | Yes (page) | 18,182 neurons/M input → ≈0.55M input tokens/day |
| `@cf/google/gemma-4-26b-a4b-it` | 256,000 | Yes (page); Vision; Reasoning | 9,091 neurons/M input → ≈1.10M input tokens/day |
| `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | 24,000 | Yes (page) | 26,668 neurons/M input → ≈0.37M input tokens/day |
| `@cf/meta/llama-3.1-8b-instruct-fp8` | 32,000 | – (JSON Mode listed for the non-fp8 `…-instruct`) | 13,778 neurons/M input → ≈0.73M input tokens/day |
| `@cf/aisingapore/gemma-sea-lion-v4-27b-it` | not stated on the pricing page | – | 31,876 neurons/M input → ≈0.31M input tokens/day |
| `@cf/meta/llama-3.2-1b-instruct`, `@cf/meta/llama-3.2-3b-instruct`, `@cf/meta/llama-3.2-11b-vision-instruct`, `@cf/qwen/qwen3-30b-a3b-fp8`, `@cf/qwen/qwen3.8-27b`, `@cf/mistralai/mistral-small-3.1-24b-instruct`, `@cf/ibm-granite/granite-4.0-h-micro`, `@cf/zai-org/glm-4.7-flash`, `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b`, `@cf/meta/llama-4-scout-17b-16e-instruct` | priced on the pricing page | per model page | priced per M tokens on the pricing page |

Indonesian text: one model on this platform is documented as tuned for the region — "`@cf/aisingapore/gemma-sea-lion-v4-27b-it` is a fine-tuned model that supports multiple South East Asian languages, including Burmese, English, **Indonesian**, Khmer, Lao, Malay, Mandarin, Tagalog, Tamil, Thai, and Vietnamese" (changelog, 2025-09-24).
Deprecation warning on the Llama IDs: the 2026-05-08 changelog entry announced that "on May 30, 2026, the following models will be deprecated: … `@cf/meta/llama-3.1-8b-instruct`, `@cf/meta/llama-3.1-8b-instruct-awq`, `@cf/meta/llama-3.1-70b-instruct`, `@cf/meta/llama-3-8b-instruct` …" while the pricing page (2026-10-01) still lists `@cf/meta/llama-3.1-8b-instruct`, `@cf/meta/llama-3-8b-instruct` and `@cf/meta/llama-3.2-1b/3b-instruct`. The same entry adds: "The `-fast` and `-lora` variants of models will remain active." **Live-page contradiction — flagged.** The `-fp8-fast` variants (Llama 3.3 70B, Llama 3.1 8B) have current model pages and current pricing.

### 6.2 Limits
Two independent ceilings: the daily neuron allocation (10,000/day, 00:00 UTC reset) and request-rate limits by task: "Text Generation — 300 requests per minute, unless the model requires the Workers Paid plan". Paid-only models: 20 RPM under standard Workers AI billing, 50 RPM with prepaid AI Gateway credits. No tokens-per-minute or tokens-per-day cap is published — the neuron budget is the token budget. No concurrency limit published. No expiry concept (daily reset). 10,000 neurons/day is small: the arithmetic in 6.1 (0.31M–1.1M input tokens/day depending on model) is the practical ceiling for a batch run.

### 6.3 Structured output and tool calling
JSON Mode: "JSON Mode is compatible with OpenAI's implementation; to enable add the `response_format` property to the request object" with `type: json_object | json_schema` and a `json_schema` "valid JSON Schema declaration". Explicit non-guarantee: "Note that Workers AI can't guarantee that the model responds according to the requested JSON Schema. Depending on the complexity of the task and adequacy of the JSON Schema, the model may not be able to satisfy the request in extreme situations. If that's the case, then an error `JSON Mode couldn't be met` is returned and must be handled. **JSON Mode currently doesn't support streaming.**" Models listed for JSON Mode: `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, `@cf/meta/llama-3-8b-instruct`, `@cf/meta/llama-3.1-8b-instruct`, `@hf/nousresearch/hermes-2-pro-mistral-7b`, `@hf/thebloke/deepseek-coder-6.7b-instruct-awq`, `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b`. Tool calling: per-model "Function calling: Yes" on `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, `@cf/openai/gpt-oss-120b`, `@cf/openai/gpt-oss-20b`, `@cf/google/gemma-4-26b-a4b-it`; classic `tools` + `tool_calls` round-trip and an embedded `@cloudflare/ai-utils` helper.

### 6.4 Determinism
Every text-generation model page documents `seed`: "`seed` `integer` minimum: 1 maximum: 9999999999 — Random seed for reproducibility of the generation." `temperature` default 0.6 (range 0–5), plus `top_p`, `top_k`, `repetition_penalty`, `frequency_penalty`, `presence_penalty`. The OpenAI-compatible endpoint also accepts `seed` ("If specified, the system will make a best effort to sample deterministically"). No explicit guarantee/denial of strict determinism beyond "best effort" is published.

### 6.5 Context length
Per model page (cited above): gpt-oss-120b 128,000; gpt-oss-20b 128,000; gemma-4-26b-a4b-it 256,000; llama-3.3-70b-instruct-fp8-fast **24,000**; llama-3.1-8b-instruct-fp8 32,000. Glossary: context window = "tokens used in the prompt + tokens used in the response"; exceeding it errors, so `max_tokens` must be set against prompt length (changelog, 2025-02-21).

### 6.6 Data use — free tier (strongest published position of the eight)
Data-usage page, verbatim: "**Cloudflare does not use your Customer Content to (1) train any AI models made available on Workers AI or (2) improve any Cloudflare or third-party services, and would not do so unless we received your explicit consent.**" and "Cloudflare does not make your Customer Content available to any other Cloudflare customer." Also: "Your inputs (e.g., text prompts …), outputs …, embeddings, and training data constitute Customer Content. You own, and are responsible for, all of your Customer Content." Storage only occurs if you separately use a storage product (R2/KV/DO/Vectorize). No free-vs-paid distinction is made in this page. Note: the page cites the general Cloudflare Privacy Policy and Self-Serve Subscription Agreement as the governing documents, and model weights are third-party ("Cloudflare neither creates nor trains the AI models made available on Workers AI"). No numeric retention window is published; the sentence above is a purpose limitation rather than a retention period.

### 6.7 Deprecation policy
No policy page exists (the docs index has no deprecations entry; only a changelog). Practice documented in the changelog: 2026-05-08 announcement → 2026-05-30 removal for a list of 18 models (≈3 weeks); an explicit alias behaviour with a price change ("On May 30, 2026, requests to `@cf/moonshotai/kimi-k2.5` will be automatically aliased to `@cf/moonshotai/kimi-k2.6`, which has a higher price"); 2025-09-18 announcement → 2025-10-01 removal (≈2 weeks). So observed notice ≈2–3 weeks, with silent alias redirects to a different-priced model possible. A guaranteed minimum notice period is `[UNVERIFIED]` (not published).

### 6.8 API shape
OpenAI-compatible: `baseURL = https://api.cloudflare.com/client/v4/accounts/${account_id}/ai/v1` for `/v1/chat/completions` and `/v1/embeddings`; "The Responses API (`/v1/responses`) is available only for GPT-OSS models" (and only non-streaming, `stream: false`). Native path: Workers AI binding (`env.AI.run`) or the account-scoped `/ai/run/<model>` REST endpoint. Cloudflare also documents `options.rejectIfBusy` to fail instead of queueing.

---

## 7. Together AI

Sources fetched: https://www.together.ai/pricing , https://docs.together.ai/docs/inference/overview , https://docs.together.ai/docs/inference/openai-compatibility , https://docs.together.ai/docs/inference/chat/structured-outputs , https://docs.together.ai/docs/inference/chat/parameters , https://docs.together.ai/docs/inference/function-calling/overview , https://docs.together.ai/docs/billing-credits , https://docs.together.ai/docs/zero-data-retention , https://docs.together.ai/docs/privacy-and-security , https://docs.together.ai/docs/deprecations , https://docs.together.ai/docs/serverless/rate-limits , https://www.together.ai/models/prism-ml-ternary-bonsai-27b — all accessed 2026-10-06.

### 7.1 Open-weight models usable at $0
Platform access itself is not free. Verbatim: "**Together AI does not currently offer free trials. Access to the Together platform requires a minimum $5 credit purchase.**" (Credits page). So the only $0 usage is models priced `$0.00` in the price list. From the pricing page (serverless chat table):

| Model ID | Pricing | Context | Notes |
| --- | --- | --- | --- |
| `Prism-ML/Ternary-Bonsai-27B` | input $0.00, output $0.00 | **262K** | Ternary (1.71 bpw) build of Qwen3.6 27B; model page: "Available free on Together AI serverless infrastructure"; "Supports text and image input … plus JSON mode for structured outputs"; tool calling score 74.41 BFCL v3 cited on the page |
| `Tev1 4B Experimental` | input $0.04, output **Free** | not stated | partially free |

Llama-family: **no free option, and the free Llama endpoints were removed** — deprecations history lists `meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` removed **2025-11-13** and `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` removed **2026-03-06**; `meta-llama/Llama-3.3-70B` is currently priced $1.04/$1.04. `openai/gpt-oss-120b` is priced $0.15/$0.60 (not free). Scheduled deprecations on the page: `openai/gpt-oss-20b` and `google/gemma-4-31B-it` — "Removal date 2026-09-14" / history "2026-09-15". **Contradiction flagged:** the pricing page fetched today still lists "Gemma 4 31B — $0.39 / $0.97" and gpt-oss-20b in the paid table even though the deprecations page says both were removed from serverless on 2026-09-15; the deprecations page itself anticipates this: "During a transition, a model can still appear in catalog listings while its route-level availability changes. If a listed model returns unavailable or disabled errors, treat the runtime API behavior and this page as the source of truth."

### 7.2 Limits
No free-tier quota; no published RPM/RPD/TPM at all. Rate-limits page: "**Most users can expect to use Together AI serverless inference without encountering rate limits.** Rate limiting may occasionally occur with high request volumes or large bursts of traffic."; exceedance gives `429` or `503`; "Serverless performance is best-effort. For committed throughput and reliability guarantees, see provisioned throughput." Credits: "prepaid balance credits … do not currently have an expiration date"; "Together AI is **fully prepaid**. You need a positive credit balance to use the platform … If your balance reaches zero, API access is suspended." No monthly free quota, no concurrency limit published.

### 7.3 Structured output and tool calling
JSON mode / JSON schema via `response_format` on chat completions ("Supported models can return JSON that conforms to any schema you supply"), plus a regex mode ("Every model that supports JSON mode also supports regex mode", e.g. `{"type":"regex","pattern":"(positive|neutral|negative)"}`). Documented requirement: "Always tell the model to respond **only in JSON** and include a plain-text copy of the schema in the prompt … Send this instruction *in addition* to passing the schema via the `response_format` parameter." Supported-model list is "the [serverless] catalogs" (per-model). Function calling: `tools` + `tool_choice` via `chat.completions.create`, with pages for single, parallel, and multi-turn/agentic patterns. OpenAI SDK compatibility matrix marks `response_format` and `tools` "Supported".

### 7.4 Determinism
`seed` documented on the parameters page: "An integer that makes sampling deterministic. With the same `seed`, prompt, model, and parameters, the model returns the same response. **Determinism is best-effort and may not hold across model or backend updates.**" and on the OpenAI-compatibility page: "`seed` is best-effort. **Determinism is not guaranteed across replicas, model versions, or load conditions.**" Also ignored-if-sent: "`service_tier`, `store`, `metadata`, and `prediction` are accepted but ignored"; `logit_bias` unsupported on most models; `logprobs` returns a non-OpenAI shape.

### 7.5 Context length
`Prism-ML/Ternary-Bonsai-27B` — 262K tokens (model page). Other contexts are per-model pages; the general serverless catalogue lists them. For the paid survivors relevant as fallbacks: gpt-oss-120b listed on the pricing page (context on its model page, not fetched here) → `[UNVERIFIED]` for that one model's context in this report.

### 7.6 Data use — free tier
Zero data retention is **off by default**. Privacy-and-security page, verbatim: "By default, Together stores the prompts you send and the responses models return, and **may use them for product improvements**. This data is not shared with third parties, and you can delete it at any time." Toggles: "**Store prompts and model responses**: on by default. Stores prompts and outputs for product improvements. Turn it off to enable zero data retention, which also turns off passthrough models because they require prompt storage." / "**Allow organization's data for training**: off by default." / "**Allow passthrough models**: **on by default**. Allows models that forward prompts and responses to third-party providers." ZDR page: with ZDR on, "the content you submit … are not stored, retained, or used for model training, product improvements, or any secondary purpose, except as needed to provide the service to you"; ZDR "does not retroactively affect data processed before then"; metadata (token counts, model IDs, timestamps) and account data are still retained. Passthrough risk is explicit: "Data sent to them is handled under that provider's own policy." No free-tier-specific policy (the only "free" model is priced $0 but is served under the same privacy settings). Together's zero-price model therefore inherits the default store-and-may-use-for-improvements behaviour unless ZDR is enabled (and enabling ZDR turns off passthrough models).

### 7.7 Deprecation policy
Most explicit policy of the eight. Upgrades (same lineage): "The current endpoint redirects to the upgraded version after a **3-day notice**." New models: "No automatic redirect. Together AI announces the new model and deprecates the old one on a **2-week timeline** (both are available during this window)." Notice table: Preview model "<24 hours of notice, after 30 days"; Serverless endpoint "2 or 3 weeks"; On-demand dedicated endpoint "2 or 3 weeks" ("Depends on usage and whether a newer version of the model is available"). Notifications by email; each deprecated model gets "a specified removal date"; after removal only dedicated endpoints can keep it alive.

### 7.8 API shape
OpenAI-compatible: `base_url="https://api.together.ai/v1"` (docs), with `chat.completions.create`, `completions.create`, `embeddings.create`, `images.generate`, `audio.speech.create`, `audio.transcriptions.create`, `models.list/retrieve` all supported. Not implemented: Assistants/Threads/Runs, OpenAI-shaped Batch and Files APIs, `moderations.create`. Model IDs are namespaced (`openai/gpt-oss-120b`, `meta-llama/…`). Minor doc inconsistency: guide pages use `https://api.together.ai/v1` while model pages show `https://api.together.xyz/v1` — both appear on Together's own docs.

---

## 8. SambaNova Cloud

Sources fetched: https://docs.sambanova.ai/docs/en/models/rate-limits , https://docs.sambanova.ai/docs/en/models/sambacloud-models , https://docs.sambanova.ai/docs/en/models/deprecations , https://docs.sambanova.ai/docs/en/features/openai-compatibility , https://docs.sambanova.ai/docs/en/features/function-calling , https://docs.sambanova.ai/docs/en/features/text-generation , https://docs.sambanova.ai/docs/en/get-started/api-keys-urls , https://sambanova.ai/cloud-end-user-license-agreement , https://sambanova.ai/privacy-policy , https://cloud.sambanova.ai/plans (JS-only, no content served) , https://community.sambanova.ai/t/data-handling-and-retention/1314 — all accessed 2026-10-06.

### 8.1 Open-weight models usable at $0
Free Tier definition, verbatim: "**Free Tier**: Applied when there is no payment method linked with your account" (rate-limits page). Models with published Free Tier limits:

| Model ID | Tier | Context | Free RPM | Free RPD | Free TPD |
| --- | --- | --- | --- | --- | --- |
| `gpt-oss-120b` | Production | 128k | 20 | 20 | 200,000 |
| `Meta-Llama-3.3-70B-Instruct` | Production | 128k | 20 | 20 | 200,000 |
| `DeepSeek-V3.1` | Production | 128k | 20 | 20 | 200,000 |
| `gemma-4-31B-it` | Preview | 128k | 20 | 20 | 200,000 |
| `DeepSeek-V3.2` | Preview | 32k | 20 | 20 | 200,000 |

Not on the Free Tier: `MiniMax-M2.7` (192k) and `MiniMax-M3` (1M) appear only in the Developer/Enterprise tables.
Llama-family: `Meta-Llama-3.3-70B-Instruct` only. `Meta-Llama-3.1-8B-Instruct` was removed 4/14/2026; `Llama-4-Maverick-17B-128E-Instruct` and `gemma-3-12b-it` removed 6/9/2026 (deprecations page).
Note the hard shape of this free tier: **20 requests per day** total. With 200,000 tokens/day it is the tightest request budget of the eight; a batch of many submissions has to be packed into very few calls or it cannot run here. Developer Tier note for contrast: "Developer Tier accounts are limited to 20M tokens per day across all models."

### 8.2 Limits
See table. Measurement: "RPM: Requests per minute; RPD: Requests per day; **TPD: Tokens per day (Free tier only)**"; "You can hit either limit type (RPM or RPD) depending on which one you reach first"; status returned in every response via `x-ratelimit-*` headers. Exceedance → error (page points to API error codes). No concurrency limit published; no monthly quota; no credit concept on the Free Tier (nothing to expire — the Tier is defined by having no payment method). Separate Free-Tier note: only preview models are described as "may be removed at short notice".

### 8.3 Structured output and tool calling
`response_format` supports `json_schema` and `json_object`. Decisive limitation, verbatim: "The `strict` parameter is accepted by the API for both `true` and `false` values: **`false` is the default. It is the only value with active enforcement today; the model uses best-effort matching against your schema. `true` is accepted without error but has no additional behavioral impact at this time.**" JSON mode error if invalid: "**Model did not output valid JSON**". Tool calling supported models (page list): `Meta-Llama-3.3-70B-Instruct`, `Qwen3-235B-A22B-Instruct-2507`, `gpt-oss-120b`, `DeepSeek-V3.1`, `DeepSeek-V3.2`, `MiniMax-M2.7`, `MiniMax-M3`, `gemma-4-31B-it`. `tool_choice`: `auto` (default), `required`, `none`, or a named function; note "`n` greater than 1 is not supported when using function calling or tools – combining them returns a 400 error"; for `gpt-oss-120b`, "set the `reasoning_effort` to `high`" for better tool quality, and the Responses-API-style `tool_choice` shape is not accepted.

### 8.4 Determinism
`seed`, verbatim: "Supported on both SambaStack and SambaCloud for text generation models. **Passing the same `seed` with the same inputs produces deterministic outputs.** Accepts any integer, including negative values." Caveats on the same page: "Unlike OpenAI, the SambaNova API does not return a `system_fingerprint` field in the response. **The `seed` parameter is not supported for multi-modality models or continuous batching (CB) models.**" `temperature` supported; `presence_penalty` and `frequency_penalty` "are not yet supported and will be ignored".

### 8.5 Context length
gpt-oss-120b 128k; Meta-Llama-3.3-70B-Instruct 128k; DeepSeek-V3.1 128k; gemma-4-31B-it 128k (text/image/video; "Audio input is not supported for this model"); DeepSeek-V3.2 32k; MiniMax-M2.7 192k; MiniMax-M3 1M. Sourced from the SambaCloud models spec table.

### 8.6 Data use — free tier
License agreement (SambaCloud ToS) §2.1: Customer Content is licensed to SambaNova "solely to the extent necessary to provide the Service to you or as may be required by law, **and for no other purposes**." §5.2: "We may collect and use query logs, and any data (but not Customer Content) relating to the operation, support and/or use of the Service ('Service Usage Data')" — i.e. telemetry explicitly excludes Customer Content. The provider's own developer-forum answer (2025-08-18, SambaNova staff) states: "**By default, input tokens and prompts sent to the API are not stored or archived and are not used for training or fine-tuning.**" Gaps: (a) no retention period for API request content is published anywhere — the website privacy policy covers website/account data only and says it "does not apply to Personal Data we process in our role as a data processor"; (b) the community answer is a forum post, not a policy document; (c) the ToS grants an "access, store and/or process" right during service provision, so transient processing is permitted; (d) the ToS is dated 2024-08-27-era and the publicly reachable copy carries no "last updated" line for the data clauses. Retention window: `[UNVERIFIED]`.

### 8.7 Deprecation policy
Verbatim: "**Production models**: Production models will receive a deprecation notice of at least **two to three weeks**." / "**Preview models**: Preview models may graduate to Production or be deprecated with short notice." Notifications by email plus the deprecations page; each entry lists model ID, removal date, and recommended replacement (examples: 6/9/2026, 5/18/2026, 4/14/2026, 4/6/2026, 3/20/2026…). No version-pinning guarantee is published (IDs are version-bearing, e.g. `DeepSeek-V3.1`).

### 8.8 API shape
OpenAI-compatible: `base_url="https://api.sambanova.ai/v1"` (API keys and URLs page: "Base URL (to be used with the OpenAI client, for example)"), with `POST /v1/chat/completions`; also a Responses endpoint and an Anthropic Messages API. Documented divergences: `presence_penalty`/`frequency_penalty` ignored; `n` supports 1–8 (OpenAI has no hard cap); `top_k` not expressible via OpenAI clients; `system_fingerprint` absent; **`seed` unsupported on multimodal and continuous-batching models** (check per model before relying on it for reproducibility).

---

## 9. Comparison table (free position only)

| Provider | Free RPM | Free RPD | Free tokens/day | Concurrent limit | Monthly free quota / credit expiry | Data use on free tier | Seed support | OpenAI-compatible base URL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Groq | 30 (gpt-oss-120b/20b, qwen3.8-27b; 3 for safeguard) — free-tier attribution `[UNVERIFIED]` (page calls the row "Developer plan") | 1,000 | 200K TPD (+8K TPM) — same caveat | not published | not published / no credit scheme | Not trained on; no retention except to operate/legal/AUP-compliance; ZDR opt-in. (Services Agreement §4.2) | `seed`, best-effort only; `temperature: 0` rewritten to `1e-8` | Yes — `https://api.groq.com/openai/v1` |
| Cerebras | 5 (both models) | not published (1M TPD) | 1M TPD; 30K uncached TPM; 1M TPH | not published | $5 credit, expires **30 days**; no permanent free tier | Not retained, not used for training/fine-tuning (Privacy §6, ToS) | `seed`, best-effort; `system_fingerprint` returned | Yes — `https://api.cerebras.ai/v1` |
| Google (Gemma free tier) | `[UNVERIFIED]` (view in AI Studio) | `[UNVERIFIED]` (RPD resets midnight PT) | `[UNVERIFIED]` | not published | none; AI Studio free, no expiry | **Used to improve products; human reviewers may read input/output; "Do not submit sensitive, confidential, or personal information"** (Unpaid Services terms) | `seed` field exists; unset = random | OpenAI endpoint exists for Gemini; Gemma compatibility `[UNVERIFIED]` |
| GitHub Models | n/a | n/a | n/a | n/a | n/a | **Retired 2026-07-30 — no service** | n/a | n/a |
| Mistral (Free mode) | `[UNVERIFIED]` (Admin Panel only) | `[UNVERIFIED]` | `[UNVERIFIED]` | not published | $10/mo included API credits (Free plan) | "we may use your data (input and output) to train our AI models"; API opt-out toggle exists (pricing table vs help article **disagree**); Labs models: no opt-out | `random_seed` documented as producing deterministic results | Yes — `https://api.mistral.ai/v1` |
| Cloudflare Workers AI | 300 (text generation, all models not paid-only); 20/50 for paid-only models | reset 00:00 UTC (daily neuron cap) | ≈0.31M–1.1M input tokens/day depending on model (arithmetic from neuron rates) | not published | 10,000 Neurons/day, resets daily; no expiry | "does not use your Customer Content to (1) train any AI models … or (2) improve any Cloudflare or third-party services … unless we received your explicit consent" | `seed` 1…9999999999, "Random seed for reproducibility" | Yes — `.../accounts/{id}/ai/v1` |
| Together AI | not published | not published | not published (best-effort, 429/503) | not published | **no free trial; $5 minimum purchase**; $0-priced models only (`Ternary-Bonsai-27B`) | Default: stored and "may use them for product improvements"; training opt-in off; **passthrough on by default**; ZDR is opt-in | `seed`, best-effort, "not guaranteed across replicas, model versions, or load conditions" | Yes — `https://api.together.ai/v1` |
| SambaNova Cloud | 20 | **20** | 200K TPD | not published | none (tier defined by having no payment method) | Customer Content usable only "to provide the Service … and for no other purposes"; telemetry excludes it; no published retention window; forum: not stored/trained | `seed` → deterministic, but **unsupported on multimodal and continuous-batching models**; no `system_fingerprint` | Yes — `https://api.sambanova.ai/v1` |

Model-level summary of free open-weight availability (what is actually callable at $0 today):

| Provider | Free chat LLMs | Llama-family free? | Notable large-context free option |
| --- | --- | --- | --- |
| Groq | gpt-oss-120b, gpt-oss-20b, gpt-oss-safeguard-20b, qwen3.8-27b (minimax-m2.7 preview) | No (3.1/3.3/4 IDs retired per deprecation page) | 131K (gpt-oss, qwen3.8) |
| Cerebras | gpt-oss-120b, qwen-3.8-27b — **but only for 30 days / $5** | No | 65K free / 131K paid |
| Google | Gemma 4 free tier (model ID `[UNVERIFIED]`); Gemini models also have a free tier | No | Gemma medium 256K |
| GitHub Models | none (retired) | n/a | n/a |
| Mistral | all listed open-weight Mistral models within $10/mo included credits (Large 3 Apache-2.0, Small 4, Ministral 3, Medium 3.5, GLM 5.3) | No | 256K (Large 3, Small 4, Ministral 3) |
| Cloudflare | gpt-oss-120b/20b, gemma-4-26b-a4b-it, llama-3.3-70b-fp8-fast, llama-3.1-8b-fp8, gemma-sea-lion-v4-27b-it (Indonesian), qwen3.8-27b, mistral-small-3.1-24b, glm-4.7-flash, granite-4.0-h-micro | Yes, but two Llama IDs sit in a live deprecation contradiction and 70B free context is 24K | gemma-4-26b-a4b-it 256K |
| Together AI | `Prism-ML/Ternary-Bonsai-27B` ($0.00/$0.00) | No (free Llama endpoints removed 2025-11-13 / 2026-03-06) | 262K (Ternary-Bonsai-27B) |
| SambaNova | gpt-oss-120b, Meta-Llama-3.3-70B-Instruct, DeepSeek-V3.1, gemma-4-31B-it (preview) | Yes, Llama 3.3 70B at 20 requests/day | 128K |

---

## 10. Not verified / gaps

1. **Groq free-tier rate limits** — the numbers in the rate-limits doc table (30 RPM / 1K RPD / 8K TPM / 200K TPD) are labelled on the same page as "base limits for the Developer plan", while the models page's Developer-plan column says 1K RPM / 250K TPM. Exact per-org limits are only on the login-gated `console.groq.com/settings/limits` page. `[UNVERIFIED]` which tier owns those values.
2. **Google free-tier rate limits** — no public RPM/TPM/RPD table; the rate-limits page only links to the AI Studio rate-limit view (login) and says "Specified rate limits are not guaranteed and actual capacity may vary".
3. **Google Gemma in the Gemini API** — Gemma 4 appears in the pricing table (free tier only) but in no model catalog entry; `…/docs/models/gemma-4-31b-it` 404s; no Gemma mention on the structured-output or function-calling docs pages. Model ID, endpoint, context, RPM/RPD, and JSON-schema/tool support via that API are all `[UNVERIFIED]`.
4. **Cloudflare deprecation policy** — no policy page; only changelog entries (≈2–3 week notices observed) and one documented automatic alias redirect to a different-priced model. No guaranteed notice period published.
5. **Cloudflare model-catalog contradiction** — changelog says `@cf/meta/llama-3.1-8b-instruct`, `-awq`, llama-3.1-70b, llama-3-8b, gemma-3-12b-it were deprecated 2026-05-30, yet the 2026-10-01 pricing page still lists several of them. Which are live today could not be resolved from docs; runtime `/v1/models` would settle it (needs an account).
6. **Together AI model-catalog contradiction** — deprecations page says `openai/gpt-oss-20b` and `google/gemma-4-31B-it` left serverless on 2026-09-15, while the pricing page still lists Gemma 4 31B with prices. Together's own docs say to trust the deprecations page over listings.
7. **Together AI gpt-oss-120b context window** — not shown on the pricing page; the model page was not fetched, so that one figure is `[UNVERIFIED]` here.
8. **Mistral Free-mode limits** — RPM/TPM per model and device/concurrency caps are only in the Admin Panel (`admin.mistral.ai/plateforme/limits`). Public pages state none.
9. **Mistral free-tier training opt-out** — Mistral's pricing-page plan table leaves the Free column's "Model training" cell blank while Pro/Team/Enterprise show "Opt-out", yet the help-centre opt-out article documents an API/Studio opt-out ("Anonymous improvement data"). Which applies to Free mode on La Plateforme today is `[UNVERIFIED]`.
10. **SambaNova retention** — no published retention period for API request content; the only direct statement is a 2025-08-18 developer-forum answer by SambaNova staff. The website privacy policy explicitly does not cover processor-role data. `[UNVERIFIED]` as policy-level evidence.
11. **No provider publishes a concurrent-request limit** — the column is empty for all eight by absence of documentation, not by confirmation.
12. **Groq Llama mismatch** — models page still lists `llama-3.1-8b-instant` / `llama-3.3-70b-versatile` (Enterprise pricing) while the deprecation page records shutdown 2026-08-16. `[UNVERIFIED]` whether either ID still answers today.
13. **Free-tier data-use differentiation** — only Google and Mistral publish *different* data handling for unpaid usage (worse than paid). Groq, Cerebras, Cloudflare, SambaNova, and Together publish one policy for all tiers; for Groq the API-content terms live in the Services Agreement + DPA, not the privacy policy, and for SambaNova/Together the operative text sits in a ToS/forum answer respectively.
14. **Not fetched / out of scope** — Mistral Large 4 specific context window; per-model context for two Together models; GitHub Models' retired terms (service gone); Gemini per-model free-tier numbers behind login. Nothing in this report relies on training-memory values.
