"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { AdminOnly } from "@/components/app-shell";
import { StatusBadge, runStatus, segmentationStatus } from "@/components/status-badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  api,
  driveRun,
  runPending,
  type AssignmentDetail,
  type ImportedFile,
  type RunSummary,
  type SubmissionSummary,
} from "@/lib/api";
import { flagSentences, importError, modeLabel, submissionLabel, warningSentences } from "@/lib/labels";

const ACCEPTED_FILES = ".pdf,.docx,.txt,.zip";

/** What the lecturer is about to spend quota on, in the wording the two choices deserve. */
function startQuestion(mode: string, onlyUngraded: boolean, ungradedCount: number): string {
  if (mode === "single_agent") {
    return onlyUngraded
      ? `Jalankan baseline untuk ${ungradedCount} kiriman yang belum dinilai? Hasil penilaian yang sudah ada tidak berubah.`
      : "Jalankan penilaian baseline lagi? Layar hasil akan menampilkan penilaian terbaru.";
  }
  return onlyUngraded
    ? `Nilai ${ungradedCount} kiriman yang belum dinilai? Hasil penilaian yang sudah ada tidak berubah.`
    : "Jalankan penilaian lagi? Layar hasil akan menampilkan penilaian terbaru.";
}

/** The English exception text and the stored caveats, kept for the developer rather than the lecturer. */
function TechnicalDetail({ lines }: { lines: string[] }) {
  if (lines.length === 0) return null;
  return (
    <details className="text-muted-foreground">
      <summary className="cursor-pointer">Detail teknis</summary>
      {lines.map((line) => (
        <p key={line}>{line}</p>
      ))}
    </details>
  );
}

function jobTotals(jobs: RunSummary["jobs"]) {
  const counts = jobs ?? {};
  const done = counts.done ?? 0;
  const failed = counts.failed ?? 0;
  return {
    done,
    failed,
    cancelled: counts.cancelled ?? 0,
    queued: counts.queued ?? 0,
    total: Object.values(counts).reduce((s, n) => s + n, 0),
  };
}

