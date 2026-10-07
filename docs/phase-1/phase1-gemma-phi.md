# Phase 1 — Google Gemma family & Microsoft Phi-4 family

All URLs accessed **2026-10-06** unless a different page date is quoted. Quotes are verbatim from the primary page fetched today.

## Cross-cutting primary sources

- Gemma Terms of Use — https://ai.google.dev/gemma/terms — access 2026-10-06
  - Page states: `Last modified: April 1, 2026` and, at top: "For Gemma 4 terms, see the [Gemma 4 license](/gemma/apache_2)."
  - Appendix (the finite list the Terms govern) includes Gemma 1, 1.1, **Gemma 2**, **Gemma 3**, Gemma 3n, FunctionGemma, EmbeddingGemma, PaliGemma/2, ShieldGemma/2, CodeGemma/1.1, Gemma 2 JPN, DataGemma, RecurrentGemma, Gemma Scope, Gemma-APS, T5Gemma, VaultGemma, T5Gemma 2, TranslateGemma. **Gemma 4 is not in the Appendix.**
  - Redistribution condition (quote): "You must include the use restrictions referenced in Section 3.2 as an enforceable provision in any agreement (e.g., license agreement, terms of use, etc.) governing the use and/or distribution of Gemma or Model Derivatives and you must provide notice to subsequent users you Distribute to that Gemma or Model Derivatives are subject to the use restrictions in Section 3.2."
  - Also required (quote): "All Distributions (other than through a Hosted Service) must be accompanied by a '**Notice**' text file that contains the following notice: 'Gemma is provided under and subject to the Gemma Terms of Use found at ai.google.dev/gemma/terms'."
  - Restriction (quote): "You must not use any of the Gemma Services: 1. for the restricted uses set forth in the Gemma Prohibited Use Policy at ai.google.dev/gemma/prohibited_use_policy … or 2. in violation of applicable laws and regulations."
  - Remote-termination clause (quote): "To the maximum extent permitted by law, Google reserves the right to restrict (remotely or otherwise) usage of any of the Gemma Services that Google reasonably believes are in violation of this Agreement."
  - Outputs (quote): "Google claims no rights in Outputs you generate using Gemma."
- Gemma 4 license page — https://ai.google.dev/gemma/apache_2 — access 2026-10-06 — page is the plain Apache License 2.0 text; page footer `Last updated 2026-04-01 UTC`. Gemma 4 model card states `**License**: [Apache 2.0](https://ai.google.dev/gemma/apache_2)`.
- Gemma 4 model overview — https://ai.google.dev/gemma/docs/core — page footer `Last updated 2026-07-08 UTC`.

---

### Gemma 2 9B / 27B (and 2B)

