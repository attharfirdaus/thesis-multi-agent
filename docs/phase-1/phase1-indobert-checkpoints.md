# Phase 1 — IndoBERT / Indonesian encoder checkpoints for the cognitive (Bloom) classifier (PRD §7a)

Access date for all claims: **2026-10-06**. All checks done live via the Hugging Face API/models and Zenodo. No recommendations; options + evidence only. Anything not confirmable on a live page is marked `[UNVERIFIED]`.

---

## 1. Does a fine-tuned Indonesian Bloom / cognitive-level classifier already exist?

**Verdict: Yes — several community checkpoints exist on the HF Hub, but none is a documented, license-clear, benchmarked artefact.** The strongest *published* research (JISEBI) reports high accuracy but releases only the dataset, **not the weights**. So a ready-made checkpoint technically exists, but with material caveats (undocumented training data, no card/no license in some cases, low reported accuracy 0.49–0.58 for the documented ones).

### Hub search queries run (2026-10-06)
API: `https://huggingface.co/api/models?search=<q>&limit=…` (and `?full=true`), plus `author=` and `filter=` variants.

- `bloom`, `blooms`, `bloom+classifier`, `bloom+taxonomy`, `taksonomi`, `taksonomi+bloom`, `cognitive+level`, `cognitive+level+indonesia`, `cognitive+domain`, `bloom+indonesian`, `indobert+bloom`, `bloom+indobert`, `taksonomi+bloom+indobert`, `bloom+classification+indonesia`, `taxonomy+indonesian`, `HOTS`, `LOTS`, `berpikir+tingkat+tinggi`
- `indobert`, `nusabert`, `indonesian` (+ authors `LazarusNLP`, `w11wo`, `cahya`, `indolem`, `indobenchmark`)
- Datasets API: `bloom`, `bloom+taxonomy`, `taksonomi`, `blooms`, `cognitive`, `cognitive+level`, `learning+objectives`, `hots`; author `SEACrowd`.

Note: the query `bloom` returns almost entirely the bigscience **BLOOM LLM** family, not Bloom's taxonomy. Taxonomy hits come from `blooms`, `bloom+taxonomy`, and the `indobert` axis.

### 1a. Indonesian / IndoBERT-based Bloom checkpoints found

| Repo id | Base model / tokenizer evidence | Labels (from `config.json`) | Reported metric | License | Hub last-modified | Card/data? |
|---|---|---|---|---|---|---|
| `hawalurahman/indobert-base-uncased-bloom-base` | `base_model: indolem/indobert-base-uncased` (card); vocab 31923, 768/12 | 6: `C1 - Mengingat … C6 - Menciptakan` | Accuracy **0.575** (loss 1.0931) | MIT | 2026-06-26 | README auto-generated; **dataset = "None"** |
| `hawalurahman/indobert-base-uncased-bloom-prediction` | `base_model: indolem/indobert-base-uncased`; vocab 31923, 768/12 | 7: `-`, `C1 - Mengingat … C6 - Menciptakan` | Accuracy **0.5564** (loss 1.1765) | MIT | 2026-04-30 | README auto-generated; dataset "None" |
| `hawalurahman/indobert-base-uncased-bloom-difficulty-prediction` | `base_model: indolem/indobert-base-uncased`; vocab 31923, 768/12 | 16: level × difficulty (`C1 - Mengingat_Mudah/Sedang/Sulit`, … `C6 - Menciptakan_Sedang`) | Accuracy **0.4938** (loss 1.7238) | MIT | 2026-06-12 | README auto-generated; dataset "None" |
| `reheri/reheri-indobert-bloom-finetuned` | config: 768/12, **vocab 50000** → indobenchmark IndoBERT family; `_name_or_path` null | 6 generic `LABEL_0…LABEL_5` | none listed | **none declared** | 2025-12-12 | **No README** (raw README 404) |
| `FadQ/Skripsi1-IndoberBase-Bloom-Classifier` | config: hidden 1024 / 24 layers (Large dims), **vocab_size 30522**; weights confirm `bert.pooler.dense.weight [1024,1024]`, `classifier.weight [14,1024]` | **14 outputs** (`id2label` LABEL_0…LABEL_13) while `_num_labels = 5` (inconsistent) | none | **none declared** | 2026-01-02 | **No README/license**; name suggests IndoBERT but config is self-inconsistent |

Decisive quotes (verbatim, card/API):
- `hawalurahman/indobert-base-uncased-bloom-base` card: *"This model is a fine-tuned version of [indolem/indobert-base-uncased] on the None dataset."* and *"Accuracy: 0.575"*.
- `FadQ/…/config.json`: `"_num_labels": 5` but `classifier.weight [14, 1024]`.
- `reheri/reheri-indobert-bloom-finetuned`: no README on `main` (HTTP 404).

Caveats: none of the above documents its training corpus/labeling protocol. `hawalurahman`'s only public dataset is `hawalurahman/log-annotator-aqg-id` (Apache-2.0), which appears unrelated to the Bloom labels. **None is a drop-in, provenance-clear classifier.**

