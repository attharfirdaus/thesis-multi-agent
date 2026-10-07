# Phase 1 — Qwen + DeepSeek families (Indonesian capability evidence)

All pages fetched live on **2026-10-06** unless stated. Access date = 2026-10-06 for every entry below. Quotes are verbatim, shortened with `…` where noted. No recommendations, no ranking — evidence only.

Landscape note (2026-10-06): the Qwen line has moved past Qwen3 to **Qwen3.5 → Qwen3.6 → Qwen3.8**, with a **Qwen4-precursor** architecture shipped as Qwen3.8-Flash-Next (`qwen4_exp` arch tag). The DeepSeek line has moved past V3/R1 to **V3.2 → V4-Flash/V4-Pro → V4.1-Flash**; the official DeepSeek API now serves only `deepseek-flash` (= DeepSeek-V4.1-Flash) and `deepseek-v4-pro` (= DeepSeek-V4-Pro-0813).

---

## Qwen family

### Qwen2.5-7B-Instruct
- Model card URL (primary): https://huggingface.co/Qwen/Qwen2.5-7B-Instruct — accessed 2026-10-06.
- License: **Apache-2.0** (`license: apache-2.0`, `license_link: …/blob/main/LICENSE` on the card). No restriction clauses.
- Params: 7.61B, dense ("Number of Parameters: 7.61B").
- Context: "Full 131,072 tokens and generation 8192 tokens".
- Bahasa Indonesia evidence: no Indonesian benchmark on the card. Card claims "Multilingual support for over 29 languages, including Chinese, English, French, Spanish, Portuguese, German, Italian, Russian, Japanese, Korean, Vietnamese, Thai, Arabic, and more." — Indonesian is **not named**. Training-data documentation for Indonesian: **no** (card documents no data mixture).
- Structured output: card claims "understanding structured data (e.g, tables), and generating structured outputs especially JSON"; no function-calling claim on the Qwen2.5 card itself. Provider claim (Model Studio, applies to "Qwen2.5 open source series"): https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-structured-output — "Enabling structured output ensures the model returns a valid JSON string." JSON Object mode listed for "Qwen2.5 open source series (excluding math and coder models)".
- Determinism caveats: gemma/others aside — listed by vLLM as batch-invariance-validated (`Qwen/Qwen2.5-7B-Instruct`) at https://docs.vllm.ai/en/latest/features/batch_invariance/ (doc dated October 4, 2026); MoE routing N/A (dense).
- Free-host availability: Cloudflare Workers AI does not list Qwen2.5-7B. Alibaba Model Studio free quota applies only to models eligible in the console (per-model check required).
- Notes: superseded generation; card lists `language: en` in YAML even though the prose claims 29+ languages.

### Qwen2.5-14B-Instruct
- Model card URL (primary): https://huggingface.co/Qwen/Qwen2.5-14B-Instruct — accessed 2026-10-06.
- License: **Apache-2.0** (`license: apache-2.0`).
- Params: 14.7B, dense.
- Context: "Full 131,072 tokens and generation 8192 tokens".
- Bahasa Indonesia evidence: none on card; same 29-language prose list (Indonesian not named). Training data: not documented.
- Structured output: same card prose as 7B; Model Studio JSON Object mode covers "Qwen2.5 open source series (excluding math and coder models)" (URL above).
- Determinism caveats: vLLM batch-invariance tested list includes `Qwen/Qwen2.5-14B-Instruct` (URL above).
- Free-host availability: not listed on Cloudflare Workers AI. Model Studio free-quota eligibility: per-model console check, not verifiable from docs.
- Notes: —

