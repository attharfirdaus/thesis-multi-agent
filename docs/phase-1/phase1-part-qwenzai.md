# Phase-1 Evidence: Alibaba Cloud Model Studio / DashScope (Qwen) + Z.ai / Zhipu AI (GLM)

Access date for every URL below: **2026-10-06**. All "current" facts were fetched live today. Quotes are verbatim (short decisive sentences).

---

## Provider A — Alibaba Cloud Model Studio (Bailian) / DashScope (Qwen)

Three deployment scopes appear in the docs: **International** (Singapore region is the free-tier one), **Global**, and China. Free quota is granted **only** in the Singapore region and only to models whose service deployment scope is "International".

### (a) Exact free-model IDs available today

The pricing page gives every Qwen text model its own independent free quota column. Confirmed free-quota (1,000,000-token) Qwen models in the Singapore/International tables today include:

| Family | Free-quota model IDs confirmed on the live pricing page |
|---|---|
| Qwen-Max | `qwen3.8-max`, `qwen3.8-max-0902`, `qwen3.7-max`, `qwen3.7-max-2026-06-08`, `qwen3.7-max-2026-05-20`, `qwen3.7-max-preview` |
| Qwen-Plus | `qwen3.7-plus`, `qwen3.7-plus-2026-05-26` (and other dated plus snapshots) |
| Qwen-Flash | `qwen3.7-flash`, `qwen3.7-flash-2026-07-15`, `qwen3.8-flash` |
| Qwen-Coder | `qwen3-coder-plus` (= `qwen3-coder-plus-2025-09-23`), `qwen3-coder-flash` (= `qwen3-coder-flash-2025-07-28`) |
| Qwen open-source | `qwen3.8-2.4t-a95b`, `qwen3.8-27b`; the page also has "Qwen3.6 / Qwen3.5 / Qwen3 / Qwen3-Coder open-source" tables with free-quota columns |

Note: the "open-source" families (Qwen3.8 / 3.6 / 3.5 / Qwen3 / Qwen3-Coder) are served as hosted models in Model Studio and carry the same 1M free-token scheme; the legacy "Qwen3" and "Qwen3-Coder" open-weight names are listed here, not the 2023-era `qwen-*` only.
Source: https://www.alibabacloud.com/help/en/model-studio/model-pricing (accessed 2026-10-06). *Last Updated: Sep 28, 2026* (per the free-quota notice page).

Eligibility sentence (verbatim): "Only models in the Singapore region with the service deployment scope set to International are eligible for a free quota. Models in other regions or with different service scopes are not eligible for a free quota."
Source: https://www.alibabacloud.com/help/en/model-studio/new-free-quota (accessed 2026-10-06; page "Last Updated: Sep 22, 2026").

### (b) Free-tier quota + credit amount & expiry

- Amount: **1,000,000 tokens per model** (input + output combined). Verbatim: "Each model (such as qwen-plus, qwen3.6-plus, or qwen3.6-plus-2026-04-02) has its own independent free quota (typically 1,000,000 tokens). Quota cannot be merged or transferred across models."
- Verbatim: "The remaining free quota shown for a model is a single combined total for input tokens and output tokens. Input and output tokens are not tracked or calculated separately."
- Expiry: **90 days**. Verbatim: "The free quota is valid for 90 days, starting from the date you activate Alibaba Cloud Model Studio, the model is released, or your model request is approved (whichever is later)."
- Snapshot vs. mainline quota are independent: "A snapshot version with a date suffix (for example, qwen3.7-max-2026-05-17) and the latest version without a date suffix (for example, qwen3.7-max) are treated as two independent models, each with its own free quota."
- Region: Singapore only; "No free quota is available in other regions." Free quota covers real-time invocation only, not batch, fine-tuning, deployment, or OSS.
- Separate OAuth free quota: "OAuth authentication provides an independent free quota for model inference (2,000 calls per day)."
- Rate limits: account-level RPM/TPM, aggregated across RAM users/workspaces/API keys. Several flagship models use **dynamic** rate limiting whose TPM baseline scales with monthly spend; e.g. Singapore `qwen3.8-max` baseline TPM = 2,000,000 (≤100k spend), 5,000,000, 10,000,000. Dated snapshot models get lower RPM (e.g. `qwen3.7-max` = 600 RPM/1,000,000 TPM vs. snapshots = 60 RPM).
  Sources: https://www.alibabacloud.com/help/en/model-studio/new-free-quota , https://www.alibabacloud.com/help/en/model-studio/rate-limit , https://www.alibabacloud.com/help/en/model-studio/quota-management (all accessed 2026-10-06).

