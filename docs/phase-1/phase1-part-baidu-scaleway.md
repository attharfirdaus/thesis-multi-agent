# Phase-1 evidence: Baidu Qianfan + Scaleway Generative APIs

Access date for every URL below: **2026-10-06**. Quotes are verbatim from the live pages fetched today. Baidu pages are Chinese-only (Gatsby/JS-rendered); content was read from the page's own embedded `page-data.json` served by Baidu's CDN (`bce.bdstatic.com`), which is the same markup the HTML page renders. That is noted where relevant. Anything not confirmed on a live page is marked `[UNVERIFIED]`.

---

## 1. Baidu Qianfan (百度千帆 / 百度智能云)

Product: `cloud.baidu.com/doc/qianfan` (Chinese only) and `intl.cloud.baidu.com` (English marketing, no free-tier or API detail). Docs are Gatsby SPAs; raw HTML has no body text, so content was read from the page's own `page-data.json`.

### (a) Free model IDs available today

The authoritative free-quota page is **新用户免费额度** (slug `Imi2rpirg`), page self-date **更新时间：2025-11-17**.
URL: https://cloud.baidu.com/doc/qianfan/s/Imi2rpirg (JSON: https://bce.bdstatic.com/p3m/bce-doc/online/qianfan/doc/qianfan/s/page-data/Imi2rpirg/page-data.json)

The page lists **17 models, each 1,000,000 (100万) free Tokens, valid 3 months (有效期 3个月)**, granted on first activation:

ERNIE-4.5-Turbo-128K, ERNIE-4.5-Turbo-32K, ERNIE-4.5-Turbo-VL, ERNIE-X1-Turbo-32K, DeepSeek-R1, DeepSeek-R1-250528, DeepSeek-V3-250324, DeepSeek-V3.1-250821, DeepSeek-V3.1-Think-250821, Kimi-K2-Instruct, Qwen3-235B-A22B-Instruct-2507, Qwen3-30B-A3B-Instruct-2507, Qwen3-Coder-30B-A3B-Instruct, Qwen3-Coder-480B-A35B-Instruct, bge-large-en, bge-large-zh, qianfan-sug-8k.

