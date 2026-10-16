"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { StatusBadge, runStatus, segmentationStatus } from "@/components/status-badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type Score, type SubmissionDetail } from "@/lib/api";
import { buildSegments, combinedDocument } from "@/lib/evidence";
import { flagSentences, levelLabel, scoreLevel } from "@/lib/labels";

const DIMENSION_LABEL: Record<Score["dimension"], string> = {
  cognitive: "Tingkat Kognitif",
  metacognitive: "Indikator Metakognitif",
};

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

  const load = useCallback(
    () =>
      api.getSubmission(id).then(
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

  const text = detail?.student_analysis_text ?? "";
  const segments = detail ? buildSegments(text, detail.scores) : [];
  const levels = detail?.rubric?.levels ?? [];
  const levelNames = detail?.rubric?.level_names ?? {};
  const storedAi = detail?.ai_output_text ?? "";
  // The offsets sent below index the same string the API splits; see combinedDocument for the rule.
  const combined = combinedDocument(storedAi, text);
  const offset = boundary ?? storedAi.length;
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

  function scoreCard(score: Score) {
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
            <span className="text-sm text-primary underline underline-offset-4">Lihat kutipan</span>
          </button>

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
                  {levels.map((level) => (
                    <option key={level} value={level}>
                      {levelLabel(level, levelNames)}
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
                disabled={savingReview || levels.length === 0}
                onClick={() => setDraft({ scoreId: score.id, level: levels[0] ?? "", reason: "" })}
              >
                Ubah
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <AppShell>
      {detail === null ? (
        <p className="text-muted-foreground">Memuat…</p>
      ) : (
        <>
          <header className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex flex-col gap-2">
              <h1 className="text-2xl font-semibold">{detail.pseudonym}</h1>
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
          {note ? (
            <Alert>
              <AlertDescription>{note}</AlertDescription>
            </Alert>
          ) : null}

          {detail.review_flags?.length ? (
            <Alert>
              <AlertDescription>
                Kiriman ini perlu ditinjau: {flagSentences(detail.review_flags).join(" ")}
              </AlertDescription>
            </Alert>
          ) : null}

          <div className="grid items-start gap-6 lg:grid-cols-2">
            <Card className="lg:sticky lg:top-8">
              <CardHeader>
                <CardTitle>Analisis mahasiswa</CardTitle>
                <CardDescription>Kutipan bukti disorot pada posisinya di dalam tulisan.</CardDescription>
              </CardHeader>
              <CardContent className="lg:max-h-[calc(100vh-14rem)] lg:overflow-y-auto">
                {text.length === 0 ? (
                  <p className="text-muted-foreground">Teks analisis mahasiswa belum tersedia.</p>
                ) : (
                  <p className="text-base leading-8 whitespace-pre-wrap">
                    {segments.map((segment) =>
                      segment.scoreIds.length === 0 ? (
                        <span key={segment.start}>{segment.text}</span>
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
                          {segment.text}
                        </mark>
                      ),
                    )}
                  </p>
                )}
              </CardContent>
            </Card>

            <div className="flex flex-col gap-6">
              {detail.scores.length === 0 ? (
                <Card>
                  <CardContent>
                    <p>Belum ada nilai untuk kiriman ini. Jalankan penilaian dari halaman tugas.</p>
                  </CardContent>
                </Card>
              ) : (
                detail.scores.map(scoreCard)
              )}

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
                    Isi teks tidak dapat diubah dari halaman ini.
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
                        max={Math.max(combined.length - 1, 0)}
                        value={offset}
                        onChange={(event) => setBoundary(Number(event.target.value))}
                        className="w-full accent-primary"
                      />
                      <p className="text-sm text-muted-foreground">
                        Batas di karakter {offset} dari {combined.length}.
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
    </AppShell>
  );
}