export default function TugasPage() {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<AssignmentDetail | null>(null);
  const [run, setRun] = useState<RunSummary | null>(null);
  const [imported, setImported] = useState<ImportedFile[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [driving, setDriving] = useState(false);
  const [editing, setEditing] = useState<{ title: string; course: string; prompt_text: string } | null>(null);
  const router = useRouter();
  const [drivenRunId, setDrivenRunId] = useState<string | null>(null);
  const [cancellingRun, setCancellingRun] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  // The owner's default: a run spends quota on what has no result yet (PRD §11 keeps re-grading as a choice).
  const [onlyUngraded, setOnlyUngraded] = useState(true);
  // The thesis compares both modes, so the baseline is a choice beside the scope, never the cheaper default.
  const [runMode, setRunMode] = useState<"multi_agent" | "single_agent">("multi_agent");
  const fileInput = useRef<HTMLInputElement>(null);
  const drivingRun = useRef<string | null>(null);
  const resumedRun = useRef<string | null>(null);
  // False once the page is left: the server keeps grading, this page just stops asking about it.
  const watching = useRef(true);
  const cancelling = useRef(false);
  const starting = useRef(false);

  const load = useCallback(
    () =>
      api.getAssignment(id).then(
        (data) => {
          setDetail(data);
          // Keep the run being driven on screen, but take the API's counters: deleting a submission
          // removes its job rows, so the counts on display are not the ones the run started with.
          setRun((current) => {
            if (data.latest_run === null) return null;
            return current?.id === data.latest_run.id ? { ...current, ...data.latest_run } : data.latest_run;
          });
        },
        (err: unknown) => setError(err instanceof Error ? err.message : "Gagal memuat tugas."),
      ),
    [id],
  );

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    watching.current = true;
    return () => {
      watching.current = false;
    };
  }, []);

  /**
   * Follow a run to its end. The server grades on its own thread and the run lives in the database,
   * so this page only starts it and polls: leaving or reloading loses the watching, never the run, and
   * coming back attaches to the same run instead of starting a second grader.
   */
  const drive = useCallback(
    async (runId: string) => {
      if (drivingRun.current === runId) return;
      drivingRun.current = runId;
      setDrivenRunId(runId);
      setDriving(true);
      setError(null);
      setNote(null);
      try {
        const last = await driveRun(runId, setRun, () => watching.current);
        if (watching.current && runPending(last)) {
          setNote("Penilaian berhenti sebelum seluruh kiriman selesai. Tekan lanjutkan untuk mencoba lagi.");
        }
      } catch (err) {
        if (!cancelling.current) setError(err instanceof Error ? err.message : "Penilaian gagal dijalankan.");
      } finally {
        drivingRun.current = null;
        setDrivenRunId(null);
        setDriving(false);
        if (watching.current) await load();
      }
    },
    [load],
  );

  const submissions = detail?.submissions ?? [];
  const totals = run ? jobTotals(run.jobs) : null;
  // Every run of this assignment that still owns a job, the one on screen first. A `running` job counts
  // on purpose: if the process that held its lease died, only a process call releases it, so this run
  // must block a *new* run while staying reachable through the control below.
  const liveRuns = detail
    ? [...(run ? [run] : []), ...detail.runs.filter((item) => item.id !== run?.id)]
    : [];
  const unfinishedRunId =
    liveRuns.find(runPending)?.id ?? null;
  const inFlightNames = (run?.in_flight ?? []).map((item) => item.pseudonym);
  const gradedCount = detail?.graded_count ?? 0;
  const ungradedCount = Math.max((detail?.submission_count ?? 0) - gradedCount, 0);
  const flaggedCount = submissions.filter((item) => (item.review_flags ?? []).length > 0).length;
  const nothingToGrade = onlyUngraded && ungradedCount === 0;
  // Cancelling stops the run this page is working on; only then the one still holding queued jobs.
  const cancelTargetId = drivenRunId ?? unfinishedRunId;

  // Self-healing after a crash or a closed tab: one process call is idempotent, and it is what clears a
  // stale lease, so an unfinished run is picked up again as soon as the page is open.
  useEffect(() => {
    if (unfinishedRunId === null) return;
    if (resumedRun.current === unfinishedRunId) return;
    resumedRun.current = unfinishedRunId;
    void drive(unfinishedRunId);
  }, [unfinishedRunId, drive]);

  async function onUpload(event: React.FormEvent) {
    event.preventDefault();
    const selected = Array.from(fileInput.current?.files ?? []);
    if (selected.length === 0) {
      setError("Pilih berkas terlebih dahulu.");
      return;
    }
    setUploading(true);
    setError(null);
    setImported(null);
    try {
      const result = await api.uploadSubmissions(id, selected);
      setImported(result.files);
      if (fileInput.current) fileInput.current.value = "";
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal mengunggah berkas.");
    } finally {
      setUploading(false);
    }
  }

  async function onStart() {
    // A double press must not create a second run: the first request may not have returned yet.
    if (starting.current) return;
    starting.current = true;
    try {
      // Only re-grading replaces the results a lecturer is already reading, so only it warns about that.
      const question = startQuestion(runMode, onlyUngraded, ungradedCount);
      if (run && !window.confirm(question)) return;
      setError(null);
      const created = await api.createRun(id, runMode, onlyUngraded);
      setRun(created);
      resumedRun.current = created.id;
      await drive(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal memulai penilaian.");
    } finally {
      starting.current = false;
    }
  }

  /** Stop what is still waiting. The submission the server already claimed cannot be stopped. */
  async function onCancel() {
    const targetId = drivenRunId ?? unfinishedRunId;
    if (targetId === null || cancelling.current) return;
    const grading = (run?.in_flight ?? []).map((item) => item.pseudonym);
    // The server finishes whatever it has already claimed, whether or not this page managed to name it.
    const stillFinishing = grading.length > 0;
    const finishingClause =
      grading.length > 0
        ? ` ${grading.join(", ")} sedang dinilai dan tetap diselesaikan.`
        : " Kiriman yang sedang dinilai tetap diselesaikan.";
    const warning = `Batalkan penilaian? Kiriman yang masih menunggu tidak akan dinilai.${
      stillFinishing ? finishingClause : ""
    }`;
    if (!window.confirm(warning)) return;

    cancelling.current = true;
    setCancellingRun(true);
    setError(null);
    setNote(null);
    try {
      const cancelled = await api.cancelRun(targetId);
      setRun(cancelled);
      const jobs = jobTotals(cancelled.jobs);
      setNote(
        `Penilaian dihentikan: ${jobs.done} selesai, ${jobs.cancelled} dibatalkan.` +
          (stillFinishing ? finishingClause : ""),
      );
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menghentikan penilaian.");
    } finally {
      cancelling.current = false;
      setCancellingRun(false);
    }
  }

  /** Delete one submission and everything derived from it. Confirmed, because nothing brings it back. */
  async function onDelete(submission: SubmissionSummary) {
    if (deletingId !== null) return;
    const confirmed = window.confirm(
      `Hapus kiriman ${submission.pseudonym}? Nilai, kutipan bukti, umpan balik, dan tautan ke identitas ` +
        "mahasiswa ikut terhapus. Tindakan ini tidak dapat dibatalkan.",
    );
    if (!confirmed) return;

    setDeletingId(submission.id);
    setError(null);
    setNote(null);
    try {
      await api.deleteSubmission(submission.id);
      await load();
      setNote(`Kiriman ${submission.pseudonym} beserta nilainya sudah dihapus.`);
    } catch (err) {
      // A refused delete (the submission is queued or being graded) keeps the row on screen.
      setError(err instanceof Error ? err.message : "Gagal menghapus kiriman.");
    } finally {
      setDeletingId(null);
    }
  }

  async function onSaveAssignment(event: React.FormEvent) {
    event.preventDefault();
    if (editing === null) return;
    setError(null);
    try {
      await api.updateAssignment(id, {
        title: editing.title.trim(),
        course: editing.course.trim(),
        prompt_text: editing.prompt_text.trim(),
      });
      setEditing(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan tugas.");
    }
  }

  /** Delete the assignment and everything under it. Confirmed, because nothing brings it back. */
  async function onDeleteAssignment() {
    const confirmed = window.confirm(
      `Hapus tugas "${detail?.title}" beserta ${detail?.submission_count ?? 0} kiriman, seluruh nilai, tinjauan, ` +
        "dan umpan baliknya? Tindakan ini tidak dapat dibatalkan.",
    );
    if (!confirmed) return;
    setError(null);
    try {
      await api.deleteAssignment(id);
      router.replace("/dasbor");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menghapus tugas.");
    }
  }

  return (
    <>
      {detail === null ? (
        <p className="text-muted-foreground">Memuat…</p>
      ) : (
        <>
          <header className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold">{detail.title}</h1>
              <p className="text-muted-foreground">
                {detail.course} · {detail.submission_count} kiriman
              </p>
              {/* KF-02: read-only — a new assignment takes the newest rubric version automatically. */}
              <p className="text-sm text-muted-foreground">
                Versi rubrik: {detail.rubric_version ?? "belum ada"}
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Link href={`/tugas/${id}/hasil`} className="underline underline-offset-4 hover:text-foreground">
                Lihat hasil penilaian
              </Link>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  setEditing({ title: detail.title, course: detail.course, prompt_text: detail.prompt_text ?? "" })
                }
              >
                Ubah tugas
              </Button>
              <Button variant="destructive" size="sm" disabled={driving} onClick={() => void onDeleteAssignment()}>
                Hapus tugas
              </Button>
            </div>
          </header>

          {editing ? (
            <Card>
              <CardHeader>
                <CardTitle>Ubah tugas</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={onSaveAssignment} className="flex flex-col gap-4">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="edit_title">Judul tugas</Label>
                    <Input
                      id="edit_title"
                      required
                      value={editing.title}
                      onChange={(e) => setEditing({ ...editing, title: e.target.value })}
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="edit_course">Mata kuliah</Label>
                    <Input
                      id="edit_course"
                      required
                      value={editing.course}
                      onChange={(e) => setEditing({ ...editing, course: e.target.value })}
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="edit_prompt">Teks tugas (opsional)</Label>
                    <textarea
                      id="edit_prompt"
                      rows={4}
                      value={editing.prompt_text}
                      onChange={(e) => setEditing({ ...editing, prompt_text: e.target.value })}
                      className="w-full rounded-lg border border-input bg-transparent px-2.5 py-1.5 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button type="submit" disabled={!editing.title.trim() || !editing.course.trim()}>
                      Simpan
                    </Button>
                    <Button type="button" variant="ghost" onClick={() => setEditing(null)}>
                      Batal
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          ) : null}

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

          {detail.prompt_text ? (
            <Card>
              <CardHeader>
                <CardTitle>Teks tugas</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap">{detail.prompt_text}</p>
              </CardContent>
            </Card>
          ) : null}

          <Card>
            <CardHeader>
              <CardTitle>Unggah kiriman</CardTitle>
              <CardDescription>
                Berkas PDF, DOCX, TXT, atau ZIP. Identitas mahasiswa dihapus saat berkas diproses.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={onUpload} className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="files">Berkas kiriman</Label>
                  <Input id="files" ref={fileInput} type="file" multiple accept={ACCEPTED_FILES} />
                </div>
                <Button type="submit" variant="outline" disabled={uploading} className="self-start">
                  {uploading ? "Mengunggah…" : "Unggah berkas"}
                </Button>
              </form>

              {imported ? (
                <ul className="mt-4 flex flex-col gap-2">
                  {imported.map((file, index) => (
                    <li key={`${file.filename}-${index}`} className="flex flex-wrap items-center gap-2 text-sm">
                      <span className="font-medium">{file.filename}</span>
                      <StatusBadge
                        tone={file.status === "imported" ? "green" : "red"}
                        label={file.status === "imported" ? "Berhasil" : "Gagal"}
                      />
                      {file.pseudonym ? <span className="text-muted-foreground">{file.pseudonym}</span> : null}
                      {file.status === "failed" ? <span>{importError(file.error)}</span> : null}
                      {file.warnings?.length ? (
                        <span className="text-muted-foreground">
                          {warningSentences(file.warnings).join(" ")}
                        </span>
                      ) : null}
                      <TechnicalDetail
                        lines={[...(file.error ? [file.error] : []), ...(file.warnings ?? [])]}
                      />
                    </li>
                  ))}
                </ul>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Penilaian</CardTitle>
              <CardDescription>
                Penilaian berjalan di server dan tetap berlanjut ketika halaman ini ditutup.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              {run && totals ? (
                <div className="flex flex-col gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusBadge {...runStatus(run.status)} />
                    <span className="text-sm text-muted-foreground">
                      {totals.done} dari {totals.total} selesai
                      {totals.queued > 0 ? ` · ${totals.queued} menunggu` : ""}
                      {totals.cancelled > 0 ? ` · ${totals.cancelled} dibatalkan` : ""}
                      {totals.failed > 0 ? ` · ${totals.failed} gagal` : ""}
                    </span>
                  </div>
                  <div
                    role="progressbar"
                    aria-label="Kemajuan penilaian"
                    aria-valuemin={0}
                    aria-valuemax={totals.total}
                    aria-valuenow={totals.done}
                    className="h-2 w-full overflow-hidden rounded-full bg-muted"
                  >
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{ width: `${totals.total > 0 ? Math.round((totals.done / totals.total) * 100) : 0}%` }}
                    />
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  Belum ada penilaian. Jalankan penilaian setelah kiriman diunggah.
                </p>
              )}

              {driving ? (
                <div className="flex flex-col gap-2">
                  <div
                    role="progressbar"
                    aria-label="Penilaian sedang berjalan"
                    className="h-2 w-full overflow-hidden rounded-full bg-muted"
                  >
                    <div className="h-full w-1/3 animate-pulse rounded-full bg-primary" />
                  </div>
                  <p className="text-sm">
                    {inFlightNames.length > 0 ? (
                      <>
                        Sedang menilai <span className="font-medium">{inFlightNames.join(", ")}</span>
                      </>
                    ) : (
                      "Menilai… menyiapkan kiriman berikutnya."
                    )}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Penilaian berjalan di server. Halaman ini boleh ditinggalkan dan dibuka lagi kapan saja.
                  </p>
                </div>
              ) : null}

              {/* The scope decides what the primary button spends quota on, so it sits directly above it. */}
              {unfinishedRunId === null && !driving ? (
                <div className="flex flex-col gap-4 sm:flex-row sm:gap-10">
                  {/* The baseline is the researcher's comparison run (Bab III.3, KF-11): admin only. */}
                  <AdminOnly>
                  <fieldset className="flex flex-col gap-2">
                    <legend className="text-sm font-medium">Mode penilaian</legend>
                    <div className="flex items-start gap-2">
                      <input
                        id="mode_multi"
                        type="radio"
                        name="run_mode"
                        className="mt-1"
                        checked={runMode === "multi_agent"}
                        onChange={() => setRunMode("multi_agent")}
                      />
                      <Label htmlFor="mode_multi" className="cursor-pointer">
                        {modeLabel("multi_agent")}
                      </Label>
                    </div>
                    <div className="flex items-start gap-2">
                      <input
                        id="mode_single"
                        type="radio"
                        name="run_mode"
                        className="mt-1"
                        checked={runMode === "single_agent"}
                        onChange={() => setRunMode("single_agent")}
                      />
                      <Label htmlFor="mode_single" className="cursor-pointer">
                        {modeLabel("single_agent")}
                      </Label>
                    </div>
                    <p className="max-w-md text-sm text-muted-foreground">
                      Baseline single-agen menilai seluruh rubrik sekaligus dan dipakai untuk perbandingan
                      pada penelitian, bukan sebagai cara menilai yang lebih hemat.
                    </p>
                  </fieldset>
                  </AdminOnly>

                  <fieldset className="flex flex-col gap-2">
                    <legend className="text-sm font-medium">Kiriman yang dinilai</legend>
                    <div className="flex items-start gap-2">
                      <input
                        id="scope_ungraded"
                        type="radio"
                        name="run_scope"
                        className="mt-1"
                        checked={onlyUngraded}
                        onChange={() => setOnlyUngraded(true)}
                      />
                      <Label htmlFor="scope_ungraded" className="cursor-pointer">
                        Hanya kiriman yang belum dinilai
                      </Label>
                    </div>
                    <div className="flex items-start gap-2">
                      <input
                        id="scope_all"
                        type="radio"
                        name="run_scope"
                        className="mt-1"
                        checked={!onlyUngraded}
                        onChange={() => setOnlyUngraded(false)}
                      />
                      <Label htmlFor="scope_all" className="cursor-pointer">
                        Nilai ulang semua kiriman (termasuk yang sudah ada nilainya)
                      </Label>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {onlyUngraded
                        ? `${ungradedCount} kiriman akan dinilai, ${gradedCount} sudah dinilai.`
                        : `Semua ${detail?.submission_count ?? 0} kiriman akan dinilai ulang.`}
                    </p>
                    {onlyUngraded && flaggedCount > 0 ? (
                      <p className="text-sm text-muted-foreground">
                        {flaggedCount} kiriman perlu ditinjau dan tidak akan dinilai ulang dengan pilihan ini.
                      </p>
                    ) : null}
                  </fieldset>
                </div>
              ) : null}

              <div className="flex flex-wrap items-center gap-3">
                <Button
                  onClick={unfinishedRunId !== null ? () => void drive(unfinishedRunId) : onStart}
                  disabled={
                    driving ||
                    (unfinishedRunId === null &&
                      (submissions.length === 0 || nothingToGrade))
                  }
                >
                  {driving
                    ? "Penilaian sedang berjalan…"
                    : unfinishedRunId !== null
                      ? "Lanjutkan penilaian"
                      : `${onlyUngraded ? "Nilai kiriman baru" : "Nilai ulang semua kiriman"}${
                          runMode === "single_agent" ? " (baseline)" : ""
                        }`}
                </Button>
                {cancelTargetId !== null ? (
                  <Button
                    variant="destructive"
                    onClick={() => void onCancel()}
                    disabled={cancellingRun}
                  >
                    {cancellingRun ? "Menghentikan…" : "Batalkan penilaian"}
                  </Button>
                ) : null}
              </div>
              {cancelTargetId !== null ? (
                <p className="text-sm text-muted-foreground">
                  Penghentian hanya berlaku untuk kiriman yang belum dinilai; kiriman yang sedang
                  dikerjakan tetap diselesaikan.
                </p>
              ) : null}
              {cancelTargetId === null && submissions.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Unggah minimal satu kiriman sebelum menilai.
                </p>
              ) : null}
              {cancelTargetId === null && submissions.length > 0 && nothingToGrade ? (
                <p className="text-sm text-muted-foreground">
                  Semua kiriman sudah dinilai. Pilih nilai ulang semua kiriman untuk menilai kembali.
                </p>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Kiriman</CardTitle>
              <CardDescription>Klik pseudonim untuk membaca hasil per kiriman.</CardDescription>
            </CardHeader>
            <CardContent>
              {submissions.length === 0 ? (
                <p className="text-muted-foreground">
                  Belum ada kiriman. Unggah berkas mahasiswa pada bagian di atas.
                </p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[640px] border-collapse text-left">
                    <thead>
                      <tr className="border-b">
                        <th scope="col" className="py-2 pr-4 font-medium">
                          Pseudonim
                        </th>
                        <th scope="col" className="py-2 pr-4 font-medium">
                          Status pemisahan
                        </th>
                        <th scope="col" className="py-2 pr-4 font-medium">
                          Tinjauan
                        </th>
                        <th scope="col" className="py-2 font-medium">
                          Catatan impor
                        </th>
                        <th scope="col" className="py-2 pl-4 font-medium">
                          Tindakan
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {submissions.map((submission) => (
                        <tr key={submission.id} className="border-b last:border-0">
                          <td className="py-2 pr-4">
                            <Link
                              href={`/kiriman/${submission.id}`}
                              className="underline underline-offset-4 hover:text-foreground"
                            >
                              {submissionLabel(submission.pseudonym, submission.real_name)}
                            </Link>
                          </td>
                          <td className="py-2 pr-4">
                            <StatusBadge {...segmentationStatus(submission.segmentation_status)} />
                          </td>
                          <td className="py-2 pr-4">
                            {submission.review_flags?.length ? (
                              <div className="flex flex-col gap-1">
                                <StatusBadge tone="amber" label="Perlu Ditinjau" className="self-start" />
                                <details className="text-sm text-muted-foreground">
                                  <summary className="cursor-pointer">Alasan</summary>
                                  {flagSentences(submission.review_flags).join(" ")}
                                </details>
                              </div>
                            ) : (
                              <span className="text-muted-foreground">—</span>
                            )}
                          </td>
                          <td className="py-2 text-muted-foreground">
                            {submission.import_warnings?.length ? (
                              <div className="flex flex-col gap-1">
                                <span>{warningSentences(submission.import_warnings).join(" ")}</span>
                                <TechnicalDetail lines={submission.import_warnings} />
                              </div>
                            ) : (
                              "—"
                            )}
                          </td>
                          <td className="py-2 pl-4">
                            <Button
                              variant="destructive"
                              size="sm"
                              aria-label={`Hapus kiriman ${submission.pseudonym}`}
                              disabled={deletingId !== null}
                              onClick={() => void onDelete(submission)}
                            >
                              {deletingId === submission.id ? "Menghapus…" : "Hapus"}
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </>
  );
}
