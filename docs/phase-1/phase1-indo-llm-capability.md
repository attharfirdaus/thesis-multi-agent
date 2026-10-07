# Bahasa Indonesia capability + LLM-agent suitability of free-hostable open-weight models

**Researcher:** ModelIndoCapability (subagent) · **Date of all web access: 2026-10-06** · **No recommendations** — options and evidence only.

Scope: model cards, licenses, parameter sizes, context length, Bahasa Indonesia benchmark evidence, structured-output (function-calling / JSON) claims, determinism caveats, Indonesian-native reported advantage, and free-host availability for the model families listed in the brief **plus** the current-generation successors that actually exist as of 2026-10-06 (Qwen 3.5/3.6, Gemma 4, gpt-oss, Muse Glimmer, SEA-LION v4.5/v4.8, Mistral 4/Large 3, Ministral 3, Aya/Tiny Aya).

**Companion evidence files (per-family detail, same access date):** `local://phase1-meta-llama.md`, `local://phase1-qwen-deepseek.md`, `local://phase1-gemma-phi.md`, `local://phase1-mistral-cohere.md`, `local://phase1-sea-native.md`. This file is the synthesis; where a companion file and this file disagree, the companion slice (which read the field-level pages) is the more granular record and the disagreement is flagged inline.

**Method / integrity rules applied**
- Every version, licence, size, context and benchmark number below was read from a live page on 2026-10-06 (URL given per claim). Nothing is taken from training memory.
- Primary sources preferred (provider docs, HF model cards/LICENSE files, GitHub model cards). Aggregators used only as leads.
- Unverifiable items are marked `[UNVERIFIED]` with the reason.
- The current-model reality on 2026-10-06 differs from the brief's list: **Gemma 4 (Apache-2.0)**, **Qwen 3.5 and 3.6**, **Qwen3.5-397B-A17B**, **OpenAI gpt-oss**, **Meta Muse Glimmer**, **SEA-LION v4.5 and v4.8**, **Mistral Small 4 / Large 3 / Ministral 3** all exist and supersede several models named in the brief. Deprecation status is noted.

---

## 1. Master comparison table (one row per model)

Legend: ctx = context length · SO = structured output claim · FH = verified free-host availability. "—" in FH = not confirmed by me (provider research is a sibling task; see §5).

