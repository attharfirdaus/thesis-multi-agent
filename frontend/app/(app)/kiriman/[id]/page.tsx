"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { AdminOnly } from "@/components/app-shell";
import { StatusBadge, runStatus, segmentationStatus } from "@/components/status-badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type ExclusionReason, type Score, type SubmissionDetail } from "@/lib/api";
import { buildSegments, combinedDocument } from "@/lib/evidence";
import {
  EXCLUSION_LABELS,
  PRESENCE_OPTIONS,
  flagSentences,
  levelLabel,
  scoreLevel,
  spreadLabel,
  submissionLabel,
} from "@/lib/labels";

const DIMENSION_LABEL: Record<Score["dimension"], string> = {
  cognitive: "Tingkat Kognitif",
  metacognitive: "Indikator Metakognitif",
};

/** The pseudo score id that marks the segment the lecturer has open, so it is highlighted like evidence. */
const OPEN_SEGMENT = "__segment";

/**
 * Text as stored keeps the line breaks of the PDF it came from, in the middle of sentences. For reading,
 * a single break becomes a space unless a blank line or a list item follows; the stored text and every
 * offset into it are untouched, because this runs on a piece that was already sliced.
 */
const unwrap = (piece: string): string => piece.replace(/(?<!\n)\n(?!\n|\s*(?:\d{1,2}[.)]|[-•–*])\s)/g, " ");

const TEXTAREA_CLASS =
  "w-full rounded-lg border border-input bg-transparent px-2.5 py-1.5 text-base leading-7 outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";