### (c) JSON-schema / structured output + tool/function calling

- **Structured output has two modes**: JSON Object (`{"type":"json_object"}`) and **JSON Schema** (`{"type":"json_schema","json_schema":{...,"strict":true}}`).
- JSON Schema support is limited. Verbatim: "Only selected qwen-plus models" and "Qwen3.7-Plus series, Qwen3.7-Flash series, Qwen3.7-Max series, Qwen3.8-Max series, and Qwen3.8-Flash series models." (JSON Object mode is supported by "Most Qwen models".)
- Function calling: text-generation page states "Function calling (custom tools that the model calls): Supported by all general-purpose models." The function-calling doc lists Qwen3.8-Max / 3.7-Max / Plus / Flash / Coder / Turbo / open-source series and multimodal series.
  Sources: https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output , https://www.alibabacloud.com/help/en/model-studio/qwen-function-calling , https://www.alibabacloud.com/help/en/model-studio/text-generation-model (accessed 2026-10-06).

### (d) Seed + temperature determinism

- The API accepts `seed` (integer, optional). Verbatim: "A random number seed. This parameter is used to ensure reproducible results with the same input and parameters. If you pass the same `seed` value in a call and other parameters remain unchanged, the model returns the same result as much as possible."
- Note the wording "as much as possible" — **not documented as a hard determinism guarantee**. `temperature`/`top_p` described as making output "more deterministic" (lower = more deterministic).
  Source: https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-dashscope (accessed 2026-10-06; page "Last Updated: Sep 28, 2026").

### (e) Context length

Per the recommended-models table (live): `qwen3.8-max` 1M, `qwen3.8-max-0902` 1M, `qwen3.8-flash` 1M, `qwen3.7-plus` 1M, `qwen3.7-flash` 1M; `qwen3.7-max` 1M. `qwen-long` = 10M. Qwen3.5 open-source models 256k; Qwen3.5-Plus/Flash 1M.
Source: https://www.alibabacloud.com/help/en/model-studio/text-generation-model (accessed 2026-10-06).

### (f) Data-use on the free tier

Model Studio does **not** distinguish free vs. paid tier in its data-use statement; the customer-data policy is stated globally.

Verbatim (training-data disclosure page): "Alibaba Cloud Model Studio does not use customer business data to develop or improve models without explicit consent."
Verbatim (product FAQ): "Alibaba Cloud protects data privacy and will never use your data for model training. All data transmitted when building applications or training models is encrypted."
Sources: https://www.alibabacloud.com/help/en/model-studio/qwen-and-wan-training-data-disclosure , https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio (accessed 2026-10-06). The separate privacy page (https://www.alibabacloud.com/help/en/model-studio/privacy-notice, accessed 2026-10-06) is the official privacy notice and notes SOC 2 compliance.
Caveat: neither the free-quota page nor these pages explicitly say "the free tier is excluded from training" — the statement is generic ("customer business data … without explicit consent"). No free-tier-specific carve-out found.

### (g) Deprecation / versioning policy

Verbatim: "For snapshot models, which are identified by a specific date in their name …, we issue a sunset notice 30 days before the official sunset date. For mainline models … we issue a sunset notice 3 months before."
Effects: from the notice date, "the QPM … and TPM … for retiring models will gradually decrease"; from the official retirement date, "Model inference will be discontinued. API calls to the retired model will fail."
Dated batches listed on the page include "Scheduled for deprecation on October 10, 2026".
Source: https://www.alibabacloud.com/help/en/model-studio/model-depreciation (accessed 2026-10-06; "Last Updated: Sep 28, 2026").

### (h) OpenAI-compatible base URL

Current dedicated workspace domains (recommended; `{WorkspaceId}` = your workspace ID):
- **International / Singapore**: `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1`
- **China (Beijing)**: `https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`
- (also Hong Kong `cn-hongkong`, Tokyo `ap-northeast-1`, Frankfurt `eu-central-1`, US Virginia `us-east-1` variants)