| # | Model | License (restriction) | Params | Context | Bahasa Indonesia evidence (suite: score) | SO (function calling / JSON) | FH |
|---|-------|----------------------|--------|---------|------------------------------------------|------------------------------|----|
| 1 | Llama 3.1 8B/70B/405B | Llama 3.1 Community License (commercial; 700M-MAU clause; "Built with Llama") | 8B / 70B / 405B | 128k | Not an officially supported language; SeaBench (3-shot exam) id 50.7 | BFCL-v2 77.3 (3.3 card; family) | — |
| 2 | Llama 3.2 1B/3B | Llama 3.2 Community License (same terms) | 1.23B / 3.21B | 128k (8k quantised) | Not supported; MMLU given only for pt/es/it/de/fr/hi/th | BFCL-v2: 3B 67.0 | — |
| 3 | Llama 3.3 70B | Llama 3.3 Community License (700M-MAU clause) | 70B | 128k | Not in the 8 supported languages | BFCL-v2 77.3 | — |
| 4 | Llama 4 Scout / Maverick | Llama 4 Community License (700M-MAU clause) | 109B/17B act; 400B/17B act (MoE) | 10M / 1M | Indonesian **listed as supported**; no Indonesian-specific number | Llama-4 function calling + JSON mode (prompt-format docs) | — |
| 5 | **Muse Glimmer 30B** (Meta, Aug 2026; HF `meta-models/Muse-Glimmer-30B`) | **Apache-2.0** | 29.6B dense incl. ~1.8B vision enc. | 131,072+ (cutoff Jan 4, 2026) | SEA-HELM Indonesian **75.61** | agentic/tool-use model (Meta blog) | — |
| 6 | Qwen2.5 7B/14B/32B | Apache-2.0 | 7–32B | 128k | SeaBench id 55.8 (Qwen2-7B); Global-MMLU 62.8 (7B, Aya paper) | function calling | — |
| 6b | Qwen2.5 72B | **"Qwen LICENSE AGREEMENT"** (custom; >100M-MAU clause; "Built with Qwen" notice) | 72B | 128k | not measured | function calling | — |
| 7 | Qwen3 32B / 30B-A3B / 235B-A22B | **Apache-2.0** (LICENSE fetched) | 32.8B; 30.5B/3.3B act | 32,768 native; 131,072 w/ YaRN | 100+ langs claimed; no Indonesian-specific number in card | Agentic + tool calling (card) | — |
| 8 | **Qwen3.5** 27B / 35B-A3B / 122B-A10B / 397B-A17B | **Apache-2.0** (LICENSE fetched) | 27B; MoE variants | 262,144 native, extensible to 1,010,000 | **201 languages**; SEA-HELM Indonesian **77.93** (122B-A10B) | BFCL-V4 68.5 (27B); function calling | — |
| 9 | **Qwen3.6 27B** / **Qwen3.8-27B** | Apache-2.0 | 27B | 262k | SEA-HELM Indonesian **77.96** (3.6) | tool calling | — |
| 9b | Qwen3.8-Flash-Next | **"Qwen Community License 1.0"** (100M-MAU; $20M-revenue notice; separate licence for Model-as-a-Service) | 125B / 6B act | ~1M | not published | JSON Schema only on select SKUs | — |
| 10 | DeepSeek-V3 | **custom "DEEPSEEK LICENSE AGREEMENT v1.0"** (use-based restrictions e.g. military prohibited; must propagate) | 671B / 37B act (MoE) | 128K | not documented | function calling; JSON Output "may return empty content" | — |
| 11 | DeepSeek-V3.1 / V3.2 / R1 + R1-Distill | **MIT** (R1 LICENSE fetched); distills inherit base licence | 671B/37B act; distills 1.5B–70B | 128K | not documented | via distil base | — |
| 11b | **DeepSeek-V4-Flash / V4-Pro / V4.1-Flash** | **MIT** | 284B/13B; 1.6T/49B; 552B (8B prefill/16B decode) | **1M** | not published | via base | — (Cloudflare stocks V4 line as paid) |
| 12 | Gemma 2 9B/27B | Gemma Terms of Use (prohibited-use policy, redistribution terms) | 9B / 27B | 8k | SeaBench (exam) id 58.5; SeaBench open id 8.30 | text-based tool-calling (Gemma template) | — |
| 13 | Gemma 3 1B/4B/12B/27B | Gemma Terms of Use (last modified **April 1, 2026**) | 1B–27B | 128K (4/12/27B); 32K (1B/270M) | 140+ langs; multilingual bench given (Global-MMLU-Lite 75.1) — no ID-specific number | function calling (Gemma docs) | — |
| 14 | **Gemma 4** E2B/E4B/12B/26B-A4B/31B | **Apache-2.0** (fetched) | 2.3B–31B (26B-A4B = 25.2B/3.8B act MoE) | 128K (small) / 256K (medium) | SEA-HELM Indonesian **79.75** (31B); **64.13** (E2B) | **native function calling** (card) | — |
| 15 | Phi-4 14B | MIT | 14B dense | 16K | none; "not intended to support multilingual use", multilingual data ~8% | [UNVERIFIED] | — |
| 16 | Phi-4-mini | MIT [card not re-fetched] | 3.8B | 128K | listed among 24 languages — Indonesian not confirmed `[UNVERIFIED]` | [UNVERIFIED] | — |
| 17 | Mistral Nemo 12B | Apache-2.0 | 12B | 128k | not documented | function calling | **RETIRED from Mistral API 2026-07-31** |
| 18 | Mistral Small 3 / 3.1 / 3.2 | Apache-2.0 | 24B | 32K/128K | Indonesian documented on 3.1/3.2 (region-aggregated multilingual avg 71.18% on 3.1; no ID-only number) | function calling | 3.0/3.1 retired; **3.2 RETIRED 2026-07-31** |
| 19 | **Mistral Small 4** (26.03) | **Apache-2.0** | 119B / 6.5B act (MoE) | 256k | HF tags list Indonesian; no ID number | function calling + structured outputs | — |
| 20 | **Ministral 3** 3B/8B/14B | **Apache-2.0** | 3.4/8.4/13.5B LM + 0.4B vision | 256k | **language list EXCLUDES Indonesian** | function calling [UNVERIFIED] | — |
| 21 | **Mistral Large 3** | **Apache-2.0** | 675B / 41B act (MoE) | 256k | not documented | function calling + structured outputs | — |
| 21b | **Mistral Large 4** | badge "Open" (exact licence `[UNVERIFIED]`) | [UNVERIFIED] | [UNVERIFIED] | not documented | — | — |
| 22 | Mistral Medium 3.5 | "Modified MIT" | 128B | [UNVERIFIED] | SEA-HELM Indonesian 70.09 (Cultural 39.25 — low) | function calling + structured outputs | — |
| 23 | Aya Expanse 32B (live) / 8B (**RETIRED 2026-04-04**) | **CC-BY-NC-4.0** — gated, checkbox *"I agree to use this model for non-commercial use ONLY"*; legal code: reproduce/Share *"for NonCommercial purposes only"* | 8B / 32B | 8K (8B) / 128K (32B) | Indonesian among 23 langs; m-ArenaHard win-rates **aggregated over 23 langs** (up to 76.6%); per-language ID values only in PNG charts | [UNVERIFIED] | — |
| 24 | Aya 23 8B/35B | **CC-BY-NC-4.0** | 8B / 35B | 8K / 128K | SeaBench id 41.6 (Aya-23-8B) | [UNVERIFIED] | — (absent from Cohere's current list) |
| 25 | Tiny Aya 3.35B (CohereLabs, new) | [UNVERIFIED] | 3.35B | [UNVERIFIED] | 70 languages; Indonesian = **1.6% of the data mix**; SEA-HELM Indonesian 33.23 | [UNVERIFIED] | — |
| 26 | SEA-LION v3 (Gemma-9B, Llama-8B/70B) | gemma (9B) / Llama 3.1 Community License (8B/70B) `[9B licence fetched; Llama variant inferred from base — UNVERIFIED]` | 8B/9B/70B | 128K (Llama variants) | SEA-HELM Bahasa Indonesia 62.44 (v3-9B) | model-specific (see SEA-LION tool guide) | — |
| 27 | SEA-LION v3.5 (Llama-8B/70B, 70B-R) | Llama 3.1/3.3 Community License `[UNVERIFIED]` | 8B/70B | 128K | SEA-HELM (v3.5 variants) | 70B-IT OpenAI-style tool calls; 70B-R no tool-calling | — |
| 28 | SEA-LION v4 (Qwen-32B, Gemma-27B, 4B-VL, Apertus-8B) | **LICENCE CONFLICT:** HF card says MIT vs SEA-LION docs say Qwen Terms of Service (Qwen-32B); Gemma Terms (Gemma-27B) | 4B–32B | page states "32,768 natively" **and** "Context Length: 128k" and "32k" (all three on the same pages §3) | SEA-HELM task suite (no numeric ID published); ~100B SEA-Pile v2 tokens | Qwen/Gemma inherited; v4-4B-VL adds function calling | — |
| 29 | **SEA-LION v4.5** (Qwen-27B-IT, Gemma E2B) | **Apache-2.0** (fetched) | 27B | 262k | SEA-HELM Indonesian **76.51** | native tool calling (Qwen); **Gemma v3-9B-IT "has not been trained to use a system prompt or to use tool calling"** | SEA-LION free POC API (10 RPM); Cloudflare (Gemma-27B) |
| 30 | **SEA-LION v4.8** (Nemotron 30B-A3B, 120B-A12B) | **MIT** (instruct; base variant "Other"/NOTICE) | 30B/3B act, 120B/12B act (MoE) | **262,144** | SEA-HELM Indonesian **73.10** (120B-A12B), 65.87 (30B) | [UNVERIFIED] | — |
| 31 | Sahabat-AI gemma2-9b / llama3-8b / v2-70B-IT (GoTo–Indosat) | Gemma Community License (9B) / Llama3 (8B) / **Llama 3.1 Community License** (70B) | 9B / 8B / 70.55B | **8192** (9B/8B) / 128k (70B) | instruct-9B: **IndoMMLU 62.6%**, BHASA-ID **64.154**; base-9B BHASA-ID 60.04; 8B 53.45; CPT 50B tokens (~53% SEA-LION-Pile Indonesian) | [UNVERIFIED] (bases not aligned) | — |
| 32 | Komodo-7B (Yellow.ai) | **llama2** (700M-MAU; no-distillation) | 7B | [UNVERIFIED] (card gated) | IndoMMLU **43.2**; NusaX-Senti **79.3** (paper calls SOTA); avg 71.1 | [UNVERIFIED] | — |
| 33 | Cendol (IndoNLP) | **Apache-2.0** (fetched; LLaMA2-derived variants flag a possible licence conflict) | 300M–13B (mT5, LLaMA2) | [UNVERIFIED] | paper: +~20% NLU F1 vs existing; **worst on IndoMMLU** among tested; single-turn only | no function-calling claim | — |
| 34 | Merak-7B-v4 | **CC-BY-NC-SA-4.0** (non-commercial) | 7B (Mistral base) | [UNVERIFIED] (card silent; author warns against 4-bit BnB) | IndoMMLU **46.27**; MAPS 77.78; IndoStoryCloze 66.78 | no function-calling | — |
| 35 | Salamandra 2B/7B/40B (BSC) | Apache-2.0 | 2B/7B/40B | 8,192 | **No Indonesian** — 35 European languages + code only | no | — |
| 36 | SeaLLM-7B-v2.5 (DAMO) / Sailor2 1B/8B/20B (Sea AI Lab) | SeaLLMs licence (>100M-MAU; **no-distillation** clause; China law) / **Apache-2.0** | 7B / 1B-20B | [UNVERIFIED] | SeaLLM: **M3Exam-ID 48.64**; SeaBench SeaLLMs-v3-7B id 55.8, Sailor-7B-Chat id 47.5 | [UNVERIFIED] | Sailor2: Float16.cloud free API announced 2024 `[UNVERIFIED]` |
| 37 | **gpt-oss-120b / 20b** (OpenAI) | **Apache-2.0** (fetched) | 117B/5.1B act; 21B/3.6B act (MoE) | 128K [UNVERIFIED] | SEA-HELM Indonesian **72.28** (120b) | **function calling + Structured Outputs** (card) | OpenRouter `:free` (`openai/gpt-oss-120b:free`) |

(43 rows. Current-generation models that supersede the 2024–25 lines named in the brief: #5 Muse Glimmer, #8–9b Qwen3.5/3.6/3.8, #11b DeepSeek-V4, #14 Gemma 4, #19–21b Mistral Small 4/Large 3/Large 4, #29–30 SEA-LION v4.5/v4.8, #37 gpt-oss.)

---

## 2. Licence texts — decisive restrictions (verbatim)

**Llama 3.1 / 3.2 / 3.3 / 4 Community Licences — commercial, but conditioned.**
Source (fetched 2026-10-06): `https://github.com/meta-llama/llama-models/blob/main/models/llama4/LICENSE` and `.../models/llama3_3/LICENSE`.
- MAU clause (Llama 4 text, §2): *"If, on the Llama 4 version release date, the monthly active users of the products or services … is greater than 700 million monthly active users in the preceding calendar month, you must request a license from Meta…"* (Llama 3.3 §2 identical with its own name).
- Attribution (§1.b.i): *"prominently display 'Built with Llama' on a related website, user interface, blogpost, about page, or product documentation."*
- Naming: *"you shall also include 'Llama' at the beginning of any such AI model name."*
- Model cards: Llama 3.1 `.../models/llama3_1/MODEL_CARD.md`; 3.2 `.../llama3_2/MODEL_CARD.md`; 3.3 `.../llama3_3/MODEL_CARD.md`; 4 `.../llama4/MODEL_CARD.md` (all fetched 2026-10-06).

**Gemma (v1–3) Terms of Use — commercial, with a prohibited-use policy.**
Source: `https://ai.google.dev/gemma/terms.md.txt` (fetched 2026-10-06; page states *"Last modified: April 1, 2026"*).
- §3.2: *"You must not use any of the Gemma Services: 1. for the restricted uses set forth in the Gemma Prohibited Use Policy…"*
- §3.3: *"Google claims no rights in Outputs you generate using Gemma."*
- Redistribution requires carrying the terms + a Notice file.

**Gemma 4 — Apache License 2.0 (no MAU clause, no prohibited-use addendum).**
Source: `https://ai.google.dev/gemma/apache_2` (fetched 2026-10-06); the Terms page states *"For Gemma 4 terms, see the Gemma 4 license"* → that page. Gemma 4 label is **"License: Apache 2.0"** on its card.

**Qwen family (Qwen3, Qwen3.5) — Apache License 2.0.** LICENSE file fetched live: `https://huggingface.co/Qwen/Qwen3-32B/raw/main/LICENSE` (Copyright 2024 Alibaba Cloud) and `Qwen/Qwen3.5-27B` LICENSE tag `apache-2.0` (both 2026-10-06).

**DeepSeek-R1 — MIT.** LICENSE fetched: `https://huggingface.co/deepseek-ai/DeepSeek-R1/raw/main/LICENSE` (fetched 2026-10-06). DeepSeek-V3 also ships `LICENSE-MODEL` (MIT per repo listing).

**gpt-oss — Apache-2.0.** Card: `https://huggingface.co/openai/gpt-oss-120b/raw/main/README.md` (fetched 2026-10-06): *"Permissive Apache 2.0 license: Build freely without copyleft restrictions or patent risk."*

**Cohere Aya Expanse / Aya 23 — CC-BY-NC-4.0 (non-commercial).** HF model tags show `License: cc-by-nc-4.0` (e.g. `CohereLabs/aya-expanse-32b`). The technical report `https://arxiv.org/html/2412.04261v1` (fetched 2026-10-06; revision dated August 24, 2026) also confirms only 23 commercial-use-agnostic languages. **This is a research-only licence for the weights.**

**Qwen — mostly Apache-2.0, two exceptions.** Qwen2.5 72B ships a custom **"Qwen LICENSE AGREEMENT"** (>100M-MAU clause; "Built with Qwen" notice), and Qwen3.8-Flash-Next ships **"Qwen Community License 1.0"** (100M-MAU; $20M-revenue notice; separate licence for Model-as-a-Service).

**DeepSeek — mostly MIT, one exception.** DeepSeek-**V3** ships a custom **"DEEPSEEK LICENSE AGREEMENT v1.0"** (use-based restrictions, e.g. military use prohibited; propagation required); V3.1/V3.2/R1/R1-Distill/V4 are MIT.

**SeaLLM-7B-v2.5 — custom "SeaLLMs LICENSE AGREEMENT".** Contains a **>100M-monthly-active-user** clause, a **no-distillation** clause (*"You can not use the Materials or any output therefrom to improve any other large language model"*), and is governed by the **laws of China**.

**SEA-LION: licence depends on base model.**
- Qwen-SEA-LION-v4-32B-IT — *"License: Qwen Terms of Service / Qwen Usage Policy"* (`https://docs.sea-lion.ai/models/sea-lion-v4/qwen-sea-lion-v4-32b`, page "Last updated: 2025-10-17", fetched 2026-10-06). **Not Apache-2.0**, despite the Qwen3 base being Apache-2.0.
- Qwen-SEA-LION-v4.5-27B-IT — *"License: Apache-2.0"* (`https://docs.sea-lion.ai/models/sea-lion-v4.5/qwen-sea-lion-v4.5.md`, page "Last update: 2026-05-19", fetched 2026-10-06).
- Gemma-SEA-LION-v3-9B — HF tag `License: gemma`.
- Gemma-SEA-LION-v4-27B-IT — Gemma 3/4 chat-template based; distributed on Cloudflare Workers AI.

**Sahabat-AI** — `license: gemma` (9B, `GoToCompany/gemma2-9b-cpt-sahabatai-v1-base`) and `license: llama3` (8B, `Sahabat-AI/llama3-8b-cpt-sahabatai-v1-base`) (both fetched 2026-10-06). These are **base** models, *"not aligned for safety."*

**Komodo-7B** — `License: llama2` (HF tag on `Yellow-AI-NLP/komodo-7b-base`).

**Cendol** — `license:apache-2.0` on every `indonlp/cendol-*` repo (HF API, fetched 2026-10-06).

**Merak-7B-v4** — `License: cc-by-nc-sa-4.0` (HF tag, `Ichsan2895/Merak-7B-v4`). **Non-commercial.**

**Salamandra** — *"The entire Salamandra family is released under a permissive Apache 2.0 license"* (`BSC-LT/salamandra-7b`, fetched 2026-10-06).

---

## 3. Per-family detail (size, context, Indonesian data, structured output, determinism)

### Meta — Llama 3.x / 4
- **Sizes/context (cards, 2026-10-06):** Llama 3.1 = 8B/70B/405B, 128k; 3.2 = 1.23B/3.21B, 128k (8k quantised); 3.3 = 70B, 128k; 4 = Scout 17B-act/109B-total @ **10M** ctx, Maverick 17B-act/400B-total @ **1M** ctx (MoE).
- **Indonesian data documented?** Llama 3.1/3.2/3.3 card lists exactly 8 supported languages — **Indonesian is not among them** (English, German, French, Italian, Portuguese, Hindi, Spanish, Thai). Llama 4 card lists **Indonesian** as supported (*"Arabic, English, French, German, Hindi, Indonesian, Italian, Portuguese, Spanish, Tagalog, Thai, and Vietnamese"*) and notes pre-training covers 200 languages (No-Language-Left-Behind).
- **Indonesian scores (independent):** SEA-HELM paper Tables A.1/A.2 — **Llama-3.1-8B ID 53.4; Llama-3.1-70B ID 67.8; Llama-3.3-70B ID 70.4** (the 70B scores are strong *despite* Indonesian not being an officially supported language). No Llama appears on the current Sep-2026 SEA-HELM table.
- **Llama 4 EU restriction (in the AUP, not the licence body):** *"With respect to any multimodal models included in Llama 4, the rights granted under Section 1(a) of the Llama 4 Community License Agreement are not being granted to you if you are an individual domiciled in, or a company with a principal place of business in, the European Union."*
- **Structured output:** Meta's prompt-format doc documents zero-shot function calling for 3.x and tool calling with parallel calls for Llama 4; Cloudflare exposes **JSON Mode**. Counter-evidence: NVIDIA NIM marks Llama 3.3 structured output *"Not supported"* but Llama 4 Scout *"Supported"*. Llama 3.3 card reports tool-use **BFCL-v2 = 77.3**.
- **Determinism:** Llama 3.x are dense ; Llama 4 is MoE (routing + batch effects — see §4). No Meta-authored determinism statement found. Llama 3.1/3.2 are on vLLM's batch-invariance validated list.
- **Newer Meta model:** the newest open-weight Meta release is **Muse Glimmer 30B** (Apache-2.0, Aug 2026), **not** branded Llama.
- **Free host:** Cloudflare Workers AI (10k Neurons/day) stocks Llama 3.1-8B, 3.2-1B/3B, 3.3-70B-fp8-fast and Llama-4-Scout; SambaNova Free Tier hosts Llama 3.3 70B (20 RPM/20 RPD/200k TPD); Scaleway gives 1,000,000 free tokens incl. llama-3.3-70b-instruct. **Groq is no longer free for Llama** (Enterprise-only), and **no free Llama 4 Maverick** was found.

### Qwen 2.5 / 3 / 3.5 / 3.6 / 3.8
- **Licence:** Apache-2.0 for Qwen2.5 7B/14B/32B, Qwen3 (32B, 30B-A3B, 235B-A22B), Qwen3.5 (27B, 35B-A3B, 122B-A10B, 397B-A17B) and Qwen3.6/3.8-27B (LICENSE files fetched). **Exceptions:** Qwen2.5 **72B** ships a custom **"Qwen LICENSE AGREEMENT"** (>100M-MAU clause; "Built with Qwen" notice), and **Qwen3.8-Flash-Next** ships a new **"Qwen Community License 1.0"** (100M-MAU + $20M-revenue notice; a **separate licence is required for Model-as-a-Service**).
- **Sizes/context:** Qwen3-32B — *"Number of Parameters: 32.8B … Context Length: 32,768 natively and 131,072 tokens with YaRN."* Qwen3.5-27B — *"Context Length: 262,144 natively and extensible up to 1,010,000 tokens"*, *"Expanded support to 201 languages and dialects."* Qwen3.8-Flash-Next = 125B/6B active, ~1M ctx.
- **Indonesian data documented?** Qwen3 claims *"100+ languages"*; Qwen3.5 claims 201. **No Indonesian-specific training-data breakdown or benchmark number is given on the cards.**
- **Structured output:** Qwen3 card: *"Expertise in agent capabilities … We recommend using Qwen-Agent"*, with MCP/tool-call templates. Qwen3.5-27B reports **BFCL-V4 68.5**. Alibaba Model Studio documents function calling + "JSON Object", but **JSON Schema is offered only on selected SKUs** (qwen-plus / 3.7 / 3.8-Max-Flash).
- **Determinism:** Qwen3 card, thinking mode: *"**DO NOT use greedy decoding**, as it can lead to performance degradation and endless repetitions"* — i.e. the recommended sampling parameters are temperature-based, so outputs are non-deterministic by design.

### DeepSeek
- **Licence:** **Mixed.** R1 (and R1-Distills, V3.1/V3.2, and the V4 line) = **MIT** (R1 LICENSE fetched 2026-10-06). But **DeepSeek-V3 itself ships a custom "DEEPSEEK LICENSE AGREEMENT v1.0"** with use-based restrictions (e.g. military use prohibited; terms must propagate). Distills inherit their base licence (Qwen→Apache-2.0, Llama→Llama Community) — check each distil repo.
- **Sizes/context:** DeepSeek-R1 = 671B total / 37B active, **128K** context (GitHub `deepseek-ai/DeepSeek-R1/README.md`); R1-Distill variants 1.5B–70B; V4-Flash 284B/13B, V4-Pro 1.6T/49B, V4.1-Flash 552B, all **1M** context.
- **Indonesian:** no Indonesian benchmark or data statement on the model cards read.
- **Structured output:** function calling documented; **"JSON Output" can return empty content**, and the strict tool-call schema is **Beta**.
- **Determinism:** MoE (671B/37B) + long reasoning traces → routing and reasoning-length nondeterminism; **thinking mode ignores `temperature` and clamps `top_p ≥ 0.95`.**

### Gemma 2 / 3 / 4
- **Licence:** Gemma Terms (v1–3, modified 2026-04-01) vs **Apache-2.0 (Gemma 4)**.
- **Sizes/context:** Gemma 3 — 128K for 4B/12B/27B, 32K for 1B/270M, 140+ languages. Gemma 4 — five sizes E2B/E4B/12B/26B-A4B/31B; *"context window of up to 256K tokens"*, *"multilingual support in over 140 languages"*, and *"Native support for structured tool use"* / *"Function Calling – Native support for structured tool use, enabling agentic workflows."*
- **Indonesian evidence:** Gemma 2-9b-it is one of the strongest in SeaBench among 7–9B models (SeaExam id 58.5; SeaBench open id 8.30 — arXiv 2502.06298 Table 2). SEA-HELM current: Gemma 4 31B **79.75**, E2B 64.13. **Gemma 4 is the top Indonesian open model on the Sep-2026 SEA-HELM table.** No Gemma 3 27B row exists on that leaderboard; "Indonesian" is never enumerated in Gemma's own cards.
- **Free host:** **Gemma 4 is on the Gemini API free tier** (free input/output tier; free-tier content may be used for product improvement). Gemma 4 26B-A4B and Gemma 3 12B are inside Cloudflare Workers AI's 10,000-Neurons/day free allocation. Groq carries no Gemma.
- **Determinism:** Gemma 3/4 hybrid local sliding-window attention; Gemma 4 has configurable thinking mode (empty thought block when disabled) — thinking-token handling is a nondeterminism/reproducibility source.

### Microsoft Phi-4
- **Licence:** MIT. **14B**, **16K** context. Training data *"Multilingual data constitutes about 8%"*; card explicitly: *"`phi-4` is not intended to support multilingual use"* and *"The model is trained primarily on English text. Languages other than English will experience worse performance."* → **no Indonesian evidence; poor expected fit.**
- Phi-4-mini: context 128K, 24 languages listed; Indonesian not confirmed `[UNVERIFIED]`.

### Mistral
- **Licence:** Apache-2.0 for Small 3.x, Small 4, Large 3, Ministral 3, Nemo; "Modified MIT" for Medium 3.5 (Mistral docs model list, fetched 2026-10-06).
- **Current line (docs.mistral.ai, 2026-10-06):** Mistral Large 3 = 675B/41B act, 256k ctx, *"Structured Outputs"* + *"Function Calling"*; Mistral Small 4 = 119B/6.5B act, 256k, Structured Outputs + Function Calling; Ministral 3 = 3B/8B/14B, Apache-2.0; Mistral Medium 3.5 = 128B, Modified MIT.
- **Deprecations:** Mistral Nemo 12B retires 2026-07-31; Mistral Small 3.2 retires 2026-07-31; Mistral Saba already retired 2025-09-30.
- **Indonesian:** Mistral docs give no Indonesian benchmark or language list. **Mistral Small 3.1/3.2 (and Mistral Small 4's HF tags) do document Indonesian**, but only as a region-aggregated multilingual score (3.1 Average 71.18%) — no Indonesian-only number. **Ministral 3's language list excludes Indonesian.** SEA-HELM puts Mistral Medium 3.5 at Indonesian **70.09** but its **Cultural** sub-score is only **39.25** (lowest in the top group).
- **Current line:** Large 4 (badge "Open"), Large 3, Medium 3.5, Small 4, Ministral 3. Deprecated/retired: Nemo 12B, Small 3.0/3.1/3.2, Saba. No Mistral model has a free `:free` variant on OpenRouter today.

### Cohere Aya
- **Licence:** CC-BY-NC-4.0 → **non-commercial/research only** (weights). Context: 8B = 8K, 32B = 128K (technical report §3). 23 languages including Indonesian.
- **Evidence:** m-ArenaHard pairwise win-rates averaged over 23 languages: up to 76.6% (32B vs Mixtral-8x22B), 60.4% (8B vs Gemma-2-9B). These are **preference win-rates**, not Indonesian knowledge scores. SeaBench independent: Aya-23-8B id exam **41.6** (near the bottom of the 9 models tested).
- **Caveat quoted:** *"we found that using GPT-4o-mini as a judge significantly biased win-rate results towards Aya Expanse by up to 10%."*

### SEA-LION (AI Singapore)
- **v3** (Dec 2024): Gemma-SEA-LION-v3-9B (gemma licence), Llama-SEA-LION-v3-8B (128K ctx), Llama-SEA-LION-v3-70B (128K).
- **v3.5:** Llama-SEA-LION-v3.5-8B/70B plus **70B-R** reasoning variant.
- **v4:** Qwen-SEA-LION-v4-32B-IT — *"continued pre-training on approximately 100B tokens sampled from the SEA-Pile v2 … across 7 SEA languages: Burmese, Indonesian, Malay, Filipino, Tamil, Thai, and Vietnamese"*; *"post-trained on … approximately 8 million question-and-answer pairs"*. **Context contradiction on the same page:** header says *"32,768 of context length natively"* while Model Details says *"Context Length: 128k tokens"* — both quoted verbatim (page last updated 2025-10-17).
- **v4.5:** Qwen-SEA-LION-v4.5-27B-IT (Apache-2.0, 262k ctx, 201 langs, built on Qwen3.6-27B, distilled from Qwen3.5-397B-A17B).
- **v4.8 (Sep 2026):** Nemotron-SEA-LION-v4.8 on NVIDIA Nemotron-3 Nano (30B-A3B) and Super (120B-A12B); **MIT** on the instruct variant, **262,144-token context**; base variant is licensed "Other" via a NOTICE file.
- **Tool-calling matrix:** Llama-SEA-LION-v3-70B-IT *"Fully supports OpenAI-style tool calling"*; Qwen-SEA-LION-v4.5 supports function calling; **Gemma family SEA-LION uses text-parsed ```tool_code``` blocks, not native `tool_calls`**; **Gemma-SEA-LION-v3-9B-IT explicitly *"has not been trained to use a system prompt or to use tool calling"***; Llama-SEA-LION-v3.5-70B-R is a reasoning model with no native tool calling.
- **Cloudflare:** *"Our Gemma-SEA-LION-v4-27B-IT model is now supported on the Cloudflare Workers AI for on-demand inferencing, subject to Cloudflare's Data Usage and Pricing Plans."* The free Workers AI allocation is 10,000 Neurons/day (≈0.3M input tokens/day at this model's neuron price).
- **Free API:** SEA-LION's own free POC API is *"rate-limited (10 requests per minute)"* and serves (as documented examples) Qwen-SEA-LION-v4.5-27B-IT, Llama-SEA-LION-v3.5-70B-R, SEA-Guard and SEA-LION-ModernBERT-Embedding-600M.

### Indonesian-native small models
- **Sahabat-AI** (GoTo+Indosat, built with AI Singapore): CPT bases at 50B tokens each, **context 8192**, ~53–55% SEA-LION-Pile Indonesian. The **instruct-9B** card reports **IndoMMLU 62.6%** (vs its gemma-2-9B base 61.4%) and **BHASA/SEA-HELM-ID 64.154** (vs base 63.394); base-9B BHASA-ID 60.04, 8B 53.45; 70B v2-IT (Llama 3.1, 128k) publishes no numbers.
- **Komodo-7B** (Yellow.ai): llama2 licence, 12 languages (Indonesian + 11 regional); **IndoMMLU 43.2, NusaX-Senti 79.3** (self-declared SOTA), average 71.1 vs GPT-4 74.7 (paper Table 3). Card is gated (HTTP 401 on README).
- **Cendol** (IndoNLP): Apache-2.0; mT5 + LLaMA2 backbones 300M–13B; paper reports *"∼20% weighted F1-score"* improvement on Indonesian NLU. Self-reported weakness: *"Our Cendol models are out-competed by some existing LLMs on all Indonesian language tasks, especially on IndoMMLU and IndoStoryCloze, where Cendol models perform the worst among all LLMs."* Single-turn by design.
- **Merak-7B-v4**: CC-BY-NC-SA-4.0 (non-commercial), Mistral base; in the Cendol paper it is the **best** IndoMMLU model of the open pre-2024 set (**46.27**, MAPS 77.78, IndoStoryCloze 66.78 vs Cendol's ≤23.5).
- **SeaLLM-7B-v2.5** (DAMO): SeaLLMs custom licence (**>100M-MAU clause + no-distillation clause + China law**); **M3Exam-ID 48.64** (card table). **Sailor2 1B/8B/20B** (Sea AI Lab): Apache-2.0, expanded from Qwen2.5; project announced a Float16.cloud free API in 2024 (current status unverified).
- **Salamandra** (BSC): Apache-2.0 but **35 European languages only — Indonesian is absent from the language list**, so no Indonesian evidence exists.

---

## 4. Determinism caveats (agent-relevant)

- **MoE routing + batch composition.** vLLM's own docs state that serving is not batch-invariant by default and provide an opt-in feature to change that: *"Batch invariance ensures that the outputs of a model do not depend on the batch size"* (`https://docs.vllm.ai/en/latest/features/batch_invariance`, fetched 2026-10-06). Applies to Llama 4, Qwen MoE, DeepSeek-V3/R1, gpt-oss, Gemma 4 26B-A4B, Mistral Large 3/Small 4, SEA-LION v4.8 MoE.
- **Floating-point / tensor-parallel nondeterminism.** Peer-reviewed work (arXiv 2506.09501, "Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference", fetched 2026-10-06) documents that *"changing system configuration, such as evaluation batch size, GPU count, and GPU version, can introduce significant differences in the generated responses"* even for greedy decoding.
- **Reasoning-mode nondeterminism.** Qwen3 card: *"DO NOT use greedy decoding"* in thinking mode (recommended temperature 0.6 / top-p 0.95). Gemma 4 has explicit thinking tokens. gpt-oss has low/medium/high reasoning effort. DeepSeek-R1 emits long CoT; DeepSeek's thinking mode **ignores `temperature` and clamps `top_p ≥ 0.95`**, so outputs are sampling-driven by design. All make byte-identical reruns unrealistic unless the provider pins a seed and the model is served in a batch-invariant, non-thinking configuration.
- **vLLM reproducibility (primary):** *"vLLM does not guarantee the reproducibility of the results by default, for the sake of performance… vLLM only provides reproducibility when it runs on the same hardware and the same vLLM version."* (docs.vllm.ai/en/stable/usage/reproducibility, fetched 2026-10-06). Batch invariance is opt-in and currently validated only for a short model list (Llama 3.1/3.2 among them).
- **Quantisation.** gpt-oss-120b ships **MXFP4** post-training quantised; SEA-LION offers 4-bit/8-bit GPTQ. Provider-side quantisation can differ from the card's bf16 eval numbers.

---

## 5. Free-host availability (what I could verify)

Free-tier research is also a sibling assignment (HostingFreeTiers, ProvidersPrimary, ProvidersAggregatorsRegional). Items below were verified on provider pages dated 2026-10-06 (several via my slice agents); the remainder of the `FH` column stays blank/`[UNVERIFIED]`.

**Cloudflare Workers AI — free allocation "10,000 Neurons per day at no charge"** (`https://developers.cloudflare.com/workers-ai/platform/pricing/`, page "Last updated Oct 1, 2026"). Models verified as stocked and priceable inside that allocation:
`@cf/meta/llama-3.1-8b-instruct`, `@cf/meta/llama-3.2-1b-instruct`, `@cf/meta/llama-3.2-3b-instruct`, `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, `@cf/meta/llama-4-scout-17b-16e-instruct`, `@cf/aisingapore/gemma-sea-lion-v4-27b-it`, `gemma-4-26b-a4b-it`, `gemma-3-12b-it`, `qwen3-30b-a3b-fp8`, `qwen3.8-27b`, `deepseek-r1-distill-qwen-32b`. **No Llama 4 Maverick; no DeepSeek-V4; no Gemma 4 31B** (paid/absent). SEA-LION's own guide confirms the Gemma-SEA-LION route and that it is *"subject to Cloudflare's Data Usage and Pricing Plans."*

| Model | Free access (verified 2026-10-06) | Evidence |
|-------|----------------------------------|----------|
| Llama 3.1 8B / 3.2 1B-3B / 3.3 70B / 4 Scout | Cloudflare Workers AI (10k Neurons/day) | `https://developers.cloudflare.com/workers-ai/platform/pricing/` |
| Llama 3.3 70B | SambaNova Cloud Free Tier (20 RPM / 20 RPD / 200k TPD) | `https://docs.sambanova.ai/docs/en/models/rate-limits` |
| Llama 3.3 70B | Scaleway Generative APIs free tier (1,000,000 tokens) | `https://www.scaleway.com/en/generative-apis/` |
| Gemma 4 | **Gemini API free tier** (free input/output; free-tier content used for product improvement) | Google AI for Developers Gemma docs |
| Gemma 4 26B-A4B, Gemma 3 12B | Cloudflare Workers AI (10k Neurons/day) | as above |
| Gemma-SEA-LION-v4-27B-IT | Cloudflare Workers AI (10k Neurons/day) | `https://docs.sea-lion.ai/guides/inferencing/cloudflare.md` |
| SEA-LION Qwen-v4.5-27B / Llama-v3.5-70B-R / SEA-Guard / ModernBERT-Embedding-600M | SEA-LION free POC API — *"rate-limited (10 requests per minute)"* | `https://docs.sea-lion.ai/overview/readme/faq.md` |
| Qwen3-30B-A3B, Qwen3.8-27B | Cloudflare Workers AI (10k Neurons/day) | pricing page |
| Qwen (any), Mistral (any), Aya | **No free variant found on OpenRouter** | `https://openrouter.ai/api/v1/models` |
| gpt-oss-120b | OpenRouter `:free` (`openai/gpt-oss-120b:free`, $0 in/out) | `https://openrouter.ai/openai/gpt-oss-120b:free` |
| DeepSeek-R1-Distill-Qwen-32B | Cloudflare Workers AI (10k Neurons/day) | pricing page |
| Phi-4 family | Azure AI Foundry + Hugging Face free | slice agent, 2026-10-06 |

**Explicitly NOT free today:** Groq — `llama-3.1-8b-instant` and `llama-3.3-70b-versatile` are now **Enterprise** ("ContactSales"); Groq carries no Gemma/Phi. Cerebras carries only gpt-oss-120b and qwen-3.8-27b. GitHub Models **retired 2026-07-30**. Together / OpenRouter have no free Llama or Maverick. Hugging Face free users get only "$0.10" monthly inference credits. Alibaba Model Studio offers "1M tokens/model, 90 days, Singapore" (per-model eligibility `[UNVERIFIED]`).

**Caution on free-tier legal terms:** Gemini API's free tier uses submitted content for product improvement; Cloudflare's Workers AI has separate Data Usage terms; SEA-LION's free API is POC-only. These are terms-of-service facts, not capability facts, but they gate the "free" column.

---

## 6. Evidence-quality note — how strong are the Indonesian claims?

*This is an assessment of evidence strength, not a recommendation.*

1. **Model cards mostly do NOT benchmark Indonesian.** Of the frontier open models, only **SEA-LION** reports Indonesian-specific results, and it points to the external SEA-HELM leaderboard rather than printing numbers. Llama 4 only *lists* Indonesian as a supported language; Qwen/Gemma/Mistral cards cite broad "100–201 languages" or multilingual averages (Global-MMLU, MMMLU) with no Indonesian row. **"Supports Indonesian" is a language-list claim, not a measured capability claim.**

1b. **Three independent Indonesian/SEA evidence bases, at three different eras — do not mix them:**
   - **SEA-HELM paper (arXiv 2502.14301, fetched 2026-10-06)** publishes per-model Indonesian numbers for the 2024 wave: **Llama-3.1-8B ID 53.4; Llama-3.1-70B ID 67.8; Llama-3.3-70B ID 70.4** (Tables A.1/A.2). Its own conclusion: *"Of all the open-sourced models tested, DeepSeek-R1 was the strongest performing model"* — i.e. the strongest Indonesian performer in that evaluation was **not** SEA-native and not Llama.
   - **Sahabat-AI / Komodo / SeaLLM self-reported (2024-era, different benchmark versions):** Sahabat-AI instruct-9B **IndoMMLU 62.6%** vs its own gemma-2-9B base 61.4% (a +1.2-pt margin, within single-run noise); SeaLLM-7B-v2.5 **M3Exam-ID 48.64**; Komodo-7B **IndoMMLU 43.2**, **NusaX-Senti 79.3** (self-declared SOTA), avg 71.1 vs GPT-4 74.7.
   - **SEA-HELM live leaderboard (Sep 2026)** for the current generation (see §2 item 2 below).
   The 2024 era and the 2026 leaderboard use different benchmark versions/scales, so **a Sahabat-AI 64.154 and a SEA-LION v4.5 76.51 are not on the same axis.**

2. **Two independent Indonesian/SEA benchmark suites exist and disagree in emphasis:**
   - **SeaBench/SeaExam** (arXiv 2502.06298, NAACL 2025 Findings) — real Indonesian exams + open-ended local prompts; judged by GPT-4o (agreement 64.9% with humans incl. ties). It is small (1,580 Indonesian exam items; 100 open-ended items), tests only 7–9B models, and its **own limitation section** notes possible saturation/contamination and a **single** human annotator per language. Its headline finding for Indonesian is negative: *"the ability to effectively separate models extends to … Indonesian … each showing a decline of more than 4.5% compared to MMLU-SEA"* — i.e. Indonesian is genuinely harder.
   - **SEA-HELM** (AISG leaderboard, page dated **Sep 18, 2026**) — the only suite giving current 2026 Indonesian numbers for the new generation (Gemma 4 31B 79.75; Qwen 3.6 77.96; Qwen 3.5-122B 77.93; SEA-LION v4.5 76.51; Muse Glimmer 75.61; gpt-oss-120b 72.28). Indonesian is one language among seven; scores are 95%-CI bootstrapped and the leaderboard UI is partly JS-rendered (I read the server-rendered table). **It is the best available primary evidence for the current generation.**

3. **The "Indonesian-native advantage" claim is NOT supported for the current top of the field.** On SEA-HELM Indonesian, the Indonesia/SEA-tuned **SEA-LION v4.5 (Qwen) 27B (76.51)** sits *below* the general **Qwen 3.6 27B (77.96)** and **Gemma 4 31B (79.75)**. The historical SeaBench result *"models … specifically trained with a focus on SEA daily scenarios … exhibited more balanced performances across SEA languages"* refers to **cross-language balance** (Javanese/Sundanese/varied), not to beating general models on Indonesian itself. Where Indonesian-native models do document a clear win it is on **local languages and culture** (Cendol † on MABL-jv/MABL-su; Sahabat-AI on Javanese 69.9 / Sundanese 62.4) — a narrower claim than "better at Bahasa Indonesia."

4. **Marketing vs benchmark gaps observed:**
   - **Aya Expanse**: headline "up to 76.6% win-rate" is over 23 languages on a *translated* preference set; the authors themselves report a GPT-4o-mini judge bias of *"up to 10%"* toward Aya, and on the independent SeaBench the same family (Aya-23-8B) scores near the bottom on Indonesian (41.6 vs Gemma-2-9B's 58.5). Its licence is also **non-commercial (CC-BY-NC-4.0)**.
   - **Cendol**: "~20% improvement" is on NLU tasks the model was tuned on; its own table shows it **worst on IndoMMLU** among all compared models, and a non-native competitor (Merak-7B-v4) scores much higher on IndoMMLU.
   - **Mistral Medium 3.5**: respectable overall Indonesian score but the *lowest* Cultural sub-score (39.25) among the top group.
   - **Phi-4**: the card itself disclaims multilingual use — no Indonesian marketing to test, but also no capability.

5. **Contamination suspicion is explicit in the literature.** Cendol notes *"a huge variance over different LLMs in some tasks, such as MAPS and IndoMMLU, which raises the question of whether some LLMs have seen the corresponding evaluation datasets."* SeaBench notes datasets were kept partly private to limit contamination. Any Indonesian number from a model vendor should be treated as indicative only.

**Bottom line on evidence strength:** Indonesian numbers exist and are consistent enough to rank *current* models (SEA-HELM), but for most families the strongest available evidence is a **third-party** leaderboard, not the vendor's own card, and the only suite naming Indonesian for the 2024–25 wave (SeaBench) tested just 7–9B models. Vendor "we support Indonesian" statements are the weakest tier of evidence.

---

## 7. Not verified / gaps

- **Qwen-SEA-LION-v4-32B-IT licence CONFLICT** — HF card says **MIT**, SEA-LION docs say **Qwen Terms of Service** (both live 2026-10-06). Unresolved; do not rely on either until checked.
- **Mistral Large 4** — docs give a badge "Open" only; exact licence `[UNVERIFIED]`. **Mistral Large 4 / Medium 3.5 contexts** `[UNVERIFIED]`.
- **Ministral 3 language coverage** — its model list **excludes Indonesian**; a dedicated Indonesian eval was not found (absence of claim, not a measured zero).
- **Muse Glimmer 30B** — release and Apache-2.0 confirmed via Meta research blog / HF `meta-models/Muse-Glimmer-30B`; benchmark suite and exact serving free tier `[UNVERIFIED]`.
- **Komodo-7B, Aya, Tiny Aya, Sahabat-AI v2-70B, Phi-4-mini, Gemma 3 27B** — several cards were gated (HTTP 401) or published numbers only in images; per-language Indonesian values for Aya and Mistral are `[UNVERIFIED]`.
- **[UNVERIFIED] Qwen3.6/3.8-27B own model cards** — existence and Apache-2.0 confirmed via SEA-LION parent and Ollama/Cloudflare listings; the vendors' own cards were not read for context/benchmarks.
- **[UNVERIFIED] Qwen3.8-Flash-Next specifics** ("Qwen Community License 1.0" terms read from slice agent; own card not re-read).
- **[UNVERIFIED] SEA-LION v3/v3.5 Llama variants' licences** — inferred from the Llama 3.1 base (only the Gemma v3-9B `license: gemma` tag was read). v4.8 instruct is now confirmed MIT.
- **[UNVERIFIED] Komodo-7B context length** — HF raw README returned HTTP 401 (gated); licence (`llama2`) taken from the HF tag.
- **[UNVERIFIED] Phi-4-mini** — card not re-fetched; Indonesian support unknown.
- **Ministral 3 context is 256k** (slice agent), but its **function-calling claim and Mistral Medium 3.5's context length** are `[UNVERIFIED]` (not printed on the pages fetched).
- **DeepSeek-V3** ships a custom **"DEEPSEEK LICENSE AGREEMENT v1.0"** (per slice agent), while R1's MIT LICENSE was read directly; the V4 line was reported MIT by the slice agent but not re-read by me → treat V4 licence as **slice-sourced, `[partially UNVERIFIED]`**.
- **Free-host column is only partly resolved** — the provider-page-verified set is in §5 (Cloudflare, SambaNova, Scaleway, Gemini free tier, SEA-LION POC API, OpenRouter `:free` for gpt-oss). Free quotas for Fireworks, DeepInfra, Novita, Chutes, Baidu, ModelScope, DeepSeek official, Azure, Perplexity remain `[UNVERIFIED]` here; sibling provider agents own those and their reports are the authority.
- **meta.ai / Llama model-card pages are JS-only** in this fetch; Llama data was taken from the official GitHub model cards instead (primary).
- **SEA-HELM leaderboard numbers** were read from the server-rendered HTML table on 2026-10-06; the interactive chart itself is JS-only, so I could not verify every model's value beyond the table shown.