**The free-quota page is stale.** Cross-checking against the live model list (slug `rmh4stp0j`, self-date **更新时间：2026-09-16**, https://cloud.baidu.com/doc/qianfan/s/rmh4stp0j) and the shutdown notice (slug `zmrykcisj`, self-date 2026-07-24, https://cloud.baidu.com/doc/qianfan/s/zmrykcisj):

| Free-quota ID | Still in live model list 2026-09-16? |
|---|---|
| ERNIE-4.5-Turbo-128K (`ernie-4.5-turbo-128k`) | Yes |
| ERNIE-4.5-Turbo-32K (`ernie-4.5-turbo-32k`) | Yes |
| ERNIE-4.5-Turbo-VL (`ernie-4.5-turbo-vl`) | Yes |
| bge-large-en / bge-large-zh | Yes |
| ERNIE-X1-Turbo-32K | No — retired; shutdown notice lists "ERNIE-X1-Turbo-32K ... 2026-07-28" |
| qianfan-sug-8k | No — Qianfan-Sug-8K listed "下线"/retired |
| DeepSeek-R1, DeepSeek-R1-250528, DeepSeek-V3-250324, DeepSeek-V3.1-250821, DeepSeek-V3.1-Think-250821 | No — not in current list (current list has DeepSeek-V3.2 / V4 only) |
| Kimi-K2-Instruct | No — current list has only Kimi-K2.6 marked "即将下线" |
| Qwen3-235B-A22B-Instruct-2507, Qwen3-30B-A3B-Instruct-2507, Qwen3-Coder-30B-A3B-Instruct, Qwen3-Coder-480B-A35B-Instruct | No — current list has Qwen3.5 family only |

So: **4 free-quota models (ernie-4.5-turbo-128k, ernie-4.5-turbo-32k, ernie-4.5-turbo-vl, bge-large-en/zh) are confirmed still in the catalogue; the rest of the 17 appear retired or absent.** Whether the free Tokens are still granted for exactly these is `[UNVERIFIED]` — no page updated after 2025-11-17 states the current free set.

Historic "permanently free" tier (ERNIE-Speed/ERNIE-Lite/ERNIE-Tiny) is **gone**: the 2026-06-30/2026-07-28 shutdown notice lists ERNIE-Speed-Pro-128K, ERNIE-Speed-Pro-8K, ERNIE-Lite-128K, ERNIE-Lite-Pro-8K, ERNIE-Lite-Pro-128K, ERNIE-Lite-8K-0922, ERNIE-3.5-8K, ERNIE-4.0-8K etc. as retired. (Aggregator claims of "ERNIE-3.5-8K/ERNIE-Speed-8K permanent free" are outdated.)

### (b) Free-tier quota, credit amount, expiry

Verbatim (free-quota page `Imi2rpirg`):
- "2025年10月24日0点起，访问千帆大模型平台，阅读并同意用户协议后，系统将自动开通千帆大模型平台并发放新用户免费Tokens额度。"
- "新用户免费额度仅支持抵扣预置模型服务在线推理（调用）消耗的Tokens，不支持抵扣批量推理（调用）消耗的Tokens。"
- "首次开通千帆大模型时，平台将自动发放指定模型的免费使用额度，赠送服务范围、Tokens量以及有限期如下表所示：" — table: **1,000,000 Tokens per model, 有效期 3个月 (3 months)**.

No credit (cash) amount and no expiry start rule beyond "3 months" is stated on that page. No separate free-tier daily/RPM cap is stated on the free-quota page; the per-model default flow control in the model list applies (see (b) rate limits below).

### (b) Rate limits (default flow control, model list `rmh4stp0j`, 2026-09-16)

| Model | RPM | TPM |
|---|---|---|
| `ernie-4.5-turbo-128k` | 5000 | 400,000 |
| `ernie-4.5-turbo-32k` | 5000 | 400,000 |
| `ernie-4.5-turbo-vl` | 1000 | 200,000 |
| `ernie-5.0` / `ernie-5.1` | 60 | 150,000 |
| `deepseek-v4-pro`, `deepseek-v4.1-flash` | 60 | 1,000,000 |
| `qwen3.5-397b-a17b` etc. | 60 | 250,000 |
| `glm-5.2`, `glm-5.3` | 60 | 1,000,000 |

Response headers expose `X-Ratelimit-Limit-Requests`, `X-Ratelimit-Limit-Input-Tokens`, `X-Ratelimit-Limit-Output-Tokens` (text-gen API doc, see (h)).

### (c) Structured output + tool/function calling

Text-generation API doc `文本生成` (slug `3m7of64lb`, https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb), body `POST https://qianfan.baidubce.com/v2/chat/completions`:
- `response_format.type`: values `json_object`, `text` (default), `json_schema`; `json_schema` field takes a JSON Schema. Note in doc: "(2) 不支持以下模型：ERNIE X1 Turbo系列".
- `tools` (array) + `tool_choice` (`none`/`auto`/`required`/specific function) + `parallel_tool_calls` (default true). Supported-model list is linked to "Function calling-支持模型范围".
- No `functions` (legacy) parameter.

### (d) Seed + determinism

Same API doc, `seed` (integer, optional) — verbatim:
- "（1）取值范围: （0,2147483647），会由模型随机生成，默认值为空"
- "（2）如果指定，系统将尽最大努力进行确定性采样，以便使用相同seed和参数的重复请求返回相同的结果"
- "（3）不支持以下模型：· ERNIE X1 Turbo系列 · Qwen2.5 · Qianfan-Agent-Intent"

So `seed` is accepted and documented as **best-effort** deterministic ("尽最大努力" = best effort), not guaranteed.

### (e) Context length (live model list `rmh4stp0j`, 2026-09-16)

| Model | Context | Max output |
|---|---|---|
| ERNIE 5.0 / 5.1 | 128k | 65536 |
| ERNIE 4.5 Turbo 32k / 128k | 32k / 128k | 12288 |
| ERNIE 4.5 Turbo VL | 128k | 16384 |
| DeepSeek-V4 / V4.1-flash | 1M | 393216 |
| DeepSeek-V3.2 | 128k | 32k |
| Qwen3.5 (397B/122B/27B/35B-A3B) | 256k | 65536 |
| GLM-5.2 / 5.3 | 1M | 131072 |
| Kimi-K2.6 | 256k | 262144 |

### (f) DATA-USE on the free tier

No free-tier-specific data-use clause exists on any page fetched. The default platform terms apply:

**User agreement** `百度千帆大模型服务及Agent开发平台用户协议` (slug `Cmh4stmpy`, self-date 2026-01-08, 协议生效时间：2026年01月09日, https://cloud.baidu.com/doc/qianfan/s/Cmh4stmpy) — §5.1(6), verbatim:
> "您在使用千帆平台进行模型推理服务时，其产生的输入、输出数据，以及上传到平台的各类知识文档、数据集，为您的用户数据，仅限您账号下在本服务中使用，除执行您的服务要求外，我们不进行任何未获授权的使用及披露。为免疑义，我们不会使用您的输入和模型输出数据、上传的知识文档、数据集进行训练，也不会将您的数据集与任何第三方共享。"

Same doc §13.2, verbatim:
> "为遵守国家法律法规要求并保障服务质量，您已充分知悉并同意授权我们，在按照符合法律法规要求的方式对本服务相关数据进行处理的前提下，将相关数据应用于服务性能优化、系统故障排查及风险控制管理等。"

Same doc §4.11, verbatim:
> "为履行法定合规要求，我们有权采取技术手段或人工手段对您使用本服务的行为及信息进行审查，包括但不限于对输入和输出进行审查、建立风险过滤机制、建立违法内容特征库等。"

**专项约定** (slug `emh4stmvj`, self-date 2025-10-30) §2.4: same "不会使用您上传的知识文档、数据集进行训练，也不会将您的数据集与任何第三方共享" wording; §2.5 adds that for AI applications/Agents, user input/output is not used or disclosed without lawful authorization.

**大模型技术体验服务协议 (technical-experience service agreement)** (slug `jmh4stmn3`, self-date 2025-10-29, https://cloud.baidu.com/doc/qianfan/s/jmh4stmn3) — this is the trial/experience agreement, §1.3, verbatim:
> "您同意百度有权在为您提供本合同所述服务及优化本合同所述服务效果的范围内对数据进行处理。"
(i.e. Baidu may process data within the scope of providing **and optimizing** the service.) Whether the new-user free Tokens fall under this "技术体验服务" agreement or only the general user agreement is not stated on any fetched page → `[UNVERIFIED]`.

**隐私政策 (privacy policy)** (slug `Plr0fi68q`, self-date 2026-04-23, https://cloud.baidu.com/doc/Agreements/s/Plr0fi68q) §8 您的业务数据, verbatim:
> "您通过百度智能云提供的服务，加工、存储、上传、下载、分发以及通过其他方式处理的数据，均为您的用户业务数据，您完全拥有您的业务数据。百度智能云作为中立的技术服务提供者，会严格执行您的委托和指示，除按与您协商一致或依据特定产品规则或基于您的要求为您提供技术协助进行故障排除或解决技术问题或执行明确的法律法规要求外，我们不对您的业务数据进行任何非授权的访问、使用或披露。"

Verdict: **no training on prompts/outputs claimed; retention/human review is possible for compliance review (4.11) and service-optimization use is authorized (13.2); the trial-service agreement adds "optimizing service" data processing.** No free-tier carve-out found.

### (g) Deprecation / versioning policy

`模型版本升级及退役机制` (slug `zmh4stou3`, self-date **2026-09-24**, https://cloud.baidu.com/doc/qianfan/s/zmh4stou3), verbatim:
- Preview models: "preview模型滚动升级不会提前通知用户" (no advance notice).
- Undated mainline models roll to a new dated version with "提前1~2周发送通知" (1–2 weeks notice).
- Dated versions: "带日期版本预置服务，其生命周期一般为3~6个月" (typically 3–6 months lifetime).
- Retirement: "新模型版本上线，已有模型版本退役，都会提前以短信、站内信等方式通知到用户。" and "受影响的客户将始终通过短信、邮件、官方文档等方式得到通知".
- Live model list also tags models "（即将下线）".

Worked example of enforcement: `7月28日服务停服通知` (slug `zmrykcisj`, 2026-07-24) — "您当前仍在使用的部分 ERNIE 和 Qianfan 系列模型已于 2026 年 6 月 30 日正式下线，目前处于下线过渡期，服务暂可继续调用，我们将于 2026 年 7 月 28 日完成停服处理".

### (h) OpenAI-compatible base URL

Verbatim (Token 福利包 doc, slug `Smoghsq3g`, self-date 2026-09-30, https://cloud.baidu.com/doc/qianfan/s/Smoghsq3g):
> "兼容 OpenAI 接口协议的Base URL：`https://qianfan.baidubce.com/v2`，如果是接口调用，完整路径为：`https://qianfan.baidubce.com/v2/chat/completions`"

Also the text-gen API doc's debug URL is `https://qianfan.baidubce.com/v2/chat/completions`. Anthropic-compatible base (same page): `https://qianfan.baidubce.com/anthropic`.

---

## 2. Scaleway Generative APIs (Serverless)

English-only. All primary, first-party pages.

### (a) Free-model IDs available today

The free tier is **credit-based across the whole Serverless catalogue**, not a "free model" list. The Serverless catalogue (live, `supported-models` page, self-date validation 2026-08-14, https://www.scaleway.com/en/docs/generative-apis/reference-content/supported-models/) and the live pricing table (https://www.scaleway.com/en/pricing/model-as-a-service/):

`glm-5.2`, `deepseek-v4-flash-0731`, `qwen3.8-27b`, `gemma-4-26b-a4b-it`, `mistral-medium-3.5-128b`, `whisper-large-v3`, `llama-3.3-70b-instruct`, `qwen3-235b-a22b-instruct-2507`, `qwen3-coder-30b-a3b-instruct`, `qwen3-embedding-8b`, `pixtral-12b-2409`, `mistral-small-3.2-24b-instruct-2506`, `gpt-oss-120b`, `bge-multilingual-gemma2`, `qwen3.6-35b-a3b`, `qwen3.5-397b-a17b`.

Every one of these is deductible from the same free allowance ("The Free Tier is applied to the most expensive tokens first"). EOL/deprecated Serverless models exist too (`llama-3.1-70b-instruct`, `mistral-small-3.1-24b-*`, `qwen2.5-coder-32b-instruct`, `deepseek-r1-distill-llama-70b`, `gemma-3-27b-it`, `pixtral-12b-2409`, `qwen3-coder-30b-a3b-instruct`, `voxtral-small-24b-2507`, `devstral-2-123b-instruct-2512`, `holo2-30b-a3b`) — several already past EOL.

### (b) Free-tier quota, credit amount, expiry

- Pricing page (https://www.scaleway.com/en/pricing/model-as-a-service/): "Try out new models with our free tier: 1 million tokens and 60 minutes of audio transcription." and "You benefit from a free tier on the first 1,000,000 tokens. You'll be charged from token number 1,000,001."
- FAQ `How does the Free Tier work?` (https://www.scaleway.com/en/docs/generative-apis/faq/, self-date validation 2026-04-13), verbatim: "There is a Free Tier available for *Serverless*. The Free Tier allows you to process, without incurring any costs, up to: - 1,000,000 tokens for models billed by tokens - 60 minutes of audio transcription for models billed by audio minutes". Also: "The Free Tier is applied to the most expensive tokens first. The minimum billing unit is 1,000 tokens."
- Corporate credit: signup page (https://www.scaleway.com/en/generative-apis-signup/): "Get started with **€100 free credit** when you create a **Business** account."
- **Expiry: not stated on any fetched page** → `[UNVERIFIED]`. Free tier is described as a first-N-tokens allowance, not time-limited.

### (b) Rate limits (Serverless)

`rate-limits` page (self-date validation 2026-04-24, https://www.scaleway.com/en/docs/generative-apis/reference-content/rate-limits/) and Organization-quotas page (self-date validation 2025-10-29, https://www.scaleway.com/en/docs/organizations-and-projects/organization/organization-quotas/):

| Limit | Payment method validated | Payment method + identity validated |
|---|---|---|
| Tokens/min (per model) | 200k–2000k (e.g. `glm-5.2` 200k → 1,000k) | — |
| Requests/min (per model) | 300 | 600 |
| Concurrent requests (all models) | 100 | 100 |
| Concurrent batches | 20 | 100 |
| Audio seconds/min | 1800 | 3600 |

"Base limits apply if you registered a valid payment method, and they are increased automatically if you also verify your identity." Batches API has no rate limit and a −50% price discount. Rate-limit headers: `x-ratelimit-limit-requests`, `x-ratelimit-limit-tokens`, etc.

### (c) Structured output + tool/function calling

- Structured outputs (`use-structured-outputs`, self-date validation 2025-08-22, https://www.scaleway.com/en/docs/generative-apis/how-to/use-structured-outputs/): JSON Schema mode `{"type": "json_schema"}` — "This mode enforces a strict schema format... Supports complex types and validation mechanisms as per the JSON schema specification, including nested schemas composition (`anyOf`, `allOf`, `oneOf` etc), `$ref`, `all` types, and regular expressions." Plus legacy `{"type": "json_object"}`. "All LLMs in the Scaleway library support **Structured outputs** and **JSON mode**."
- Function calling (`use-function-calling`, self-date validation 2025-08-22, https://www.scaleway.com/en/docs/generative-apis/how-to/use-function-calling/): "All the [chat models] ... hosted by Scaleway support function calling." `tools` + `tool_choice` supported; parallel tool calls supported but "Meta models do not support parallel tool calls."
- API reference (https://www.scaleway.com/en/developers/api/generative-apis, docs version v1.8929.0): `/v1/chat/completions` "Supports many features such as: Structured outputs (JSON response format); Tool calling ...; Sending and analyzing images; Sending and analyzing audio files". Unsupported params include `user`, `store`, `metadata`, `prompt_cache_key`, `web_search_options`. Only `function` tools, no `custom` tools.

### (d) Seed + determinism

Seed **is documented as deterministic (best-effort)** in the official OpenAPI schema (`https://www.scaleway.com/en/developers/api/generative-apis/v1/schema.yml`, downloaded 2026-10-06), verbatim:
> "Value which controls the randomness of the output to ensure determinism.\nWhen using the same seed value along with identical input and parameters,\nyou should receive the same model response each time. This holds true even when\ntemperature is set above 0.\n\nNote that fully deterministic output is not guaranteed over long periods of time (such\nas several months), as the inference model may be updated and optimized."

Also the `Temperature` schema: "Note that `temperature` does not affect request reproducibility (only affected by the `seed` parameter). With the same `seed` and `temperature`, two identical requests to a model will generate the same response." `seed` is in the supported-parameters list of the OpenAI-compatibility doc (self-date validation 2026-04-24, https://www.scaleway.com/en/docs/generative-apis/reference-content/openai-compatibility/).

### (e) Context length (supported-models page, 2026-08-14)

| Model | Max context | License |
|---|---|---|
| glm-5.2 | 256k (1M capable; preview cap) | MIT |
| deepseek-v4-flash-0731 | 256k (1M capable; preview cap) | MIT |
| qwen3.8-27b | 256k | Apache 2.0 |
| qwen3.6-35b-a3b | 256k | Apache 2.0 |
| qwen3.5-397b-a17b | 250k | Apache 2.0 |
| qwen3-235b-a22b-instruct-2507 | 250k | Apache 2.0 |
| qwen3-coder-30b-a3b-instruct | 128k | Apache 2.0 |
| gemma-4-26b-a4b-it | 256k | Apache 2.0 |
| gpt-oss-120b | 128k | Apache 2.0 |
| llama-3.3-70b-instruct | 100k (Serverless) | Llama 3.3 Community |
| mistral-medium-3.5-128b | 180k (1M capable; preview cap) | Modified MIT |
| mistral-small-3.2-24b-instruct-2506 | 128k | Apache 2.0 |
| pixtral-12b-2409 | 128k | Apache 2.0 |
| devstral-2-123b-instruct-2512 | 200k (Serverless) | Modified MIT |
| holo2-30b-a3b | 22k | CC-BY-NC-4.0 |
| qwen3-embedding-8b | 32k | Apache 2.0 |

Serverless max output is capped per model (e.g. qwen3.6/qwen3.8/gpt-oss 32k, qwen3.5-397b 16k); "you cannot increase the maximum number of output tokens beyond the limits for each model".

### (f) DATA-USE

`Understand the Generative APIs Privacy Policy` (self-date validation **2025-10-03**, https://www.scaleway.com/en/docs/generative-apis/reference-content/data-privacy/), verbatim:
> "By default we apply a Zero Data Retention Policy, collecting only data required to provide the service reliably and securely."
> "Parameters defined by the user, **excluding the actual content of the prompts (system, user, etc.)**"
> "We do not collect, read, reuse, or analyze the content of your inputs, prompts, or outputs generated by the API. The only exception being when your traffic harms our service operations or your resource availability such as generating abnormal errors - like HTTP 500 errors - or may represent malicious activity. In this case, we may store temporarily the corresponding HTTP request content to identify and fix root cause issues or any security vulnerability."
> "Your data is not accessible to the creators of the underlying large language models (LLMs). Your data is not used for training, retraining, or improving the base models."
> "Your personal data may be stored in the following region: Paris, France."
> "As a European company, Scaleway's AI services are not subject to extraterritorial laws such as the American Cloud Act."

Exception window: "Data is stored for up to two weeks, only to reproduce, investigate, and fix the underlying issue." API usage data (anonymized) retained "up to 6 months". Same policy applies to free tier — **no free-tier-specific carve-out** (the page does not distinguish paid vs free).

**Hosting region (explicit):** FAQ — "All *Serverless models* are currently hosted in a secure data center located in Paris, France, operated by [OPCORE](https://www.opcore.com/). ... we will continue to guarantee that *Serverless models* accessible through `api.scaleway.ai` remain hosted in Europe." API reference: region `fr-par` (Paris).

### (g) Deprecation / versioning policy

`Understand Generative APIs model lifecycle` (self-date validation 2026-04-24, https://www.scaleway.com/en/docs/generative-apis/reference-content/model-lifecycle/), verbatim:
> "We guarantee support for new models in `Active` status for at least 8 months starting from their regional launch. Customers will receive a 3-month notice before any model is marked as End-of-Life (EOL)."
> "We guarantee support for new models in `Preview` status for at least 1 month starting from their regional launch. Customers will receive a 1-month notice before any `Preview` model is removed from Generative APIs."

Statuses: Preview / Active / Deprecated / EOL. Deprecated models keep working until their EOL date, and traffic may be auto-redirected to a replacement model. Live EOL table (supported-models page) lists dates, e.g. `pixtral-12b-2409` EOL 2026-10-01, `qwen3-coder-30b-a3b-instruct` EOL 2026-10-01, `gemma-3-27b-it` EOL 2026-08-01.

### (h) OpenAI-compatible base URL

**`https://api.scaleway.ai/v1`** — verbatim from Quickstart (self-date validation 2026-04-16, https://www.scaleway.com/en/docs/generative-apis/quickstart/): `base_url="https://api.scaleway.ai/v1", # Scaleway's Generative APIs - Serverless service URL`. Same URL in signup page, OpenAI-compatibility doc, and API reference.

---

## Not verified / gaps

1. **Baidu free-tier model list is stale (2025-11-17)** — no page updated after that date confirms the current exact set of models that receive the 1M free Tokens. 4 of 17 IDs confirmed still in catalogue; the rest appear retired. `[UNVERIFIED]` which IDs currently receive free Tokens.
2. **Baidu free-tier-specific data-use** — no clause found; general user-agreement / privacy-policy terms reported. Whether new-user free Tokens are governed by 用户协议 or the 大模型技术体验服务协议 is not stated. `[UNVERIFIED]`.
3. **Baidu free-tier-specific rate limits** — free-quota page states none; only per-model default flow control is published. `[UNVERIFIED]` whether free Tokens are additionally rate-limited.
4. **Baidu free quota "credit amount"** — no cash credit value published (only Token amounts). The 50元 experience credit seen on aggregators could not be confirmed on a Baidu page.
5. **Baidu docs are Chinese-only.** All Baidu quotes above are Chinese; English `intl.cloud.baidu.com` carries marketing only.
6. **Baidu page dates** are the docs' self-declared "更新时间"; the free-quota page's last update (2025-11-17) predates the 2026-06-30/07-28 model shutdowns.
7. **Scaleway free-tier expiry** — never stated; `[UNVERIFIED]` whether the 1M tokens expire.
8. **Scaleway €100 Business credit** — conditions/expiry not stated on the signup page. `[UNVERIFIED]`.
9. **Scaleway stale FAQ text** — the signup page FAQ still contains an outdated block: "This service is totally free while in beta. Once in general availability stage, Generative APIs will be with a 'pay-as-you-go' pricing" — this **contradicts** the current free-tier + per-token pricing on the same page and on the pricing page. Treat as stale marketing copy.
10. **Scaleway free tier vs payment method** — rate-limit docs say base limits require a valid payment method; whether the 1M free tokens require a payment method is not explicitly stated. `[UNVERIFIED]`.
11. Model IDs in Scaleway's supported-models table are plain names; their per-model API `model` strings sometimes differ (e.g. `qwen/qwen3.6-35b-a3b:bf16`), shown only for a few models.
