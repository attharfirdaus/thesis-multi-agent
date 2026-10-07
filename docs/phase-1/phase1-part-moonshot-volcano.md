# Phase-1 evidence — Moonshot AI / Kimi and ByteDance Volcano Engine (Ark)

**All pages fetched 2026-10-06.** Every "current" fact below comes from a page fetched today; quotes are verbatim; the page's own last-updated stamp is given where the site displays one.

**Retrieval notes (important for reproducibility)**
- Moonshot's docs serve clean Markdown alternates (`<url>.md`); `platform.moonshot.ai` **301-redirects to `platform.kimi.ai`** (verified via HTTP headers, 2026-10-06). Doc host ≠ API host.
- Volcengine doc pages (`www.volcengine.com/docs/...`) are **JS-only**: a plain fetch returns an empty shell. Content below was pulled from the site's *own* docs API that the page itself calls (`https://docs.volcengine.com/api/doc/getDocDetail?type=online&LibraryCode=ark&DocumentCode=<code>`), which returns the same `MDContent` the page renders. The product/marketing page (`/product/ark`) was rendered through `r.jina.ai` because it has no docs-API equivalent. **Ark docs are Chinese-only** (the API exposes an `EnContent` field, but it is empty for these docs).
- BytePlus (ByteDance's international cloud, running ModelArk = the international Ark) docs are also JS-only; rendered through `r.jina.ai`.

---

## Provider 1 — Moonshot AI / Kimi (Kimi Open Platform)

Contracting entity per ToS: "Moonshot AI PTE. LTD.", governing law Singapore ([ToS](https://platform.kimi.ai/docs/agreement/modeluse), page shows **Last Updated: July 30th, 2026**).

### (a) Free model IDs available today
**None.** The platform is pay-as-you-go only:
> "The Kimi API Open Platform uses pay-as-you-go billing with no subscription plan."
> — [Compare with Other Kimi Products](https://platform.kimi.ai/docs/guide/product-plans) (fetched 2026-10-06)

Currently available (paid) models — [Model List](https://platform.kimi.ai/docs/models) (fetched 2026-10-06):

| Model ID | Context | Description (verbatim, abridged) |
|---|---|---|
| `kimi-k3` | 1M tokens | "Kimi's most capable model to date, with 2.8 trillion parameters, native visual understanding, and a 1M-token context window" |
| `kimi-k2.7-code` | 256k | dedicated coding model |
| `kimi-k2.7-code-highspeed` | 256k | "output speed of approximately 180 Tokens/s" |
| `kimi-k2.6` | 256k | text + image + video, thinking/non-thinking |

Prices ([Model Inference Pricing](https://platform.kimi.ai/docs/pricing/chat), fetched 2026-10-06): kimi-k3 $3.00/M in, $15.00/M out; kimi-k2.x $0.95/M in (miss), $4.00/M out.

### (b) Free tier, quota, credit, expiry, rate limits
There is **no free tier**. Entry cost and credit:

> "To prevent abuse, you need to recharge at least \$1 to start using, and when your cumulative recharge reaches \$5, you will receive a \$5 voucher."
> — [Recharge and Rate Limiting](https://platform.kimi.ai/docs/pricing/limits) (fetched 2026-10-06)

Same page, rate limits keyed to cumulative recharge (Tier0 = the $1 entry tier):

| Tier | Cumulative recharge | Concurrency | RPM | TPM | TPD | Web-search QPS |
|---|---|---|---|---|---|---|
| Tier0 | $1 | 1 | 3 | 500,000 | 1,500,000 | 1 |
| Tier1 | $10 | 15 | 100 | 2,000,000 | Unlimited | 3 |
| Tier2 | $20 | 40 | 100 | 3,000,000 | Unlimited | 5 |
| Tier3 | $100 | 50 | 200 | 3,000,000 | Unlimited | 10 |
| Tier4 | $1,000 | 60 | 200 | 4,000,000 | Unlimited | 20 |
| Tier5 | $3,000 | 100 | 300 | 5,000,000 | Unlimited | 50 |

Additional credit facts:
- "Vouchers do not count towards the cumulative recharge total." (same page)
- New-user vouchers exist but are restricted: "Kimi K3 requires available balance in your account; vouchers granted from new-user verification cannot be used for Kimi K3." ([Use Kimi Models in OpenCode](https://platform.kimi.ai/docs/guide/open-code))
- **Voucher amount and expiry: [UNVERIFIED]** — no page fetched today states the signup voucher value or its validity period. Historical ¥15/$1-ish trial credits could not be confirmed on any live page; the only credit figures found today are the $5 voucher above.
- Billing split (changelog entry, platform changelog in `llms-full.txt`): "Account usage is now deducted at a uniform ratio of 50% cash and 50% vouchers."
- Batch API is cheaper than online inference ([BatchJob Pricing](https://platform.kimi.ai/docs/pricing/batch)).

### (c) Structured output + tool/function calling
Both supported ([response_format](https://platform.kimi.ai/docs/guide/response_format), [tool calls](https://platform.kimi.ai/docs/guide/use-kimi-api-to-complete-tool-calls), fetched 2026-10-06):
- `response_format`: `json_object` (JSON Mode) and `json_schema` (Structured Output, with `strict: true` and a "MFJS (Moonshot Flavored JSON Schema)" profile).
- Model caveats quoted: "`kimi-k3` reliably supports Structured Output, including nested objects, arrays, and `anyOf`." / "`kimi-k2.7-code` has the most stable Structured Output support…" / "`kimi-k2.6` occasionally behaves unstably with complex schemas; for example, `$ref` may return a Markdown code block".
- Tool calling: `tools` + `tool_choice`. `tool_choice: "required"` is supported **only** by `kimi-k3`; "kimi-k2.6 and kimi-k2.7-code do not support `required` and return an error if it is passed" ([Model Parameter Reference](https://platform.kimi.ai/docs/api/models-overview)).
- Constrained decoding is token-level CFG per the docs ("Token-level constrained decoding (CFG), filtering illegal tokens during sampling").

### (d) Seed + temperature determinism
**No `seed` parameter exists.** A full-text scan of the complete Kimi docs bundle (`https://platform.kimi.ai/docs/llms-full.txt`, 772 KB, fetched 2026-10-06) returns **zero** occurrences of `seed`; the Chat Completions parameter reference likewise has none. Determinism is therefore **not controllable via seed**.

Sampling knobs are largely **locked** on current models ([Model Parameter Reference](https://platform.kimi.ai/docs/api/models-overview)):
| Parameter | kimi-k3 | kimi-k2.7-code | kimi-k2.6 |
|---|---|---|---|
| `temperature` | Fixed at `1.0` | Fixed at `1.0` | `1.0` thinking / `0.6` non-thinking |
| `top_p` | Fixed at `0.95` | Fixed at `0.95` | Fixed at `0.95` |
| `n`, penalties | Fixed at `1` / `0` | Fixed at `1` / `0` | Fixed at `1` / `0` |

> "\"Fixed\" means the parameter cannot be modified: passing any other value returns an error, so do not pass it explicitly."
> "Do not pass `temperature` explicitly when calling these models."

Caveat for the thesis: temperature is fixed at 1.0 (nonzero), and no seed exists → **API-level reproducibility of sampling is not offered**; only prefix caching (a billing/caching feature) is deterministic.

### (e) Context length
- `kimi-k3`: **1,048,576 tokens** (pricing page "Context Window"; model list says "1M-token context window").
- `kimi-k2.7-code`, `kimi-k2.7-code-highspeed`, `kimi-k2.6`: **262,144 tokens**.
Sources: [pricing/chat](https://platform.kimi.ai/docs/pricing/chat), [models](https://platform.kimi.ai/docs/models) (fetched 2026-10-06).

### (f) Data use
Key clause, [Terms of Service §4 Content](https://platform.kimi.ai/docs/agreement/modeluse) (Last Updated July 30th, 2026):
> "We may use Content to provide, maintain, develop, support, and improve the Services, comply with applicable law, enforce our terms and policies, and keep the Services safe and secure. Customer who requires restrictions on the use of Customer Content for training or improving Moonshot AI models may contact Moonshot AI to discuss available enterprise arrangements or separate written agreements. **Unless otherwise expressly agreed in writing, Customer Content may be used for the foregoing purposes.**"

Enterprise default (no ZDR needed for the training part), [What is Zero Data Retention (ZDR)?](https://platform.kimi.ai/docs/guide/zero-data-retention):
> "By default, the Kimi Open Platform does not use enterprise customer data to train models."
ZDR itself (content retention) is **enterprise-only and on request**: "ZDR is available on request to enterprise customers." ZDR limits quoted: prompts "deleted as soon as the response is returned"; "ZDR cannot be guaranteed for images or videos submitted through direct file uploads. Operational data, such as security logs and billing records, is outside the scope of zero data retention. Third-party models, connectors, and plugins are not covered by this policy."

Privacy policy (applies to account/user data), [Kimi OpenPlatform Privacy Policy](https://platform.kimi.ai/docs/agreement/userprivacy):
> "To Improve and Develop Our Services: … This includes training and refining our underlying technology, such as machine learning models and algorithms." (legal basis: legitimate interests / consent)
> Retention: "account, input, and payment information are retained while your account is active."

**Verdict, free/non-enterprise tier:** content *may* be used to develop/train models unless a separate written (enterprise) arrangement is made; no distinct "free-tier" clause exists because there is no free tier.

### (g) Deprecation / versioning policy
No separate policy document exists; deprecations are published as dated notices in the model list ([Model List](https://platform.kimi.ai/docs/models), fetched 2026-10-06):
- `kimi-k2.5` — "officially discontinued on **August 31, 2026**"
- `moonshot-v1` series (incl. `moonshot-v1-auto`, `-vision-preview`) — "**August 31, 2026**"
- `kimi-k2` series — "**May 25, 2026**"
- `kimi-latest` — "**January 28, 2026**"; `kimi-thinking-preview` — "**November 11, 2025**"
Wording used: "no longer maintained or supported". **No minimum advance-notice period is documented** (grep of the full docs bundle finds none) — [UNVERIFIED] whether any guaranteed notice window exists.

### (h) OpenAI-compatible base URL
> "OpenAI Chat Completions | `https://api.moonshot.ai/v1` | `/chat/completions`"
> "Anthropic Messages | `https://api.moonshot.ai/anthropic` | `/messages`"
> — [API Overview](https://platform.kimi.ai/docs/api/overview) (fetched 2026-10-06)

Endpoint table also lists `/v1/responses`, `/v1/models`, `/v1/files`, `/v1/batches`, `/v1/tools/search`, `/v1/tools/search_pro`, `/v1/tools/fetch`.

Regional isolation note: "API Keys from `platform.kimi.ai` and `platform.kimi.com` are completely independent. Using a Key from one platform on the other will result in a 401 error." Plus: "accounts, balances, and keys on platform.kimi.ai are isolated from other regional Kimi platforms." A China-mainland platform (`platform.moonshot.cn` / `api.moonshot.cn`) is referenced indirectly (Moonshot email domain `api-feedback@moonshot.cn`, changelog "launched the Global edition of Kimi Open Platform" in May 2025) but **its current status, quotas and data policy were not verified today — [UNVERIFIED]**.

---

## Provider 2 — ByteDance Volcano Engine / Ark (mainland-China site, zh-only docs)

### (a) Free model IDs available today
Free quota is granted **per model** to accounts that have not activated model service ([免费推理额度](https://www.volcengine.com/docs/ark/free-inference-quota?lang=zh), doc UpdatedTime **2026-08-24T13:58:51Z**).

From the Ark product page free-quota table ([volcengine.com/product/ark](https://www.volcengine.com/product/ark), rendered 2026-10-06) — **50万 tokens (500,000) free per model**:
- 文本生成: `Doubao-Seed-2.1-pro`, `Doubao-Seed-2.1-turbo`, `Doubao-Seed-Evolving`, `Doubao-Seed-Character`
- 向量模型: `Doubao-embedding-vision`
- 图像生成: Seedream 5.0-lite (50 张) / 4.5 / 4.0 (200 张); 语音: 语音合成 5000 字符, 声音复刻 5000 字符+10 复刻声音, 流式/录音文件识别 20 小时; 联网插件: 联网资源 2 万次/月

**Hosted open-weight / third-party models (DeepSeek-V4.x, GLM-5.x) are NOT listed in the free-quota table** → no free quota documented for them on the CN site. [UNVERIFIED: no page fetched today states a free quota for DeepSeek/GLM/Qwen/Llama on Ark CN.]

Definition of "free" models here: not free of charge forever, only "free quota for accounts that have not activated the model service":
> "每个模型提供一定额度的免费调用量，免费额度消耗完后可在开通管理页中开通模型，并继续付费使用，开通服务后仍优先消耗剩余免费额度。"
> — [开通管理](https://www.volcengine.com/docs/ark/activation-management) (UpdatedTime 2026-09-30T08:22:03Z)

### (b) Quota amounts, validity, and the data-for-tokens alternative
Free-inference quota rules ([免费推理额度](https://www.volcengine.com/docs/ark/free-inference-quota?lang=zh)):
> "免费额度仅适用于抵扣 **按 token 后付费产生的在线推理费用** ，不能抵扣使用各类插件、知识库等产生的费用。"
- "免费推理额度，不同模型分别计算，主账号下共享" (per-model, shared under the main account; sub-account usage draws down the main account's per-model quota; the doc's worked example uses 500 (k token) per model)
- "免费推理额度，基础模型和精调后模型共享" (base and fine-tuned models of the same base share one quota)
- Batch inference and fine-tuning **cannot** consume the free quota. Context-cache **storage** fees cannot be offset either.
- 安心体验模式 (Free Tokens Only mode), [doc](https://www.volcengine.com/docs/ark/free-tokens-only-mode) (UpdatedTime 2026-09-30T08:16:44Z): "在安心体验模式下，您调用推理 API 时仅消耗平台赠送的 50w token 免费额度，接近免费额度后服务将暂停，避免产生额外费用。" Eligibility: accounts that "**未开通过模型服务**" and never enabled/disabled the mode; **once disabled it cannot be re-enabled**.
- **Expiry of the 500k inference quota: [UNVERIFIED]** — neither the free-quota doc nor the activation doc states a validity period. (The separate Managed Agents welcome pack is documented as "每个账号仅赠送一次，有效期 2 年" — 30 hours Agent runtime + 500 `web_search` calls — [模型服务计费说明](https://www.volcengine.com/docs/ark/model-service-pricing), UpdatedTime 2026-09-30T08:16:44Z. Do not conflate.)

**Alternative free-token source — 协作奖励计划 (Data Collaboration Rewards)**, [doc](https://www.volcengine.com/docs/ark/collaboration-reward-program) (UpdatedTime 2026-09-21T08:08:38Z); this is the "up to 5M tokens/day" offer seen in marketing:
> "调用已获授权的推理接入点，每日将采集每个模型不超过500万tokens的推理数据，并于次日发放有效期为30天的等量免费资源包；未获授权的接入点数据将不予采集，该部分使用量次日也不会返还资源包。"
Requires real-name verification; currently the reward entry supports `Doubao-Seed-Evolving`; rewards do not offset batch inference / model-unit / TPM packages / cache storage.

Rate limits (per model, from the model list): e.g. `doubao-seed-2-1-pro-260915` "最大 RPM: 500 / 最大 TPM: 1000000"; `doubao-seed-2-1-lite-260915` "最大 RPM: 30000 / 最大 TPM: 5000000" ([模型列表](https://www.volcengine.com/docs/ark/model-list), UpdatedTime 2026-09-28T03:59:13Z).

### (c) Structured output + tool/function calling
- Structured output (`response_format` with `text` / `json_object` / `json_schema`, `json_schema.strict`) — **beta**:
  > "该能力尚在 beta 阶段，受资源与平台负载影响，服务可用性可能随访问情况产生波动，请谨慎在生产环境使用。" ([结构化输出(beta)](https://www.volcengine.com/docs/ark/structured-output-beta), UpdatedTime 2026-09-22T08:52:17Z)
  Supported models are tagged in the model list (e.g. `doubao-seed-2-1-pro-260915`, `doubao-seed-2-0-lite-260428` "结构化输出（推荐使用 `json_schema` 模式）"). **Not supported with TPM 保障包** inference.
- Function calling: `tools` (`tools.function.name/description/parameters/strict`, `tools.type=function`) — [Function Calling](https://www.volcengine.com/docs/ark/function-calling), UpdatedTime 2026-09-22T08:52:16Z; Chat API doc lists `tools` (default null) and `tool_choice`-adjacent fields ([对话(Chat) API](https://www.volcengine.com/docs/ark/chat-api), UpdatedTime **2026-09-24T04:03:52Z**).

### (d) Seed + temperature determinism
**No `seed` parameter.** The Chat API parameter reference was read in full; there is no `seed` field, and no "seed" string anywhere except model names ("seed 系列模型"). Determinism is only discussed for `top_p`:
> "取值越大生成的随机性越高，取值越低生成的确定性越高。" (higher top_p = more random; lower = more deterministic)
`temperature` default 1.0, `top_p` default 0.7 — with model-specific overrides (e.g. `doubao-seed-2-0-pro-260215` and `doubao-seed-2-0-lite-260215` pin `top_p` to 0.95, ignoring manual values). → **No seed-based reproducibility offered on Ark.**

### (e) Context length (from [模型列表](https://www.volcengine.com/docs/ark/model-list), UpdatedTime 2026-09-28T03:59:13Z)
| Model ID | Context window | Max input | Max output (incl. CoT) | Max RPM / TPM |
|---|---|---|---|---|
| `doubao-seed-evolving` | 1024k | 1024k | 256k (default 4k) | 500 / 1,000,000 |
| `doubao-seed-2-1-pro-260915` | 1024k | 1024k | 256k | 500 / 1,000,000 |
| `doubao-seed-2-1-lite-260915` | 1024k | 1024k | 256k | 30000 / 5,000,000 |
| `doubao-seed-2-1-pro-260628` | 256k | 256k | 256k | 500 / 1,000,000 |
| `doubao-seed-2-1-turbo-260628` | 256k | 256k | 256k | 500 / 1,000,000 |
| `doubao-seed-2-0-lite-260428` | 256k | 224k | 128k | 30000 / 5,000,000 |
| `deepseek-v4-1-flash-260910` | 1024k | 1024k | 384k | 500 / 1,000,000 |
| `glm-5-3-flash-260828` | 1024k | 1024k | 128k | 500 / 1,000,000 |

### (f) Data use
Model service agreement, [豆包模型服务协议](https://www.volcengine.com/docs/ark/doubao-model-service-agreement) (UpdatedTime 2026-09-18T06:35:02Z), §四:
> "4.1 除非您单独同意，本服务将不使用您提交给服务或使用服务输出的内容训练、重新训练或改进基础模型。您单独同意的情况包括：
> 4.1.1 同意火山引擎的《数据授权使用协议》；或
> 4.1.2 参与火山引擎协作奖励计划，包括奖励资源包或不定期为您提供的其他奖励或优惠活动等。"
> "4.2 为履行法定合规要求，火山引擎有权采取技术手段对您使用本服务的行为及信息进行审查，包括但不限于对您提交给服务或使用服务输出的内容进行自动化过滤审核…"

So: **default = no training on your content; opting into either (i) the Data Authorization Agreement or (ii) the rewards program turns training ON** — and the rewards program is precisely how free daily tokens are obtained.

[火山引擎数据授权使用协议](https://www.volcengine.com/docs/ark/volcengine-data-authorization-agreement) (fetched 2026-10-06) — the opt-in document (written for Coding/Agent Plan subscriptions):
> "2.1 授权目的：本规则项下的授权将用于开发机器学习、人工智能相关技术和模型的优化、开发、使用、学术理论研究及发表等目的。"
> "2.3 授权期限：… **授权期限为 永久**。"
It grants a "非独家的、不可转让的…免费的" right to "传输、存储、使用、复制、下载、修改或以其他方式处理" the submitted data, with a carve-out that already-used data stays authorized after withdrawal.

[协作奖励计划](https://www.volcengine.com/docs/ark/collaboration-reward-program) data-safety claims:
> "无授权不采集：当您从未授权、撤回授权，或者本计划终止时，您的数据不会被采集" / "您可以随时在数据协作奖励计划活动页面撤回授权。"
But the daily data collection itself is stated plainly: "每日将采集每个模型不超过500万tokens的推理数据" (see (b)).

Monthly inference free-token mode (安心体验) carries **no** data-collection condition — it consumes the standard granted quota.

Security whitepaper page ([火山方舟大模型服务安全白皮书](https://www.volcengine.com/docs/ark/volcengine-ark-model-service-security-whitepaper)) links a PDF; the HTML page contains only images → **retention periods are [UNVERIFIED] on the CN site** (no text-retention window found on any fetched page). The equivalent statement exists on the BytePlus side (below).

### (g) Deprecation / versioning policy
[模型下线公告](https://www.volcengine.com/docs/ark/model-deprecation-notice) (UpdatedTime 2026-09-30T08:16:44Z):
> "当某个模型确定下线计划时，我们会通过短信、站内信等方式发布通知，请及时关注。"
Lifecycle stages are explicit per batch, e.g. 第十批 (10th batch):
| 节点 | 时间 |
|---|---|
| 启动&通知 (quota begins to be reduced) | 2026-09-22 10:00 (UTC+8) |
| EOM (模型停止新购) | 2026-09-24 10:00 (UTC+8) |
| EOS (模型服务下线) | **2026-11-24 14:00** (UTC+8) |
with an early EOS of **2026-10-22 14:00** for `doubao-seed-2-0-lite-260215` and `doubao-seed-2-0-mini-260215`; unmigrated endpoints are auto-migrated or shut down. Model IDs already flagged `即将下线` in the model list: `doubao-seed-2-0-pro-260215`, `doubao-seed-2-0-lite-260215`, `doubao-seed-2-0-mini-260215`, `doubao-seed-2-0-code-preview-260215`, `deepseek-v4-pro-260425`.

### (h) OpenAI-compatible base URL
[Base URL及鉴权](https://www.volcengine.com/docs/ark/base-url-and-authentication) (UpdatedTime 2026-06-23T08:51:46Z):
> "数据面 API：https://ark.cn\-beijing.volces.com/api/v3"
> "管控面 API：https://ark.cn\-beijing.volcengineapi.com/"
Auth: `Authorization: Bearer $ARK_API_KEY`; example uses `POST /chat/completions` with `"model": "doubao-seed-2-1-pro-260628"`. Access-Key auth requires the `model` field to be an Endpoint ID. Note the doc warns Coding Plan uses a *different* base URL.

---

## Provider 2b — International counterpart: BytePlus ModelArk (en, same ByteDance platform)

`volcengine.com` itself is the mainland site; ByteDance's international model platform is **BytePlus ModelArk** (`byteplus.com`, `docs.byteplus.com/en/docs/ModelArk/...`), which is the Ark stack with overseas regions. Evidence:

**(a)/(b) Free quota** — product page [byteplus.com/en/product/modelark](https://www.byteplus.com/en/product/modelark) (rendered 2026-10-06):
> "Get started with **500,000 free tokens for every Large Language Model** and 2,000,000 free tokens for every vision model. Enterprise customers can unlock even greater value with our exclusive partnership program, receiving 5 million tokens…"
Free-LLM list on that page (500k tokens each): `Dola-Seed-2.0-lite`, `Dola-Seed-2.0-mini`, `Dola-Seed-2.0-pro`, `Dola-Seed-2.0-Code`, `ByteDance-Seed-1.8`, `Skylark-pro`, **`DeepSeek-V4-pro`**, **`DeepSeek-V4-flash`**, **`DeepSeek-V3.2`**, `ByteDance-Seed-1.6`, `ByteDance-Seed-1.6-flash`. (So on the international platform open-weight DeepSeek models *do* get 500k free tokens — unlike the CN site.)
Also [Inference free trial](https://docs.byteplus.com/en/docs/ModelArk/1399514) (same doc body as the CN 免费推理额度 doc, in English) and [Free Tokens Only mode](https://docs.byteplus.com/en/docs/ModelArk/free-tokens-only-mode): "calls to the inference API consume only the 500k free tokens granted by the platform. When the free quota is nearly exhausted, the service will be automatically paused".
[Terms and Conditions for Free-Token Campaign](https://docs.byteplus.com/en/docs/legal/termsandconditions_modelark_free-token_campaign): "with a value of 500,000 (Five Hundred Thousand) tokens per Model"; "This offer is redeemable only once per BytePlus account."; "The Free-Token Package may have a validity period, which can be viewed in the…" (**amount/validity per account: [UNVERIFIED] beyond the 500k/model figure**).
[Promotion page](https://docs.byteplus.com/en/docs/ModelArk/promotion): "Each model can enjoy a 50% discount on usage of up to 1 billion tokens. The 50% discount will apply for 14 days (336 hours)."
Data-collaboration alternative: [Data Collaboration Rewards](https://docs.byteplus.com/en/docs/ModelArk/collaboration-reward-program) — "Ongoing Benefit: Enjoy 5,000,000 tokens free every day!"; daily packages ≤ that day's consumption of the enrolled model.

**(c)/(d)** Structured output (`response_format` with `json_schema`, `strict`) and tools are present in the [Chat API](https://docs.byteplus.com/en/docs/ModelArk/chat-api) parameter list; **no `seed` parameter** there either (checked in full). Model list flags "Tool use" / "Structured output" capabilities and per-model "Max RPM / Max TPM" ([model list](https://docs.byteplus.com/en/docs/ModelArk/model-list)).

**(e) Context lengths**, international model IDs: e.g. `dola-seed-2-1-turbo-260628` context 256K, `seed-2-0-lite-260428` 256K, plus 1024K-context models such as `deepseek-v4-1-flash`, `glm-5-3-flash` (model list, rendered 2026-10-06).

**(f) Data use** — [BytePlus ModelArk data processing](https://docs.byteplus.com/en/docs/ModelArk/BytePlus_ModelArk_Data_Processing) (Published Time **Tue, 28 Jul 2026**):
> "Without the customer's prior authorization, BytePlus ModelArk will neither interfere with the data processing nor use Customer Data for its own model training."
> "BytePlus ModelArk service may store your Customer Data for content safety purposes; **input and output triggered by the filter are retained for 180 days in Malaysia.**"
Data center locations quoted: "Malaysia, Indonesia, and/or the EU/EEA".
Campaign override (opt-in, permanent): [Data Collaboration Rewards T&C](https://docs.byteplus.com/en/docs/ModelArk/collaboration-reward-program):
> "The Input and Output submitted or generated through your selected Campaign endpoints within the Daily Maximum Token Amount limit (the 'Authorized Data') **will be permanently used to provide, maintain, develop or improve our model services or the underlying technologies**…"
> Withdrawal: "the right and license you grant hereunder should continue in effect after such withdrawal or termination."

**(g) Deprecation** — [Model deprecations](https://docs.byteplus.com/en/docs/ModelArk/1350667) (Last Updated **September 10, 2026**):
> "Notifications will be issued at least 30 calendar days before the model is officially deactivated."
Timetable model: First Notification Date → Deprecation Date (no new endpoints/fine-tuning) → Deactivation Date; 4th batch example: 2026-09-08 → 2026-09-15 → **2026-11-11**, with "starting from the First Notification Date, quotas for deprecated models will be gradually reduced."

**(h) OpenAI-compatible base URL** — [Base URL and authentication](https://docs.byteplus.com/en/docs/ModelArk/1298459):
> "Data plane API: `https://ark.ap-southeast.bytepluses.com/api/v3`"
Control plane uses the BytePlus OpenAPI host; Coding Plan uses a different base URL (warned explicitly in the same doc).

---

## Not verified / gaps

1. **Moonshot new-user voucher value & expiry — [UNVERIFIED]**. Docs confirm such vouchers exist ("vouchers granted from new-user verification cannot be used for Kimi K3") but no page fetched today states the amount or validity. The historic ¥15 / $1 trial credit could not be confirmed anywhere live; the only documented credit today is the **$5 voucher at $5 cumulative recharge**.
2. **Moonshot China platform (`platform.moonshot.cn` / `api.moonshot.cn`) — [UNVERIFIED]**. Not fetched; only indirect references. The task's "China-hosted vs api.moonshot.ai international" split could not be evidenced beyond: entity = Moonshot AI PTE. LTD. (Singapore law), `platform.kimi.ai` vs `platform.kimi.com` keys are isolated, and a "Global edition" was launched May 2025.
3. **Moonshot deprecation notice period — [UNVERIFIED]**: only dated retirements are published; no guaranteed notice window documented.
4. **Ark CN 500k free-quota expiry — [UNVERIFIED]**: no validity period stated. (The 2-year validity figure found belongs to the *Managed Agents* welcome pack, not model inference.)
5. **Ark CN free quota for hosted open-weight models (DeepSeek/GLM/Qwen/Llama) — [UNVERIFIED]/absent**: the CN free-quota table covers only Doubao/Seedream/voice/embedding models.
6. **Ark CN data retention window — [UNVERIFIED]**: the security whitepaper page is image/PDF-only; no text retention statement found. The 180-day content-safety retention figure is documented for **BytePlus** (Malaysia), not for the CN region.
7. **Seed/determinism**: neither provider documents a `seed` parameter (verified by full-text scans of the Kimi docs bundle and the Ark/BytePlus Chat API parameter references). Report as "not offered", not as "unsupported in practice".
8. **Ark CN `model-pricing` free-quota column**: the CN pricing doc (UpdatedTime 2026-09-28T13:39:45Z) documents prices; the free-quota *amounts* per model come from the product page table only. The console (开通管理) is the authoritative per-account source but requires login.
9. JS-only rendering means Volcengine/BytePlus content was obtained via the sites' own JSON docs API / a rendering proxy; wording matches the rendered pages but punctuation/spacing in the raw JSON (`\-` escapes) was normalized in quotes above.

---

### Quick comparison (evidence-only, no recommendation)
| Axis | Moonshot/Kimi | Ark CN (volcengine) | BytePlus ModelArk (intl) |
|---|---|---|---|
| Free tokens today | none (min $1 recharge; $5 voucher at $5 cumulative) | 500k/model (unactivated accts); 5M tok/day via data-rewards program | 500k/LLM (2M vision), free for DeepSeek-V3.2/V4, Skylark; 5M/day via rewards |
| Entry-tier rate limits | Tier0 ($1): RPM 3, TPM 500k, TPD 1.5M, concurrency 1 | per-model Max RPM/TPM (e.g. 500 / 1M for doubao-seed-2.1-pro) | per-model Max RPM/TPM (e.g. 500 / 1M; 30K / 1.5M for lite) |
| JSON-schema + tools | yes (GA), `strict` + MFJS | yes (structured output **beta**), tools | yes (structured output beta), tools |
| `seed` | not documented | not documented | not documented |
| Data use (free/default) | may be used for training unless separate written agreement; ZDR enterprise-only | no training unless opting into Data Authorization Agreement **or** rewards program (which grants the free daily tokens) | no training without authorization; content-safety-filtered I/O retained 180 days (Malaysia) |
| OpenAI base URL | `https://api.moonshot.ai/v1` | `https://ark.cn-beijing.volces.com/api/v3` | `https://ark.ap-southeast.bytepluses.com/api/v3` |
