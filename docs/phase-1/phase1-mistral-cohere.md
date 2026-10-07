# Phase 1 — Mistral family & Cohere Aya family (Indonesian capability)

All URLs accessed **2026-10-06**. Today = 2026-10-06. Nothing below is from memory: every current
version / license / size / context / benchmark claim traces to a page fetched today, or is marked
`[UNVERIFIED]` with the reason.

> **Headline status changes found today (2026-10-06).** The two Mistral models the ticket named as
> "current" are **retired** from Mistral's API: `Mistral Nemo 12B` (deprecation 5/22/2026, retirement
> 7/31/2026) and `Mistral Small 3.2` (deprecation 4/30/2026, retirement 7/31/2026) — see
> <https://docs.mistral.ai/models> (accessed 2026-10-06), "Deprecated & retired models" table, which
> prints both rows with `Retirement 7/31/2026`. Their Apache-2.0 weights remain downloadable on HF.
> The Mistral lineup as of today is Mistral Large 4, Mistral Large 3, Mistral Medium 3.5,
> Mistral Small 4, Ministral 3 (3B/8B/14B) — same page. Likewise on the Cohere side,
> **Aya Expanse 8B and Aya Vision 8B were retired 2026-04-04**; the current Aya models served are
> Aya Expanse 32B, Aya Vision 32B and the new **Tiny Aya** family
> (<https://docs.cohere.com/v2/docs/models>, accessed 2026-10-06).

---

## Cross-cutting primary sources (used by several model sections)

- **Mistral function calling.** <https://docs.mistral.ai/studio/conversations/function-calling>
  (accessed 2026-10-06). Verbatim: *"Function calling, under the Tool Calling umbrella, allows
  Mistral models to connect to external local tools."* The page's "Available Models" table lists
  exactly these as function-calling capable: **Mistral Large 3, Mistral Medium 3.5, Mistral Small 3.2,
  Mistral Small Creative, Ministral 3 14B, Ministral 3 8B, Ministral 3 3B** (general), plus
  Devstral/Codestral/Voxtral (specialized) and Magistral Medium 1.2 / Magistral Small 1.2 (reasoning).
  **Mistral Nemo and Mistral Small 3.0 / 3.1 are NOT in that list.**
- **Mistral structured output / JSON.** <https://docs.mistral.ai/studio/conversations/structured-output>
  (accessed 2026-10-06). Verbatim: *"We offer a reliable method to obtain structured output in your
  desired format. Our system includes a built-in mode for JSON output, along with the capability to use
  custom structured outputs."* Caveat quoted from the same page: *"For JSON mode, it is essential to
  explicitly instruct the model in your prompt to output JSON and specify the desired format. Custom
  structured outputs are more reliable and are recommended whenever possible."*
- **Mistral determinism (applies to every Mistral model below).**
  <https://docs.mistral.ai/inference/sampling> (accessed 2026-10-06), boxed note, verbatim:
  *"While intuitively, setting `temperature` to 0 should make outputs fully deterministic and
  consistent (same prompt and settings = same completion output), in reality, even with greedy sampling
  at `temperature=0`, **slight variances** can sometimes occur due to hardware differences and rounding
  errors. … This effect becomes especially evident during long completions (input and/or output), where
  a single differing token can create an entirely new sequence, resulting in significantly different
  outputs for the same prompt-even with greedy sampling."*
- **vLLM reproducibility (vLLM is the runtime Mistral's own model cards recommend).**
  <https://docs.vllm.ai/en/latest/usage/reproducibility/> (accessed 2026-10-06). Verbatim:
  *"vLLM does not guarantee the reproducibility of the results by default, for the sake of performance."*
  and *"Even with the above settings, vLLM only provides reproducibility when it runs on the same
  hardware and the same vLLM version."*
- **Mistral prices (today).** <https://docs.mistral.ai/inference/pricing> (accessed 2026-10-06):
  Mistral Large 3 $0.5/M in, $1.5/M out; Mistral Small 4 $0.15/$0.6; Ministral 3 14B $0.2/$0.2;
  Ministral 3 8B $0.15/$0.15; Ministral 3 3B $0.1/$0.1. No free tier is stated on this pricing doc.
- **Mistral consumer "Free" plan.** <https://mistral.ai/pricing/> (accessed 2026-10-06). FAQ, verbatim:
  *"Does Mistral have a free plan?" — "Yes, Mistral's Free plan provides limited access to Vibe,
  including our latest models, chat, search, creation, and Vibe for code for agentic coding in your
  terminal. On the Free plan, you also get access to Mistral Studio."* The Free-plan card on the same
  page lists the bullet **"$10 /mo in API credits"** (Pro lists "$30 /mo in API credits"). The
  deprecated help-centre article on the older "Experiment plan"
  (<https://help.mistral.ai/en/articles/455206-…>) **now 404s** (checked 2026-10-06).
- **OpenRouter catalogue (free vs paid), fetched 2026-10-06** from
  <https://openrouter.ai/api/v1/models>. **No Mistral and no Aya/Cohere-Aya model has a `:free`
  variant today.** Every Mistral entry is paid, e.g. `mistralai/mistral-nemo` prompt price
  `0.000000019` USD/token, `mistralai/mistral-small-3.2-24b-instruct` `0.00000009375`,
  `mistralai/ministral-8b-2512` `0.00000015`, `mistralai/mistral-large-2512` `0.0000005`. The only
  `:free` Cohere-family entry is `cohere/north-mini-code:free`, which is **Cohere North, not Aya**.
  Aya Expanse / Aya 23 / Aya Vision / Tiny Aya are **absent from OpenRouter entirely**.
- **Hugging Face Inference Providers, free credits.** <https://huggingface.co/docs/inference-providers/pricing>
  (accessed 2026-10-06), table, verbatim: *"Free Users | $0.10, subject to change"* per month;
  *"PRO Users | $2.00"*. These are **credits**, not free models.

---

### Mistral Nemo 12B (Mistral-Nemo-Instruct-2407)

- Model card URL (primary): <https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407> (accessed 2026-10-06); card text via `/raw/main/README.md`.
- License: **Apache-2.0** (`license: apache-2.0` in card front-matter; card body: *"Released under the **Apache 2 License**"*). Doc page shows badge "Apache 2.0" — <https://docs.mistral.ai/models/mistral-nemo-12b-24-07> (accessed 2026-10-06). No non-commercial restriction.
- Params: **12.2B dense** (HF safetensors weight count `"total": 12247782400`; HF API, accessed 2026-10-06). Card architecture: 40 layers, dim 5120, GQA.
- Context length: **128k** — card: *"Trained with a **128k context window**"*; docs page: *"Context 128k"*.
- Bahasa Indonesia evidence: **NOT documented.** HF card `language:` list = en, fr, de, es, it, pt, ru, zh, ja (no `id`); the card's "Multilingual Benchmarks (MMLU)" table lists only French 62.3%, German 62.7%, Spanish 64.6%, Italian 61.3%, Portuguese 63.3%, Russian 59.2%, Chinese 59.0%, Japanese 59.0% — **no Indonesian row, no Indonesian score**. Training-data composition for Indonesian: **not documented** (card says only *"Trained on a large proportion of **multilingual and code data**"*, no language list).
- Structured output: card ships a worked **function-calling** example using `mistral_common` `Tool(...)`, and notes *"Mistral **does** use tool call IDs … They should be exactly 9 alphanumeric characters."* No JSON-mode claim on the card. **Not in Mistral's current function-calling model table** (<https://docs.mistral.ai/studio/conversations/function-calling>, accessed 2026-10-06). → function calling demonstrated on card, JSON output [UNVERIFIED] for this model.
- Determinism caveats: dense (no MoE routing). Cite the two cross-cutting quotes above: Mistral sampling doc's `temperature=0` "slight variances … due to hardware differences and rounding errors", and vLLM's "does not guarantee the reproducibility of the results by default".
- Free-host availability: **no free host verified.** Mistral API entry is retired (deprecation 5/22/2026, retirement 7/31/2026, per <https://docs.mistral.ai/models>). Not on OpenRouter free (paid `mistralai/mistral-nemo`, $0.000000019/token). HF `inferenceProviderMapping` for this repo returned `{}` (empty) — HF API `?expand[]=inferenceProviderMapping`, accessed 2026-10-06. → **[UNVERIFIED]**, no provider found offering it free.
- Notes: docs page carries the banner *"This model is deprecated. Use Ministral 3 8B for new integrations."* — so as of today Nemo is a weights-only legacy option.

### Mistral Small 3 / 24B Instruct 2501

- Model card URL (primary): <https://huggingface.co/mistralai/Mistral-Small-24B-Instruct-2501> (accessed 2026-10-06).
- License: **Apache-2.0** (`license: apache-2.0`); card: *"**Apache 2.0 License:** Open license allowing usage and modification for both commercial and non-commercial purposes."*
- Params: **24B dense** (card: *"boasting 24B parameters"*). Context: **32k** — card: *"**Context Window:** A 32k context window."*
- Bahasa Indonesia evidence: **NOT documented.** Card's Multilingual list, verbatim: *"Supports dozens of languages, including English, French, German, Spanish, Italian, Chinese, Japanese, Korean, Portuguese, Dutch, and Polish."* HF `language:` tags = en, fr, de, es, it, pt, zh, ja, ru, ko — **no `id`**. All published benchmark tables (MMLU-Pro, GPQA, HumanEval, MATH, MT-Bench, WildBench, Arena Hard, IFEval) are English-only; **no Indonesian number**. Indonesian in training data: not stated.
- Structured output: card, verbatim: *"**Agent-Centric:** Offers best-in-class agentic capabilities with native function calling and JSON outputting."* plus a full function-calling example. Not listed in Mistral's current function-calling model table (retired).
- Determinism caveats: dense; cite cross-cutting Mistral sampling + vLLM quotes.
- Free-host availability: **none verified.** Mistral API: deprecation 11/6/2025, retirement 11/30/2025 (<https://docs.mistral.ai/models>) → retired. OpenRouter: paid only (`mistralai/mistral-small-24b-instruct-2501`, $0.00000005/token).
- Notes: superseded by Small 3.1 → 3.2 → Small 4.

### Mistral Small 3.1 / 24B Instruct 2503

- Model card URL (primary): <https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503> (accessed 2026-10-06).
- License: **Apache-2.0**; card: *"**Apache 2.0 License:** Open license allowing usage and modification for both commercial and non-commercial purposes."*
- Params: **24B dense** (*"With 24 billion parameters"*). Context: **128k** (*"enhances long context capabilities up to 128k tokens"*; *"**Context Window:** A 128k context window."*).
- Bahasa Indonesia evidence: **Indonesian IS documented in the language list.** Card, verbatim: *"**Multilingual:** Supports dozens of languages, including English, French, German, Greek, Hindi, **Indonesian**, Italian, Japanese, Korean, Malay, Nepali, Polish, Portuguese, Romanian, Russian, Serbian, Spanish, Swedish, Turkish, Ukrainian, Vietnamese, Arabic, Bengali, Chinese, Farsi."* HF `language:` tags include **`id`** (24 tags). Indonesian/Latin training data documented: **yes, at language-list level only**; no Indonesian-specific corpus disclosure. Numeric Indonesian score: card's "Multilingual Evals" table is region-aggregated, not per-language — Small 3.1 24B Instruct **Average 71.18%**, European 75.30%, East Asian 69.17%, Middle Eastern 69.08% (vs Gemma 3 27B IT 70.19%, GPT-4o Mini 70.36%, Claude 3.5 Haiku 70.16%, Cohere Aya-Vision 32B 62.15%). **No per-language Indonesian figure → [UNVERIFIED] for an Indonesian-only number.**
- Structured output: card, verbatim: *"**Agent-Centric:** Offers best-in-class agentic capabilities with native function calling and JSON outputting."* Card also states *"low-latency function calling"* as an intended use, and gives a vLLM `--tool-call-parser mistral --enable-auto-tool-choice` recipe.
- Determinism caveats: dense; cross-cutting Mistral sampling + vLLM quotes.
- Free-host availability: **HF Inference Providers** — this repo's `inferenceProviderMapping` shows `featherless-ai` with `"status": "live"` (HF API, accessed 2026-10-06); usable via HF's routed billing where the free-user monthly credit is **$0.10**. That is a credit, not a free model. Mistral API: deprecation 11/6/2025, retirement 11/30/2025 → retired. OpenRouter: paid only ($0.000000351/token).
- Notes: newest Mistral model whose **documented** language coverage explicitly names Indonesian in prose.

### Mistral Small 3.2 / 24B Instruct 2506

- Model card URL (primary): <https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506> (accessed 2026-10-06).
- License: **Apache-2.0** (`License: apache-2.0`, HF API + card front-matter). No non-permissive clause.
- Params: **24B dense** (an update of the 24B Small 3.1; card: *"Mistral-Small-3.2-24B-Instruct-2506 is a minor update of Mistral-Small-3.1-24B-Instruct-2503"*).
- Context length: **128k** — <https://docs.mistral.ai/models/mistral-small-3-2-25-06> (accessed 2026-10-06): *"Context 128k"*.
- Bahasa Indonesia evidence: **Indonesian IS tagged** — HF model metadata `language:` list includes **`id`** (24 languages, identical list to Small 3.1: en, fr, de, es, pt, it, ja, ko, ru, zh, ar, fa, **id**, ms, ne, pl, ro, sr, sv, tr, uk, vi, hi, bn). Card body defers: *"Key Features — same as Mistral-Small-3.1-24B-Instruct-2503"*, i.e. it inherits 3.1's Indonesian language claim. **No Indonesian numeric score on the card.** Card benchmarks are English/general: Wildbench v2 **65.33%**, Arena Hard v2 **43.1%**, internal IF **84.78%**, MMLU 80.50%, MMLU Pro 69.06%, MATH 69.42%, GPQA Diamond 46.13%, HumanEval Plus Pass@5 92.90%, MBPP Plus Pass@5 78.33%, SimpleQA 12.10%; vision MMMU 62.50%, Mathvista 67.09%, ChartQA 87.4%, DocVQA 94.86%, AI2D 92.91%. Indonesian in training data: not disclosed beyond the language tag.
- Structured output: card, verbatim: *"**Function calling**: Small-3.2's function calling template is more robust"*, plus a vLLM `--tool-call-parser mistral` function-calling recipe and the sentence *"Mistral-Small-3.2-24B-Instruct-2506 is excellent at function / tool calling tasks via vLLM."* JSON: covered by the cross-cutting Mistral structured-output doc; no model-specific JSON guarantee. Listed in Mistral's current function-calling table.
- Determinism caveats: dense; cross-cutting Mistral sampling + vLLM quotes. Card also recommends a fixed low temperature: *"We recommend using a relatively low temperature, such as `temperature=0.15`."*
- Free-host availability: **no free host verified.** Mistral API row: deprecation 4/30/2026, retirement 7/31/2026 → **retired as of today**; docs banner *"This model is deprecated. Use Mistral Small 4 for new integrations."* OpenRouter: paid only ($0.00000009375/token ≈ $0.094/M). HF `inferenceProviderMapping` = `{}` (empty) — **no HF Inference provider**.
- Notes: this is the model most often assumed to be "the" Mistral 24B; today it is API-retired and weights-only.

### Ministral 3 — 3B / 8B / 14B Instruct 2512

- Model card URLs (primary), accessed 2026-10-06:
  <https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512>,
  <https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512>,
  <https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512>.
  Provider docs: <https://docs.mistral.ai/models/ministral-3-3b-25-12>, `…/ministral-3-8b-25-12`, `…/ministral-3-14b-25-12` (all accessed 2026-10-06).
- License: **Apache-2.0** for all three (`license: apache-2.0`; docs badge "Apache 2.0"). Card: *"**Apache 2.0 License:** Open-source license allowing usage and modification for both commercial and non-commercial purposes."* No non-permissive clause.
- Params (**dense**, each = language model + small vision encoder):
  - 3B: *"**3.4B Language Model**"* + *"**0.4B Vision Encoder**"* (≈3.8B total)
  - 8B: *"**8.4B Language Model**"* + *"0.4B Vision Encoder**"* (≈8.8B total)
  - 14B: *"**13.5B Language Model**"* + *"**0.4B Vision Encoder**"* (≈13.9B total)
  (Also shipped as *Reasoning* and *Base* checkpoints; instruct weights are FP8.)
- Context length: **256k** for all three — card: *"**Large Context Window:** Supports a 256k context window."*; docs: *"Context 256k"*.
- Bahasa Indonesia evidence: **NOT documented.** All three cards carry the identical sentence, verbatim: *"**Multilingual:** Supports dozens of languages, including English, French, Spanish, German, Italian, Portuguese, Dutch, Chinese, Japanese, Korean, Arabic."* HF `language:` tags for all three = en, fr, es, de, it, pt, nl, zh, ja, ko, ar — **no `id`**. Only multilingual metric is Base "Multilingual MMLU": **14B 0.742, 8B 0.706, 3B 0.652** — aggregated, no Indonesian breakdown, and no Indonesian/language-mix data statement.
- Structured output: all three cards, verbatim: *"**Agentic:** Offers best-in-class agentic capabilities with native function calling and JSON outputting."*; vLLM recipe uses `--enable-auto-tool-choice --tool-call-parser mistral`. All three are in Mistral's current function-calling model table.
- Determinism caveats: dense (no MoE routing). Cards advise *"Use a **temperature below 0.1** for daily-driver and production environments"*. Cross-cutting Mistral sampling + vLLM quotes apply. Reasoning-mode nondeterminism: the Reasoning checkpoints are separate repos, but **no primary doc was found describing their sampling nondeterminism → [UNVERIFIED]**.
- Free-host availability: **no free-of-charge endpoint verified.** Mistral's paid API ($0.1–$0.2/M in/out); Mistral **Free plan includes "$10 /mo in API credits"** (mistral.ai/pricing, accessed 2026-10-06) which is a credit, not a free model. OpenRouter: paid only (`ministral-3b-2512` $0.0000001, `ministral-8b-2512` $0.00000015, `ministral-14b-2512` $0.0000002 per token). HF `inferenceProviderMapping` for `Ministral-3-8B-Instruct-2512` = `{}` (empty).
- Notes: docs mark Ministral 3 8B as the official replacement for the retired Mistral Nemo 12B, and Ministral 3 8B for Mistral Small Creative; Ministral 3 14B is positioned as *"performance comparable to its larger Mistral Small 3.2 24B counterpart"* (14B card).

### Mistral Large 3 (Mistral-Large-3-675B-Instruct-2512) — open-weight, confirmed

- Model card URL (primary): <https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512> (accessed 2026-10-06). Provider docs: <https://docs.mistral.ai/models/mistral-large-3-25-12> (accessed 2026-10-06).
- License: **Apache-2.0** — docs badge "Apache 2.0"; card front-matter `license: apache-2.0`; card: *"**Apache 2.0 License:** Open-source license allowing usage and modification for both commercial and non-commercial purposes."* Docs describe it as *"open-weight"*. → **Yes, open-weight as of 2026-10-06.**
- Params: **Mixture-of-Experts**, *"**41B active parameters** and **675B total parameters**"* (docs/OG description). Card detail: *"A Granular MoE Language Model with 673B params and 39B active"* + *"A 2.5B Vision Encoder"*.
- Context length: **256k** — card: *"Supports a 256k context window"*; docs "Context 256k"; vLLM example `--max-model-len 262144`.
- Bahasa Indonesia evidence: **NOT documented.** Card, verbatim: *"**Multilingual:** Supports dozens of languages, including English, French, Spanish, German, Italian, Portuguese, Dutch, Chinese, Japanese, Korean, Arabic."* HF `language:` tags = en, fr, es, de, it, pt, nl, zh, ja, ko, ar — **no `id`**. Card's benchmark section is **three images only** (no extractable Indonesian or multilingual numbers) → **no Indonesian number, and benchmark text [UNVERIFIED]** (values are in PNGs).
- Structured output: card, verbatim: *"**Agentic:** Offers best-in-class agentic capabilities with native function calling and JSON outputting."* Docs model page lists both "Structured Outputs" and "Function Calling" features on `/v1/chat/completions` and `/v1/conversations`. Listed first in Mistral's function-calling table.
- Determinism caveats: **MoE → expert routing**. No primary doc found stating MoE routing nondeterminism for this model → **[UNVERIFIED]**. What *is* documented: the Mistral sampling `temperature=0` variance note and vLLM's *"does not guarantee the reproducibility of the results by default"* — both quoted above. Card advises *"temperature below 0.1"*; card also lists under **Known Issues / Limitations**: *"Not a dedicated reasoning model"* and *"Complex deployment"*.
- Free-host availability: Mistral **Free plan = "$10 /mo in API credits"** (mistral.ai/pricing, accessed 2026-10-06) and Free-plan access to Mistral Studio — credit-based, not a free model. OpenRouter: paid only (`mistralai/mistral-large-2512` $0.0000005/token; `mistralai/mistral-large-4-0` also paid). HF `inferenceProviderMapping` for `Mistral-Large-3-675B-Instruct-2512` returned `null` — **no HF Inference provider**. → **no free endpoint verified.**
- Notes: priced $0.5/M in, $1.5/M out (docs pricing, Mistral docs model page).

### Mistral Small 4 (Mistral-Small-4-119B-2603) — current successor (added for completeness)

- Model card URL (primary): <https://huggingface.co/mistralai/Mistral-Small-4-119B-2603> (accessed 2026-10-06). Docs: <https://docs.mistral.ai/models/mistral-small-4-0-26-03>.
- License: **Apache-2.0**. Card: *"**Apache 2.0 License:** Open-source license for both commercial and non-commercial use."*
- Params: **MoE**, *"**119B parameters**, with **6.5B activated per token**"*, *"**MoE**: 128 experts, 4 active."* Context: **256k**.
- Bahasa Indonesia evidence: **split signal.** HF metadata `language:` list **includes `id`** (en, fr, de, es, pt, it, ja, ko, ru, zh, ar, fa, **id**, ms, ne, pl, ro, sr, sv, tr, uk, vi, hi, bn), but the card's prose Multilingual bullet, verbatim: *"Supports dozens of languages, including English, French, Spanish, German, Italian, Portuguese, Dutch, Chinese, Japanese, Korean, and Arabic."* — **Indonesian not named in prose.** Benchmark sections are images (AA LCR 0.72, LiveCodeBench/AIME25 as PNGs) — **no Indonesian number**.
- Structured output: card: *"**Agentic:** Best-in-class agentic capabilities with native function calling and JSON output."*
- Determinism caveats: MoE + **dual instruct/reasoning mode** (`reasoning_effort="none"|"high"`, card). Reasoning-mode nondeterminism: **[UNVERIFIED]** (no primary doc found). Cross-cutting sampling/vLLM quotes apply.
- Free-host availability: Mistral Free plan credits ($10/mo, mistral.ai/pricing); OpenRouter paid (`mistralai/mistral-small-2603` $0.00000015 and a `:batch` variant). No free-of-charge model endpoint verified.

### Aya Expanse 32B (CohereLabs/aya-expanse-32b) and Aya Expanse 8B

- Model card URL (primary): <https://huggingface.co/CohereLabs/aya-expanse-32b> and
  <https://huggingface.co/CohereLabs/aya-expanse-8b> (accessed 2026-10-06). **Both repos are gated**:
  the HF API reports `"Access: Gated"`, and both `/raw/main/README.md` fetches returned **HTTP 401**
  (2026-10-06). Provider doc: <https://docs.cohere.com/docs/aya-expanse> and
  <https://docs.cohere.com/v2/docs/models> (both accessed 2026-10-06). Paper:
  <https://arxiv.org/abs/2412.04261> + full text <https://arxiv.org/pdf/2412.04261v1> (accessed 2026-10-06).
  The card text below is read from a **community mirror** of the 8B card
  (<https://huggingface.co/jebish7/aya-expanse-8b/raw/main/README.md>, accessed 2026-10-06); the gating
  text it quotes is byte-identical to the official gating metadata returned by the HF API for
  `CohereLabs/aya-expanse-32b` (see license bullet). **Treat mirror-only sentences as secondary.**
- License: **CC-BY-NC-4.0** (`license: cc-by-nc-4.0`, HF API for both repos). Official gating field,
  verbatim from HF API `cardData.extra_gated_fields` for `CohereLabs/aya-expanse-32b` (accessed
  2026-10-06): `"I agree to use this model for non-commercial use ONLY": "checkbox"`, with
  `extra_gated_prompt` naming *"the License Agreement (https://cohere.com/c4ai-cc-by-nc-license)"*.
  Mirror card terms, verbatim: *"This model is governed by a CC-BY-NC License with an acceptable use
  addendum, and also requires adhering to C4AI's Acceptable Use Policy"* and
  *"License: CC-BY-NC, requires also adhering to C4AI's Acceptable Use Policy"*.
  **NC clause, verbatim from the CC BY-NC 4.0 legal code**
  (<https://creativecommons.org/licenses/by-nc/4.0/legalcode.en>, accessed 2026-10-06):
  §2(a)(1) *"the Licensor hereby grants You a worldwide, royalty-free, non-sublicensable, non-exclusive,
  irrevocable license to exercise the Licensed Rights … to: reproduce and Share the Licensed Material,
  in whole or in part, **for NonCommercial purposes only**"*; §1(9) *"**NonCommercial** means not
  primarily intended for or directed towards commercial advantage or monetary compensation."*
  → **CC-BY-NC-4.0 is research / non-commercial only.** Applies to weights, derivatives and
  redistribution.
- Params: **8B dense** and **32B dense** (paper: *"the Aya Expanse models are an open-weights release of
  both 8-billion and 32-billion parameters"*; mirror card: *"Model Size: 8 billion parameters"*).
- Context length: **8K for 8B**, **128K for 32B** — paper, verbatim: *"the 8B model is trained with a
  maximum context length of 8K, while the 32B model is trained with a maximum context length of 128K."*
  Provider doc for the 32B: *"Context Length 128k | Maximum Output Tokens 4k"*
  (<https://docs.cohere.com/docs/aya-expanse>, accessed 2026-10-06).
- Bahasa Indonesia evidence: **Indonesian is an officially covered language, and the eval suite spans it.
  No per-language Indonesian figure was publishable.**
  - Coverage, verbatim (paper §3): *"These 23 languages are: Arabic, Chinese (simplified & traditional),
    Czech, Dutch, English, French, German, Greek, Hebrew, Hindi, **Indonesian**, Italian, Japanese,
    Korean, Persian, Polish, Portuguese, Romanian, Russian, Spanish, Turkish, Ukrainian and Vietnamese."*
    Same list in <https://docs.cohere.com/docs/aya-expanse> and `…/v2/docs/models` (accessed 2026-10-06).
  - **m-ArenaHard win-rates, averaged across all 23 languages** (paper §5.1, GPT-4o-2024-08-06 judge,
    translating the 500 Arena-Hard-Auto prompts): Aya Expanse 8B **up to 70.6%** vs Llama-3.1-8B,
    **60.4%** vs Gemma-2-9B, **55.7%** vs Qwen-2.5-7B; Aya Expanse 32B **up to 76.6%** vs Mixtral 8x22B,
    **54.0%** vs Llama-3.1-70B, **51.8%** vs Gemma-2-27B, **53.6%** vs Qwen-2.5-32B. Source URL as above.
  - **Aggregate academic benchmarks** (tables 2–3, averaged over the 23 languages, "Discriminative"
    = avg of XWinograd/XCOPA/XStoryCloze 0-shot): Aya-Expanse-8B — discriminative **70.3**, Global-MMLU
    (5-shot) **53.7**, MGSM (5-shot) **67.0**, FLORES chrF++ **57.2**, xCOMET **93.2**;
    Aya-Expanse-32B — discriminative **72.6**, Global-MMLU **66.9**, MGSM **73.4**, chrF++ **58.8**,
    xCOMET **93.5**. Note: MGSM covers only 7 languages (EN/DE/ES/FR/JA/RU/ZH) — **Indonesian is not in
    MGSM**.
  - **Per-language Indonesian win-rate: [UNVERIFIED].** The card's per-language charts exist only as PNG
    images (`winrates_by_lang.png`, `winrates_marena_hard_complete.png`, listed in the HF repo file tree,
    accessed 2026-10-06); values are not machine-readable and the paper's Figure 4 only plots
    *"selected 8 diverse languages"* without enumerating them. **No SeaBench and no IndoMMLU number
    appears anywhere in the Aya Expanse card, the Cohere docs, or the paper** (searched the paper full
    text for "IndoMMLU", "SeaBench", "Indo" — zero hits).
  - Indonesian/Latin training data documented: **yes, at language-coverage level** (23-language pretrain
    mixture inherited from the Cohere Command series, paper §3); no Indonesian corpus sizes or
    proportions are published in this report.
- Structured output: **No function-calling and no JSON-output claim exists on the Aya Expanse card, in
  the Cohere Aya docs page, or in the paper.** The Cohere Aya docs page contains no "tool"/"function
  calling"/"JSON" statement. Mirror card's Model Details: *"**Input**: Models input text only.
  **Output**: Models generate text only."* → treat reliable function calling / JSON mode as
  **not documented (absent)** for Aya Expanse.
- Determinism caveats: no MoE (dense). Provider doc, verbatim
  (<https://docs.cohere.com/docs/aya-expanse>, accessed 2026-10-06): *"remember: these models are
  stochastic, and what you see might look quite different"*. Mirror card's example uses
  `do_sample=True, temperature=0.3`. No seed parameter is documented on the Aya docs page. Batch/
  quantisation nondeterminism: **[UNVERIFIED]** (no Aya-specific primary doc).
- Free-host availability:
  - **Aya Expanse 32B** is **Live** on Cohere's API as `c4ai-aya-expanse-32b` (128k ctx, 4k max output) —
    <https://docs.cohere.com/v2/docs/models>, accessed 2026-10-06. Cohere's key doc, verbatim:
    *"Cohere offers two kinds of API keys: **evaluation keys (free but limited in usage)**, and
    production keys (paid…)"* and *"Trial keys (and prod keys on newer Chat model variants) are limited
    to **1,000 API calls a month**."* (<https://docs.cohere.com/docs/rate-limits>, accessed 2026-10-06).
    **Caveat:** that page's per-model table lists only Command A+/A/… and North Mini Code —
    `c4ai-aya-expanse-32b` is **not listed**, so whether a free trial key can call Aya today is
    **[UNVERIFIED]**. There is also a free HF Space playground,
    <https://huggingface.co/spaces/CohereForAI/aya_expanse> (linked from the Cohere docs page).
  - **HF Inference Providers**: `CohereLabs/aya-expanse-32b` `inferenceProviderMapping` = `cohere`
    (`"status": "live"`, `providerId: c4ai-aya-expanse-32b`, `isModelAuthor: true`) — HF API
    `?expand[]=inferenceProviderMapping`, accessed 2026-10-06. Routable with HF's monthly credits
    (free users $0.10/mo) — a credit, not a free model.
  - **Aya Expanse 8B: retired from the Cohere API on 2026-04-04** — `c4ai-aya-expanse-8b` shows
    *"Retired Apr 4, 2026"* (<https://docs.cohere.com/v2/docs/models>) and appears under
    *"2026-04-04: Embed v2.0, Aya Expanse 8B … Effective April 4th, 2026, the following models will be
    retired: … `c4ai-aya-expanse-8b` …"* (<https://docs.cohere.com/docs/deprecations>, accessed
    2026-10-06). Weights remain on HF under CC-BY-NC-4.0.
  - OpenRouter: Aya absent; no free variant.
- Notes: 8B was retired 2026-04-04; the 32B remains the only Aya Expanse endpoint. The context/gating
  facts are solid (HF API + Cohere docs), while card-body sentences come from a mirror because the
  official card is gated.

### Aya 23 — 8B and 35B (CohereLabs/aya-23-8B, aya-23-35B)

- Model card URLs (primary): <https://huggingface.co/CohereLabs/aya-23-35B> and
  <https://huggingface.co/CohereLabs/aya-23-8B> (accessed 2026-10-06). **Both gated** ("Access: Gated"
  in HF API); `/raw/main/README.md` returned **HTTP 401** on 2026-10-06 → **card body [UNVERIFIED]**.
  Paper: <https://arxiv.org/abs/2405.15032> and full text <https://arxiv.org/html/2405.15032v1>
  (accessed 2026-10-06).
- License: **CC-BY-NC-4.0** (`license: cc-by-nc-4.0`, HF API `cardData` for `aya-23-35B`, accessed
  2026-10-06). Same NC restriction as Aya Expanse; the CC BY-NC 4.0 §2(a)(1) "**for NonCommercial
  purposes only**" quote above applies. Gating prompt is the same non-commercial agreement form.
- Params: **8B dense** and **35B dense** — paper: *"We release the open weights for both the 8B and
  35B models"*.
- Context length: **[UNVERIFIED] from the card** (gated). What the paper documents is training context,
  not serving context: *"we fine-tune the base models for 13,200 update steps using an **8192 context
  length** with data packing enabled"* (paper §3.2). Do not read that as a card-stated context window.
- Bahasa Indonesia evidence: **Indonesian is an officially covered language.** Paper §4, verbatim:
  *"we focus on 23 languages that are covered by the new Aya model family. These 23 languages are:
  Arabic, Chinese (simplified & traditional), Czech, Dutch, English, French, German, Greek, Hebrew,
  Hindi, **Indonesian**, Italian, Japanese, Korean, Persian, Polish, Portuguese, Romanian, Russian,
  Spanish, Turkish, Ukrainian and Vietnamese."* The paper's language table also lists Indonesian:
  *"id Indonesian Latin Austronesian Malayo-Polynesian 43 million"* (speaker count used for selection).
  **No Indonesian-only score was extracted**; the paper's discriminative/generative tables are
  per-language for a subset of benchmarks — **[UNVERIFIED] for an Indonesian-specific number**.
  Indonesian data provenance: documented as language coverage only.
- Structured output: no function-calling / JSON claim found in the paper or in Cohere's docs →
  **not documented (absent)**. Aya 23 is additionally **absent from Cohere's current model list**
  (`docs.cohere.com/v2/docs/models` Aya section names only Tiny Aya, Aya Expanse 32B, Aya Vision 32B),
  so there is no served endpoint whose docs could claim it.
- Determinism caveats: dense; **no primary doc found** for Aya-23-specific nondeterminism →
  **[UNVERIFIED]**. The general Cohere "these models are stochastic" line is on the Aya Expanse doc page,
  not the Aya 23 page.
- Free-host availability: **none verified.** Aya 23 does not appear on Cohere's current model list
  (checked 2026-10-06), is absent from OpenRouter, and has no HF `inferenceProviderMapping` entry
  published for the 35B repo (gated metadata). → **[UNVERIFIED]**, weights-only under CC-BY-NC-4.0.
- Notes: Aya 23 is the predecessor generation; the Aya Expanse paper states Expanse improves on Aya 23 by
  *"up to 16% increase in language understanding and 1.8x increase in mathematical reasoning."*

### Tiny Aya (CohereLabs/tiny-aya-global / -earth / -fire / -water) — the newer Aya

- Model card URL (primary): <https://huggingface.co/CohereLabs/tiny-aya-global> (accessed 2026-10-06).
  **Gated** — `/raw/main/README.md` = **HTTP 401**; card body therefore reads through the HF API
  metadata plus the technical report. Provider doc: <https://docs.cohere.com/v2/docs/models>
  (accessed 2026-10-06). Paper: <https://arxiv.org/abs/2603.11510> and
  <https://arxiv.org/html/2603.11510v1> (accessed 2026-10-06).
- License: **CC-BY-NC-4.0** (`license: cc-by-nc-4.0`, HF API, accessed 2026-10-06), same non-commercial
  restriction as the other Aya releases (CC BY-NC 4.0 §2(a)(1) quote above). Gated repo.
- Params: **3.35B** — paper abstract: *"all with just 3.35B parameters"*; docs: *"a compact
  3.35B-parameter multilingual model supporting 70 languages"*.
- Context length: **8k** — Cohere docs table: `tiny-aya-global | … | Context Length 8k | Maximum Output
  Tokens 8k`, same for `tiny-aya-earth`, `tiny-aya-fire`, `tiny-aya-water`.
- Bahasa Indonesia evidence: **Indonesia is directly in scope, with a documented data share.**
  - Coverage: HF `language:` tags include **`id`** (and `jv` Javanese, `ms`, `tl`, `vi`) among 70
    languages; paper Table 1 lists Asia Pacific = *"Tagalog, Malay, **Indonesian**, Vietnamese,
    Javanese (Javanese), Khmer, Thai, Lao, Chinese (Traditional and Simplified Han), Burmese,
    Japanese, Korean."*
  - Data share: paper Table 12, verbatim row: *"**Indonesian 1.6 0.1 2.0 0.1**"* (% of tokens across the
    "All Regions" / "South Asia" / "Europe+WA+AP" / "Europe+WA+Af" data mixes) — i.e. **Indonesian is
    1.6% of the globally balanced mix**.
  - Benchmarks: suite = *"Global MMLU (42 langs), INCLUDE (44), Global PIQA (116), Flores, WMT24++,
    GlobalMGSM, mDolly, mArenaHard, NormAd (54), BLEnD, MultiJail, XSTest"* (paper Table 3). NormAd is
    evaluated per country with the country's official language, and the mapping table includes
    *"Indonesia | ID | Indonesian | Asia Pacific"*. **The extracted text gives per-region NormAd
    accuracy, not a per-language Indonesian cell → Indonesian-specific score [UNVERIFIED].**
  - No IndoMMLU and no SeaBench appear in the Tiny Aya paper (searched full text, 0 hits).
- Structured output: **no function-calling / JSON claim found** in the Cohere docs model table or the
  paper abstract/extracted text → **not documented (absent)**.
- Determinism caveats: dense 3.35B; no Tiny-Aya-specific primary doc on determinism → **[UNVERIFIED]**.
- Free-host availability: `tiny-aya-global/earth/fire/water` are **"Live"** on the Cohere API
  (docs.cohere.com/v2/docs/models, accessed 2026-10-06). Cohere trial/evaluation keys are described as
  *"free but limited in usage"* with *"1,000 API calls a month"*
  (<https://docs.cohere.com/docs/rate-limits>) — but the rate-limit table does **not** list Tiny Aya, so
  free-trial coverage for Tiny Aya is **[UNVERIFIED]**. Open-weights are also on HF under CC-BY-NC-4.0
  (non-commercial). No OpenRouter entry for Tiny Aya.
- Notes: this is the newest Aya generation as of 2026-10-06, released after Aya Expanse/Aya Vision, and
  the only Aya family with a published per-language **data proportion** for Indonesian.

---

## Not verified / gaps

1. **Indonesian-only benchmark numbers are missing almost everywhere.**
   - Mistral: **no Mistral model card publishes an Indonesian (or any per-language) score.** Small 3.1's
     multilingual table is region-aggregated (Average 71.18%). Ministral 3 / Large 3 / Small 4 publish
     only "Multilingual MMLU" aggregates (0.652/0.706/0.742 for Ministral 3 3B/8B/14B base).
   - Aya: the mArenaHard/Global-MMLU figures are **averaged across all 23 languages**; the per-language
     charts exist only as PNGs (`winrates_by_lang.png` on the gated card; paper Figure 4 covers
     "selected 8 diverse languages" without naming them). **Specific Indonesian values [UNVERIFIED].**
   - **No IndoMMLU and no SeaBench number was found for any Mistral or Cohere Aya model** (searched the
     Aya Expanse paper, the Aya 23 paper, and the Tiny Aya paper full text — 0 hits for both strings).
2. **Gated cards.** `CohereLabs/aya-expanse-32b`, `aya-expanse-8b`, `aya-vision-32b`, `aya-23-35B`,
   `aya-23-8B`, `tiny-aya-global` all returned **HTTP 401** on `/raw/main/README.md` (2026-10-06).
   Aya Expanse card sentences above come from a **community mirror** (`jebish7/aya-expanse-8b`); mirror
   text is secondary and should be re-confirmed with a HF token. Aya 23 and Tiny Aya card bodies are
   **entirely [UNVERIFIED]** — only HF API metadata and the papers were readable.
3. **Aya 23 context length** — not verified (card gated). The 8192 figure in the paper is a *training*
   context, not a serving limit.
4. **Aya 23 status at Cohere** — it is absent from the current model list, but **no deprecation/retirement
   entry naming `c4ai-aya-23-*` was found** on <https://docs.cohere.com/docs/deprecations>. Whether it is
   withdrawn or simply undocumented is **[UNVERIFIED]**.
5. **MoE routing nondeterminism** (Mistral Large 3, Mistral Small 4): **no primary provider doc found**
   stating expert-routing nondeterminism. Only dense-model determinism guidance (Mistral sampling note;
   vLLM "does not guarantee reproducibility") is documented. **[UNVERIFIED]**
6. **Reasoning-mode nondeterminism** (Ministral 3 Reasoning checkpoints, Mistral Small 4
   `reasoning_effort`): **[UNVERIFIED]** — no provider doc found.
7. **Batch/quantisation nondeterminism** for the Aya models: **[UNVERIFIED]** — no Cohere/Labs doc found.
8. **Free hosting.**
   - **OpenRouter: no Mistral and no Aya model is free today** (verified by pulling
     <https://openrouter.ai/api/v1/models> on 2026-10-06 and filtering for zero-priced entries: only
     NVIDIA Nemotron and `cohere/north-mini-code:free` — North, not Aya).
   - **Together AI**: the pricing page (accessed 2026-10-06) lists **no Mistral and no Cohere/Aya chat
     model** in its serverless tables — only branding assets contain "Mistral". Whether any Mistral model
     is offered (paid) on Together was **not** confirmable from that page → **[UNVERIFIED]**.
   - **NVIDIA NIM / build.nvidia.com**: free API credits for NVIDIA-hosted NIM endpoints are documented
     (*"anyone can sign up to the NVIDIA API Catalog for free credits to access models through
     NVIDIA-hosted NIM endpoints"*, <https://developer.nvidia.com/blog/access-to-nvidia-nim-now-available-free-to-developer-program-members>,
     accessed 2026-10-06), and the model list shows "Free Endpoint 38". **But the catalog page is
     JS-rendered and I could not verify that any *Mistral* or *Aya* model sits behind a Free Endpoint
     today** → **[UNVERIFIED]** for these specific models. The 2024 blog named only Mistral 7B Instruct,
     not Nemo/Small/Ministral/Aya.
   - **Azure AI Foundry**: the Mistral pricing page lists only `mistral-document-ai-*`, Mistral OCR, and
     "Mistral Medium 3.5 Global" under serverless deployment; **no Mistral Small / Ministral / Nemo row
     appears**, and **no Aya/Cohere model row** (only the generic statement that the catalog includes
     Mistral AI and Cohere). Azure's "**Get free cloud services and a $200 credit to explore Azure for
     30 days**" and per-model "Prices are estimates only" text are on the same page — so free *credit*
     exists, but free access to these specific models is **[UNVERIFIED]**.
   - **Perplexity**: no evidence found that Perplexity serves Mistral Nemo/Small/Ministral or any Aya
     model; **no pricing/model page confirming or denying it was retrieved** → **[UNVERIFIED]**.
   - **Hugging Face Inference Providers**: only `Mistral-Small-3.1-24B-Instruct-2503` (via `featherless-ai`)
     and `CohereLabs/aya-expanse-32b` (via `cohere`) have live provider mappings among the models
     checked; the rest returned `{}`/`null`. Free amount is **$0.10/month credits for free users**
     (a credit, not a free model).
   - **Mistral's own free tier**: the FAQ confirms a Free plan with Studio access and a "$10 /mo in API
     credits" bullet, but **no page confirms which models the free tier's API credits can call**, and
     the retired help-centre "Experiment plan" article now 404s → **[UNVERIFIED]** for model-level
     free-tier eligibility.
   - **Cohere trial keys**: documented as *"free but limited"*, *"1,000 API calls a month"*, but the
     per-model table omits **every** Aya model → free-trial coverage of Aya is **[UNVERIFIED]**.
9. **Mistral Large 3 benchmark text** — the card publishes its benchmarks only as three PNGs; no
   multilingual/Indonesian figure extractable.
10. **Mistral Small 4 / Large 3 / Ministral 3 language metadata vs prose disagree** on Indonesian:
    HF `language:` tags include `id` for Small 4 only, while the prose "Multilingual" bullets for
    Large 3, Ministral 3 and Small 4 omit Indonesian. Which is authoritative is not stated by Mistral.
11. A direct attempt to open the official Cohere Labs Aya Expanse card and the Mistral "Experiment plan"
    help article today returned **401** and **404** respectively; archived copies via the Wayback
    availability API returned **429 Too Many Requests**, so no archive snapshot was obtained.