Legacy domains (still functional per the docs' migration tip): the DashScope API reference states migration "from `https://dashscope-intl.aliyuncs.com` to `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com`" (International) and "from `https://dashscope.aliyuncs.com` to `https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com`" (Beijing).
Sources: https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio , https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-dashscope (accessed 2026-10-06).
**Gap:** the live pages show the legacy *domains* but I did not find the `/compatible-mode/v1` suffix printed for the legacy domains today → the exact legacy OpenAI-compatible path is **[UNVERIFIED]** (commonly `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` / `https://dashscope.aliyuncs.com/compatible-mode/v1`, but not confirmed on a live page today).

---

## Provider B — Z.ai / Zhipu AI (GLM)

Zhipu operates two separate platforms: the **international** platform **Z.ai** (entity: JINGSHENG HENGXING TECHNOLOGY PTE.LTD, Singapore) and the **China** platform **BigModel** (bigmodel.cn; entity: 北京智谱华章科技股份有限公司). Hosting/regions differ; API keys are not shared.

### (a) Exact free-model IDs available today

**Z.ai (international), Z.ai pricing page — "Free" rows (all four price columns = Free):**
- `GLM-4.7-Flash` — text, "Free, Lightweight", context **200K**
- `GLM-4.5-Flash` — text, "Free, Lightweight", context **200K**
- `GLM-4.6V-Flash` — vision, "Free, Native Function Call Support", context **128K**
Verbatim pricing row: "| GLM-4.7-Flash | Free | Free | Free | Free |" and "| GLM-4.5-Flash | Free | Free | Free | Free |".
The GLM-4.7 guide labels the Flash variant: "Positioning: Lightweight, Completely Free"; context 200K, max output 128K.
Sources: https://docs.z.ai/guides/overview/pricing , https://docs.z.ai/guides/overview/overview , https://docs.z.ai/guides/llm/glm-4.7 (accessed 2026-10-06).

**BigModel (China), pricing page (`免费` rows):**
- `GLM-4.7-Flash` (200K, 免费)
- `GLM-4-Flash-250414` (128K, 免费)
- `GLM-Z1-Flash` (128K, 免费)
- `GLM-4.6V-Flash` (vision, 免费)
- `GLM-4V-Flash` (vision, 4K, 免费)
- `GLM-4.1V-Thinking-Flash` (vision, 64K, 免费)
- `CogView-3-Flash` (image, 免费) and `CogVideoX-Flash` (video, 免费)
Source: https://docs.bigmodel.cn/cn/guide/start/pricing (accessed 2026-10-06).

### (b) Free-tier quota + credit amount & expiry

- **Z.ai:** the free Flash models are listed as $0 input/output permanently — no token-count quota or expiry is stated on the pricing page (i.e. free, not a time-limited credit). No free-credit amount published today.
- **BigModel (China):** new-user trial credit **平台体验金** ("platform trial credit ... for new-customer trial scenarios, usable for API consumption"). Verbatim: "除非在赠送时对有效期另有约定，通常平台体验金的使用有效期为自发放之日起 30 天" = "unless otherwise agreed at grant time, the trial credit is normally valid for **30 days** from the date of issue"; non-withdrawable, non-transferable.
- **Rate limits:** BigModel documents **concurrency-based** limits, not fixed RPM/TPM: "速率限制主要体现在：并发请求数限制、不同模型设有独立的并发限制、不同用户权益等级、不同套餐对应不同的并发限制、高峰期的动态限流". Error 1302 = account rate limit exceeded; 1305 = platform overload. Concrete per-model concurrency numbers are shown only in the signed-in console (`bigmodel.cn/usercenter/proj-mgmt/rate-limits`), not on the public page → **[UNVERIFIED: exact numbers]**.
  Z.ai's rate-limit doc (`https://docs.z.ai/api-reference/rate-limit`) **redirects to `https://z.ai/manage-apikey/rate-limits`, a JS-only app page that returns no readable rate-limit content** (curl returns a ~198 KB HTML shell with no numbers) → **Z.ai free-tier rate/concurrency numbers [UNVERIFIED]**. The core-parameters doc only says concurrency "Limits: Different users or subscription plans may have different concurrency quotas" with no figures.
  Sources: https://docs.bigmodel.cn/cn/terms/service-agreement (体验金), https://docs.bigmodel.cn/cn/api/rate-limit , https://docs.z.ai/guides/overview/concept-param , https://z.ai/manage-apikey/rate-limits (accessed 2026-10-06).

### (c) JSON-schema / structured output + tool/function calling

- **Structured output = JSON Object mode only.** Docs: "set `response_format` to `{"type": "json_object"}`"; schema validation is done client-side with the `jsonschema` library, not by the API.
- The OpenAPI spec confirms the ceiling: `response_format.type` enum = `["text", "json_object"]`. **No `json_schema` anywhere** (grep of `https://docs.z.ai/openapi.json`: 0 matches for `json_schema`). BigModel's `openapi-en.json`: same, 0 matches for `json_schema`.
- **Function calling:** supported (parameter `tools`; `tool_choice` default `auto`, "only supports `auto`"). GLM-4.7 guide lists "Function Call" and "Structured Output" as capabilities of the GLM-4.7 series (incl. Flash).
  Sources: https://docs.z.ai/guides/capabilities/struct-output , https://docs.z.ai/guides/capabilities/function-calling , https://docs.z.ai/openapi.json , https://docs.bigmodel.cn/openapi/openapi-en.json (accessed 2026-10-06).

### (d) Seed + temperature determinism

- **No `seed` parameter exists.** Grep of both OpenAPI specs (`docs.z.ai/openapi.json`, `docs.bigmodel.cn/openapi/openapi-en.json`) returns **0 matches for `"seed"`**. No seed is listed in the core-parameters reference (which lists `do_sample`, `temperature`, `top_p`, `max_tokens`, `stream`, `thinking`, `reasoning_effort`).
- Determinism is offered via `do_sample=false` (greedy): verbatim "Set to `false` when you need reproducible, deterministic output." — a sampling-strategy control, not a seeded guarantee.
  Sources: https://docs.z.ai/guides/overview/concept-param (accessed 2026-10-06).

### (e) Context length

| Model | Context | Max output |
|---|---|---|
| GLM-4.7-Flash | 200K | 128K |
| GLM-4.5-Flash | 200K | 96K (glm-4.5 max_tokens cap 98304) |
| GLM-4.6V-Flash (vision) | 128K | 32K |
| GLM-5.3 / 5.3-Flash / 5.2 / 5.1 / 5 | 1M / 200K (varies) | 131072 |
BigModel equivalents: GLM-4.7-Flash 200K; GLM-4-Flash-250414 128K; GLM-Z1-Flash 128K.
Sources: https://docs.z.ai/guides/overview/overview , https://docs.z.ai/guides/overview/concept-param , https://docs.bigmodel.cn/cn/guide/start/pricing (accessed 2026-10-06).

### (f) Data-use (training/logging) — the decisive ambiguity

Z.ai's Terms of Use split individual users from API developers, and the two clauses point opposite ways:

- Individual users — Z.ai **may train on your content**. Verbatim (§IV.3.a): "For individual users, we reserve the right to process any User Content to improve our existing Services and/or to develop new products and services … You hereby explicitly authorize and consent to our: (i) utilization and storage of User Content that does not constitute personal data for the purpose of developing and improving our machine learning and artificial intelligence technologies".
- API developers/enterprises — **no training without opt-in**. Verbatim (§IV.7): "For enterprises and developers using API Services, we will not use your User Content for developing or improving Services unless you explicitly agree to such use. Please refer to Additional Terms for further details."
- API DPA — **no storage of content**. Verbatim (DPA §4(b)): "The Company do not store any of the content the Customer or its End Users provide or generate while using our Services. This includes any texts, or other data you input. This information is processed in real-time to provide the Customer and End Users with the API Service and is not saved on our servers."

**Interpretation limit (mine, flagged):** the free Flash models are reached through an API key on the z.ai API platform, so Z.ai's own framing ("developers using the API services … you are also subject to the Additional Terms for API Services") points to §IV.7 + the DPA (no training without consent; no content storage). But the Terms only name "enterprises and developers" in §IV.7; a hobbyist individual using a free API key is arguably still an "individual user" under §IV.3.a. **The free-tier API key is not explicitly assigned to either bucket on a live page → residual ambiguity, no recommendation made.**
Sources: https://docs.z.ai/legal-agreement/terms-of-use (**Last Update: April 14, 2026**), https://docs.z.ai/legal-agreement/privacy-policy (**Last Update: September 29, 2025**) (accessed 2026-10-06).

**BigModel (China) data-use:** service agreement §4.4–4.6: "就您的数据，除为您提供服务所必需外，智谱不会进行任何未获授权的使用及披露" ("regarding your data, other than what is necessary to provide the service, Zhipu will not perform any unauthorized use or disclosure"); "智谱仅在为您提供服务和满足合规要求所需的最小必要范围内存储您的数据，且会进行必要的匿名化和加密处理" ("Zhipu stores your data only within the minimum scope necessary to serve you and meet compliance requirements, with necessary anonymization and encryption"). Privacy policy adds that **anonymized** data may be used, including "使用匿名数据进行机器学习或模型算法训练" (using anonymized data for machine learning or model algorithm training). Storage is in mainland China ("我们在中国境内运营中收集和产生的个人信息存储在中国境内"; "目前我们不会跨境传输或存储您的个人信息").
Sources: https://docs.bigmodel.cn/cn/terms/service-agreement , https://docs.bigmodel.cn/cn/terms/privacy-policy (**最新版本生效日期：2025 年 5 月 20 日**) (accessed 2026-10-06).

### (g) Deprecation / versioning policy

**Not found on any live page today** → **[UNVERIFIED]**. The Z.ai docs index (llms.txt) and BigModel docs index list no model-lifecycle/deprecation page; the only versioning signal is dated snapshot suffixes on some model IDs and the "Legacy Plan Migration" notices for the Coding Plan (not for free API models). Sources checked: https://docs.z.ai/llms.txt , https://docs.bigmodel.cn/llms.txt (accessed 2026-10-06).

### (h) OpenAI-compatible base URL

- **Z.ai (international):** `https://api.z.ai/api/paas/v4/` — verbatim from OpenAI-SDK example: `base_url="https://api.z.ai/api/paas/v4/"`.
- **BigModel (China):** `https://open.bigmodel.cn/api/paas/v4/` — verbatim: `base_url="https://open.bigmodel.cn/api/paas/v4/"`.
Sources: https://docs.z.ai/guides/overview/quick-start , https://docs.bigmodel.cn/cn/guide/develop/openai/introduction (accessed 2026-10-06).

---

## Not verified / gaps

1. **Z.ai free-tier rate limits (international):** the docs' rate-limit URL redirects to a JS-only page (`https://z.ai/manage-apikey/rate-limits`); no readable RPM/concurrency numbers → [UNVERIFIED]. BigModel publishes only the *mechanism* (concurrency by tier), actual numbers behind login → [UNVERIFIED].
2. **Legacy Alibaba OpenAI-compatible path:** live pages show the legacy domains `dashscope-intl.aliyuncs.com` / `dashscope.aliyuncs.com` but not the printed `/compatible-mode/v1` suffix for them → [UNVERIFIED].
3. **Alibaba free-tier-specific data policy:** the "does not use customer business data … without explicit consent" statement is global; no page states explicitly whether the *free* tier is treated identically → the free-tier-specific wording is [UNVERIFIED], though no contrary carve-out was found.
4. **Z.ai free-model function calling/structured-output per-model support matrix:** docs give a general "such as glm-5, glm-4.7, glm-4.5, glm-4.6" list and the GLM-4.7 page lists these as series capabilities, but no explicit "GLM-4.7-Flash supports json_object/tools" line was found → per-flash-model support [UNVERIFIED].
5. **Deprecation/versioning policy for Z.ai and BigModel:** no such page exists in either docs index → [UNVERIFIED].
6. **Free-tier rate limits for Alibaba free models:** the rate-limit page states account-level RPM/TPM and lists some numbers, but I did not exhaustively enumerate every free model's RPM/TPM (page is 14,578 lines); the dynamic-rate-limiting models' free-tier TPM is spend-tier-dependent → treat specific per-model numbers as partially verified only.
7. **Z.ai free-model expiry:** pricing lists the Flash models as "Free" with no stated end date; no page confirms the free tier is permanent or time-limited → [UNVERIFIED].