### Qwen2.5-32B-Instruct
- Model card URL (primary): https://huggingface.co/Qwen/Qwen2.5-32B-Instruct — accessed 2026-10-06.
- License: **Apache-2.0** (`license: apache-2.0`, `license_link: …/Qwen2.5-32B-Instruct/blob/main/LICENSE`).
- Params: 32.5B, dense.
- Context: "Full 131,072 tokens and generation 8192 tokens".
- Bahasa Indonesia evidence: none on card; Indonesian not named in the 29-language list. Training data: not documented.
- Structured output: card prose on JSON; Model Studio JSON Object mode applies to the Qwen2.5 open-source series (URL above).
- Determinism caveats: vLLM batch-invariance tested list includes `Qwen/Qwen2.5-32B-Instruct` (URL above).
- Free-host availability: not on Cloudflare Workers AI price list (https://developers.cloudflare.com/workers-ai/platform/pricing/, page updated 2026-10-01).
- Notes: also the base for `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B`.

### Qwen2.5-72B-Instruct
- Model card URL (primary): https://huggingface.co/Qwen/Qwen2.5-72B-Instruct — accessed 2026-10-06. License file: https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/raw/main/LICENSE — accessed 2026-10-06.
- License: **"Qwen LICENSE AGREEMENT"** (card YAML: `license: other`, `license_name: qwen`), release date September 19, 2024. Key restrictions, verbatim:
  - "If you are commercially using the Materials, and your product or service has more than 100 million monthly active users, you shall request a license from us."
  - "If you use the Materials or any outputs or results therefrom to create, train, fine-tune, or improve an AI model that is distributed or made available, you shall prominently display “Built with Qwen” or “Improved using Qwen” in the related product documentation."
  - Governing law: "The People's Courts in Hangzhou City shall have exclusive jurisdiction over any dispute arising out of this Agreement."
- Params: 72.7B (non-embedding 70.0B), dense.
- Context: "Full 131,072 tokens and generation 8192 tokens".
- Bahasa Indonesia evidence: none on card; Indonesian not named in the language list. Training data: not documented.
- Structured output: card prose claims JSON capability; Model Studio JSON Object mode covers "Qwen2.5 open source series (excluding math and coder models)" — 72B is in that series per that doc's wording (exact per-model listing not enumerated): https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-structured-output
- Determinism caveats: dense model; not in vLLM batch-invariance tested list (that list has 0.5B–32B only) → batch-invariance status [UNVERIFIED].
- Free-host availability: not on Cloudflare Workers AI list. [UNVERIFIED] elsewhere.
- Notes: the only Qwen2.5 open-weight size under the custom Qwen license (0.5B–32B are Apache-2.0).

### Qwen3-32B (dense)
- Model card URL (primary): https://huggingface.co/Qwen/Qwen3-32B — accessed 2026-10-06.
- License: **Apache-2.0** (HF model API field: `License: apache-2.0`; card `license: apache-2.0`, `license_link: …/Qwen3-32B/blob/main/LICENSE`).
- Params: "Number of Parameters: 32.8B" (non-embedding 31.2B), dense.
- Context: "Context Length: 32,768 natively and 131,072 tokens with YaRN".
- Bahasa Indonesia evidence: no Indonesian benchmark on card; claim is "Support of 100+ languages and dialects with strong capabilities for multilingual instruction following and translation". Training data: **no** Indonesian/Latin data documentation (card documents no data mixture).
- Structured output: "Qwen3 excels in tool calling capabilities. We recommend using Qwen-Agent to make the best use of agentic ability of Qwen3." Card also documents thinking/non-thinking switching; official framework doc: https://qwen.readthedocs.io/en/latest/framework/function_call.html — "We recommend using Hermes-style tool use for Qwen3 to maximize function calling performance." Model Studio function calling lists "Qwen3 open source series": https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-function-calling
- Determinism caveats: thinking-mode sampling instruction, verbatim: "For thinking mode, use Temperature=0.6, TopP=0.95, TopK=20, and MinP=0 (the default setting in generation_config.json). **DO NOT use greedy decoding**, as it can lead to performance degradation and endless repetitions." (card). Dense model → no MoE routing nondeterminism; batch-size nondeterminism covered generically by vLLM: "vLLM does not guarantee the reproducibility of the results by default, for the sake of performance." (https://docs.vllm.ai/en/latest/usage/reproducibility/, page dated April 28, 2026).
- Free-host availability: Cloudflare Workers AI does not list Qwen3-32B (its Qwen listings are `@cf/qwen/qwq-32b`, `@cf/qwen/qwen2.5-coder-32b-instruct`, `@cf/qwen/qwen3-30b-a3b-fp8`, `@cf/qwen/qwen3.8-27b`) — https://developers.cloudflare.com/workers-ai/platform/pricing/. Alibaba Model Studio: model eligible under the free-quota program only if the console shows a quota bar (not verifiable per model). OpenRouter serves `qwen/qwen3-32b` at $0.08/M input, $0.28/M output — **not free** (OpenRouter public model API, fetched 2026-10-06: https://openrouter.ai/api/v1/models).
- Notes: —

### Qwen3-30B-A3B (MoE)
- Model card URL (primary): https://huggingface.co/Qwen/Qwen3-30B-A3B — accessed 2026-10-06.
- License: **Apache-2.0** (`license: apache-2.0`).
- Params: "30.5B in total and 3.3B activated" (MoE; 128 experts, 8 activated).
- Context: "32,768 natively and 131,072 tokens with YaRN".
- Bahasa Indonesia evidence: none on card; "Support of 100+ languages and dialects". Training data: not documented. (Indonesian evidence exists only via third-party SEA-HELM-type evaluations, which today list no Qwen3-30B-A3B.)
- Structured output: same card text as Qwen3-32B; Model Studio function calling lists "Qwen3 open source series".
- Determinism caveats: MoE. vLLM lists this exact model under batch-invariance "Tested Models" → "Qwen3 (MoE): `Qwen/Qwen3-30B-A3B`, `Qwen/Qwen3-Next-80B-A3B-Instruct`, `Qwen/Qwen3-30B-A3B-Thinking-2507-FP8`" (https://docs.vllm.ai/en/latest/features/batch_invariance/). Batch-size/order nondeterminism by default: "vLLM does not guarantee the reproducibility of the results by default" (vLLM reproducibility page). MoE-*routing*-specific nondeterminism: not documented on the Qwen card → [UNVERIFIED].
- Free-host availability: **Cloudflare Workers AI `@cf/qwen/qwen3-30b-a3b-fp8`** — served under the free allocation ("Our free allocation allows anyone to use a total of 10,000 Neurons per day at no charge"), and it is **not** in Cloudflare's list of models requiring a paid billing method (that list is Kimi K2.6/K2.7-code, GLM 5.2/5.3/5.3-flash, deepseek-v4-flash-0731, deepseek-v4-pro-0813): https://developers.cloudflare.com/workers-ai/platform/pricing/ (updated 2026-10-01). OpenRouter also serves `qwen/qwen3-30b-a3b` ($0.12/$0.5 per 1M) — not free.
- Notes: newer 2507 revision exists: `Qwen/Qwen3-30B-A3B-Instruct-2507` card states "Context Length: **262,144 natively**" (license on that card not re-fetched → [UNVERIFIED]).

### Qwen3-235B-A22B (MoE)
- Model card URL (primary): https://huggingface.co/Qwen/Qwen3-235B-A22B — accessed 2026-10-06.
- License: **Apache-2.0** (`license: apache-2.0`).
- Params: "235B in total and 22B activated" (non-embedding 234B; 128 experts, 8 activated).
- Context: "32,768 natively and 131,072 tokens with YaRN". The 2507 revision card states "262,144 natively and extendable up to 1,010,000 tokens".
- Bahasa Indonesia evidence: none on card ("Support of 100+ languages and dialects"). Not present on SEA-HELM Indonesian page (that page states "Model Size: ≤200B").
- Structured output: same as other Qwen3 cards (Qwen-Agent / Hermes-style; Model Studio "Qwen3 open source series").
- Determinism caveats: MoE; not in vLLM batch-invariance tested list → not validated, generic vLLM non-reproducibility applies.
- Free-host availability: not on Cloudflare Workers AI list. OpenRouter serves `qwen/qwen3-235b-a22b-2507` at $0.09/$0.55 per 1M — not free. Alibaba Model Studio: per-model quota check.
- Notes: carrier model for the Qwen3 thinking/non-thinking API (`enable_thinking`).

### Qwen3.5-27B (dense, vision-language)
- Model card URL (primary): https://huggingface.co/Qwen/Qwen3.5-27B — accessed 2026-10-06.
- License: **Apache-2.0** (`license: apache-2.0`).
- Params: "Number of Parameters: 27B", dense (Gated DeltaNet + Gated Attention hybrid; "MTP: trained with multi-steps").
- Context: "262,144 natively and extensible up to 1,010,000 tokens."
- Bahasa Indonesia evidence: **yes, third-party, current**: SEA-HELM Indonesian leaderboard (page dated Sep 18, 2026) lists "Qwen 3.5 122B MoE" with Indonesian overall **77.93** (95% CI −1.29/+1.25) and sub-scores Cultural 73.23, Instruction Following 94.69, Knowledge 86.01, Linguistic Diagnostics 72.64, Multi-Turn Chat 88.03, NLG 55.11, NLR 90.07, NLU 80.66, Safety 60.89 — https://leaderboard.sea-lion.ai/detailed/ID (leaderboard restricts to open models ≤200B). The **27B** entry is not separately listed there. Qwen card claims: "Expanded support to 201 languages and dialects". Training data: Indonesian/Latin data **not documented** — only the language-coverage claim.
- Structured output: Model Studio function calling supports "Qwen3.5 open source series"; JSON Object structured output supports "Qwen3.5 open source series (non-thinking mode)" with the caveat: "Models labeled "non-thinking mode" also accept `response_format` … in thinking mode without error, but some may return content that is not strictly valid JSON" (https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-structured-output, and …/qwen-function-calling).
- Determinism caveats: dense LM; thinking mode with `enable_thinking`; hosted Qwen3.5-Flash variant advertises "1M context length by default and official built-in tools" (card). Reasoning-effort controls per model family — no primary determinism guarantee statement on card → [UNVERIFIED] for reasoning-mode determinism.
- Free-host availability: [UNVERIFIED] — not listed in Cloudflare's model price table; OpenRouter lists `qwen/qwen3.5-27b` at $0.195/$1.56 per 1M (not free); Alibaba Model Studio free quota requires the console to show a quota bar.
- Notes: card is multimodal (`pipeline_tag: image-text-to-text`).

### Qwen3.5-35B-A3B (MoE, vision-language)
- Model card URL (primary): https://huggingface.co/Qwen/Qwen3.5-35B-A3B — accessed 2026-10-06.
- License: **Apache-2.0**.
- Params: "35B in total and 3B activated" (MoE).
- Context: "262,144 natively and extensible up to 1,010,000 tokens."
- Bahasa Indonesia evidence: not listed on SEA-HELM Indonesian page (which lists the 122B-A10B only). Language claim: "Expanded support to 201 languages and dialects". Data documentation: none for Indonesian.
- Structured output: Model Studio function calling supports "Qwen3.5 open source series"; JSON Object structured output lists "Qwen3.5 open source series (non-thinking mode)".
- Determinism caveats: MoE + thinking mode; card states "Qwen3.5-Flash is the hosted version corresponding to Qwen3.5-35B-A3B with more production features, e.g., 1M context length by default and official built-in tools." No routing-determinism statement → [UNVERIFIED].
- Free-host availability: OpenRouter `qwen/qwen3.5-35b-a3b` $0.08/$0.75 per 1M — not free. Cloudflare: not listed. Model Studio: console-dependent.
- Notes: cheapest per-token Qwen3.5 tier on OpenRouter among the 3.5 dense line.

### Qwen3.5-122B-A10B (MoE, vision-language)
- Model card URL (primary): https://huggingface.co/Qwen/Qwen3.5-122B-A10B — accessed 2026-10-06.
- License: **Apache-2.0**.
- Params: "122B in total and 10B activated" (MoE).
- Context: "262,144 natively and extensible up to 1,010,000 tokens."
- Bahasa Indonesia evidence: **yes, third-party, current**: SEA-HELM Indonesian leaderboard, "Qwen 3.5 122B MoE", Indonesian overall **77.93** (CI −1.29/+1.25), Knowledge 86.01, Instruction Following 94.69, Cultural 73.23 — https://leaderboard.sea-lion.ai/detailed/ID (Sep 18, 2026). Card language claim: 201 languages/dialects; no Indonesian data documentation.
- Structured output: Model Studio lists "Qwen3.5 open source series" for function calling; JSON Object mode only for its non-thinking mode.
- Determinism caveats: MoE; not in vLLM batch-invariance tested list → [UNVERIFIED] specifically; generic vLLM non-reproducibility applies.
- Free-host availability: OpenRouter does not list 122B-A10B among the ≤$0.0000002/token set; Cloudflare does not list it. [UNVERIFIED] for a free host.
- Notes: the strongest Indonesian-scoring Qwen entry on SEA-HELM ID under 200B (tied with Qwen 3.6 27B within CI).

### Qwen3.8-27B (current open flagship, dense, vision-language)
- Model card URL (primary): https://huggingface.co/Qwen/Qwen3.8-27B — accessed 2026-10-06.
- License: **Apache-2.0** (`license: apache-2.0`).
- Params: "Number of Parameters: 27B", dense.
- Context: "262,144 natively and extensible up to 1,000,000 tokens."
- Bahasa Indonesia evidence: no Indonesian benchmark on card; SEA-HELM ID page lists "Qwen 3.6 27B" (**Indonesian 77.96**, CI −1.22/+1.20; Knowledge 84.63, IF 96.69, Cultural 77.18, Linguistic Diagnostics 68.60) but the Qwen3.8-27B itself is not yet in that leaderboard snapshot (page dated Sep 18, 2026). Card: thinking control only; no language-count claim on the 3.8-27B card.
- Structured output: **Qwen Cloud product page (primary)** lists both features for `qwen3.8-27b`: "Function Calling — Use function calling to connect large language models with external tools and systems." and "Structured Outputs — Structured Outputs help ensure the model returns a JSON string in the expected format." — https://www.qwencloud.com/models/qwen3.8-27b (accessed 2026-10-06). Card also documents `reasoning_effort` ("xhigh" default, `medium`, `low`) and `preserve_thinking`.
- Determinism caveats: "Flexible Thinking Control: Thinking mode is on by default and can be disabled per request; reasoning depth can be tuned with `reasoning_effort`…" (card). No card-level determinism guarantee → [UNVERIFIED]; generic vLLM statements apply for self-hosted serving.
- Free-host availability: **Cloudflare Workers AI `@cf/qwen/qwen3.8-27b`** is priced $0.45/M in, $3.20/M out and is **not** in the paid-billing-required list → usable within the free 10,000 Neurons/day allocation: https://developers.cloudflare.com/workers-ai/platform/pricing/ (updated 2026-10-01). Also **Groq** serves `qwen/qwen3.8-27b` (rate-limit table: 30 RPM, 1K RPD, 8K TPM, 200K TPD on the Developer plan base limits): https://console.groq.com/docs/rate-limits (accessed 2026-10-06) — whether Groq's no-card free tier covers it is [UNVERIFIED] (pricing page https://groq.com/pricing redirects to the marketing homepage). Qwen Cloud pricing for the hosted 1M-context version: $0.5/M in, $3/M out.
- Notes: card says the hosted `qwen3.8-27b` service was "coming soon" at snapshot time; the Qwen Cloud page already documents pricing, rate limits and context (Max Input 991K, Max Output 131K, Context 1M).

### Qwen3.8-Flash-Next (Qwen4-precursor, MoE-ish hybrid, vision-language)
- Model card URL (primary): https://huggingface.co/Qwen/Qwen3.8-Flash-Next — accessed 2026-10-06. License file: https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE — accessed 2026-10-06.
- License: **"Qwen Community License 1.0"** (card YAML `license: other`, `license_name: qwen-community-1.0`). Key restrictions, verbatim:
  - "If the Software (or any derivative works thereof) is Used for any of the licensee's commercial products or services that have more than 100,000,000 monthly active users or US$ 20,000,000 (or equivalent in other currencies) monthly revenue, respective model name must be prominently displayed on the user interface of such product or service"
  - "If the licensee or any of its affiliates conducts a Model as a Service or AI Work Assistant business, the licensee shall obtain a separate license from Qwen before Using the Software or its derivative works for any commercial purpose."
- Params: "125B with 6B activated, plus 51B n-gram embedding and 4B MTP" (hybrid: Gated DeltaNet + Qwen Sparse Attention, Gated Residual, N-gram Embedding).
- Context: "262,144 natively and extensible up to 1,000,000 tokens."
- Bahasa Indonesia evidence: none on card. Card positions it as "This experimental preview of the architecture that will underpin Qwen4". Language/data documentation: none.
- Structured output: card does not claim function calling/JSON; not listed in Model Studio function-calling or structured-output model lists → [UNVERIFIED] (provider-side support not documented).
- Determinism caveats: MoE-style sparse activation + experimental architecture; no determinism statement → [UNVERIFIED].
- Free-host availability: [UNVERIFIED] — not in Cloudflare's price list; not in OpenRouter's ≤$0.0000002/token set; Model Studio eligibility unknown (model is not named in the Model Studio FC/structured-output lists).
- Notes: the only `qwen4_exp`-tagged open release found on 2026-10-06; FP8 variant exists as `Qwen/Qwen3.8-Flash-Next-FP8` (same license tag).

---

## DeepSeek family

### DeepSeek-V3
- Model card URL (primary): https://huggingface.co/deepseek-ai/DeepSeek-V3 — accessed 2026-10-06. License: https://raw.githubusercontent.com/deepseek-ai/DeepSeek-V3/main/LICENSE-MODEL — accessed 2026-10-06. (The HF repo has **no** `LICENSE` file — `https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/LICENSE` returns **HTTP 404**, so the license lives only in the GitHub repo; HF model API shows no `license:` tag for this repo.)
- License: **"DEEPSEEK LICENSE AGREEMENT", Version 1.0, 23 October 2023** (card badges: Code License MIT, Model License "Model_Agreement"). Key restrictions, verbatim from Attachment A / §5:
  - "5. Use-based restrictions. The restrictions set forth in Attachment A are considered Use-based restrictions. Therefore You cannot use the Model and the Derivatives of the Model for the specified restricted uses."
  - "You agree not to use the Model or Derivatives of the Model: … - For military use in any way; - For the purpose of exploiting, harming or attempting to exploit or harm minors in any way; … - For fully automated decision making that adversely impacts an individual's legal rights or otherwise creates or modifies a binding, enforceable obligation; …"
  - "4.a … Use-based restrictions as referenced in paragraph 5 MUST be included as an enforceable provision by You in any type of legal agreement (e.g. a license) governing the use and/or distribution of the Model or Derivatives of the Model".
  - Governing law: PRC law; "The courts located in the domicile of Hangzhou DeepSeek Artificial Intelligence Fundamental Technology Research Co., Ltd. shall have exclusive jurisdiction".
- Params: "671B total parameters with 37B activated for each token" (MoE; MLA + DeepSeekMoE). Note: "The total size of DeepSeek-V3 models on HuggingFace is 685B, which includes 671B of the Main Model weights and 14B of the Multi-Token Prediction (MTP) Module weights."
- Context: 128K ("DeepSeek-V3 performs well across all context window lengths up to **128K**", NIAH figure label).
- Bahasa Indonesia evidence: none on card. Multilingual rows are "MMMLU-non-English (Acc.) 79.4" (base) and MMMLU/Middle; no Indonesian-specific number. Training data: 14.8T tokens, language mix not documented per language → Indonesian documentation: **no**.
- Structured output: Model Studio serves `deepseek-v3` for function calling (https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-function-calling, "DeepSeek" tab: deepseek-v4-pro, deepseek-v4-flash, deepseek-v3.2, deepseek-v3.2-exp (non-thinking mode), deepseek-v3.1 (non-thinking mode), deepseek-r1, deepseek-r1-0528, deepseek-v3). Model Studio JSON Object structured output lists only "deepseek-v4-pro, deepseek-v4-flash".
- Determinism caveats: "Since FP8 training is natively adopted in our framework, we only provide FP8 weights." (card, §6) — FP8 weight + FP8 KV/GEMM paths are a quantisation-dependent determinism variable. vLLM batch-invariance tested list includes `deepseek-ai/DeepSeek-V3` (https://docs.vllm.ai/en/latest/features/batch_invariance/). MoE expert-routing nondeterminism specifically: not stated on the card → [UNVERIFIED].
- Free-host availability: official DeepSeek API no longer serves V3 (see V4.1 entry). Cloudflare Workers AI lists no DeepSeek-V3 endpoint (only `deepseek-r1-distill-qwen-32b`, `deepseek-v4-flash-0731`, `deepseek-v4-pro-0813`). Model Studio free quota is per-model console-dependent. OpenRouter: `deepseek/deepseek-v3` present but not free.
- Notes: superseded by V3-0324 (MIT tag) and V3.1/V3.2 per HF author listing (fetched 2026-10-06).

### DeepSeek-V3.1
- Model card URL (primary): https://huggingface.co/deepseek-ai/DeepSeek-V3.1 — accessed 2026-10-06 (model API + card; last modified 2025-09-05).
- License: **MIT** (`license: mit` in card data; `LICENSE` file present in the repo file list).
- Params: "DeepSeek-V3.1 | 671B | 37B | 128K" (card table, total/activated/context).
- Context: 128K (card table).
- Bahasa Indonesia evidence: none found on card. Not on SEA-HELM Indonesian page.
- Structured output: Model Studio function calling lists "deepseek-v3.1 (non-thinking mode)". Card ships a chat template with explicit tool-call tokens (`<｜tool▁calls▁begin｜>…`).
- Determinism caveats: FP8 (`quantization_config: quant_method fp8`, `num_experts_per_tok: 8` in config.json). Thinking toggle in the chat template (`{%- if not thinking %}{{'</think>'}}`). vLLM batch-invariance tested list includes `deepseek-ai/DeepSeek-V3.1`.
- Free-host availability: [UNVERIFIED] on mainstream free hosts; not in Cloudflare's list.
- Notes: the first MIT-licensed checkpoint in the V3 line after the custom Model Agreement.

### DeepSeek-V3.2
- Model card URL (primary): https://huggingface.co/deepseek-ai/DeepSeek-V3.2 — accessed 2026-10-06. Config: https://huggingface.co/deepseek-ai/DeepSeek-V3.2/raw/main/config.json — accessed 2026-10-06.
- License: **MIT** — card verbatim: "This repository and the model weights are licensed under the [MIT License](LICENSE)." plus the card badge "License-MIT".
- Params: card does not restate totals; config.json shows MoE architecture `DeepseekV32ForCausalLM`, `n_routed_experts: 256`, `num_experts_per_tok: 8`, `num_hidden_layers: 61`, `hidden_size: 7168` — total/active parameter counts **not stated on the V3.2 card** → [UNVERIFIED] (its base `deepseek-ai/DeepSeek-V3.2-Exp-Base` would need to be read for the 671B/37B figure).
- Context: config.json `max_position_embeddings: 163840` (≈160K); card does not restate a context figure.
- Bahasa Indonesia evidence: none on card. Card covers IMO/IOI/ICPC submissions, GPT-5 comparisons, agentic synthesis — no Indonesian or SEA benchmark. Not on SEA-HELM Indonesian page.
- Structured output: card introduces "a revised format for tool calling and the introduction of a 'thinking with tools' capability"; warns the released parser "does not attempt to correct or recover from malformed output … It is not suitable for production use without robust error handling." Model Studio: function calling lists `deepseek-v3.2`; JSON Object mode does **not** list v3.2 (only v4-pro/v4-flash). DeepSeek API docs: "From DeepSeek-V3.2, the API supports tool use in the thinking mode." (https://api-docs.deepseek.com/guides/tool_calls)
- Determinism caveats: card: "For local deployment, we recommend setting the sampling parameters to `temperature = 1.0, top_p = 0.95`." No determinism guarantee stated → [UNVERIFIED]; DeepSeek Sparse Attention (DSA) is a source of implementation-specific nondeterminism not documented by DeepSeek.
- Free-host availability: [UNVERIFIED] free; Model Studio free quota applies only if the console shows quota for the model; Cloudflare does not list it.
- Notes: the Speciale variant is "designed exclusively for deep reasoning tasks and does not support the tool-calling functionality".

### DeepSeek-R1
- Model card URL (primary): https://huggingface.co/deepseek-ai/DeepSeek-R1 — accessed 2026-10-06.
- License: **MIT** (card badge "License-MIT"; HF API `License: mit`; LICENSE at https://github.com/deepseek-ai/DeepSeek-R1/blob/main/LICENSE).
- Params: "DeepSeek-R1 | 671B | 37B | 128K"; also "DeepSeek-R1-Zero | 671B | 37B | 128K" (table).
- Context: 128K (card table).
- Bahasa Indonesia evidence: none on card (benchmarks are math/code/reasoning: AIME, MATH-500, Codeforces, GPQA, etc.). Training data language mix: not documented. Not on SEA-HELM Indonesian page.
- Structured output: Model Studio function calling lists `deepseek-r1` and `deepseek-r1-0528` (DeepSeek tab). DeepSeek API: thinking mode + tool calls documented at https://api-docs.deepseek.com/guides/thinking_mode#tool-calls.
- Determinism caveats: reasoning-model output nondeterminism is explicit in the provider surface: DeepSeek API thinking mode "does not support the `temperature`, `presence_penalty`, or `frequency_penalty` parameters. Please note that, for compatibility with existing software, setting these parameters will not trigger an error but will also have no effect." and "`top_p` only takes effect in thinking mode, where the effective range is `0.95`–`1.0`: values below `0.95` are treated as `0.95`" (https://api-docs.deepseek.com/guides/thinking_mode). FP8 for the open weights (HF tags `fp8`); vLLM batch-invariance tested (`deepseek-ai/DeepSeek-R1`).
- Free-host availability: not on Cloudflare paid-only list, but R1 itself is not in Cloudflare's model table (only the R1-Distill-Qwen-32B). Official DeepSeek API now serves only V4.1-Flash/V4-Pro. [UNVERIFIED] for a current free host of R1-671B.
- Notes: R1-0528 revision exists (`deepseek-ai/DeepSeek-R1-0528`, 205K downloads) and is listed in Model Studio function calling; its license tag was not re-fetched → [UNVERIFIED] (R1-0528-Qwen3-8B also exists, 677K downloads, no license tag read).

### DeepSeek-R1-Distill-Qwen-32B (and sibling distills)
- Model card URL (primary): https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B — accessed 2026-10-06.
- License: **MIT** (HF API `License: mit`; card badge "License-MIT"). Note the **base** is Qwen2.5-32B (Apache-2.0), so the released distill is more permissive than the largest Qwen2.5 checkpoint.
- Params: dense 32B — the distill family is "based on Qwen2.5 and Llama3 series": 1.5B, 7B, 8B, 14B, 32B, 70B (R1 card). Exact per-checkpoint counts not restated on the distill cards → the 32B is a Qwen2.5-32B derivative (32.5B per the Qwen card).
- Context: not stated on the distill card → [UNVERIFIED] (inherits Qwen2.5-32B's 131,072-token support per the Qwen card, but the DeepSeek card does not claim it).
- Bahasa Indonesia evidence: none on card. Not on SEA-HELM Indonesian page (≤200B open models).
- Structured output: Model Studio does not list the distills ("DeepSeek" tab lists only deepseek-v3/v3.1/v3.2/v3.2-exp/v4-pro/v4-flash/r1/r1-0528) → provider-side function calling for this checkpoint [UNVERIFIED].
- Determinism caveats: dense (no MoE routing); reasoning-distill output style includes long CoT; sampling recommendations are inherited from R1 ("We recommend setting temperature=0.6"); card's Usage Recommendations section exists (R1 card) — no determinism guarantee.
- Free-host availability: **Cloudflare Workers AI `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b`** at $0.497/M in, $4.881/M out in Neurons-equivalent pricing, and it is **not** in the paid-billing-required list → usable inside the free 10,000 Neurons/day allocation: https://developers.cloudflare.com/workers-ai/platform/pricing/ (updated 2026-10-01). Note: at 44,375,600 neurons per M output tokens, 10k neurons/day is a very small amount of output (≈0.2k output tokens/day at list price).
- Notes: siblings verified present with MIT tags (HF author listing, 2026-10-06): `DeepSeek-R1-Distill-Qwen-1.5B`, `-7B`, `-14B`, `-32B`, `-Llama-8B`, `-Llama-70B`.

### DeepSeek-V4-Flash / V4-Flash-0731
- Model card URL (primary): https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731 — accessed 2026-10-06 (also https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash).
- License: **MIT** (`license: mit` on both repos per HF listing).
- Params: "DeepSeek-V4-Pro with 1.6T parameters (49B activated) and DeepSeek-V4-Flash with 284B parameters (13B activated)" (V4-Flash card, preview release text); card table repeats `# Total Params 284B`, `# Activated Params 13B`. MoE.
- Context: "both supporting a context length of **one million tokens**".
- Bahasa Indonesia evidence: none on card (benchmarks: AGIEval, MMLU-Pro, C-Eval, MultiLoKo, SimpleQA-Verified, SuperGPQA, BBH, BBEH, DROP, HellaSwag, BigCodeBench, HumanEval, GSM8K, MATH, MGSM, LongBench-V2 — no Indonesian and no SEA benchmark). Training data language documentation: none.
- Structured output: Model Studio function calling lists `deepseek-v4-flash`; Model Studio JSON Object structured output lists "deepseek-v4-pro, deepseek-v4-flash". DeepSeek API: "Json Output ✓ / Tool Calls ✓" for both served models (https://api-docs.deepseek.com/quick_start/pricing), with the caveat "When using the JSON Output feature, the API may occasionally return empty content. We are actively working on optimizing this issue." (https://api-docs.deepseek.com/guides/json_mode).
- Determinism caveats: MoE (13B activated of 284B) → routing-dependent compute; FP8/8-bit tags on the repo; no determinism statement in the card → [UNVERIFIED]. Official API status: "the legacy names `deepseek-v4-flash` and `deepseek-v4-flash-vision-exp` are still accepted, but the corresponding models have been retired, their requests are served by the DeepSeek-V4.1-Flash model and billed at the Flash price." (api-docs.deepseek.com/quick_start/pricing).
- Free-host availability: **Cloudflare Workers AI requires paid billing** for `@cf/deepseek-ai/deepseek-v4-flash-0731` ("Some models require a paid billing method. This applies to … `@cf/deepseek-ai/deepseek-v4-flash-0731`, and `@cf/deepseek-ai/deepseek-v4-pro-0813`") — i.e. **not free**. OpenRouter `deepseek/deepseek-v4-flash-0731` lists $0.0000053/token in, $0.00000128/token out (not free). DeepSeek official: paid.
- Notes: weights are MIT, so self-hosting is unconstrained by license (the constraint is hardware).

### DeepSeek-V4-Pro-0813 / V4-Pro
- Model card URL (primary): https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813 — accessed 2026-10-06.
- License: **MIT** (`license: mit` per HF listing).
- Params: "1.6T parameters (49B activated)" per the V4-Flash card's preview text and the V4.1 comparison table (`# Backbone Params 1.6T`, `# Activated Params 49B`). MoE.
- Context: 1M tokens ("both supporting a context length of one million tokens"; V4.1 card: "All agentic evaluations use `temperature=1.0, top_p=0.95`", 1M-token context window used for code-agent benchmarks).
- Bahasa Indonesia evidence: none on card or in the V4.1 comparison tables; no Indonesian/SEA benchmark columns.
- Structured output: served as `deepseek-v4-pro` on the official API with "Json Output ✓ / Tool Calls ✓" (https://api-docs.deepseek.com/quick_start/pricing); Model Studio lists `deepseek-v4-pro` for both function calling and JSON Object structured output.
- Determinism caveats: MoE + 1M context + FP8; official API thinking mode ignores `temperature` (see thinking-mode doc). No card-level determinism statement → [UNVERIFIED].
- Free-host availability: not free — Cloudflare requires paid billing; official API paid; OpenRouter paid. [No free verified host on 2026-10-06]
- Notes: the official API names it `deepseek-v4-pro`; pricing $0.66/M in (cache miss, off-peak) … $1.32/M (peak), $1.98–3.96/M out (@docs.deepseek.com/quick_start/pricing, fetched 2026-10-06).

### DeepSeek-V4.1-Flash (current official "deepseek-flash")
- Model card URL (primary): https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash — accessed 2026-10-06. Technical report PDF linked from card: `DeepSeek_V41_Tech_Report.pdf` (not fetched).
- License: **MIT** (card badge "License-MIT"; HF API `License: mit`).
- Params: "a multimodal Mixture-of-Experts (MoE) model with 552B backbone parameters and support for contexts of up to one million tokens"; "activate only **8B parameters per token during prefill** and **16B during decode**"; "The model uses 1 shared expert and 384 routed experts per MoE layer, activating 6 routed experts per token." Also "Engram conditional memory (196B parameters, sparsely accessed via token-based lookup)".
- Context: "support for contexts of up to one million tokens"; API doc states "CONTEXT LENGTH 1M", "MAX OUTPUT 384K".
- Bahasa Indonesia evidence: none. Card tables cover MMLU-Pro, C-Eval, MultiLoKo, SuperGPQA, MMLU-Pro (base = 74.1), GPQA Diamond, HLE, Codeforces, Terminal-Bench, etc. No Indonesian benchmark anywhere on the card. Training: "45T tokens" multimodal corpus, no per-language documentation.
- Structured output: official API "Json Output ✓ / Tool Calls ✓" for `deepseek-flash`; **strict mode** for tool calls exists: "In `strict` mode, the model strictly adheres to the format requirements of the Function's JSON schema when outputting a tool call" (https://api-docs.deepseek.com/guides/tool_calls, Beta base_url required).
- Determinism caveats: **controllable reasoning effort**: "The model supports a continuously controllable reasoning effort setting (integer 1–100) that trades inference cost for accuracy." (card); API: thinking mode is default with effort `high`, `temperature`/penalties have no effect, `top_p` clamped to ≥0.95 — verbatim: "Thinking mode does not support the `temperature`, `presence_penalty`, or `frequency_penalty` parameters… setting these parameters will not trigger an error but will also have no effect." (https://api-docs.deepseek.com/guides/thinking_mode). MoE routing (384 routed experts, 6 active) → per-token expert choice is an additional nondeterminism surface; DeepSeek does not document routing determinism → [UNVERIFIED]. FP4 main KV cache (E2M1) + 890 bytes/token KV is a quantisation-dependent determinism variable (card).
- Free-host availability: `deepseek-flash` on the official API is **paid** (pricing table lists per-token rates; there is "granted balance" language but no free tier documented — https://api-docs.deepseek.com/quick_start/pricing). Cloudflare does **not** currently offer V4.1-Flash (its DeepSeek endpoints are V4-Flash-0731 and V4-Pro-0813, both paid-only). Novita serves "DeepSeek V4.1 Flash" at $0.3/M in, $1.2/M out (https://novita.ai/pricing, fetched 2026-10-06) — not free.
- Notes: the only DeepSeek model on the official API served under the plain name `deepseek-flash`.

---

## Cross-cutting: Indonesian benchmark evidence (what exists today)

- **SEA-HELM Indonesian leaderboard** (primary, page dated Sep 18, 2026; fetched 2026-10-06): https://leaderboard.sea-lion.ai/detailed/ID — "Indonesian Scores by Model", "Average of 2000 bootstraps. 95% CI are shown." Scope stated on the leaderboard: "Open models only", "Model Size: ≤200B".
  - Qwen 3.6 27B (Alibaba): Indonesian **77.96** [−1.22, +1.20]; Knowledge 84.63; Instruction Following 96.69; Cultural 77.18; Linguistic Diagnostics 68.60; Multi-Turn Chat 86.05; NLG 55.18; NLR 89.96; NLU 82.66; Safety 60.74.
  - Qwen 3.5 122B-A10B MoE (Alibaba): Indonesian **77.93** [−1.29, +1.25]; Knowledge 86.01; Instruction Following 94.69; Cultural 73.23; Linguistic Diagnostics 72.64; Multi-Turn Chat 88.03; NLG 55.11; NLR 90.07; NLU 80.66; Safety 60.89.
  - **No DeepSeek model appears on the Indonesian page** (as of 2026-10-06).
- **IndoMMLU / IndoNLU / NusaX numbers for these specific checkpoints**: not found on any primary page (model cards or an official leaderboard) in this session. Searches returned only aggregator sites (benchlm.ai, llm-stats.com, pricepertoken.com) — **not** used as evidence.

## Cross-cutting: structured output / function calling (primary sources)

- Qwen (framework): https://qwen.readthedocs.io/en/latest/framework/function_call.html — "We recommend using Hermes-style tool use for Qwen3 to maximize function calling performance."
- Qwen (provider): https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-function-calling — supported-model list includes "Qwen3.8 open source series", "Qwen3.5 open source series", "Qwen3 open source series", "Qwen2.5 open source series", plus a DeepSeek tab (`deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-v3.2`, `deepseek-v3.2-exp` (non-thinking), `deepseek-v3.1` (non-thinking), `deepseek-r1`, `deepseek-r1-0528`, `deepseek-v3`).
- Qwen (provider JSON): https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-structured-output — two modes, "JSON Object" and "JSON Schema"; JSON Object covers Qwen3.8/3.6/3.5/3/Qwen2.5 open-source series (3.6/3.5/3 only in non-thinking mode) and DeepSeek only `deepseek-v4-pro`/`deepseek-v4-flash`; **JSON Schema mode only for "Qwen3.7-Plus series, Qwen3.7-Flash series, Qwen3.7-Max series, Qwen3.8-Max series, and Qwen3.8-Flash series models"** → for open-weight checkpoints, strictly-schema-constrained JSON is not documented.
- Qwen Cloud product page for the hosted sibling: https://www.qwencloud.com/models/qwen3.8-27b — "Function Calling" and "Structured Outputs" both listed as features, with pricing $0.5/M in, $3/M out, Context 1M, Max Input 991K, TPM 5M, RPM 5K.
- DeepSeek: https://api-docs.deepseek.com/guides/json_mode (JSON Output caveat: "the API may occasionally return empty content"), https://api-docs.deepseek.com/guides/tool_calls (strict mode Beta; thinking-mode tool use from V3.2), https://api-docs.deepseek.com/guides/thinking_mode (temperature/penalties inert in thinking mode; top_p clamped ≥0.95; reasoning_content round-trip rules).

## Cross-cutting: determinism (primary sources)

- vLLM engine-level: "vLLM does not guarantee the reproducibility of the results by default, for the sake of performance." Options: `VLLM_ENABLE_V1_MULTIPROCESSING=0` (offline only) or batch invariance; "Even with the above settings, vLLM only provides reproducibility when it runs on the same hardware and the same vLLM version." — https://docs.vllm.ai/en/latest/usage/reproducibility/ (page dated April 28, 2026).
- Batch invariance doc (dated October 4, 2026): "Batch invariance ensures that the output of a model is deterministic and independent of the batch size or the order of requests in a batch." Enabling it "may impact performance compared to the default non-deterministic mode". Tested models relevant here: **DeepSeek**: V3, V3-0324, R1, V3.1; **Qwen3 MoE**: Qwen3-30B-A3B, Qwen3-Next-80B-A3B-Instruct, Qwen3-30B-A3B-Thinking-2507-FP8; **Qwen2.5**: 0.5B/1.5B/3B/7B/14B/32B-Instruct — https://docs.vllm.ai/en/latest/features/batch_invariance/.
- DeepSeek **reasoning-mode** nondeterminism by construction: thinking mode disables `temperature`/penalties and clamps `top_p` to 0.95–1.0 (docs above); effort mapping is lossy ("minimal→low, low→low, medium→high, high→high, xhigh→high, max→max, ultra→max").
- DeepSeek **FP8 weights only**: "Since FP8 training is natively adopted in our framework, we only provide FP8 weights." (DeepSeek-V3 card) — quantisation-dependent numerics.
- **MoE expert-routing nondeterminism**: no primary provider statement found on any Qwen or DeepSeek model card; only engine-level generic statements (vLLM). Marked [UNVERIFIED] per model.

## Cross-cutting: free-host availability (verified 2026-10-06)

- **Cloudflare Workers AI** (https://developers.cloudflare.com/workers-ai/platform/pricing/, page updated 2026-10-01): "Our free allocation allows anyone to use a total of **10,000 Neurons per day at no charge**." Qwen endpoints listed: `@cf/qwen/qwen3-30b-a3b-fp8` ($0.051/M in, $0.335/M out), `@cf/qwen/qwen3.8-27b` ($0.45/M in, $3.20/M out), plus `@cf/qwen/qwq-32b`, `@cf/qwen/qwen2.5-coder-32b-instruct`, `@cf/qwen/qwen3-embedding-0.6b`. DeepSeek endpoints: `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b` (free-tier eligible), and `@cf/deepseek-ai/deepseek-v4-flash-0731` + `@cf/deepseek-ai/deepseek-v4-pro-0813` which **require a paid billing method**.
- **Alibaba Cloud Model Studio** (https://www.alibabacloud.com/help/en/model-studio/new-free-quota, fetched 2026-10-06): new users in the **Singapore** region get a free quota per model — "Each model (such as qwen-plus, qwen3.6-plus, or qwen3.6-plus-2026-04-02) has its own independent free quota (typically 1,000,000 tokens)"; validity: "The free quota is valid for 90 days, starting from the date you activate Alibaba Cloud Model Studio, the model is released, or your model request is approved (whichever is later)." "Free Quota Only" mode can cap usage at zero spend. OAuth authentication has a separate free quota: "2,000 calls per day". Per-model eligibility today could not be read without the console → **per-model free status [UNVERIFIED]**; the page is the authoritative rule set.
- **OpenRouter** (public model API https://openrouter.ai/api/v1/models, fetched 2026-10-06): the free catalogue (`:free` ids) contains **16 models, none of them Qwen or DeepSeek** (they are Gemma 4, Nemotron 3/3.5, Poolside Laguna, Thinking Machines Inkling, Cohere North Mini Code, Liquid LFM, Dots, InclusionAI, Apodex). The OpenRouter models page https://openrouter.ai/models?max_price=0 rendered JS-only and returned no model list to `read` — the API endpoint was used instead. Cheapest Qwen/DeepSeek entries on OpenRouter (USD per token, as published): `deepseek/deepseek-v4-flash` $0.0000000018 in / $0.00000128 out; `qwen/qwen3.7-flash` $0.00000003 / $0.00000013; `qwen/qwen3-32b` $0.00000008 / $0.00000028.
- **Groq** (https://console.groq.com/docs/rate-limits, fetched 2026-10-06): serves `qwen/qwen3.8-27b` with 30 RPM / 1K RPD / 8K TPM / 200K TPD base limits on the Developer plan. A no-card **free tier** is asserted by secondary sources only; https://groq.com/pricing redirected to the marketing homepage and https://console.groq.com/docs/billing returned HTTP 404 → Groq free-tier status **[UNVERIFIED]**.
- **DeepSeek official API**: paid only (per-token price table; no free tier documented) — https://api-docs.deepseek.com/quick_start/pricing.
- **Novita** (https://novita.ai/pricing, fetched 2026-10-06): paid token pricing for DeepSeek V4/V4.1/R1 lines (e.g. DeepSeek V4.1 Flash $0.3/M in, $1.2/M out; V4 Flash $0.14/M in, $0.28/M out); no free tier shown on the pricing page.
- **Nebius / Hyperbolic / Together / Fireworks free tiers for these exact checkpoints**: not verified in this session (sibling agents cover provider pages).

---

## Not verified / gaps

- **Qwen2.5-72B-Instruct model card prose vs YAML**: card YAML says `language: en` while prose claims 29+ languages; Indonesian is not named. No Indonesian benchmark for Qwen2.5 at 7B/14B/32B/72B on any primary page found.
- **Qwen3 dense/MoE Indonesian numbers**: none found. Qwen3-32B, Qwen3-30B-A3B, Qwen3-235B-A22B absent from SEA-HELM Indonesian page (≤200B open-model scope; SEA-HELM lists only Qwen 3.5-122B-A10B and Qwen 3.6 27B from Alibaba).
- **Qwen3.5-27B / Qwen3.5-35B-A3B / Qwen3.8-27B Indonesian scores**: not on the Sep 18, 2026 SEA-HELM ID snapshot (only 3.5-122B-A10B and 3.6-27B). The Qwen 3.6 27B number is reported here as context; the 3.6 card itself was not fetched.
- **DeepSeek Indonesian evidence: none at all.** No Indonesian/SEA benchmark on any DeepSeek card (V3, V3.1, V3.2, R1, V4-Flash, V4-Pro, V4.1-Flash) and no DeepSeek row on SEA-HELM ID. IndoMMLU numbers for any Qwen/DeepSeek checkpoint are [UNVERIFIED] — no primary leaderboard reached (only aggregator pages, which were not treated as evidence).
- **DeepSeek-V3.2 total/active parameter counts**: card omits them; config.json confirms 256 routed experts / 61 layers / max_position 163,840 but no parameter totals → [UNVERIFIED] without reading `DeepSeek-V3.2-Exp-Base`.
- **DeepSeek-V3 license on HF**: `.../raw/main/LICENSE` is HTTP 404 on the HF repo; the binding text is only in GitHub `LICENSE-MODEL` (DeepSeek License Agreement v1.0, 23 Oct 2023). HF model API exposes no license tag for that repo.
- **DeepSeek-R1-0528 / R1-Distill sibling licenses**: R1-0528 and R1-0528-Qwen3-8B exist (HF author listing) but their license files were not fetched → [UNVERIFIED] (the six R1-Distill repos all carry `license:mit` tags).
- **Qwen2.5-72B Qwen-license source**: license text fetched from `Qwen/Qwen2.5-72B-Instruct`; the base `Qwen/Qwen2.5-72B` repo was not separately fetched (assumed identical — [UNVERIFIED] assumption).
- **Qwen3-30B-A3B-Instruct-2507 / Qwen3-235B-A22B-Instruct-2507 licenses**: context lines verified from their READMEs, license fields not fetched → [UNVERIFIED].
- **Qwen3.5/Qwen3.8 hosted-service free tier on Model Studio / Qwen Cloud**: per-model free-quota eligibility is only visible in the Alibaba Cloud console; docs describe the program generically (1M tokens/model, 90 days, Singapore region) → per-model [UNVERIFIED].
- **Groq free tier**: no primary page confirmed it (pricing URL redirects; /docs/billing 404). qwen3.8-27b is confirmed served, but "free" is [UNVERIFIED].
- **MoE routing nondeterminism**: no primary statement from Alibaba or DeepSeek; only vLLM's engine-level non-reproducibility/batch-invariance docs. [UNVERIFIED] as a provider claim.
- **Free-host coverage for Nebius, Hyperbolic, Together, Fireworks, DeepInfra free tiers on these exact checkpoints**: not fetched in this session.
- **Qwen3.8-Flash-Next / Qwen3.8-Flash provider support** (`qwen4_exp`-era experimental model): not listed in Model Studio function-calling or structured-output model lists → [UNVERIFIED].
- **OpenRouter `deepseek/deepseek-v4-flash` input price of $0.0000000018/token**: taken verbatim from the public OpenRouter models API on 2026-10-06; it is ~50× below the next-cheapest DeepSeek listing and was not independently corroborated → treat as unconfirmed (possible promotional or mis-published value).
- **Qwen3.8-Flash-Next n-gram embedding effective parameter semantics** (125B + 51B n-gram + 4B MTP): reported as the card states; per-token active-parameter behaviour under n-gram lookup is not documented on the card → [UNVERIFIED].
