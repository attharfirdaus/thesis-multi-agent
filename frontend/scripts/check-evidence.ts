/**
 * Runnable check for the reading-pane slicer (FR-10), the review-flag wording (PRD §9) and the
 * guarantee that every flag token the backend defines has its own sentence.
 *
 * `node --experimental-strip-types scripts/check-evidence.ts` runs it; there is no test runner in the
 * frontend, and the slicer is the one piece of client logic where an off-by-one silently corrupts the
 * sense of a quote.
 */

import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import type { Evidence, Score } from "../lib/api.ts";
import { buildSegments, combinedDocument } from "../lib/evidence.ts";
import {
  FLAG_FALLBACK,
  FLAG_SENTENCES,
  flagSentences,
  levelLabel,
  scoreLevel,
  STRENGTH_WORDS,
  warningSentence,
  warningSentences,
} from "../lib/labels.ts";

/** The flag tokens live with the agents that write them; the scan reads them rather than a copy. */
const AGENT_SOURCES = fileURLToPath(new URL("../../backend/app/agents/", import.meta.url));
const FLAG_CONSTANT = /^[A-Z_]+ = "([a-z0-9_]+)"$/gm;

const text =
  "Keluaran AI menyebut inflasi sebagai penyebab. Siswa meneliti laporan BPS. " +
  "Siswa meneliti laporan BPS lalu menyimpulkan penyebabnya berbeda.";

const scoreWith = (id: string, start: number, end: number): Score => ({
  id,
  dimension: "metacognitive",
  indicator: "elaborasi",
  level: "Kuat",
  rationale: null,
  evidence: [{ quote: text.slice(start, end), start_offset: start, end_offset: end } as Evidence],
});

// 1. no scores -> the whole text, unhighlighted
const plain = buildSegments(text, []);
assert.equal(plain.length, 1);
assert.equal(plain[0].text, text);
assert.equal(plain[0].scoreIds.length, 0);

// 2. one span -> the highlight sits on the exact offsets, and the slices rebuild the source
const one = buildSegments(text, [scoreWith("a", 40, 68)]);
assert.equal(one.map((s) => s.text).join(""), text);
const highlighted = one.filter((s) => s.scoreIds.length > 0);
assert.equal(highlighted.length, 1);
assert.equal(highlighted[0].text, text.slice(40, 68));
assert.deepEqual(highlighted[0].scoreIds, ["a"]);

// 3. adjacent spans of two scores -> one highlight carrying both
const adjacent = buildSegments(text, [scoreWith("a", 40, 68), scoreWith("b", 68, 90)]);
assert.equal(adjacent.filter((s) => s.scoreIds.length > 0).length, 1);
assert.deepEqual(
  adjacent.find((s) => s.scoreIds.length > 0)?.scoreIds,
  ["a", "b"],
);
assert.equal(adjacent.find((s) => s.scoreIds.length > 0)?.text, text.slice(40, 90));

// 4. overlapping spans -> the union, both scores on it
const overlapping = buildSegments(text, [scoreWith("a", 40, 70), scoreWith("b", 60, 90)]);
const union = overlapping.find((s) => s.scoreIds.length > 0);
assert.equal(union?.start, 40);
assert.equal(union?.end, 90);
assert.deepEqual(union?.scoreIds, ["a", "b"]);

// 5. a span past the end of the text is dropped without blanking the pane
const stale = buildSegments(text, [scoreWith("a", 10, text.length + 50)]);
assert.equal(stale.every((s) => s.scoreIds.length === 0), true);
assert.equal(stale.map((s) => s.text).join(""), text);

// 6. a repeated quote highlights the position the offsets point at, not the first occurrence
const repeatStart = text.lastIndexOf("Siswa meneliti laporan BPS");
assert.equal(repeatStart > text.indexOf("Siswa meneliti laporan BPS"), true);
const repeated = buildSegments(text, [scoreWith("a", repeatStart, repeatStart + 24)]);
assert.equal(repeated.find((s) => s.scoreIds.length > 0)?.start, repeatStart);

// 7. empty text renders nothing
assert.equal(buildSegments("", [scoreWith("a", 0, 3)]).length, 0);

// 8. the segmentation document matches the API's join, and the default handle lands on the split
const aiSegment = "Keluaran AI menyebut inflasi sebagai penyebab.";
const document = combinedDocument(aiSegment, text);
assert.equal(document, `${aiSegment}\n${text}`);
assert.equal(document.slice(0, aiSegment.length), aiSegment);
assert.equal(document.slice(aiSegment.length), `\n${text}`);
assert.equal(combinedDocument("", text), text);

// 9. every flag token the backend defines has its own sentence, and the map holds no stray code.
//    Membership is what is asserted, not the wording: `needs_review` deliberately reads the same as
//    FLAG_FALLBACK, so comparing sentences would either forbid that or pass a lazy copy of it.
const backendFlags = new Set<string>();
for (const name of readdirSync(AGENT_SOURCES)) {
  if (!name.endsWith(".py")) continue;
  for (const match of readFileSync(join(AGENT_SOURCES, name), "utf8").matchAll(FLAG_CONSTANT)) {
    backendFlags.add(match[1]);
  }
}
assert.notEqual(
  backendFlags.size,
  0,
  `no flag constant found under ${AGENT_SOURCES} - check the path and the pattern`,
);
for (const code of backendFlags) {
  assert.equal(
    Object.hasOwn(FLAG_SENTENCES, code),
    true,
    `the backend defines ${code} and the UI has no sentence for it`,
  );
  assert.notEqual(flagSentences([code])[0], code, `${code} must not reach the lecturer`);
}
for (const code of Object.keys(FLAG_SENTENCES)) {
  assert.equal(
    backendFlags.has(code),
    true,
    `the UI maps ${code}, which the backend does not define`,
  );
}

