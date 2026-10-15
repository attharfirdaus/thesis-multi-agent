/**
 * Runnable check for the reading-pane slicer (FR-10) and the review-flag wording (PRD §9).
 *
 * `node --experimental-strip-types scripts/check-evidence.ts` runs it; there is no test runner in the
 * frontend, and the slicer is the one piece of client logic where an off-by-one silently corrupts the
 * sense of a quote.
 */

import assert from "node:assert/strict";

import type { Evidence, Score } from "../lib/api.ts";
import { buildSegments, combinedDocument } from "../lib/evidence.ts";
import { flagSentence, scoreLevel, warningSentence } from "../lib/labels.ts";

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

// 9. every known flag reads as a sentence, and an unknown code never leaks as itself
for (const code of [
  "cognitive_agent_failed",
  "metacognitive_agent_failed",
  "synthesis_agent_failed",
  "synthesis_retried",
  "needs_review",
]) {
  const sentence = flagSentence(code);
  assert.notEqual(sentence, code);
  assert.equal(sentence.endsWith("."), true);
}
const unknown = flagSentence("some_flag_from_the_future");
assert.notEqual(unknown, "some_flag_from_the_future");
assert.equal(unknown.includes("_"), false);

// 10. the presence words never reach the lecturer, and the rubric's own words pass through
assert.equal(scoreLevel("absent"), "Tidak ditemukan");
assert.equal(scoreLevel("present"), "Ada");
assert.equal(scoreLevel("kuat"), "kuat");
assert.equal(scoreLevel("C4 - Menganalisis"), "C4 - Menganalisis");
assert.equal(scoreLevel("kuat", ["lemah", "sedang", "kuat"]), "kuat");
assert.equal(scoreLevel("absent", ["lemah", "sedang", "kuat"]), "Tidak ditemukan");
assert.equal(scoreLevel("no_strength", ["lemah", "sedang", "kuat"]), "Tidak ditemukan");
assert.equal(scoreLevel("C4 - Menganalisis", ["C1", "C4 - Menganalisis"]), "C4 - Menganalisis");

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

console.log("check-evidence: 11 assertion groups passed");