export default function KirimanPage() {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<SubmissionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [activeScoreId, setActiveScoreId] = useState<string | null>(null);
  const [draft, setDraft] = useState<{ scoreId: string; level: string; reason: string } | null>(null);
  const [savingReview, setSavingReview] = useState(false);
  const [feedbackDraft, setFeedbackDraft] = useState<string | null>(null);
  const [savingFeedback, setSavingFeedback] = useState(false);
  const [boundary, setBoundary] = useState<number | null>(null);
  const [savingSeg, setSavingSeg] = useState(false);
  const [commentDrafts, setCommentDrafts] = useState<Record<string, string>>({});
  const [savingComment, setSavingComment] = useState(false);
  const [openSegment, setOpenSegment] = useState<{ start: number; end: number } | null>(null);

  // `?run=` names the run to show: the results screen links here with the run it is displaying. Read
  // from the address bar at call time — `load` only ever runs in the browser.
  const load = useCallback(
    () =>
      api.getSubmission(id, new URLSearchParams(window.location.search).get("run")).then(
        (data) => {
          setDetail(data);
          return data;
        },
        (err: unknown) => {
          setError(err instanceof Error ? err.message : "Gagal memuat kiriman.");
          return null;
        },
      ),
    [id],
  );

  useEffect(() => {
    void load();
  }, [load]);

  // The confirmation floats over the page, so it clears itself.
  useEffect(() => {
    if (note === null) return;
    const timer = setTimeout(() => setNote(null), 5000);
    return () => clearTimeout(timer);
  }, [note]);

  const text = detail?.student_analysis_text ?? "";
  const highlighted: Score[] = detail
    ? [
        ...detail.scores,
        ...(openSegment
          ? [
              {
                id: OPEN_SEGMENT,
                dimension: "cognitive" as const,
                indicator: null,
                level: "",
                rationale: null,
                evidence: [{ quote: "", start_offset: openSegment.start, end_offset: openSegment.end }],
              },
            ]
          : []),
      ]
    : [];
  const segments = detail ? buildSegments(text, highlighted) : [];
  const levels = detail?.rubric?.levels ?? [];
  const levelNames = detail?.rubric?.level_names ?? {};
  const storedAi = detail?.ai_output_text ?? "";
  // The offsets sent below index the same string the API splits; see combinedDocument for the rule.
  const combined = combinedDocument(storedAi, text);
  const offset = boundary ?? storedAi.length;
  // The boundary snaps to the start of a line: it always falls between two blocks of the document, and
  // a slider over single characters could not be placed (one pixel was a dozen characters or more).
  const lineStarts = [0];
  for (let i = combined.indexOf("\n"); i !== -1; i = combined.indexOf("\n", i + 1)) lineStarts.push(i + 1);
  const lineIndex = Math.max(lineStarts.findLastIndex((start) => start <= offset), 0);
  const previewAi = combined.slice(0, offset);
  const previewAnalysis = combined.slice(offset);

  /** Offsets are half-open into the analysis text, so the highlight is found by its span, not by its words. */
  function focusEvidence(scoreId: string) {
    setActiveScoreId(scoreId);
    const highlight = document.querySelector(`[data-evidence~="${CSS.escape(scoreId)}"]`);
    highlight?.scrollIntoView({ block: "center", behavior: "smooth" });
  }

  async function onReview(scoreId: string, action: "accept" | "override", level: string, reason: string) {
    setSavingReview(true);
    setError(null);
    setNote(null);
    try {
      await api.reviewScore(
        scoreId,
        action === "accept" ? { action } : { action, new_level: level, reason: reason.trim() },
      );
      setDraft(null);
      setNote("Tinjauan tersimpan. Nilai dari sistem tetap tersimpan sebagai pembanding.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan tinjauan.");
    } finally {
      setSavingReview(false);
    }
  }

  /** Accept every score of the run on screen that has no review yet. Reviewed scores are left alone. */
  async function onAcceptAll() {
    if (!detail?.run) return;
    const confirmed = window.confirm(
      "Terima semua nilai yang belum ditinjau pada kiriman ini, termasuk label setiap segmen? " +
        "Nilai yang sudah Anda terima atau ubah tidak berubah.",
    );
    if (!confirmed) return;
    setSavingReview(true);
    setError(null);
    try {
      const { accepted } = await api.acceptAll(id, detail.run.id);
      await load();
      setNote(`${accepted} nilai diterima.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan tinjauan.");
    } finally {
      setSavingReview(false);
    }
  }

  /** Opening a segment highlights it in the text beside it, like a piece of evidence. */
  function onSegmentToggle(open: boolean, start: number, end: number) {
    if (!open) return;
    setOpenSegment({ start, end });
    setActiveScoreId(OPEN_SEGMENT);
    requestAnimationFrame(() =>
      document.querySelector(`[data-evidence~="${OPEN_SEGMENT}"]`)?.scrollIntoView({ block: "center", behavior: "smooth" }),
    );
  }

  async function onComment(scoreId: string) {
    const body = (commentDrafts[scoreId] ?? "").trim();
    if (!body) return;
    setSavingComment(true);
    setError(null);
    setNote(null);
    try {
      await api.commentScore(scoreId, body);
      setCommentDrafts((drafts) => ({ ...drafts, [scoreId]: "" }));
      setNote("Komentar tersimpan.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan komentar.");
    } finally {
      setSavingComment(false);
    }
  }

  async function onExclusion(reason: ExclusionReason | null) {
    setError(null);
    setNote(null);
    try {
      await api.setExclusion(id, reason);
      setNote(reason ? "Kiriman ditandai di luar data evaluasi." : "Kiriman dikembalikan ke data evaluasi.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan status evaluasi.");
    }
  }

  async function onSaveFeedback(event: React.FormEvent) {
    event.preventDefault();
    if (feedbackDraft === null) return;
    setSavingFeedback(true);
    setError(null);
    setNote(null);
    try {
      // A blank box means "no edit" and stores nothing, so the original text comes back.
      const saved = await api.patchFeedback(id, feedbackDraft);
      setDetail((previous) => (previous ? { ...previous, feedback: saved } : previous));
      setFeedbackDraft(null);
      setNote("Umpan balik tersimpan.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan umpan balik.");
    } finally {
      setSavingFeedback(false);
    }
  }

  async function onSaveSegmentation(event: React.FormEvent) {
    event.preventDefault();
    if (
      detail?.scores.length &&
      !window.confirm(
        "Nilai, tinjauan, dan umpan balik kiriman ini dibuat dari teks dengan batas yang lama, sehingga akan " +
          "dihapus dan kiriman perlu dinilai ulang. Simpan batas baru?",
      )
    ) {
      return;
    }
    setSavingSeg(true);
    setError(null);
    setNote(null);
    try {
      await api.patchSegmentation(id, offset);
      await load();
      setBoundary(null);
      setNote("Batas pemisahan tersimpan.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan pemisahan.");
    } finally {
      setSavingSeg(false);
    }
  }

  /** One score with its review and comment controls. `inSegment` marks a segment label (KF-09), whose
   *  quote is not one of the text-level highlights, so it offers no jump to them. */
  function scoreCard(score: Score, inSegment = false) {
    // An indicator is nominal (Bab II.2.4): the lecturer corrects presence, not a Bloom level.
    const options = score.dimension === "metacognitive" ? PRESENCE_OPTIONS : levels;
    const review = [...(detail?.reviews ?? [])].reverse().find((item) => item.system_score_id === score.id);
    return (
      <Card key={score.id}>
        <CardContent className="flex flex-col gap-3">
          <button
            type="button"
            onClick={() => focusEvidence(score.id)}
            className="flex flex-wrap items-baseline gap-2 rounded text-left focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            <span className="font-medium">{DIMENSION_LABEL[score.dimension]}</span>
            <span className="text-muted-foreground">
              {score.indicator ? `${score.indicator} · ` : ""}
              {levelLabel(scoreLevel(score.level, levels), levelNames)}
            </span>
            {inSegment ? null : (
              <span className="text-sm text-primary underline underline-offset-4">Lihat kutipan</span>
            )}
          </button>

          {score.distribution ? (
            <p className="text-sm text-muted-foreground">
              Sebaran tingkat (jumlah segmen): {spreadLabel(score.distribution)}
            </p>
          ) : null}

          <div>
            <p className="text-sm font-medium">Penjelasan</p>
            <p className="text-muted-foreground">{score.rationale ?? "Tidak ada penjelasan."}</p>
          </div>

          {score.evidence.length > 0 ? (
            <div className="flex flex-col gap-2">
              <p className="text-sm font-medium">Kutipan bukti</p>
              {score.evidence.map((evidence) => (
                <button
                  key={`${evidence.start_offset}-${evidence.end_offset}`}
                  type="button"
                  onClick={() => focusEvidence(score.id)}
                  className="border-l-2 border-amber-500 pl-3 text-left italic focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                  “{evidence.quote}”
                </button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Kutipan bukti tidak ditemukan.</p>
          )}

          {review ? (
            <p className="text-sm text-muted-foreground">
              Tinjauan terakhir:{" "}
              {review.action === "accept"
                ? "diterima"
                : `diubah menjadi ${levelLabel(scoreLevel(review.new_level ?? "", levels), levelNames)}`}
              {review.reason ? ` — ${review.reason}` : ""}
            </p>
          ) : null}

          {draft?.scoreId === score.id ? (
            <form
              onSubmit={(event) => {
                event.preventDefault();
                void onReview(score.id, "override", draft.level, draft.reason);
              }}
              className="flex flex-col gap-3 rounded-lg bg-muted/60 p-3"
            >
              <div className="flex flex-col gap-2">
                <Label htmlFor={`level-${score.id}`}>Tingkat menurut penilaian Anda</Label>
                <select
                  id={`level-${score.id}`}
                  value={draft.level}
                  onChange={(event) => setDraft({ ...draft, level: event.target.value })}
                  className="h-8 w-full rounded-lg border border-input bg-background px-2 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                  {options.map((level) => (
                    <option key={level} value={level}>
                      {levelLabel(scoreLevel(level, levels), levelNames)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor={`reason-${score.id}`}>Alasan singkat</Label>
                <Input
                  id={`reason-${score.id}`}
                  required
                  value={draft.reason}
                  onChange={(event) => setDraft({ ...draft, reason: event.target.value })}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={savingReview || !draft.reason.trim() || !draft.level}>
                  {savingReview ? "Menyimpan…" : "Simpan tinjauan"}
                </Button>
                <Button type="button" variant="ghost" onClick={() => setDraft(null)}>
                  Batal
                </Button>
              </div>
            </form>
          ) : (
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={savingReview} onClick={() => void onReview(score.id, "accept", "", "")}>
                Terima
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={savingReview || options.length === 0}
                onClick={() => setDraft({ scoreId: score.id, level: options[0] ?? "", reason: "" })}
              >
                Ubah
              </Button>
            </div>
          )}

          <div className="flex flex-col gap-2 border-t pt-3">
            {(score.comments ?? []).map((comment) => (
              <p key={comment.id} className="text-sm text-muted-foreground">
                Komentar: {comment.body}
              </p>
            ))}
            <form
              onSubmit={(event) => {
                event.preventDefault();
                void onComment(score.id);
              }}
              className="flex gap-2"
            >
              <Label htmlFor={`comment-${score.id}`} className="sr-only">
                Komentar untuk nilai ini
              </Label>
              <Input
                id={`comment-${score.id}`}
                placeholder="Tulis komentar…"
                value={commentDrafts[score.id] ?? ""}
                onChange={(event) => setCommentDrafts((drafts) => ({ ...drafts, [score.id]: event.target.value }))}
              />
              <Button
                type="submit"
                variant="outline"
                size="sm"
                disabled={savingComment || !(commentDrafts[score.id] ?? "").trim()}
              >
                Kirim
              </Button>
            </form>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      {detail === null ? (
        <p className="text-muted-foreground">Memuat…</p>
      ) : (
        <>
          <header className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex flex-col gap-2">
              <h1 className="text-2xl font-semibold">{submissionLabel(detail.pseudonym, detail.real_name)}</h1>
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge {...segmentationStatus(detail.segmentation_status)} />
                {detail.run ? <StatusBadge {...runStatus(detail.run.status)} /> : null}
                {detail.review_flags?.length ? <StatusBadge tone="amber" label="Perlu Ditinjau" /> : null}
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <Link
                href={`/tugas/${detail.assignment_id}`}
                className="underline underline-offset-4 hover:text-foreground"
              >
                Kembali ke tugas
              </Link>
              <Link
                href={`/tugas/${detail.assignment_id}/hasil`}
                className="underline underline-offset-4 hover:text-foreground"
              >
                Lihat hasil penilaian
              </Link>
            </div>
          </header>

          {error ? (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : null}
          {/* Fixed, so a confirmation is seen from wherever on this long page the action was taken. */}
          {note ? (
            <div
              role="status"
              className="fixed right-4 bottom-4 z-50 max-w-sm rounded-lg bg-foreground px-4 py-3 text-sm text-background shadow-lg"
            >
              {note}
            </div>
          ) : null}

          {detail.review_flags?.length ? (
            <Alert>
              <AlertDescription>
                Kiriman ini perlu ditinjau: {flagSentences(detail.review_flags).join(" ")}
                {detail.unlocated_quotes?.length ? (
                  <ul className="mt-2 list-disc pl-5">
                    {detail.unlocated_quotes.map((item) => (
                      <li key={`${item.source}-${item.segment}-${item.quote}`}>
                        Segmen {item.segment} ({DIMENSION_LABEL[item.source].toLowerCase()}): kutipan “{item.quote}”
                        tidak ada pada segmen itu.
                      </li>
                    ))}
                  </ul>
                ) : null}
              </AlertDescription>
            </Alert>
          ) : null}

          <div className="grid items-start gap-6 lg:grid-cols-2">
            <div className="flex flex-col gap-4 lg:sticky lg:top-8">
            {storedAi ? (
              <details className="rounded-xl bg-card p-4 ring-1 ring-foreground/10">
                <summary className="cursor-pointer font-medium">Keluaran AI yang dianalisis mahasiswa</summary>
                <p className="mt-3 max-h-72 overflow-y-auto text-base leading-7 whitespace-pre-wrap text-muted-foreground">
                  {unwrap(storedAi)}
                </p>
              </details>
            ) : null}
            <Card>
              <CardHeader>
                <CardTitle>Analisis mahasiswa</CardTitle>
                <CardDescription>Kutipan bukti disorot pada posisinya di dalam tulisan.</CardDescription>
              </CardHeader>
              <CardContent className="lg:max-h-[calc(100vh-18rem)] lg:overflow-y-auto">
                {text.length === 0 ? (
                  <p className="text-muted-foreground">Teks analisis mahasiswa belum tersedia.</p>
                ) : (
                  <p className="text-base leading-8 whitespace-pre-wrap">
                    {segments.map((segment) =>
                      segment.scoreIds.length === 0 ? (
                        <span key={segment.start}>{unwrap(segment.text)}</span>
                      ) : (
                        <mark
                          key={segment.start}
                          data-evidence={segment.scoreIds.join(" ")}
                          className={`rounded px-0.5 text-inherit ${
                            activeScoreId !== null && segment.scoreIds.includes(activeScoreId)
                              ? "bg-amber-300 ring-2 ring-primary"
                              : "bg-amber-100"
                          }`}
                        >
                          {unwrap(segment.text)}
                        </mark>
                      ),
                    )}
                  </p>
                )}
              </CardContent>
            </Card>
            </div>

            <div className="flex flex-col gap-6">
              {detail.synthesis ? (
                <Card>
                  <CardHeader>
                    <CardTitle>Ringkasan penilaian</CardTitle>
                    <CardDescription>Penjelasan yang menyatukan kedua dimensi.</CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col gap-3">
                    <p className="text-muted-foreground">{detail.synthesis.rationale}</p>
                    {detail.synthesis.inconsistencies.length > 0 ? (
                      <div>
                        <p className="text-sm font-medium">Alasan yang tidak sesuai dengan kutipannya</p>
                        <ul className="list-disc pl-5 text-sm text-muted-foreground">
                          {detail.synthesis.inconsistencies.map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    ) : null}
                  </CardContent>
                </Card>
              ) : null}

              {detail.run && detail.scores.length > 0 ? (
                <div className="flex flex-wrap items-center gap-3">
                  <Button variant="outline" disabled={savingReview} onClick={() => void onAcceptAll()}>
                    Terima semua yang belum ditinjau
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    {new Set(detail.reviews.map((review) => review.system_score_id)).size} dari{" "}
                    {detail.scores.length + (detail.segment_scores?.length ?? 0)} nilai sudah ditinjau.
                  </span>
                </div>
              ) : null}

              {detail.scores.length === 0 ? (
                <Card>
                  <CardContent>
                    <p>Belum ada nilai untuk kiriman ini. Jalankan penilaian dari halaman tugas.</p>
                  </CardContent>
                </Card>
              ) : (
                detail.scores.map((score) => scoreCard(score))
              )}

              {detail.segment_scores?.length ? (
                <Card>
                  <CardHeader>
                    <CardTitle>Penilaian per segmen</CardTitle>
                    <CardDescription>
                      Analisis dinilai per kalimat. Tingkat kognitif teks adalah tingkat tertinggi dari segmen,
                      dan indikator teks adalah indikator yang muncul di segmen mana pun. Buka satu segmen untuk
                      menerima, mengubah, atau mengomentari labelnya.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col gap-2">
                    {[...new Set(detail.segment_scores.map((s) => s.segment_index))].map((index) => {
                      const rows = detail.segment_scores!.filter((s) => s.segment_index === index);
                      const cognitive = rows.find((s) => s.dimension === "cognitive");
                      const present = rows
                        .filter((s) => s.dimension === "metacognitive" && s.level !== "absent")
                        .map((s) => s.indicator);
                      const unit = rows[0];
                      return (
                        <details
                          key={index}
                          className="rounded-lg border p-3"
                          onToggle={(event) =>
                            onSegmentToggle(event.currentTarget.open, unit.segment_start, unit.segment_end)
                          }
                        >
                          <summary className="cursor-pointer">
                            <span className="font-medium">Segmen {index}</span>
                            {" · "}
                            {cognitive ? levelLabel(scoreLevel(cognitive.level, levels), levelNames) : "—"}
                            {" · "}
                            {present.length ? present.join(", ") : "tanpa indikator"}
                          </summary>
                          <div className="mt-3 flex flex-col gap-3">
                            <p className="border-l-2 pl-3">{unwrap(text.slice(unit.segment_start, unit.segment_end))}</p>
                            {rows.map((score) => scoreCard(score, true))}
                          </div>
                        </details>
                      );
                    })}
                  </CardContent>
                </Card>
              ) : null}

              <AdminOnly>
                <Card>
                  <CardHeader>
                    <CardTitle>Data evaluasi penelitian</CardTitle>
                    <CardDescription>
                      Kiriman yang dikeluarkan tetap dinilai, tetapi ditandai pada ekspor riset.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col gap-2">
                    <Label htmlFor="exclusion">Status</Label>
                    <select
                      id="exclusion"
                      value={detail.exclusion_reason ?? ""}
                      onChange={(event) => void onExclusion((event.target.value || null) as ExclusionReason | null)}
                      className="h-8 w-full rounded-lg border border-input bg-background px-2 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                    >
                      <option value="">Termasuk data evaluasi</option>
                      {Object.entries(EXCLUSION_LABELS).map(([value, label]) => (
                        <option key={value} value={value}>
                          Dikeluarkan: {label}
                        </option>
                      ))}
                    </select>
                  </CardContent>
                </Card>
              </AdminOnly>

              <Card>
                <CardHeader>
                  <CardTitle>Umpan balik</CardTitle>
                  <CardDescription>Umpan balik untuk mahasiswa, disunting sebelum diekspor.</CardDescription>
                </CardHeader>
                <CardContent>
                  {detail.feedback === null ? (
                    <p className="text-muted-foreground">Umpan balik belum tersedia untuk kiriman ini.</p>
                  ) : (
                    <form onSubmit={onSaveFeedback} className="flex flex-col gap-3">
                      <Label htmlFor="feedback">Teks umpan balik</Label>
                      <textarea
                        id="feedback"
                        rows={8}
                        value={feedbackDraft ?? detail.feedback.edited_text ?? detail.feedback.generated_text ?? ""}
                        onChange={(event) => setFeedbackDraft(event.target.value)}
                        className={TEXTAREA_CLASS}
                      />
                      <p className="text-sm text-muted-foreground">
                        Kosongkan teks untuk kembali ke umpan balik awal.
                      </p>
                      <div className="flex items-center gap-3">
                        <Button type="submit" variant="outline" disabled={savingFeedback}>
                          {savingFeedback ? "Menyimpan…" : "Simpan umpan balik"}
                        </Button>
                        {detail.feedback.edited_text ? (
                          <span className="text-sm text-muted-foreground">Sudah disunting.</span>
                        ) : null}
                      </div>
                    </form>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Perbaiki pemisahan teks</CardTitle>
                  <CardDescription>
                    Geser batas jika keluaran AI dan analisis mahasiswa terpisah pada tempat yang keliru.
                    Isi teks tidak dapat diubah dari halaman ini. Nilai yang sudah ada dihapus saat batas
                    berubah, karena dibuat dari teks yang lama.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={onSaveSegmentation} className="flex flex-col gap-4">
                    <div className="flex flex-col gap-2">
                      <p className="text-sm font-medium">Keluaran AI</p>
                      <p className="max-h-40 overflow-y-auto rounded-lg bg-muted/60 p-3 whitespace-pre-wrap">
                        {previewAi || "Tidak ada teks pada sisi ini."}
                      </p>
                    </div>
                    <div className="flex flex-col gap-2">
                      <p className="text-sm font-medium">Analisis mahasiswa</p>
                      <p className="max-h-40 overflow-y-auto rounded-lg bg-muted/60 p-3 whitespace-pre-wrap">
                        {previewAnalysis || "Tidak ada teks pada sisi ini."}
                      </p>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label htmlFor="boundary">Batas pemisahan</Label>
                      <input
                        id="boundary"
                        type="range"
                        min={0}
                        max={lineStarts.length - 1}
                        value={lineIndex}
                        onChange={(event) => setBoundary(lineStarts[Number(event.target.value)])}
                        className="w-full accent-primary"
                      />
                      <p className="text-sm text-muted-foreground">
                        Batas di awal baris {lineIndex + 1} dari {lineStarts.length}. Gunakan tombol panah
                        untuk menggeser satu baris.
                      </p>
                    </div>
                    <Button type="submit" disabled={savingSeg || boundary === null} className="self-start">
                      {savingSeg ? "Menyimpan…" : "Simpan batas pemisahan"}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>
          </div>
        </>
      )}
    </>
  );
}