// 9b. two flags that resolve to the same text are shown once, and an unknown code falls back
assert.equal(flagSentences(["needs_review", "evidence_unverified", "needs_review"]).length, 2);
assert.equal(flagSentences(["evidence_unverified"])[0], FLAG_SENTENCES.evidence_unverified);
assert.equal(flagSentences(["some_flag_from_the_future"])[0], FLAG_FALLBACK);
assert.equal(FLAG_FALLBACK.includes("_"), false);
assert.equal(flagSentences(["unknown_a", "unknown_b"]).length, 1);

// 10. the presence words never reach the lecturer, the rubric's own words pass through, and the
//     metacognitive strength words stay themselves even though rubric.levels does not list them
assert.equal(scoreLevel("absent"), "Tidak ditemukan");
assert.equal(scoreLevel("present"), "Ada");
assert.equal(scoreLevel("kuat"), "kuat");
assert.equal(scoreLevel("C4 - Menganalisis"), "C4 - Menganalisis");
assert.equal(scoreLevel("kuat", ["lemah", "sedang", "kuat"]), "kuat");
assert.equal(scoreLevel("absent", ["lemah", "sedang", "kuat"]), "Tidak ditemukan");
assert.equal(scoreLevel("no_strength", ["lemah", "sedang", "kuat"]), "Tidak ditemukan");
assert.equal(scoreLevel("C4 - Menganalisis", ["C1", "C4 - Menganalisis"]), "C4 - Menganalisis");
// The real rubric's `levels` is the cognitive scale alone (["C1".."C6"]), so a strength word must survive
// it: the strict fallback would otherwise turn every real metacognitive score into "Tidak ditemukan".
assert.equal(scoreLevel("kuat", ["C1", "C2", "C3", "C4", "C5", "C6"]), "kuat");

// The words themselves come from the backend, so they are read rather than remembered.
const MODELS_SOURCE = fileURLToPath(new URL("../../backend/app/agents/models.py", import.meta.url));
const strengthMatch = /^Strength = Literal\[([^\]]+)\]$/m.exec(readFileSync(MODELS_SOURCE, "utf8"));
assert.notEqual(strengthMatch, null, `no Strength literal found in ${MODELS_SOURCE}`);
const backendStrengths = (strengthMatch?.[1] ?? "")
  .split(",")
  .map((part) => part.trim().replace(/^"|"$/g, ""))
  .filter(Boolean);
assert.deepEqual([...backendStrengths].sort(), [...STRENGTH_WORDS].sort());
for (const word of backendStrengths) {
  assert.equal(scoreLevel(word, ["C1", "C4"]), word, `${word} must reach the lecturer as itself`);
}

// 10b. the rubric's name sits beside the code, and a code the rubric does not name stands alone
assert.equal(levelLabel("C4", { C1: "Remember", C4: "Analyze", C6: "Create" }), "C4 Analyze");
assert.equal(levelLabel("C1", { C4: "Analyze" }), "C1");
assert.equal(levelLabel("C4", {}), "C4");
assert.equal(levelLabel("kuat", { C4: "Analyze" }), "kuat");
assert.equal(levelLabel(scoreLevel("absent"), { C4: "Analyze" }), "Tidak ditemukan");

// 11. a stored caveat reads as a sentence, including the page-level one, and never as the raw text
assert.equal(
  warningSentence("page 3: no extractable text or tables (image-only page)"),
  "Halaman 3 tidak berisi teks atau tabel yang dapat dibaca.",
);
assert.equal(
  warningSentence("No extractable text was found in this file."),
  "Tidak ada teks yang dapat dibaca pada berkas ini.",
);
assert.equal(
  warningSentence("no AI segment was detected; the student's analysis covers the whole document"),
  "Bagian keluaran AI tidak terdeteksi, sehingga seluruh dokumen dibaca sebagai analisis mahasiswa.",
);
const unknownWarning = warningSentence("Some unexpected extractor note.");
assert.notEqual(unknownWarning, "Some unexpected extractor note.");
assert.equal(unknownWarning.includes("extractor"), false);

// 11b. the two stored phrasings of one caveat render as one sentence, and two facts stay two
assert.deepEqual(
  warningSentences([
    "no AI segment was detected; the student's analysis covers the whole document",
    "No AI-output segment was detected; the whole document was treated as the student's analysis.",
    "no AI segment was detected; the student's analysis covers the whole document",
  ]),
  ["Bagian keluaran AI tidak terdeteksi, sehingga seluruh dokumen dibaca sebagai analisis mahasiswa."],
);
assert.equal(warningSentences([]).length, 0);
assert.equal(
  warningSentences([
    "page 2: no extractable text or tables (image-only page)",
    "page 3: no extractable text or tables (image-only page)",
    "page 2: no extractable text or tables (image-only page)",
  ]).length,
  2,
);

console.log(`check-evidence: all assertion groups passed (${backendFlags.size} backend flag tokens)`);