- Model card URL (primary): https://ai.google.dev/gemma/docs/core/model_card_2 — access 2026-10-06 (page footer: `Last updated 2025-02-25 UTC`)
- License: **Gemma Terms of Use** (non-OSI). Card links "Terms of Use: Terms"; the live Terms Appendix lists `[Gemma 2](https://ai.google.dev/gemma/docs/core/model_card_2)`. Terms last modified 2026-04-01. Key restriction = Section 3.2 use restrictions (Gemma Prohibited Use Policy) + redistribution conditions quoted above (notice file, pass-through of restrictions, remote-restriction reservation).
- Params: dense text-only LLMs at 2B / 9B / 27B. Card: "the 27B model was trained with 13 trillion tokens, the 9B model was trained with 8 trillion tokens, and 2B model was trained with 2 trillion tokens."
- Context length: **NOT stated on the card** (card text never prints a token context length). Tech report describes Gemma 2 as the "1:1, sw=4096" configuration — https://arxiv.org/html/2503.19786v1 (quote: "The '1:1, sw=4096' is used in Gemma 2."). Max context for Gemma 2 is **[UNVERIFIED]** from the card fetched today.
- Bahasa Indonesia evidence: **none**. Card says the models are "available in English" and web text is "Primarily English-language content." No Indonesian/IndoMMLU/SeaBench/SEA-HELM score on the card. Live SEA-HELM Indonesian board (below) lists no Gemma 2 entry. → [UNVERIFIED] / effectively no documented Indonesian evidence.
- Structured output: card makes no function-calling or JSON claim; inputs/outputs described only as text. → **No claim** on the model card.
- Determinism caveats: no sampling/determinism statement on the card. Gemma 2 uses a sliding window of 4096 ("1:1, sw=4096" quote above, from the Gemma 3 tech report); no primary doc claims window-induced nondeterminism for outputs. Framework-level caveats in the "Determinism" section at the end.
- Free-host availability: Gemma 2 weights are on Kaggle (card links https://www.kaggle.com/models/google/gemma-2) and Vertex Model Garden; hosted-inference free tier for Gemma 2 today: **[UNVERIFIED]** — the Cloudflare Workers AI model catalogue fetched today lists `gemma-2b-it-lora` and `gemma-7b-it-lora` (LoRA-only) but no Gemma 2 9B/27B; Groq's model page lists no Gemma at all (see providers section).
- Notes: legacy generation; superseded by Gemma 3/4. Card is English-centric, so it is a weak candidate for Indonesian evaluation on documented evidence.

---

### Gemma 3 1B / 4B / 12B / 27B (+ 270M)

- Model card URL (primary): https://ai.google.dev/gemma/docs/core/model_card_3 — access 2026-10-06 (page footer: `Last updated 2025-08-14 UTC`). HF card: https://huggingface.co/google/gemma-3-27b-it — access 2026-10-06, metadata `License: gemma`, `Access: Gated`.
- License: **Gemma Terms of Use** (HF license tag `gemma`; card links "Terms of Use: Terms"). Non-permissive: Prohibited Use Policy incorporated by reference, redistribution must carry the Notice text file and downstream-enforceable use restrictions, and Google "reserves the right to restrict (remotely or otherwise) usage" (quotes + URL under Cross-cutting sources).
- Params: 1B, 4B, 12B, 27B (+ 270M variant on the same card). Vision encoder shared across 4B/12B/27B (tech report, https://arxiv.org/html/2503.19786v1: "we share the vision encoder across our 4B, 12B, and 27B models"); the 1B is listed separately with 32K context.
- Context length: **128K tokens** for 4B/12B/27B; **32K tokens** for 1B and 270M. Card quote: "Total input context of 128K tokens for the 4B, 12B, and 27B sizes, and 32K tokens for the 1B and 270M sizes." Text + image input (images "normalized to 896 x 896 resolution and encoded to 256 tokens each").
- Bahasa Indonesia evidence: **no Indonesian-specific number.** Card multilingual table (IT): Global-MMLU-Lite 75.1 (27B), 69.5 (12B), 54.5 (4B), 34.2 (1B); ECLeKTic 16.7 / 10.3 / 4.6 / 1.4; WMT24++ 53.4 / 51.6 / 46.8 / 35.9 — no per-language (Indonesian) breakdown. PT: MGSM 74.3 (27B), Global-MMLU-Lite 75.7, XQuAD 76.8, IndicGenBench 63.4. URL: model_card_3. The live SEA-HELM Indonesian leaderboard (accessed 2026-10-06, page dated Sep 18, 2026) shows only **Gemma 4 31B** and **Gemma 4 (E2B)** for Google, plus the SEA-LION Gemma-E2B derivative — **no Gemma 3 27B entry**: https://leaderboard.sea-lion.ai/detailed/ID
- Training-data language documentation: card says "The training dataset includes content in over 140 languages", knowledge cutoff **August 2024**. **Indonesian is not explicitly enumerated** on the Gemma 3 card; grep of the Gemma 3 technical report text (https://arxiv.org/html/2503.19786v1) for "Indonesian" returned no match, so an explicit Indonesian listing is **[UNVERIFIED]**.
- Structured output: **no function-calling or JSON claim on the Gemma 3 card** (it lists text generation and image understanding uses only). Gemma's function-calling documentation page fetched today is Gemma-4-specific (`function-calling-gemma4`); Google also ships a separate FunctionGemma family, implying Gemma 3 IT is not the documented tool-calling path. → Gemma 3: **no primary claim found**; treat function calling/JSON as unverified for Gemma 3.
- Determinism caveats: card carries no sampling-parameter section (Gemma 4's card has one; Gemma 3's does not). Architecture is hybrid local/global attention: tech report — "We alternate between a local sliding window self-attention and global self-attention …, with a pattern of 5 local layers for every global layer" and "sliding windows of 1024 ('sw=1024')". No primary source fetched today claims the sliding window by itself makes outputs nondeterministic; framework-level caveats apply (see Determinism section).
- Free-host availability:
  - **Cloudflare Workers AI** still prices `@cf/google/gemma-3-12b-it` at $0.345 per M input / $0.556 per M output tokens, inside the free 10,000-Neurons/day Workers Free allocation — https://developers.cloudflare.com/workers-ai/platform/pricing/ (page `Last updated Oct 1, 2026`), accessed 2026-10-06.
  - **Google AI Studio / Gemini API free tier**: the live pricing page lists a free tier for "**Gemma 4**" only; Gemini API's `Used to improve our products` = **Yes** on the free tier — https://ai.google.dev/gemini-api/docs/pricing (page footer `Last updated 2026-10-06 UTC`). No Gemma 3 row → Gemma 3 via Gemini API free tier **[UNVERIFIED]** today.
  - Gemma 3 27B on any free host: **[UNVERIFIED]** — no provider page fetched today lists Gemma 3 27B.
- Notes: multimodal (text+image) for 4B/12B/27B; training tokens 14T (27B)/12T (12B)/4T (4B)/2T (1B).

---

### Gemma 4 (E2B / E4B / 12B Unified / 26B A4B MoE / 31B) — released, Apache 2.0

- Model card URL (primary): https://ai.google.dev/gemma/docs/core/model_card_4 — access 2026-10-06 (page footer: `Last updated 2026-07-30 UTC`). Overview: https://ai.google.dev/gemma/docs/core. Technical report: https://arxiv.org/abs/2607.02770 (cited on card).
- License: **Apache 2.0** — card: `**License**: [Apache 2.0](https://ai.google.dev/gemma/apache_2)`; license page https://ai.google.dev/gemma/apache_2 (Apache 2.0 text, page `Last updated 2026-04-01`). The Gemma Terms page says "For Gemma 4 terms, see the Gemma 4 license" and does **not** list Gemma 4 in its Appendix, i.e. the Prohibited-Use-Policy / Notice-file restrictions quoted above are **Terms of Use (Gemma 1–3) restrictions, not Gemma 4 restrictions**. No use-restriction sentence is quoted for Gemma 4 on the live Apache page.
- Params (dense + MoE): E2B `2.3B effective (5.1B with embeddings)`; E4B `4.5B effective (8B with embeddings)`; 12B Unified `11.95B`; 31B Dense `30.7B`; **26B A4B MoE: `25.2B` total / `3.8B` active**, "Expert Count: 8 active / 128 total and 1 shared". Architecture note (quote): "While it only activates 4 billion parameters per token during generation, **all 26 billion parameters** must be loaded into memory…" (overview page).
- Context length: **128K tokens (E2B/E4B); 256K tokens (12B, 26B A4B, 31B)**; sliding window 512 tokens (E2B/E4B) or 1024 tokens (12B/26B/31B); vocab 262K. Quote: "Gemma 4 features a context window of up to 256K tokens and maintains multilingual support in over 140 languages."
- Bahasa Indonesia evidence (primary leaderboard, fetched today):
  - Source: SEA-HELM leaderboard, Indonesian page — https://leaderboard.sea-lion.ai/detailed/ID — accessed 2026-10-06 (leaderboard dated **Sep 18, 2026**).
  - **Gemma 4 31B — Indonesian (ID) 79.75** [95% CI −1.25/+1.20]; components: Cultural 76.45, Inst. Following 97.75, Knowledge 84.70, Linguistic Diagnostics 78.66, Multi-Turn Chat 86.59, NLG 56.53, NLR 90.35, NLU 83.18, Safety 63.57. Overall SEA average 76.17.
  - **Gemma 4 (E2B) — Indonesian 64.13** [−1.39/+1.41]; SEA average 58.82.
  - Derivative for context: **SEA-LION v4.5 (Gemma E2B)** Indonesian 63.96.
  - Card-internal multilingual (not Indonesian-specific): MMMLU 88.4 (31B), 86.3 (26B A4B), 83.4 (12B), 76.6 (E4B), 67.4 (E2B), vs Gemma 3 27B (no think) 70.7.
  - Training data: "The training dataset includes content in over 140 languages", cutoff **January 2025**; card states "Out-of-the-box support for 35+ languages, pre-trained on 140+ languages". **Indonesian is not enumerated by name** → explicit-listing is **[UNVERIFIED]** (only "140+ languages" + SEA-HELM scores).
- Structured output: card (quote) — "**Function Calling** – Native support for structured tool use, enabling agentic workflows." Provider doc: Cloudflare model page for `@cf/google/gemma-4-26b-a4b-it` flags `Function calling | Yes` and its request schema includes `response_format` — "Specifies the format the model must output", plus `tools[]`, `tool_choice`, `parallel_tool_calls` (default true), and `seed` ("If specified, the system will make a best effort to sample deterministically") — https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/ — access 2026-10-06. Google's own how-to (https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4, access 2026-10-06) shows tool declarations passed via `apply_chat_template(..., tools=[...])` and the model emitting `<|tool_call>call:get_current_temperature{location:<|"|>London<|"|>}<tool_call|>`. Note the page's own caveat heading "Important Caveat: Automatic vs. Manual Schemas". No card claim of *guaranteed* valid JSON — claims are "native support", plus a caveat section.
- Determinism caveats (primary, from today's pages):
  - Thinking mode is on/off by prompt token and emits tagged reasoning: trigger "by including the `<|think|>` token at the start of the system prompt"; output structure `<|channel>thought\n**[Internal reasoning]**<channel|>`; when thinking is disabled (except E2B/E4B) the empty block `<|channel>thought\n<channel|>` is still emitted. Card also requires: "In multi-turn conversations, the historical model output should only include the final response. Thoughts from previous model turns must *not be added*…" → reasoning-mode output differs by prompt construction.
  - Card's canonical sampling: `temperature=1.0`, `top_p=0.95`, `top_k=64` — i.e. the documented best-practice default is stochastic sampling, not greedy.
  - 26B A4B is MoE with 8-of-128 expert routing; **no primary page fetched today states whether routing is deterministic** → **[UNVERIFIED]** at model level; framework-level caveats below.
  - Sliding-window/global hybrid attention: "The models employ a hybrid attention mechanism that interleaves local sliding window attention with full global attention, ensuring the final layer is always global." (card). No primary claim that this changes outputs run-to-run.
- Free-host availability (verified today):
  - **Gemini API (Gemma 4) — free tier confirmed**: pricing page section "## [Gemma 4]" — Input price: `Free of charge`, Output price: `Free of charge`, Context caching: `Free of charge`, Paid tier: `Not available`, `Used to improve our products`: **Yes** (free tier). URL https://ai.google.dev/gemini-api/docs/pricing, page `Last updated 2026-10-06 UTC`. Page notes "Google AI Studio usage is free of charge in all available regions." **Rate limits: the live rate-limits page publishes no numeric Gemma row** — it directs to AI Studio: "For details on those rate limits, see the [AI Studio Rate Limit] page" (https://ai.google.dev/gemini-api/docs/rate-limits, `Last updated 2026-09-02 UTC`) → Gemma-4 free-tier RPM/RPD **not published** on the docs page (rate-limit numbers **[UNVERIFIED]**).
  - **Cloudflare Workers AI** — `@cf/google/gemma-4-26b-a4b-it`, `$0.10 per M input tokens, $0.30 per M output tokens` (9091 / 27273 neurons per M tokens), inside the free allocation: "Our free allocation allows anyone to use a total of **10,000 Neurons per day at no charge**." Model page: https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/ ; pricing page https://developers.cloudflare.com/workers-ai/platform/pricing/ (`Last updated Oct 1, 2026`). gemma-4-26b-a4b-it is **not** in the "Some models require a paid billing method" list (that list names kimi-k2.6/k2.7, glm-5.2/5.3/5.3-flash, deepseek-v4-flash-0731/v4-pro-0813) → usable on the free allocation.
  - **Ollama cloud** — `gemma4` is in the pay-as-you-go model table at `$0.14` input / `$0.05` cached input / `$0.40` output per M tokens; Free plan gives "Starter usage credits included", "Includes access to starter models", and "Free includes 1 concurrent request" — https://ollama.com/cloud (redirects to https://ollama.com/pricing), access 2026-10-06. Whether `gemma4` is inside the Free plan's starter model set is **[UNVERIFIED]**.
  - **Together AI** — Gemma 4 31B at `$0.39` input / `$0.97` output per M tokens (no free tier stated for it): https://www.together.ai/pricing, access 2026-10-06.
  - **Kaggle / Hugging Face** — weights distribution, not hosted inference: card buttons "Get it on Kaggle" / "Get it on Hugging Face"; Kaggle docs confirm gated-model consent flow and kagglehub download (https://www.kaggle.com/docs/models, access 2026-10-06). Kaggle free notebook GPU quota for Gemma 4: **[UNVERIFIED]** (no quota statement fetched).
  - **Groq — no Gemma of any version**: https://console.groq.com/docs/models lists Llama 3.1/3.3, GPT-OSS, Whisper, MiniMax M2.7, Qwen3.8-27B etc. — **no Gemma**, access 2026-10-06.
  - **Cerebras — no Gemma**: https://inference-docs.cerebras.ai/models/overview lists only `gpt-oss-120b` and `qwen-3.8-27b` on Shared Inference (free trial + PAYG) → no Gemma, access 2026-10-06.
  - **GitHub Models — service retired**: "As of July 30, 2026, GitHub Models has been fully retired. The playground, model catalog, inference API, and bring your own key (BYOK) are no longer available to any customer." https://docs.github.com/en/github-models — access 2026-10-06 → no free Gemma/Phi hosting there.
  - **Hugging Face Inference Providers** free credits: Free Users `$0.10`/month (subject to change), PRO `$2.00`, "no markup from Hugging Face" — https://huggingface.co/docs/inference-providers/pricing, access 2026-10-06.
- Notes: Gemma 4 ships QAT checkpoints (GGUF/w4a16/mobile) and Multi-Token-Prediction draft models for speculative decoding; memory table: 31B needs 69.9 GB BF16 (17.5 GB Q4_0), 26B A4B 57.7 GB BF16.

---

### Phi-4 (14B)

- Model card URL (primary): https://huggingface.co/microsoft/phi-4 — access 2026-10-06 (HF metadata: License `mit`, language `en`, arxiv 2412.08905).
- License: **MIT** (`License: MIT` in the summary table; `license_link: https://huggingface.co/microsoft/phi-4/resolve/main/LICENSE`). Microsoft's Phi portal likewise states "Phi models are open source through the MIT License" (https://azure.microsoft.com/en-us/products/phi, access 2026-10-06). No non-permissive restriction sentence to quote; permissive, commercial use permitted.
- Params: **14B, dense** — card: "14B parameters, dense decoder-only Transformer model".
- Context length: **16K tokens** — card: "16K tokens".
- Bahasa Indonesia evidence: **none.** Card data overview: "Multilingual data constitutes about 8% of our overall data." Benchmark table includes MGSM 80.6 (multilingual grade-school math) with **no per-language Indonesian result**; languages tag is `en` only. Card explicitly: "`phi-4` is not intended to support multilingual use." → Indonesian evidence **[UNVERIFIED]** (no Indonesian number surfaced).
- Structured output: **no function-calling/JSON claim on the phi-4 card**; the card documents only a ChatML-style chat format and `inference: parameters: temperature: 0`. Tool-calling is documented on Phi-4-mini / Phi-4-multimodal instead.
- Determinism caveats: card ships `temperature: 0` as the sample inference parameter (suggesting greedy), but note the model is DPR-aligned chat; no determinism guarantee stated. Reasoning-mode caveats apply to the Phi-4-reasoning variants, not to phi-4 itself.
- Free-host availability:
  - **Azure / Microsoft Foundry (free)**: Phi portal — "Users can also access Phi models for free for real-time deployment through Microsoft Foundry or Hugging Face." and "Phi is available open source through the Azure AI Foundry Models, Hugging Face, and Ollama." https://azure.microsoft.com/en-us/products/phi, accessed 2026-10-06.
  - **Hugging Face**: weights are public and marked `endpoints_compatible` + `deploy:azure`; hosted inference runs under HF's monthly credits (Free $0.10/month, PRO $2.00 — pricing page above).
  - **Groq / Cerebras / Cloudflare**: absent from all three live catalogues fetched today (Groq list; Cerebras Shared Inference list; Cloudflare Workers AI 69-model list contains no `phi*` entry, only `@cf/microsoft/resnet-50`) → no free Phi-4 hosting verified there.
  - **GitHub Models**: retired (quote above) → not available.
- Notes: 9.8T training tokens; 1920 H100-80G; release 2024-12-12; knowledge cutoff June 2024.

---

### Phi-4-mini-instruct (3.8B)

- Model card URL (primary): https://huggingface.co/microsoft/Phi-4-mini-instruct — access 2026-10-06 (metadata: License `mit`; `language: multilingual, ar, zh, cs, da, nl, en, fi, fr, de, he, hu, it, ja, ko, no, pl, pt, ru, es, sv, th, tr, uk`; arxiv 2503.01743).
- License: **MIT** (`license: mit`; `license_link: …/Phi-4-mini-instruct/resolve/main/LICENSE`). Permissive.
- Params: **3.8B, dense** — card: "Phi-4-mini-instruct has 3.8B parameters and is a dense decoder-only Transformer model."
- Context length: **128K tokens** — card: "Context length: 128K tokens". Vocabulary up to `200064`.
- Bahasa Indonesia evidence: **no Indonesian number, and Indonesian is not among the listed supported languages** ("Arabic, Chinese, Czech, Danish, Dutch, English, Finnish, French, German, Hebrew, Hungarian, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish, Swedish, Thai, Turkish, Ukrainian"). Multilingual benchmarks on the card are aggregate: Multilingual MMLU (5-shot) **49.3**, MGSM (0-shot, CoT) **63.9**; per-language results absent. Card warns: "Languages other than English will experience worse performance as well as performance disparities across non-English." → Indonesian evidence **[UNVERIFIED]**.
- Structured output: **yes, documented on the model card** — "#### Tool-enabled function-calling format — This format is used when the user wants the model to provide function calls based on the given tools. The user should provide the available tools in the system prompt, wrapped by `<|tool|>` and `<|/tool|>` tokens. The tools should be specified in JSON format, using a JSON dump structure." Release notes: "better post-training techniques were used for instruction following, function calling".
- Determinism caveats: card's own inference examples use `temperature=0.0` and `do_sample=False` (transformers) / `temperature=0.0` (vLLM). No determinism guarantee beyond that. vLLM lists the Phi series (`microsoft/phi-4`) as batch-invariance-tested (https://docs.vllm.ai/en/latest/features/batch_invariance/, access 2026-10-06) — but that page pins only `microsoft/phi-4` among Phi, so mini is **[UNVERIFIED]** there.
- Free-host availability: Microsoft Foundry / Hugging Face (Phi portal statement above). Note the model card's own links: Try It Azure + HF space https://huggingface.co/spaces/microsoft/phi-4-mini. Not on Groq/Cerebras/Cloudflare lists fetched today. GitHub Models retired.
- Notes: 5T tokens, 512 A100-80G, release February 2025, cutoff June 2024; grouped-query attention, shared input/output embedding.

---

### Phi-4-multimodal-instruct

- Model card URL (primary): https://huggingface.co/microsoft/Phi-4-multimodal-instruct — access 2026-10-06 (metadata: License `mit`, multilingual + same 23 language codes; arxiv 2503.01743).
- License: **MIT** (`license: mit`, `license_link` to repo LICENSE). Permissive.
- Params: not printed on the fetched part of the card (Phi-4-mini-instruct-sized multimodal model; family card links `phi-4-mini`); **parameter count [UNVERIFIED]** from this card. (Independent Microsoft statements describe it as ~5.6B — not verified on a page fetched today.)
- Context length: **128K tokens** — card: "comes with 128K token context length".
- Bahasa Indonesia evidence: **none.** Card language table: Text — Arabic, Chinese, Czech, Danish, Dutch, English, Finnish, French, German, Hebrew, Hungarian, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish, Swedish, Thai, Turkish, Ukrainian; Vision — English; Audio — English, Chinese, German, French, Italian, Japanese, Spanish, Portuguese. **Indonesian appears in none of the three lists.** Benchmarks are speech/vision only (e.g. ASR; "Ranking number 1 on the Huggingface OpenASR leaderboard with word error rate 6.14% … as of March 04, 2025"). → Indonesian evidence **[UNVERIFIED]**.
- Structured output: **claimed** — Primary Use Cases list includes "4) Function and tool calling"; release notes: "better post-training techniques were used for instruction following and function calling". No JSON-reliability guarantee quoted.
- Determinism caveats: no determinism statement on the card; sampling params in its usage examples are not shown in the fetched portion. Speech/vision logit paths add modality-dependent variance → treat as **[UNVERIFIED]** at doc level.
- Free-host availability: Azure (Microsoft Foundry playground: https://github.com/marketplace/models/azureml/Phi-4-multimodal-instruct/playground — the linked GitHub Models playground is now dead because GitHub Models retired 2026-07-30), HF space playground https://huggingface.co/spaces/microsoft/phi-4-multimodal, NVIDIA NIM link on card. Phi portal's blanket statement "free for real-time deployment through Microsoft Foundry or Hugging Face" covers it. Not on Groq/Cerebras/Cloudflare.
- Notes: text+vision+audio in one network; 4 languages listed for audio translation output (Card's speech-translation figures).

---

### Phi-4-reasoning (14B) and Phi-4-reasoning-plus

- Model card URL (primary): https://huggingface.co/microsoft/Phi-4-reasoning — access 2026-10-06 (metadata: License `mit`, language `en`, base_model `microsoft/phi-4`, arxiv 2504.21318).
- License: **MIT** (`license: mit`).
- Params: **14B dense** — card: "Base model same as previously released Phi-4, 14B parameters, dense decoder-only Transformer model". `Phi-4-reasoning-plus` is listed alongside in the quality table (AIME24 81.3, AIME25 78.0, OmniMath 81.9, GPQA-D 68.9, LiveCodeBench 53.1) — card does not restate its parameter count.
- Context length: **32k tokens** — card: "32k tokens"; usage suggests `max_new_tokens=32768` for hard prompts.
- Bahasa Indonesia evidence: **none.** Card: "It provides uses for general purpose AI systems and applications (primarily in English)"; "Phi-4-reasoning is not intended to support multilingual use." "This model is designed and tested for math reasoning only." Benchmarks are math/science/code only. → Indonesian evidence **[UNVERIFIED]**.
- Structured output: **no function-calling/JSON claim** on the card. Card states outputs are two blocks: "a reasoning chain-of-thought block followed by a summarization block" using `<think> {Thought section} </think> {Solution section}`. Function calling on a reasoning Phi-4 is **not documented** here.
- Determinism caveats (**documented, important**): card, verbatim — "To fully take advantage of the model's capabilities, inference must use `temperature=0.8`, `top_k=50`, `top_p=0.95`, and `do_sample=True`. For more complex queries, set `max_new_tokens=32768` to allow for longer chain-of-thought (CoT)." Sample code repeats `temperature=0.8, top_k=50, top_p=0.95, do_sample=True`. So the documented operating point is **stochastic sampling with a required system prompt**; CoT length also varies with `max_new_tokens`, so scores are prompt/budget-sensitive.
- Free-host availability: Phi portal blanket statement (Microsoft Foundry / Hugging Face / Ollama), HF credits (Free $0.10/month). `deploy:azure` tag present. Not on Groq/Cerebras/Cloudflare lists fetched today. GitHub Models retired.
- Notes: trained on ~16B tokens (≈8.3B unique), RL + SFT from phi-4; release 2025-04-30; cutoff March 2025.

---

### Phi-4-mini-reasoning (3.8B)

- Model card URL (primary): https://huggingface.co/microsoft/Phi-4-mini-reasoning — access 2026-10-06 (metadata: License `mit`, language `en`, arxiv 2504.21233).
- License: **MIT** (`license: mit`, "The model is licensed under the MIT license").
- Params: **3.8B dense** — "shares the same architecture as Phi-4-Mini, which has 3.8B parameters and is a dense decoder-only Transformer model."
- Context length: **128K tokens** — card: "Context length: 128K tokens".
- Bahasa Indonesia evidence: **none.** "Supported languages: English"; "This model is designed and tested for math reasoning only." Benchmarks: AIME 57.5, MATH-500 94.6, GPQA Diamond 52.0. → Indonesian evidence **[UNVERIFIED]**.
- Structured output: not claimed (card shows chat format only).
- Determinism caveats: undocumented stochastic setting in the card's example — `temperature=0.8, top_p=0.95, do_sample=True`, `max_new_tokens=32768`; trained by distilling DeepSeek-R1 rollouts (8 rollouts per problem, verified correct).
- Free-host availability: `endpoints_compatible`, "available in Azure AI Studio" link on card; HF credits; Phi portal statement. Not verified on Groq/Cerebras/Cloudflare.
- Notes: 150B training tokens, 128 H100-80G, release April 2025, cutoff February 2025.

---

## Determinism (cross-cutting, primary-doc evidence)

- **vLLM (serving framework):** "vLLM does not guarantee the reproducibility of the results by default, for the sake of performance." Mitigations: `VLLM_ENABLE_V1_MULTIPROCESSING=0` (offline, deterministic scheduling) or batch invariance; "Even with the above settings, vLLM only provides reproducibility when it runs on the same hardware and the same vLLM version." — https://docs.vllm.ai/en/latest/usage/reproducibility/ , access 2026-10-06.
- **Batch/order sensitivity:** "Batch invariance ensures that the output of a model is deterministic and independent of the batch size or the order of requests in a batch." Requires `VLLM_BATCH_INVARIANT=1`, NVIDIA compute capability ≥ 8.0 (or Intel XPU + Triton attention), and "Enabling batch invariance may impact performance compared to the default non-deterministic mode." Tested-model list includes `microsoft/phi-4` (Phi series) and MoE models (Qwen3 MoE, Granite 3.1 MoE, DeepSeek V3/R1) — **Gemma 3/Gemma 4 are not on the validated list** → [UNVERIFIED] for Gemma. — https://docs.vllm.ai/en/latest/features/batch_invariance/ , access 2026-10-06.
- **MoE routing (Gemma 4 26B A4B):** architecture confirmed (8 active of 128 experts + 1 shared, card). No primary page fetched today states MoE routing nondeterminism for this model → **[UNVERIFIED]** (no Gemma-4-specific determinism statement exists in the sources fetched).
- **Quantisation:** Gemma 4 QAT checkpoints (`-qat-q4_0-gguf`, `-qat-w4a16-ct`, `-qat-mobile-*`) are documented as trained-for-quantisation variants, and the overview warns "Unlike standard Post-Training Quantization (PTQ), which compresses a fully trained model and can lead to quality degradation, QAT integrates quantization simulation into the training process itself." Numeric equivalence to BF16 is claimed as "nearly identically", not identical. Ollama cloud states cloud models use "Native weights, as released by the model provider." and "may use accelerated data formats supported by Blackwell and Vera Rubin architectures (e.g. NVFP4)" → provider-side precision can differ from local runs. URLs: model_card_4 + https://ai.google.dev/gemma/docs/core + https://ollama.com/cloud .
- **Reasoning-mode nondeterminism:** Gemma 4 thinking mode changes the emitted token stream (`<|think|>` trigger; `<|channel>thought` blocks; thoughts must be excluded from history) — model_card_4. Phi-4-reasoning requires `do_sample=True` with `temperature=0.8/top_k=50/top_p=0.95` — Phi-4-reasoning card. Both make score replication prompt- and sampling-dependent.
- **Provider-side sampling caveat:** Cloudflare Workers AI documents `seed` as "If specified, the system will make a **best effort** to sample deterministically." — https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/ , access 2026-10-06.

## Provider / free-host matrix (all rows verified on provider pages today, 2026-10-06)

| Provider | Gemma | Phi-4 family | Free? | Evidence |
|---|---|---|---|---|
| Google Gemini API / AI Studio | **Gemma 4** rows exist; input+output "Free of charge", paid "Not available" | none | **Yes (free tier)**; free-tier content "used to improve our products" = Yes | https://ai.google.dev/gemini-api/docs/pricing (updated 2026-10-06) |
| Cloudflare Workers AI | `gemma-4-26b-a4b-it` ($0.10/$0.30 per M tok), `gemma-3-12b-it` ($0.345/$0.556), `gemma-2b/7b-it-lora`, `gemma-sea-lion-v4-27b-it`, `embeddinggemma-300m` | **none** | **Yes**: 10,000 Neurons/day free allocation | https://developers.cloudflare.com/workers-ai/platform/pricing/ (2026-10-01) + model page |
| Ollama cloud | `gemma4` $0.14/$0.40 per M tok | not listed in price table | Free plan = starter credits + "starter models", 1 concurrent req; gemma4 tier **[UNVERIFIED]** | https://ollama.com/cloud |
| Together AI | Gemma 4 31B $0.39/$0.97 | none listed | No free tier stated | https://www.together.ai/pricing |
| Hugging Face Inference Providers | weights hosted (`google/gemma-*`) | weights hosted (`microsoft/phi-*`) | Free users **$0.10/month** credits, PRO $2.00 | https://huggingface.co/docs/inference-providers/pricing |
| Azure / Microsoft Foundry | not the Gemma host | Phi-4, -mini, -multimodal, -reasoning | "free for real-time deployment through Microsoft Foundry or Hugging Face" | https://azure.microsoft.com/en-us/products/phi |
| Groq | **no Gemma models at all** | **no Phi models** | — | https://console.groq.com/docs/models |
| Cerebras Shared Inference | none (only gpt-oss-120b, qwen-3.8-27b) | none | free trial + PAYG for those two only | https://inference-docs.cerebras.ai/models/overview |
| GitHub Models | — | — | **Retired 2026-07-30** | https://docs.github.com/en/github-models |
| Kaggle | Gemma/Gemma 4 weights, kagglehub download, gated-consent flow | Phi not checked | weights free; notebook-compute quota **[UNVERIFIED]** | https://www.kaggle.com/docs/models |

## Not verified / gaps

- **Gemma 4 license page URL used by Cloudflare** (`https://ai.google.dev/gemma/docs/gemma_4_license`, linked as "Terms and License" on the Cloudflare model page) was not fetched; the canonical Gemma 4 license URL from Google's own pages is `https://ai.google.dev/gemma/apache_2` (Apache 2.0 text). Whether the docs URL 404s is unconfirmed.
- **Indonesian explicitly named** in any Gemma 3 / Gemma 4 language list: not found. Both cards say "over 140 languages" (pre-training) / "35+ languages" (Gemma 4 out-of-the-box); "Indonesian" does not appear on model_card_3, model_card_4, or in the Gemma 3 technical-report text fetched today. Grep of the report HTML for "indonesian" returned no match.
- **Gemma 3 27B Indonesian score**: absent from the live SEA-HELM Indonesian board (only Gemma 4 31B/E2B and the SEA-LION Gemma-E2B derivative appear). An aggregator (digitalinasia.com) cites "Gemma 3 27B at 67.70" on SEA-HELM, but that number is **not on the primary leaderboard today** → [UNVERIFIED].
- **IndoMMLU numbers for Gemma or Phi**: the IndoMMLU dataset card (https://huggingface.co/datasets/indolem/IndoMMLU) publishes scores only for GPT-3.5, XGLM, Falcon, BLOOMZ, mT0, LLaMA, Bactrian-X. No Gemma/Phi rows → no IndoMMLU evidence for either family. Dataset itself is CC BY-NC-SA 4.0 (non-commercial).
- **SeaBench** (as named in the task) was not located as a live primary benchmark page today; only SEA-HELM and IndoMMLU were confirmed → [UNVERIFIED].
- **Gemma free-tier numeric rate limits** (RPM/TPM/RPD for Gemma 4 on the Gemini API free tier): not published on the docs rate-limit page; it defers to the AI Studio UI (requires sign-in) → [UNVERIFIED].
- **Gemma 2 context length**: not printed on model_card_2; tech-report line only implies the "1:1, sw=4096" configuration → [UNVERIFIED].
- **Gemma 3 function calling / JSON**: no claim found on model_card_3 or a Gemma-3-specific function-calling doc; the live function-calling guide is Gemma-4-specific. Gemma 3 JSON reliability → [UNVERIFIED].
- **Phi-4-multimodal-instruct parameter count**: not stated in the fetched card portion → [UNVERIFIED].
- **Phi-Cerebras / Phi-Cloudflare / Phi-Groq hosting**: verified *absent* from their live catalogues; other hosts (DeepInfra, Novita, Fireworks, etc.) not checked by this slice.
- **Kaggle free compute quota for Gemma 4 notebooks**: not verified (no quota page fetched).
- **Ollama Free-plan inclusion of `gemma4`**: not verified ("starter models" set not enumerated).
- **MoE routing nondeterminism wording** for Gemma 4 26B A4B: no vendor statement found; the only primary determinism statements come from vLLM docs, whose validated-model list excludes Gemma.