### 1b. Non-Indonesian Bloom taxonomy classifiers found (for completeness — not usable for Bahasa Indonesia)
`cip29/bert-blooms-taxonomy-classifier` (bert-base-uncased, Apache-2.0), `cip29/blooms_bert`, `phoenix28/bloom-taxonomy-classifier` (bert-base-uncased, Apache-2.0), `Jrine/blooms` (bert-base-uncased, Apache-2.0, `language: en`), `Adi2021/bloomstaxonomy` (`_name_or_path: bert-base-uncased`, 6 labels), `Malithi200/bloom-taxonomy-classifier`, `hyperxlogic/blooms-taxonomy-classifier` (distilbert), `guirrock/gemma-Finetune-bloom-taxonomy`, `itsskofficial/falcon-7b-blooms-taxonomy` (decoder-only LLM, not an encoder head). None targets Indonesian; none documents training data (several 404 the README).

### 1c. Published Indonesian Bloom-classifier research (weights NOT released)

| Paper | Base | Data | Reported metrics | Weights released? |
|---|---|---|---|---|
| Baharuddin & Naufal, *"Fine-Tuning IndoBERT for Indonesian Exam Question Classification Based on Bloom's Taxonomy"*, JISEBI 9(2):253-263, 2023. DOI 10.20473/jisebi.9.2.253-263 | IndoBERT (HuggingFace BERT-base config) | 449 Indonesian elementary-school **multiple-choice exam questions**; 4 classes C1–C4; 60/40 split | Accuracy 97%, F1 97%, Precision 97%, Recall 97% (abstract) | **No.** "Data Availability" names only the dataset (Zenodo). No model/GitHub/HF link in the paper. |
| *"Optimizing IndoBERT for Revised Bloom's Taxonomy Question classification"*, JISEBI (article 65795) | IndoBERT (+CNN/LSTM) | not fetched (page JS/502) | snippet: *"IndoBERT-LSTM outperformed IndoBERT-CNN. The optimal hyperparameter configuration, batch size of 64…"* | `[UNVERIFIED]` — article download returned HTTP 502 on 2026-10-06 |

Note: these classify **exam questions** (multiple-choice), not student free-text analysis. Relevant as prior art / labeling protocol, not as a student-answer model.

---

## 2. Candidate BASE checkpoints (encoder-only, for FR-07's classifier head)

Dimensionality from each repo's `config.json` (fetched 2026-10-06); "params" quoted from the model card where stated, else config dims given with `[est.]`.

| Repo id | License | Params | Pretraining corpus (source of the statement) | Config (hidden/layers/heads/intermediate/max_pos/vocab) | Hub last-modified |
|---|---|---|---|---|---|
| `indobenchmark/indobert-base-p1` | MIT | **124.5M** (card table) | **Indo4B (23.43 GB of text)** — card table; card front-matter `datasets: Indo4B`; paper arXiv:2009.05387 | 768 / 12 / 12 / 3072 / 512 / `vocab_size` field 50000 | **2021-05-19** |
| `indobenchmark/indobert-base-p2` | MIT | 124.5M (card) | Indo4B (card table) | 768 / 12 / 12 / 3072 / 512 / 50000 | 2021-05-19 |
| `indobenchmark/indobert-large-p2` | MIT | **335.2M** (card table) | **Indo4B (23.43 GB of text)** — card table | 1024 / 24 / 16 / 4096 / 512 / 30522 | **2021-05-19** |
| `indolem/indobert-base-uncased` | MIT | `[est.]` ~110M (BERT-base dims; card does not state a count) | **220M words**: Indonesian Wikipedia 74M + news (Kompas, Tempo, Liputan6) 55M + Indonesian Web Corpus 90M — card §About; arXiv:2011.00677 | 768 / 12 / 12 / 3072 / 512 / 31923 | **2023-08-09** |
| `indolem/indobertweet-base-uncased` | Apache-2.0 | `[est.]` ~110M | **409M Indonesian tweet tokens**, crawled Dec 2019–Dec 2020, 60 keywords; data not released (Twitter policy) — card §3 | BERT-base dims (not re-checked) | 2021-09-18 |
| `LazarusNLP/NusaBERT-base` | Apache-2.0 | `[est.]` ~110M | Continued pretraining on `sabilmakbar/indo_wiki` + `acul3/KoPI-NLLB` + `uonlp/CulturaX`, **~16B tokens**; fine-tuned from `indobenchmark/indobert-base-p1` — card | 768 / 12 / 12 / 3072 / 512 / 32032 | **2024-03-05** |
| `LazarusNLP/NusaBERT-large` | Apache-2.0 | `[est.]` ~335M | Same three corpora — card | 1024 / 24 / 16 / 4096 / 512 / 32032 | **2024-03-05** |
| `indobenchmark/indobert-lite-base-p2` | MIT | **11.7M** (card) | Indo4B (card table) | ALBERT lite (`model_type: albert`) | 2020-12-11 |
| `cahya/bert-base-indonesian-1.5G` | MIT | `[est.]` ~110M | `wikipedia` + `id_newspapers_2018` (card tags) | BERT-base dims | 2021-05-19 |

