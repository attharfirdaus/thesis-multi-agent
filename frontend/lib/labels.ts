/**
 * Values that the backend stores as machine vocabulary rather than as prose. PRD §9 keeps that
 * vocabulary out of the lecturer's screen, so every one of them is translated here before it can be
 * rendered. An unknown value must still read as a sentence: a new flag or a new stored word may never
 * leak a raw identifier into the interface.
 */

export const FLAG_SENTENCES: Record<string, string> = {
  cognitive_agent_failed: "Penilaian tingkat kognitif gagal — coba jalankan ulang.",
  metacognitive_agent_failed: "Penilaian indikator metakognitif gagal — coba jalankan ulang.",
  single_agent_failed: "Penilaian baseline gagal — coba jalankan ulang.",
  synthesis_agent_failed: "Penjelasan dan umpan balik belum bisa dibuat.",
  synthesis_retried: "Penjelasan disusun ulang karena kutipan tidak ditemukan.",
  synthesis_inconsistency: "Alasan penilaian tidak sesuai dengan kutipan buktinya.",
  evidence_unverified: "Kutipan bukti tidak ditemukan pada tulisan mahasiswa.",
  needs_review: "Perlu ditinjau dosen.",
};

/** The generic sentence an unmapped code falls back to. */
export const FLAG_FALLBACK = "Perlu ditinjau dosen.";

/**
 * One statement per distinct meaning: two flags may legitimately resolve to the same sentence (that is
 * what the fallback does), and the lecturer should read each statement once.
 */
export function flagSentences(codes: string[]): string[] {
  return [...new Set(codes.map((code) => FLAG_SENTENCES[code] ?? FLAG_FALLBACK))];
}

/**
 * How a run grades. The database constrains `runs.mode` to these two values (migration 0001), so the
 * fallback cannot fire in practice; it is there so a future mode reads as itself rather than vanishing.
 */
const MODE_LABELS: Record<string, string> = {
  multi_agent: "Multi-agen",
  single_agent: "Baseline single-agen",
};

export const modeLabel = (mode: string): string => MODE_LABELS[mode] ?? mode;

/**
 * The pseudonym stays the system identifier everywhere it already appears; the real name (captured
 * at upload, stored outside the database — DECISIONS.md 2026-10-16) is shown beside it when ingest
 * found one. `null` means no name was captured, not an error, so it adds nothing rather than a
 * placeholder.
 */
export const submissionLabel = (pseudonym: string, realName?: string | null): string =>
  realName ? `${realName} (${pseudonym})` : pseudonym;

/**
 * A metacognitive indicator is nominal (Bab II.2.4): the backend stores `present` or `absent`
 * (`app/agents/persist.py`). Runs scored before 2026-11-03 stored a strength word instead (lemah, sedang,
 * kuat); those read as present. When the rubric's levels are at hand anything outside them is machine
 * vocabulary, not a level.
 */
const PRESENCE_LEVELS: Record<string, string> = {
  absent: "Tidak ditemukan",
  present: "Ada",
  lemah: "Ada",
  sedang: "Ada",
  kuat: "Ada",
};

/** The two values a metacognitive override may take, with their labels. */
export const PRESENCE_OPTIONS = ["present", "absent"];

export function scoreLevel(level: string, rubricLevels: string[] = []): string {
  if (PRESENCE_LEVELS[level] !== undefined) return PRESENCE_LEVELS[level];
  if (rubricLevels.length === 0 || rubricLevels.includes(level)) return level;
  return "Tidak ditemukan";
}

/** Tabel III.4: why a submission sits outside the evaluation set. */
export const EXCLUSION_LABELS: Record<string, string> = {
  calibration_source: "Sumber contoh kalibrasi",
  author_own: "Milik penulis sebagai peserta",
  unreadable_or_unsegmentable: "Tidak dapat dibaca atau dipisahkan",
};

/**
 * The rubric's own name for a level, beside its code (`C4 Analyze`). The name comes from the rubric row
 * the run froze (PRD §13), so a code the rubric does not name is shown alone: inventing a word here would
 * put a scale in the app that the rubric does not carry.
 */
export function levelLabel(level: string, levelNames: Record<string, string>): string {
  const name = levelNames[level];
  return name ? `${level} ${name}` : level;
}

/**
 * KF-07's level spread, `{rendah: 1, menengah: 2, tinggi: 0}`, as one readable line. The group names are
 * the rubric's own (Bab III.6), so they are shown as stored, capitalised.
 */
export function spreadLabel(distribution?: Record<string, number> | null): string {
  if (!distribution || Object.keys(distribution).length === 0) return "—";
  // jsonb does not keep key order, so the seeded groups are put back in theirs.
  const rank = (group: string) => {
    const index = GROUP_ORDER.indexOf(group);
    return index === -1 ? GROUP_ORDER.length : index;
  };
  return Object.entries(distribution)
    .sort(([a], [b]) => rank(a) - rank(b) || a.localeCompare(b, "id"))
    .map(([group, count]) => `${group.charAt(0).toUpperCase()}${group.slice(1)} ${count}`)
    .join(" · ");
}

const GROUP_ORDER = ["rendah", "menengah", "tinggi"];

/** A rubric code as a heading: `orientasi` is stored lower-case, a column title is not. */
export const indicatorLabel = (indicator: string): string =>
  indicator.charAt(0).toUpperCase() + indicator.slice(1);

/** Why one uploaded file was refused, in the lecturer's language (the stored text is English). */
export function importError(error?: string | null): string {
  if (!error) return "Berkas ini gagal dibaca.";
  if (error.startsWith("This file duplicates")) return "Berkas ini sama dengan kiriman yang sudah ada, jadi tidak diimpor lagi.";
  if (error.startsWith("No analysis text")) return "Tidak ada teks analisis yang dapat dibaca pada berkas ini.";
  if (error.includes("unsupported file type")) return "Jenis berkas tidak didukung. Gunakan PDF, DOCX, TXT, atau ZIP.";
  if (error.includes("larger than")) return "Berkas terlalu besar (maksimum 20 MB).";
  return "Berkas ini gagal dibaca.";
}

/** What an extraction caveat says, in the lecturer's language (the stored text is English). */
const WARNING_SENTENCES: Record<string, string> = {
  "no AI segment was detected; the student's analysis covers the whole document":
    "Bagian keluaran AI tidak terdeteksi, sehingga seluruh dokumen dibaca sebagai analisis mahasiswa.",
  "No AI-output segment was detected; the whole document was treated as the student's analysis.":
    "Bagian keluaran AI tidak terdeteksi, sehingga seluruh dokumen dibaca sebagai analisis mahasiswa.",
  "No extractable text was found in this file.":
    "Tidak ada teks yang dapat dibaca pada berkas ini.",
};

const IMAGE_ONLY_PAGE = /^page (\d+): no extractable text or tables \(image-only page\)$/;

export function warningSentence(warning: string): string {
  const known = WARNING_SENTENCES[warning];
  if (known !== undefined) return known;
  const imageOnly = IMAGE_ONLY_PAGE.exec(warning);
  if (imageOnly !== null) {
    return `Halaman ${imageOnly[1]} tidak berisi teks atau tabel yang dapat dibaca.`;
  }
  return "Berkas diproses dengan catatan yang belum dapat dijelaskan otomatis.";
}

/**
 * One statement per distinct caveat. The backend has stored two phrasings of the same fact (the
 * segmenter's and the ingest router's), so the same sentence could otherwise be read twice in one cell.
 */
export function warningSentences(warnings: string[]): string[] {
  return [...new Set(warnings.map(warningSentence))];
}
