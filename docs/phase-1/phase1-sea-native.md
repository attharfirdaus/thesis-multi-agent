# Phase 1 — Southeast-Asian / Indonesian-native open models

All pages fetched 2026-10-06 (access date). Quotes are verbatim from the cited page.
No recommendations, no ranking — evidence only.

Terminology: "SEA-HELM ID" = the Indonesian column of the SEA-HELM leaderboard
(`https://leaderboard.sea-lion.ai/detailed/SEA`, accessed 2026-10-06; leaderboard snapshot dated Sep 18, 2026).

---

### Nemotron-SEA-LION-v4.8-30B-A3B (and -120B-A12B)

- Model card URL (primary): https://huggingface.co/aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B (accessed 2026-10-06); docs page https://docs.sea-lion.ai/models/sea-lion-v4.8/nemotron-sea-lion-v4.8.md (accessed 2026-10-06; page marked "Last update: 2026-09-18").
- License: MIT. HF metadata tag `license:mit`; card field "**License:** [MIT](https://mit-license.org/)". No named restriction quoted on the card. NOTE: the *base* variant's docs page lists "**License:** [Other](https://huggingface.co/aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B-Base/blob/main/NOTICE.md)" — so base and instruct licensing differ; verify separately if the base is used. NVIDIA parent-model terms were not read here.
- Params: 30B total / 3B active (MoE), dense-hybrid Mamba2-Transformer: "30-billion parameter base large language model with 3 billion active parameters, built on a Mamba2-Transformer Hybrid Mixture of Experts (MoE) architecture" (docs page). Sibling 120B-A12B = 120B total / 12B active (LatentMoE + Mamba-2 + MTP).
- Context length: card: "**Context length:** 262,144 tokens"; docs page says 8K (Base model) / 256K. Also: "All models were served at their full context length of 262,144 tokens with default vLLM settings" (docs page).
- Bahasa Indonesia evidence: no per-task ID number on the card; card points to the leaderboard. SEA-HELM leaderboard ID column (snapshot Sep 18, 2026): **SEA-LION v4.8 (Nemotron) 120B = 73.10** [-1.16,+1.21]; **SEA-LION v4.8 (Nemotron) 30B = 65.87** [-1.29,+1.33] (https://leaderboard.sea-lion.ai/detailed/SEA). SEA overall: 120B 63.44, 30B 51.57. Indonesian training data documented: yes — CPT data lists `aisingapore/SEA-Instruct-2602` and multilingual/parallel sets; language list includes Indonesian, Javanese, Sundanese, Balinese: "**Language(s):** Balinese, Burmese, English, Indonesian, Javanese, Khmer, Lao, Malay, Mandarin, Sundanese, Tamil, Thai, and Vietnamese" (docs page).
- Structured output: no function-calling/JSON claim found on card or docs page. [UNVERIFIED] for tool-calling claims; [UNVERIFIED] for reliable-JSON claims.
- Determinism caveats: MoE (routing nondeterminism) + Mamba2 hybrid; card gives no determinism statement. Also FP8 checkpoint guidance: "We recommend the FP8 static checkpoint as the default for both model sizes… it matches BF16 within noise on SEA-HELM" (docs page) — implies quantisation-level differences exist. No primary determinism doc found → [UNVERIFIED] beyond that.
- Free-host availability: not found on a free provider page today. Cloudflare pricing page (updated Oct 1, 2026) lists `@cf/nvidia/nemotron-3-120b-a12b` (not the SEA-LION CPT) — no SEA-LION Nemotron entry. [UNVERIFIED].
- Notes: GGUF/NVFP4/FP8 quants exist; "not aligned for safety"; throughput table measured on H200 with vLLM/GuideLLM.

---

### Qwen-SEA-LION-v4.5-27B-IT (current SEA-LION flagship)

- Model card URL (primary): docs https://docs.sea-lion.ai/models/sea-lion-v4.5/qwen-sea-lion-v4.5.md (accessed 2026-10-06; "Last update: 2026-05-19"); weights https://huggingface.co/aisingapore/Qwen-SEA-LION-v4.5-27B-IT.
- License: Apache-2.0 — "**License:** [Apache-2.0](https://github.com/QwenLM/Qwen3.6/blob/main/LICENSE)". No restricting clause quoted.
- Params: 27B dense ("built upon the Qwen3.6-27B dense architecture, a 27-billion parameter model featuring a hybrid Linear and Full Attention design"). Text+vision ("Causal Language Model with Vision Encoder").
- Context length: "**Context length:** 262k"; "**Context Window (262K):** Reduce if facing OOM errors but keep ≥128K to preserve full reasoning capabilities."
- Bahasa Indonesia evidence: SEA-HELM leaderboard ID column = **76.51** [-1.23,+1.23] (SEA overall 73.24) for SEA-LION v4.5 (Qwen) 27B (https://leaderboard.sea-lion.ai/detailed/SEA, 2026-10-06). Training data documented: yes — distilled from Qwen/Qwen3.5-397B-A17B on `aisingapore/SEA-Instruct-2602`, "fine-tuned on Burmese, Indonesian, Filipino, Malay, Tamil, Thai, and Vietnamese".
- Structured output: yes, claimed. Docs: "The SEA-LION v4.5 model supports function calling, enabling agentic workflows where the model autonomously decides which tools to call…" plus a worked `tools=`/`tool_choice="auto"` example over the OpenAI-compatible API (https://docs.sea-lion.ai/guides/inferencing/api.md, 2026-10-06). A local Transformers tool-calling example with `enable_thinking=False` and "disable CoT for structured tool call output" is on the model docs page. No explicit "reliable JSON" wording found.
- Determinism caveats: reasoning-mode switch exists (`enable_thinking`) and docs warn about caching: "If you are not observing any changes in response when toggling `thinking_mode` on/off, your API responses might have been cached" (API docs) — a reproducibility gotcha for API use. No MoE (dense), so no routing nondeterminism. No batch/quant determinism statement → [UNVERIFIED].
- Free-host availability: yes, SEA-LION API free POC tier — "Our free APIs are intended for proof-of-concept (POC) development and are rate-limited (10 requests per minute)" (https://docs.sea-lion.ai/overview/readme/faq.md, 2026-10-06); rate limit page: "As of 04 Jun 2026, our rate limits is set to **10 requests per minute per user**" (API docs). This exact model is the example used in the API docs (`"model": "aisingapore/Qwen-SEA-LION-v4.5-27B-IT"`). Also on Ollama per docs.
- Notes: sibling `Qwen-SEA-LION-v4.5-27B-IT-SpecDecoder` (draft model, must be paired).

---

### Qwen-SEA-LION-v4-32B-IT

- Model card URL (primary): https://huggingface.co/aisingapore/Qwen-SEA-LION-v4-32B-IT (accessed 2026-10-06; card "Last update: 2025-10-16"); docs page https://docs.sea-lion.ai/models/sea-lion-v4/qwen-sea-lion-v4-32b.md (accessed 2026-10-06; "Last updated: 2025-10-17").
- License: **CONTRADICTION between two first-party pages.** HF model card: "**License:** [MIT](https://mit-license.org/)" (YAML `license: mit`). SEA-LION docs page for the same model: "**License:** [Qwen Terms of Service](https://qwen.ai/termsservice) / [Qwen Usage Policy](https://qwen.ai/usagepolicy)". Both accessed 2026-10-06. Resolve before relying on it.
- Params: 32B dense (based on Qwen3-32B; docs page describes it as "a decoder model using the Gemma 3 architecture", which is inconsistent with the Qwen3 base named on the same page — flagging the doc inconsistency).
- Context length: **conflicting on the same page**: "32,768 of context length natively" and "**Context Length:** 128k tokens" and "**Context Length:** 32k tokens" (HF card) — verify against Qwen3-32B config before use.
- Bahasa Indonesia evidence: no numeric ID score published; card embeds only an image (`sea-helm_scores_17_oct_10am.png`) and says "For details … please refer to the SEA-HELM leaderboard". The leaderboard's detailed table (2026-10-06) does **not** list Qwen-SEA-LION-v4-32B → [UNVERIFIED] numeric ID result. Training data documented: yes — "continued pre-training on approximately **100B tokens** sampled from the SEA-Pile v2 pretraining corpus of over one trillion tokens across 7 SEA languages: Burmese, Indonesian, Malay, Filipino, Tamil, Thai, and Vietnamese"; post-trained on ~8M QA pairs.
- Structured output: no function-calling/JSON claim on this card or docs page (unlike v4.5). Thinking mode exists: "The model defaults to non-thinking mode. To enable thinking mode, please use `enable_thinking=True`." → treat tool calling as [UNVERIFIED] for this model.
- Determinism caveats: dense model; eval protocol documented as "Each evaluation comprised of 8 runs with different seeds and the final results were averaged across these runs" (i.e. the benchmark itself reports seed-averaged scores). Thinking/non-thinking mode exists → mode-dependent outputs. No batch/quant determinism statement → [UNVERIFIED].
- Free-host availability: not verified on any free provider page today. [UNVERIFIED].
- Notes: quantised 4BIT/8BIT and OpenVINO 8BIT/4BIT variants; VRAM table (BF16 61.03 GB VRAM on H200, p50 over 10 requests).

---

### Gemma-SEA-LION-v4-4B-VL

- Model card URL (primary): docs https://docs.sea-lion.ai/models/sea-lion-v4/gemma-sea-lion-v4-4b-vl.md (accessed 2026-10-06; "Last updated: 2026-02-05"); weights https://huggingface.co/aisingapore/Gemma-SEA-LION-v4-4B-VL.
- License: Gemma Terms of Use. Card: "**License:** [Gemma Terms of Use](https://ai.google.dev/gemma/terms)"; HF YAML `license: gemma`. Restriction quoted verbatim from the Gemma Terms (§3.2 Use Restrictions): "You must not use any of the Gemma Services: 1. for the restricted uses set forth in the Gemma Prohibited Use Policy at ai.google.dev/gemma/prohibited_use_policy ("**Prohibited Use Policy**"), which is hereby incorporated by reference into this Agreement; or 2. in violation of applicable laws and regulations." Also §3.1: "You must provide all third party recipients of Gemma or Model Derivatives a copy of this Agreement." (https://ai.google.dev/gemma/terms, "Last modified: April 1, 2026", accessed 2026-10-06). Note the appendix lists Gemma 3 → these terms apply; Gemma 4 has a separate Apache-2.0-based licence ("For Gemma 4 terms, see the Gemma 4 license").
- Params: 4B dense VLM — "**Gemma-SEA-LION-v4-4B-VL** is a 4-billion parameter Vision-Language Model (VLM) built upon the gemma-3-4b-it architecture." HF safetensors total: 4,300,079,472 (BF16).
- Context length: "**Context length:** 128k tokens".
- Bahasa Indonesia evidence: no numeric ID score on the card; card claim: "As of Feb 2026, Gemma-SEA-LION-v4-4B-VL outperforms other open models in the small parameter class on SEA tasks, achieving performance comparable to larger, proprietary models." (no number; [UNVERIFIED] as a quantified claim). SEA-HELM ID column lists "SEA-LION v4.5 (Gemma E2B)" = 63.96 but that is a different (v4.5/E2B) model, not this 4B-VL. Training data documented: yes — "rigorous post-training on a curated dataset of approximately **8.54 million** instruction-text pairs. This curated dataset included various SEA Languages such as Burmese, Malay, Tagalog and Tamil"; datasets `aisingapore/SEA-Instruct-2602`, `allenai/Dolci-Instruct-SFT-Tool-Use`, `Agent-Ark/Toucan-1.5M`, RL sets.
- Structured output: yes, claimed, with an explicit experiment: "we experimented with: 1. Adding function calling to the model to allow for this model to be used in tool calling applications" (docs page). Note the model's own docs (tool-calling guide) describes Gemma-family tool calling as text-parsing-based, not native: "Uses text-based tool calling format… Does not utilize standard `tool_calls` parameter" (https://docs.sea-lion.ai/guides/tool_calling.md — note that page is written about Gemma-SEA-LION-v4-27B-IT). The HF repo ships `Toolcalling_05_Feb_1pm.png` and a `chat_template.jinja` containing `<tool_call>` JSON handling. No wording about "reliable JSON" → [UNVERIFIED].
- Determinism caveats: VLM (image preprocessing) + Gemma chat template; no determinism doc → [UNVERIFIED].
- Free-host availability: not verified. [UNVERIFIED].
- Notes: "The model has not been aligned for safety."; "not tested for robustness against adversarial prompting".

---

### Gemma-SEA-LION-v4-27B-IT (served free-ish on Cloudflare)

- Model card URL (primary): docs https://docs.sea-lion.ai/models/sea-lion-v4/gemma-sea-lion-v4-27b.md (accessed 2026-10-06) — page body not quoted here beyond what is below.
- License: Gemma Terms of Use (family card: "**License:** [Gemma Terms of Use](https://ai.google.dev/gemma/terms)"); restricting quote as above (Gemma Terms §3.2).
- Params: 27B dense (CPT of Gemma 3 27B IT per docs index table "CPT² of Gemma 3 27B IT").
- Context length: docs index lists 128K for Gemma 3 27B IT family; Cloudflare model page lists "Context Window: 128,000 tokens" (https://developers.cloudflare.com/workers-ai/models/gemma-sea-lion-v4-27b-it/, accessed 2026-10-06).
- Bahasa Indonesia evidence: no numeric ID score found on the model docs page; leaderboard detailed table (2026-10-06) lists Gemma-based SEA-LION entries only for v4.5 (E2B) and v4.8 (Nemotron) → [UNVERIFIED] for a numeric ID score for this exact model. Training data: SEA languages documented generally; specific corpus for the 27B page not fetched in detail.
- Structured output: yes but text-parsed, not native. Docs: "Gemma-SEA-LION-v4-27B-IT does not parse the `tools` parameter, hence it is recommended to handle tool-calling via the parsing of the model's message response"; "Tool calls are wrapped in \`\`\`tool_code blocks"; example response content `\`\`\`tool_code\nget_time(timezone="Asia/Singapore")\n\`\`\`` (https://docs.sea-lion.ai/guides/tool_calling.md, 2026-10-06). Config note: "When `tool_choice` is configured to enforce usage of a specific tool, the `tool_calls` parameter will be returned, but this removes flexibility."
- Determinism caveats: none documented → [UNVERIFIED].
- Free-host availability: **yes, verified on a provider page.** Cloudflare Workers AI hosts it ("Cloudflare-hosted", model id `@cf/aisingapore/gemma-sea-lion-v4-27b-it`, unit pricing "$0.351 per M input tokens, $0.555 per M output tokens"), and Workers AI has a standing free allocation: "Our free allocation allows anyone to use a total of **10,000 Neurons per day at no charge**" (https://developers.cloudflare.com/workers-ai/platform/pricing/, "Last updated Oct 1, 2026", accessed 2026-10-06). The model costs 31,876 neurons per M input tokens / 50,488 neurons per M output tokens → the free daily allocation is small (~0.3M input tokens/day equivalent). Model is NOT in Cloudflare's paid-only list.
- Notes: SEA-LION docs also publish a Cloudflare quickstart (https://docs.sea-lion.ai/guides/inferencing/cloudflare.md, 2026-10-06). HF repo carries FP8_Dynamic / NVFP4 / mlx-4bit quants.

---

### Gemma-SEA-LION-v3-9B-IT (v3 generation, still widely used)

- Model card URL (primary): https://huggingface.co/aisingapore/Gemma-SEA-LION-v3-9B-IT (accessed 2026-10-06; card "Current Version: `14.04.2025`").
- License: Gemma Community License — "**License:** [Gemma Community License](https://ai.google.dev/gemma/terms)"; HF `license: gemma`. Restricting quote: Gemma Terms §3.2 (same text as quoted under Gemma-SEA-LION-v4-4B-VL, https://ai.google.dev/gemma/terms, accessed 2026-10-06).
- Params: 9B dense (CPT of Gemma2 9B; docs index: "9B / 8192 / CPT² of Gemma2"). Note the HF repo tag says `gemma2` architecture.
- Context length: "The model has a context length of 8192."
- Bahasa Indonesia evidence: evaluated on SEA-HELM + IFEval/MT-Bench, but the card publishes no numeric table (points to leaderboard) → [UNVERIFIED] numeric ID score from the card. Anchored comparison: SEA-HELM paper Figure 2 and text state Gemma2-based SEA-LION was strongest of the evaluated 7–9B models: "The Gemma2 family of models (gemma-2-9b-it) and the continued pre-trained/fine-tuned model (gemma2-9b-cpt-sea-lionv3-instruct) performed the best of all the evaluated models." (https://arxiv.org/html/2502.14301v1, fetched 2026-10-06; paper arXiv:2502.14301). Training data documented: yes — instruction tuning "in English and also in ASEAN languages such as Indonesian, Thai and Vietnamese" on the CPT base `aisingapore/Gemma-SEA-LION-v3-9B`; supported languages include Indonesian, Javanese, Sundanese.
- Structured output: **explicitly absent** — "**NOTE** This model has not been trained to use a system prompt or to use tool calling." (HF card, verbatim).
- Determinism caveats: none documented → [UNVERIFIED].
- Free-host availability: none verified on a free provider page today → [UNVERIFIED].
- Notes: "This is the repository for the commercial instruction-tuned model."

---

### Llama-SEA-LION-v3.5-8B-R / -70B-R (reasoning generation)

- Model card URL (primary): docs index https://docs.sea-lion.ai/models/sea-lion-v3.5.md (not fetched in full) + weights `aisingapore/Llama-SEA-LION-v3.5-70B-R`.
- License: not verified on a live page in this pass → [UNVERIFIED]. (Base is Llama 3.1 → expect Llama 3.1 Community License; the v3 Llama variants inherit Meta's terms per SEA-LION's own licensing note: "if the model leverages Meta's Llama3 codebase, it may be bound by the Llama3 License… which places certain restrictions on commercial use", https://docs.sea-lion.ai/overview/readme.md, 2026-10-06.)
- Params: 8B / 70B dense (SFT of Llama-SEA-LION-v3 base, per docs index table).
- Context length: 128K (docs index table lists 128k for both).
- Bahasa Indonesia evidence: [UNVERIFIED] — no number fetched.
- Structured output: **reasoning model without native tool calling.** "**Llama-SEA-LION-v3.5-70B-R**: Reasoning model without tool calling capability; Tool-calling can be done via parsing from message response" (https://docs.sea-lion.ai/guides/tool_calling.md, 2026-10-06). Contrast: Llama-SEA-LION-v3-70B-IT "Fully supports OpenAI-style tool calling… Reliable for production tool calling applications."
- Determinism caveats: reasoning-mode nondeterminism — reasoning defaults ON: "Our v3.5 models offers dynamic reasoning capabilities, and defaults to reasoning with `thinking_mode="on"`"; toggle via `chat_template_kwargs: {"thinking_mode": "off"}` (https://docs.sea-lion.ai/guides/inferencing/api.md, 2026-10-06). Parsing caution: parse tool calls only after the reasoning segment "to prevent multiple redundant tool calls".
- Free-host availability: free POC API lists `aisingapore/Llama-SEA-LION-v3.5-70B-R` as a callable example model (same URL) → usable on the 10 RPM free tier.
- Notes: SSE/answer cached responses can mask thinking_mode changes (see API docs note quoted above).

---

### Sailor2 family (Sea AI Lab) — Indonesian + Javanese + Sundanese

- Model card URL (primary): https://huggingface.co/sail/Sailor2-8B-Chat (accessed 2026-10-06); blog https://sea-sailor.github.io/blog/sailor2/ (accessed 2026-10-06).
- License: Apache-2.0. Card: "**License:** apache-2.0"; "Sailor2 is distributed under the terms of the Apache License 2.0. No restrict on the research and the commercial use."
- Params: 1B / 8B / 20B dense — "The Sailor2 model comes in three sizes, 1B, 8B, and 20B, which are **expanded from the Qwen2.5 base models** of 0.5B, 7B, and 14B, respectively."
- Context length: not stated on card or blog → [UNVERIFIED].
- Bahasa Indonesia evidence: benchmarks reported as images only (no numeric table in blog); blog text claims "The Sailor2-8B model stands out as the best multilingual model for SEA languages in the < 10B category" and "our 20B model significantly outperforms others in extremely low-resource languages, such as M3Exam-Javanese, achieving an improvement of +14.6 over Qwen2.5-32B" (claims, no ID-specific number, [INFERENCE] that M3Exam-ID figures exist in the figure). Third-party anchor with a number: SEA-HELM paper: "Sailor2-8B-Chat is observed to perform exceptionally well for SEA-MTBench… but has much poorer performance for LINDSEA and SEA-IFEval, which indicates that it is much weaker in terms of linguistic understanding as well as native instruction following" (https://arxiv.org/html/2502.14301v1, 2026-10-06). Training data documented: yes, in detail — Indonesian 1.3T on disk, 94B effective tokens in Stage 1 + 12.8B high-quality in Stage 2 (blog).
- Structured output: no function-calling or JSON claim on card/blog → [UNVERIFIED].
- Determinism caveats: none documented → [UNVERIFIED].
- Free-host availability: a free API is announced by the project itself: "We also offer a limited free API service for Sailor2-20B-Chat in collaboration with Float16.cloud" with endpoint `https://api.float16.cloud/v1/chat/completions` and bearer `sailor2` (blog, dated December 2, 2024). Whether this is still live on 2026-10-06 is **[UNVERIFIED]** (no live probe; announcement is ~22 months old).
- Notes: languages include Indonesian, Javanese, Sundanese, Malay, plus Philippine languages.

---

### SeaLLM (DAMO Academy / Alibaba) — SeaLLM-7B-v2.5, SeaLLM3

- Model card URL (primary): https://huggingface.co/SeaLLMs/SeaLLM-7B-v2.5 (accessed 2026-10-06); terms of use file https://huggingface.co/SeaLLMs/SeaLLM-13B-Chat/raw/main/LICENSE (accessed 2026-10-06).
- License: "SeaLLMs LICENSE AGREEMENT" (HF `license: other`, `license_name: seallms`). Restricting sentences, verbatim: "4. Restrictions: If you are commercially using the Materials, and your product or service has more than 100 million monthly active users, You shall request a license from Us. You cannot exercise your rights under this Agreement without our express authorization." and "5. Rules of use … b. You can not use the Materials or any output therefrom to improve any other large language model (excluding SeaLLMs or derivative works thereof)." Also §9: "This Agreement and any dispute arising out of or relating to it will be governed by the laws of China".
- Params: 7B dense, built on Gemma-7b: "SeaLLM-7B-v2.5 was built on top of Gemma-7b, and underwent large scale SFT and carefully designed alignment." HF safetensors total: 8,537,680,896.
- Context length: not stated on the card → [UNVERIFIED].
- Bahasa Indonesia evidence (numbers, from the card's own tables): 3-shot M3Exam Indonesian = **48.64** for SeaLLM-7B-v2.5 (vs SeaLLM-7B-v2 42.25, GPT-3.5 49.27); GSM8K-id 71.5, MATH-id 30.1 (https://huggingface.co/SeaLLMs/SeaLLM-7B-v2.5, 2026-10-06). SEA-HELM-era context from the Cendol paper (below): SeaLLM 7B MABL-id 64.24, IndoMMLU 33.60, IndoStoryCloze 68.55 (arXiv:2404.06138). Training data documented: yes at language level ("retain the documents for the major languages in Southeast Asia, namely Thai, Vietnamese, Indonesian, Chinese, Khmer, Lao, Malay, Burmese, and Tagalog", arXiv:2312.00738v1 §2.1).
- Structured output: no function-calling/JSON claim → [UNVERIFIED].
- Determinism caveats: the card carries explicit generation-format hazards: "`<bos>` must be at start of prompt… otherwise, it would not work!" and "Repitition penalty… must be set to **1** , otherwise will lead to degeneration!" (typos verbatim). No quantisation/batch determinism statement → [UNVERIFIED].
- Free-host availability: none verified on a provider page today → [UNVERIFIED]. HF Space demo `SeaLLMs/SeaLLM-7B-v2.5` is referenced on the card (free interactive demo, not an API SLA).
- Claim of regional advantage (quote + strength): "As shown, SeaLLM-13b outperforms ChatGPT-3.5 by large margins in most non-Latin languages, such as Burmese (Mya), Lao, Khmer and Thai." and "for non-Latin languages, our SeaLLM-13b surpasses ChatGPT by up to 90%" (Sea-bench peer comparison, GPT-4-as-judge; https://arxiv.org/html/2312.00738v1 §4.2, 2026-10-06). Strength: self-reported, judge-model-based, radar-chart-only numbers for the peer comparison; Indonesian is a Latin-script language and is explicitly in the weaker group ("SeaLLM-13b is equal or better than ChatGPT for 40% of the times for Latin-based languages (Eng, Vie, Ind, Msa)") — i.e. the headline SEA advantage claim does not establish Indonesian superiority.
- Notes: card banner: "SeaLLM3 is released"; SeaLLM3-7B-Chat not researched here.

---

### Salamandra 2B / 7B (Barcelona Supercomputing Center)

- Model card URL (primary): https://huggingface.co/BSC-LT/salamandra-2b-instruct and https://huggingface.co/BSC-LT/salamandra-7b-instruct (both accessed 2026-10-06).
- License: Apache-2.0, permissive, no territorial/MAU clause. "The entire Salamandra family is released under a permissive [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0)."
- Params: 2B = "Total Parameters 2,253,490,176" (24 layers, hidden 2,048); 7B = "Total Parameters 7,768,117,248" (32 layers, hidden 4,096). Dense, decoder-only, LlamaForCausalLM.
- Context length: 8,192 (both cards: "Context length | 8,192").
- Bahasa Indonesia evidence: **none — and no Indonesian capability is claimed.** Pretraining corpus = "text in 35 European languages and code"; the language list contains no `id` (Indonesian), no SEA language. Card also disclaims: "It has been optimized to engage in conversation but has *NOT* been aligned through RLHF to filter or avoid sensitive topics." → Indonesian benchmark number: [UNVERIFIED] (none exists on the card; absence of Indonesian in the cardData `language` list is a positive indication it is out of scope).
- Structured output: no function-calling/JSON claim → [UNVERIFIED].
- Determinism caveats: none documented → [UNVERIFIED].
- Free-host availability: none verified on a provider page today; HF metadata tag `deploy:azure` (Azure AI Foundry listing) is not a free-tier claim → [UNVERIFIED].
- Notes: 40B variant exists. Card warns it is "a first proof-of-concept".

---

### Sahabat-AI (GoTo + Indosat Ooredoo Hutchison, with AI Singapore)

### Sahabat-AI / gemma2-9b-cpt-sahabatai-v1-instruct

- Model card URL (primary): https://huggingface.co/GoToCompany/gemma2-9b-cpt-sahabatai-v1-instruct (accessed 2026-10-06).
- License: Gemma Community License — "**License:** [Gemma Community License](https://ai.google.dev/gemma/terms)"; HF `license: gemma`. Restricting quote: Gemma Terms §3.2, as quoted above (https://ai.google.dev/gemma/terms, accessed 2026-10-06). Note the underlying base chain is `Gemma-SEA-LION-v3-9B` (HF metadata `base_model: aisingapore/Gemma-SEA-LION-v3-9B` for the -base variant), so SEA-LION terms inherit on top.
- Params: 9B dense (Gemma2 9B CPT).
- Context length: "The model has a context length of 8192."
- Bahasa Indonesia evidence (numbers from the card's own tables, accessed 2026-10-06):
  - SEA-HELM/BHASA Indonesian = **64.154** (vs gemma-2-9B 63.394, Llama-3.1-8B 51.944, sea-lionv2.1-8B 54.579); Javanese 64.439; Sundanese 54.913; Overall (ID+JV+SU) 61.169.
  - **IndoMMLU = 62.6%** (vs gemma-2-9B 61.4%, Llama-3.1-8B 53.8%, sea-lionv2.1-8B 54.4%).
  - English Open-LLM-Leaderboard average 33.67 (caveat on page: "VLLM caps the context size at **4096 tokens** while HuggingFace was set to **8192 tokens**").
  Training data documented: yes — "fine-tuned with around **448,000 Indonesian instruction-completion pairs** alongside an Indonesian-dialect pool consisting of **96,000 instruction-completion pairs in Javanese** and **98,000 instruction-completion pairs in Sundanese**. Additionally, we added a pool of **129,000 instruction-completion pairs in English**."
- Structured output: no function-calling/JSON claim → [UNVERIFIED].
- Determinism caveats: none documented → [UNVERIFIED]. Note the card's own vLLM-vs-HF 4096/8192 context caveat above as a reproducibility hazard for benchmark comparison.
- Free-host availability: none verified on a free provider page today → [UNVERIFIED].
- Notes: IFEval used "only … on Bahasa Indonesia".

### Sahabat-AI / llama3-8b-cpt-sahabatai-v1-base (and -instruct)

- Model card URL (primary): https://huggingface.co/GoToCompany/llama3-8b-cpt-sahabatai-v1-base (accessed 2026-10-06).
- License: **Llama 3 Community License** (`license: llama3`). Restricting quote from the Llama 3.1 Community License (the published Meta text for the Llama 3.1 family; for Llama 3 it is the analogous Llama 3 agreement): "**Additional Commercial Terms.** If, on the Llama 3.1 version release date, the monthly active users of the products or services made available by or for Licensee, or Licensee's affiliates, is greater than 700 million monthly active users in the preceding calendar month, you must request a license from Meta, which Meta may grant to you in its sole discretion, and you are not authorized to exercise any of the rights under this Agreement unless or until Meta otherwise expressly grants you such rights." (https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/LICENSE — official Meta repo, accessed 2026-10-06). Also requires: "prominently display "Built with Llama"" and name derivatives with "Llama" at the start. NOTE: Meta's own license page (llama.com / dev.meta.ai) rendered JS-only and could not be read; the GitHub LICENSE in Meta's official `llama-models` repo was used instead.
- Params: 8.03B (HF safetensors total 8,030,261,248, BF16); Llama architecture.
- Context length: not stated on the fetched metadata/card → [UNVERIFIED].
- Bahasa Indonesia evidence: not fetched in this pass → [UNVERIFIED]. Base lineage: `base_model: aisingapore/Llama-SEA-LION-v2-8B-IT` (interesting: the Sahabat-AI base is derived from a SEA-LION v2 instruct model, per HF metadata).
- Structured output: no claim fetched → [UNVERIFIED].
- Determinism caveats: none documented → [UNVERIFIED].
- Free-host availability: none verified → [UNVERIFIED].

### Sahabat-AI / Llama-Sahabat-AI-v2-70B-IT (newest, June 2025)

- Model card URL (primary): https://huggingface.co/GoToCompany/Llama-Sahabat-AI-v2-70B-IT (accessed 2026-10-06); launch PR: https://www.gotocompany.com/en/news/press/sahabat-ai-gets-smarter-indosat-and-goto-launch-new-70-billion-parameter-model-with-multilingual-chat-service (2 June 2025; accessed 2026-10-06).
- License: Llama 3.1 Community License — "**License:** [Llama 3.1 Community License](https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct/blob/main/LICENSE)"; HF `license: llama3.1`. Restricting quote: the 700M-MAU clause above; plus Llama 3.1 §2 attributes/notice requirements.
- Params: 70.55B (HF safetensors total 70,553,706,496, BF16). "To load this model in FP16 or BF16 precision, you need a minimum of approximately **140 GB of VRAM**."
- Context length: "The model has a context length of 128k."
- Bahasa Indonesia evidence: card states it was evaluated on IndoMMLU, SEA-HELM and SEA-IFEval/SEA-MTBench but publishes **no numeric table** — "For more details on Llama-Sahabat-AI-v2-70B-IT benchmark performance, please refer to the [Sahabat-AI leaderboard.](https://huggingface.co/spaces/Sahabat-AI/Sahabat-AI-Leaderboard)" → [UNVERIFIED] numbers (leaderboard not read in this pass). Training data documented: partially — supported languages "English, Indonesian, Javanese, Sundanese, Batak Toba, Balinese"; PR: "The latest Sahabat-AI model can now operate across five local languages: Bahasa Indonesia, Javanese, Sundanese, Balinese and Bataknese". PR also states a served chat product: "the new Sahabat-AI chat service, which is available on [sahabat-ai.com]… or under "Popular Services" within the GoPay app's home screen" — i.e. a free public chat surface, not an API with published limits.
- Structured output: no function-calling/JSON claim → [UNVERIFIED]. (The shipped `chat_template.jinja` does contain Llama-3.1-style tool-call JSON scaffolding, but no reliability claim is made.)
- Determinism caveats: none documented → [UNVERIFIED].
- Free-host availability: no free *API* verified; weights are free to download ("the LLM can be freely downloaded from the Sahabat-AI website and the official Hugging Face page", PR). HF org for the ecosystem: https://huggingface.co/Sahabat-AI (referenced in PR).
- Notes: "Sahabat-AI-v2-70B-IT has been aligned for general safety."

---

### Komodo-7B (Yellow.ai)

- Model card URL (primary): https://huggingface.co/Yellow-AI-NLP/komodo-7b-base (accessed 2026-10-06) — **card is gated**; the fetch returned only the HF metadata header, and direct README fetches returned HTTP 401. Paper: https://arxiv.org/html/2403.09362v1 (accessed 2026-10-06).
- License: **Llama 2 Community License** (`license: llama2` in HF metadata). Restricting sentence, verbatim from the Llama 2 Community License Agreement: "**2. Additional Commercial Terms.** If, on the Llama 2 version release date, the monthly active users of the products or services made available by or for Licensee, or Licensee's affiliates, is greater than 700 million monthly active users in the preceding calendar month, you must request a license from Meta…" and "**1.b.v.** You will not use the Llama Materials or any output or results of the Llama Materials to improve any other large language model (excluding Llama 2 or derivative works thereof)." (https://raw.githubusercontent.com/facebookresearch/llama/main/LICENSE — official Meta repo, accessed 2026-10-06).
- Params: 7B dense ("Komodo-7B, 7-billion-parameter Large Language Models"), built on Llama-2: "We have built our language model on top of the Llama-2 model, but with some unique adjustments" + vocabulary expanded to 35,008 tokens.
- Context length: not stated in the paper section read; card gated → [UNVERIFIED].
- Bahasa Indonesia evidence (numbers, Komodo paper Table 3, accessed 2026-10-06): **IndoMMLU 43.2**; ID-EN entailment 90.5; XCOPA-ID 79.6; **NusaX-Senti 79.3 (paper calls this SOTA)**; TydiQA-ID 90.3; IndoSum 43.0; average 71.1 (vs GPT-4-1106-preview 74.7, GPT-3.5-turbo-0613 68.9, Sealion-7B-Instruct-NC 38.9). Training data documented: yes — Indonesian textbooks grades 1–12, colloquial data (subtitles, news), alternate-parallel bilingual data across English/Indonesian and 11 regional languages; ~8.79B tokens pre-training.
- Structured output: no function-calling/JSON claim in the paper → [UNVERIFIED] (absence of claim).
- Determinism caveats: none documented; LoRA-based CPT/SFT noted (LoRA "safeguards against catastrophic forgetting") → no determinism statement, [UNVERIFIED].
- Free-host availability: none verified on a free provider page today; the HF weights are additionally **gated** (must accept terms) → [UNVERIFIED].
- Notes: 11 regional Indonesian languages + Lampungnese; reports beating "the existing Indonesian Large Language Model (LLM) SEA-LION … in almost every task by a significant margin" (that is SEA-LION v1/v2 generation, not v4).

---

### Cendol (IndoNLP; mT5 + LLaMA-2 backbones)

- Model card URL (primary): https://huggingface.co/indonlp/cendol (accessed 2026-10-06); individual cards e.g. https://huggingface.co/indonlp/cendol-llama2-7b-chat, https://huggingface.co/indonlp/cendol-mt5-base-inst (accessed 2026-10-06); paper https://arxiv.org/html/2404.06138 (accessed 2026-10-06).
- License: Apache-2.0. "Use of Cendol is licensed under the [Apache 2.0 license](https://choosealicense.com/licenses/apache-2.0/)"; HF `license: apache-2.0`. No restriction quoted. Caveat: the LLaMA-2-derived variants inherit Llama-2's terms in principle, but the model cards themselves assert Apache-2.0 — flagging as a possible licence conflict (HF `license: apache-2.0` on `cendol-llama2-7b-chat`, https://huggingface.co/indonlp/cendol-llama2-7b-chat, accessed 2026-10-06).
- Params: **dense, two families** — mT5 (encoder-decoder) 300M/580M/1.2B/3.7B/13B and LLaMA-2 (decoder-only) 7B/13B. "ranging in scale from 560 million to 13 billion parameters" (card) / "300 million to 13 billion" (paper abstract).
- Context length: not stated on the collection card or the fetched sub-cards → [UNVERIFIED]. (13B models are LoRA-tuned; card notes LoRA issues.)
- Bahasa Indonesia evidence (Cendol paper, Table 2 + §6, accessed 2026-10-06): Cendol is **not best-in-class on Indonesian**: "Our Cendol models are out-competed by some existing LLMs on all Indonesian language tasks, especially on IndoMMLU and IndoStoryCloze, where Cendol models perform the worst among all LLMs." Numbers (IndoMMLU / MABL-id / IndoStoryCloze): Cendol LLaMA2 7B = 23.54 / 58.19 / 57.41; Cendol mT5 XXL = 14.46 / 62.30 / 56.87; compared with Merak 7B v4 = 46.27 / 62.30 / 66.78 and SeaLLM 7B = 33.60 / 64.24 / 68.55. Cendol's positive claims are aggregated: "the best Cendolinst model (i.e., Cendol mT5XL) outperforms all existing LLMs both multilingual, SEA languages, and Indonesian LLMs on the comparable size by ∼20% weighted F1-score" on NLU, and "state-of-the-art performance on two local language tasks, i.e., MABL-jv and MABL-su" (Cendol mT5 XXL MABL-jv 55.80, MABL-su 52.71). Training data documented: yes, extensively — Cendol Collection ~53.5M prompts from NusaCrowd, Indonesian Wikipedia/WikiHow, 18 local languages, IndoPuisi, human-centric prompts (https://arxiv.org/html/2404.06138 §3).
- Structured output: no function-calling/JSON claim; card explicitly frames scope as "intended for a single turn instruction" ("Both Cendol-Instruct and Cendol-Chat are designed for a single-turn conversation") → structured output not claimed.
- Determinism caveats: none documented → [UNVERIFIED]. Reproducibility caveat documented instead: "we observed a huge variance over different LLMs in some tasks, such as MAPS and IndoMMLU, which raises the question of whether some LLMs have seen the corresponding evaluation datasets."
- Free-host availability: none verified on a free provider page today → [UNVERIFIED].
- Notes: paper abstract licence claim "Cendol models are released under Apache 2.0 license"; training Oct 2023–Jan 2024, so benchmarks are ~2.5 years old relative to today.

---

### Merak-7B (Ichsan2895; the classic Indonesian community model)

- Model card URL (primary): https://huggingface.co/Ichsan2895/Merak-7B-v4 (accessed 2026-10-06).
- License: **CC-BY-NC-SA-4.0 — non-commercial.** "Licensed under Creative Commons-By Attribution-Share Alike-Non Commercial (CC-BY-SA-NC 4.0) Merak-7B empowers AI enthusiasts, researchers alike." HF metadata `license: cc-by-nc-sa-4.0`. The decisive restriction is the "-NC" clause (verbatim quote above; there is no separate restricting sentence beyond the licence name as written on the card).
- Params: 7B dense, based on Mistral-7B-OpenOrca: "This model is based on [Mistral-7B-OpenOrca] and fine tuned by some of Indonesia Wikipedia articles that I cleaned before." ("Leveraging QLoRA… Merak-7B is able to run with 16 GB VRAM".)
- Context length: not stated on the card → [UNVERIFIED]. (Mistral-7B family is 32k in the base, but not claimed here.)
- Bahasa Indonesia evidence: no benchmark table on the card. Third-party numbers: Cendol paper Table 2 (IndoMMLU 46.27, MABL-id 62.30, MAPS 77.78, COPAL 55.82, IndoStoryCloze 66.78) — and per the card's own changelog the model was fine-tuned on `Ichsan2895/alpaca-gpt4-indonesian` / Wikipedia, so IndoMMLU exposure is a live contamination question ("we observed a huge variance… raises the question of whether some LLMs have seen the corresponding evaluation datasets", Cendol paper §6.4, accessed 2026-10-06). Training data documented: yes — Indonesian Wikipedia articles (200k→600k articles across versions), OASST_Top1_Indonesian, alpaca-gpt4-indonesian, ChatML format, FFT.
- Structured output: no function-calling/JSON claim; usage example uses a plain ChatML-style chat template with a fixed system prompt → structured output not claimed.
- Determinism caveats: none documented; card recommends against 4-bit BitsAndBytes for quality: "For better answer, please don't use BitsandBytes 4-bit Quantization, but it using higher VRAM" — that is an explicit quantisation-quality caveat from the author.
- Free-host availability: none verified on a free provider page today → [UNVERIFIED].
- Notes: v1–v4 lineage; also `Merak-7B-v4-GGUF` (same CC-BY-NC-SA-4.0, https://huggingface.co/Ichsan2895/Merak-7B-v4-GGUF).

---

### Cross-model: SEA-HELM leaderboard Indonesian column (primary evidence, one page)

Source: https://leaderboard.sea-lion.ai/detailed/SEA ("Sep 18, 2026"; accessed 2026-10-06). "SEA Overall" = average of 2000 bootstraps, 95% CI shown. Indonesian (ID) column:

| Model | SEA | ID | ID 95% CI |
|---|---|---|---|
| Gemma 4 31B (Google) | 76.17 | 79.75 | [-1.25, +1.20] |
| Qwen 3.6 27B (Alibaba) | 74.64 | 77.96 | [-1.22, +1.20] |
| Qwen 3.5 122B-A10B MoE | 74.66 | 77.93 | [-1.29, +1.25] |
| **SEA-LION v4.5 (Qwen) 27B** | 73.24 | **76.51** | [-1.23, +1.23] |
| Muse Glimmer 30B (Meta) | 72.13 | 75.61 | [-1.13, +1.10] |
| GPT OSS 120B MoE mxfp4 | 66.14 | 72.28 | [-1.35, +1.33] |
| Mistral Medium 3.5 128B | 64.71 | 70.09 | [-1.18, +1.13] |
| **SEA-LION v4.8 (Nemotron) 120B MoE** | 63.44 | **73.10** | [-1.16, +1.21] |
| **SEA-LION v4.8 (Nemotron) 30B MoE** | 51.57 | **65.87** | [-1.29, +1.33] |
| **SEA-LION v4.5 (Gemma E2B) 5B MoE** | 59.23 | **63.96** | [-1.38, +1.37] |
| Gemma 4 (E2B) 5B | 58.82 | 64.13 | [-1.39, +1.41] |
| Tiny Aya Water 3B (CohereLabs) | 19.75 | 33.23 | [-1.13, +1.13] |

Reading: the Indonesian-native entries with published v3-era numbers (Sahabat-AI 9B 64.154 on the older BHASA-era SEA-HELM scale; Komodo 7B IndoMMLU 43.2 / NusaX-Senti 79.3) are **not** directly comparable to the numbers above — different benchmark versions/scales and dates (BHASA/Sahabat-AI tables are 2024-era; the leaderboard is Sep 2026). Any comparison must be made on a single suite/version.

**Reported "Indonesian-native beats general model" claims and how strong they are**
- SeaLLM paper: "our SeaLLM-13b surpasses ChatGPT by up to 90%" (non-Latin languages, GPT-4 judge, radar-chart numbers; Indonesian is in the Latin group where the claim is only "equal or better … 40% of the times"). Strength: self-reported, judge-model-based, no per-language Indonesian figure in text. https://arxiv.org/html/2312.00738v1 §4.2 (2026-10-06).
- Komodo paper: "Komodo-7B-Instruct outperforms various models across different tasks" and IndoMMLU 43.2 vs Sealion-7B-Instruct-NC 23.9 vs GPT-3.5-turbo-0613 52.7. Strength: single-run table with GPT-4-0613 heuristic judging for some tasks, no seed variance reported; the same authors note they fine-tuned baselines themselves. https://arxiv.org/html/2403.09362v1 Table 3 (2026-10-06).
- Sahabat-AI 9B card: IndoMMLU 62.6% vs gemma-2-9B 61.4% (a +1.2 pt margin over its own base) and BHASA-ID 64.154 vs 63.394. Strength: single-run numbers, self-reported; the base-model gap is small relative to typical single-run noise. https://huggingface.co/GoToCompany/gemma2-9b-cpt-sahabatai-v1-instruct (2026-10-06).
- Cendol paper contradicts the generic "regional model wins" story for Indonesian: "Our Cendol models are out-competed by some existing LLMs on all Indonesian language tasks". https://arxiv.org/html/2404.06138 §6.4 (2026-10-06).
- SEA-HELM paper: continued pre-training helps, but the strongest SEA-HELM performers are not SEA-native: "Of all the open-sourced models tested, DeepSeek-R1 was the strongest performing model…" and for 7–9B "The Gemma2 family of models (gemma-2-9b-it) and the continued pre-trained/fine-tuned model (gemma2-9b-cpt-sea-lionv3-instruct) performed the best". https://arxiv.org/html/2502.14301v1 §3.4 (2026-10-06).
- Note on the ~Sep 2026 leaderboard: the top Indonesian scores are Qwen 3.5/3.6 and Gemma 4, with the SEA-LION entries below them in the ID column — the page itself makes no "native wins" claim.

---

## Not verified / gaps

1. **Qwen-SEA-LION-v4-32B-IT licence conflict** — HF card says MIT, SEA-LION docs say "Qwen Terms of Service / Qwen Usage Policy" (both 2026-10-06). Not resolved.
2. **Qwen-SEA-LION-v4-32B-IT context length** — same pages state 32,768 / 128k / 32k. Not resolved.
3. **Komodo-7B** — HF model cards are gated (HTTP 401 on both the model page and `/raw/main/README.md`); context length, card-level benchmark table and any tool-calling statement could not be read. Only HF metadata (license llama2, languages id/en/jv/su) and the arXiv paper were usable.
4. **Llama 3 / Llama 3.1 / Llama 2 licence pages** — llama.com and dev.meta.ai rendered JS-only (no licence text); `huggingface.co/meta-llama/...` LICENSE files returned HTTP 401 (gated). Used the LICENSE files in Meta's official GitHub repos instead (`meta-llama/llama-models`, `facebookresearch/llama`); these are first-party Meta repositories but not the canonical licence URL.
5. **SEA-HELM leaderboard is JS-rendered** — the root page and the language tabs show charts only; numeric extraction worked only on `https://leaderboard.sea-lion.ai/detailed/SEA`. Per-task Indonesian breakdowns (QA/sentiment/translation/NLI/LINDSEA/toxicity) and the SEA-IFEval/SEA-MTBench/LINDSEA Indonesian numbers shown in SEA-HELM paper Figure 2(c) are images → no numbers extracted.
6. **Qwen-SEA-LION-v4-32B-IT Indonesian score** — not on the Sep 2026 detailed table; only an image on the model card → no number.
7. **Gemma-SEA-LION-v4-27B-IT Indonesian score** — model docs page and leaderboard show no dedicated numeric ID figure for this exact checkpoint → no number.
8. **Gemma-SEA-LION-v3-9B-IT Indonesian score** — card has no numbers; only the qualitative SEA-HELM-paper statement.
9. **Llama-SEA-LION-v3.5-8B-R / -70B-R** — licence, params and Indonesian evidence not verified on a live page in this pass.
10. **Context lengths not documented** for: Sailor2 (all sizes), SeaLLM-7B-v2.5, Cendol (all sizes), Merak-7B-v4, Sahabat-AI llama3-8b-v1-base, Komodo-7B.
11. **Free-host availability** verified for only two things: Cloudflare Workers AI `@cf/aisingapore/gemma-sea-lion-v4-27b-it` (with the 10,000 neurons/day free allocation) and the SEA-LION free POC API (10 RPM, models: `aisingapore/Qwen-SEA-LION-v4.5-27B-IT`, `aisingapore/Llama-SEA-LION-v3.5-70B-R`, `aisingapore/SEA-Guard`, `aisingapore/SEA-LION-ModernBERT-Embedding-600M` as documented examples). Everything else (Sailor2/SeaLLM/Salamandra/Sahabat-AI/Komodo/Cendol/Merak, and the Qwen-SEA-LION-v4-32B / Gemma-SEA-LION-v4-4B-VL / Nemotron-SEA-LION-v4.8 checkpoints) → [UNVERIFIED]; no free provider page was found listing them. Hugging Face Inference Providers listings were not checked for these repos.
12. **Sailor2 Float16.cloud free API** — announced Dec 2024 on the primary blog; not probed today, so current availability is [UNVERIFIED].
13. **Determinism documentation** — none of the Indonesian-native model cards/documents make an explicit determinism statement (MoE routing, batching, quantisation, reasoning-mode). The only related primary statements found are: SEA-LION's "it matches BF16 within noise on SEA-HELM" (FP8 vs BF16), SEA-LION's API cache note, SeaLLM's mandatory BOS/repetition-penalty rules, Sahabat-AI's vLLM-4096-vs-HF-8192 caveat, and the Merak author's "don't use BitsandBytes 4-bit" advice. Everything else is [UNVERIFIED].
14. **Salamandra** — no Indonesian or other SEA language is claimed anywhere on the 2B/7B cards; recorded as a gap rather than a score.
15. **Nemotron-SEA-LION-v4.8 base-model licence** — docs page points to a `NOTICE.md` ("Other"); the NOTICE file itself was not fetched.
16. **Sahabat-AI v2 70B benchmark numbers** — card points to an HF Space leaderboard that was not read.