Observed config/tokenizer inconsistency worth flagging: `indobenchmark/indobert-base-p1` `config.json` reports `vocab_size: 50000`, but the shipped `vocab.txt` has **30,522 tokens** (contains Indonesian subwords such as `yang`, `dan`, `##kan`, `##nya`) and differs from `bert-base-uncased`'s vocab (md5 `9767…` vs `6480…`). The large-p1/-p2 configs report `30522`, matching the file. `[UNVERIFIED]` which (`50000` vs `30522`) is authoritative for the embedding matrix — verify before use.

Dates/last-modified for base repos come from `https://huggingface.co/api/models/<id>`.

---

## 3. Encoder-only vs otherwise (FR-07 suitability)

- **Encoder-only (usable as classifier-head base):** all of `indobenchmark/indobert-*` (`BertModel` / `AlbertModel`), `indolem/indobert-base-uncased` & `indobertweet-base-uncased` (`BertForMaskedLM`), `LazarusNLP/NusaBERT-base` & `NusaBERT-large` (`BertForMaskedLM`), `cahya/bert-base-indonesian-1.5G`. BERT/AlBERT = bidirectional encoders.
- **Not encoder-only:** `itsskofficial/falcon-7b-blooms-taxonomy*`, `guirrock/gemma-Finetune-bloom-taxonomy` — decoder-only causal LLMs, not a `ForSequenceClassification` base.
- All five Indonesian Bloom classifier checkpoints in §1a are `BertForSequenceClassification` (encoder + linear head): `reheri` vocab 50000 (indobenchmark family) and `FadQ`/others shown by config/weights.

---

## 4. Labelled Indonesian dataset with Bloom levels?

**Exam questions (found):** `Baharuddin, F. (2023). "Elementary School Indonesian Exam Questions with Bloom's Taxonomy Dataset", Zenodo, DOI 10.5281/zenodo.8331563` (access 2026-10-06). Verified by downloading `dataset (1).csv` (35.5 kB, 449 rows): columns `pertanyaan, Taksonomi`; class counts `C4 - Analisis 123, C3 - Aplikasi 116, C1 - Pengetahuan 110, C2 - Pemahaman 100`. Labels were manually set and validated by two Indonesian teachers (JISEBI 2023, §Data Labeling). **This is multiple-choice exam questions, 4 of 6 Bloom classes (no C5/C6), NOT student free-text analysis.**

**Student analysis/essay text labelled with Bloom levels: NONE FOUND.** No HF dataset, Zenodo, or Mendeley dataset of *student-written* Indonesian analysis text labelled by Bloom/cognitive level was located. The labelling pass remains the human's own work and must **not** be assumed.

Other non-applicable Bloom datasets seen: `jsano/blooms_taxonomy` (HF, `<1K`, mixed-language, no card), `itsskofficial/falcon-7b-blooms-taxonomy-data` (CC0, English), `harshvivek14/Blooms-Followup-Questions` (`language: en`), `marzieh-alidadi/Research-BloomTaxonomy-LLM-Persian-Questions` (`language: fa`), Mendeley "Data set for predicting student performance using bloom taxonomy" (2022 — not Indonesian student analysis text). SEACrowd's `bloom_*` datasets are the bigscience BLOOM LLM data, not taxonomy.

---

## Not verified / gaps

- JISEBI second paper (article 65795, *"Optimizing IndoBERT for Revised Bloom's Taxonomy…"*): page is JS-only and the PDF/download endpoint returned **HTTP 502** on 2026-10-06. Metrics/dataset/weight-release `[UNVERIFIED]`; only a search-result snippet was read.
- JISEBI first paper PDF also 502 on the publisher domain; text was read from the author-deposit mirror `repository.ubaya.ac.id/45491/3/…pdf` (same title/authors/DOI).
- `FadQ/Skripsi1-IndoberBase-Bloom-Classifier` label pickle is a Git-LFS pointer (not fetchable as plain pickle), so the 14 class names are `[UNVERIFIED]`; only config/weights shapes were read.
- `hawalurahman` Bloom checkpoints: underlying labeled dataset is not published (card says "None"); class balance, train/test size, and labeling protocol `[UNVERIFIED]`.
- `reheri/reheri-indobert-bloom-finetuned` and `FadQ/…`: no license and no model card → redistribution/licensing terms `[UNVERIFIED]`.
- Parameter counts for `indolem/*`, `NusaBERT-*`, `cahya/*` are `[est.]` from config dims; only the indobenchmark card states explicit counts.
- No attempt was made to contact authors or inspect private/unlisted repos; hub searches cover public repos indexed by the HF API only.
