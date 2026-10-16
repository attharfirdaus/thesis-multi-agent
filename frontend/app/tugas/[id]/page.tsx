"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { StatusBadge, runStatus, segmentationStatus } from "@/components/status-badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type AssignmentDetail, type ImportedFile, type RunSummary, type SubmissionSummary } from "@/lib/api";
import { flagSentences, warningSentences } from "@/lib/labels";

/** Jobs per request: one call must not sit on the whole batch, and the page shows progress between calls. */
const PROCESS_CHUNK = 2;

/** Consecutive calls that finished no job mean the batch is stuck; stop driving and let the lecturer decide. */
const MAX_STALLED = 2;

/**
 * Bound on one process request. The backend's own worst case is three 120-second attempts per agent,
 * so this is generous on purpose; it exists only so a dead connection cannot pin the page for ever.
 */
const PROCESS_TIMEOUT_MS = 30 * 60 * 1000;

const ACCEPTED_FILES = ".pdf,.docx,.txt,.zip";

/**
 * While a process call is in flight the page asks the run for its state, because that is the only way
 * to see which submission the server has claimed: the lease is written when the job starts, and the
 * process response only arrives when it is over.
 */
const IN_FLIGHT_POLL_MS = 3000;

/** A run in one of these states is over; a leftover counter on it is history, not work to do. */
const TERMINAL_RUN_STATUS = ["done", "failed", "cancelled"];

/** Jobs the queue still owns. A `running` job is already claimed, so it must not be started again. */
const pendingJobs = (jobs: RunSummary["jobs"]) => (jobs.queued ?? 0) + (jobs.running ?? 0);

function duration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return minutes === 0 ? `${rest} detik` : `${minutes} menit ${rest} detik`;
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
  const [calling, setCalling] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [drivenRunId, setDrivenRunId] = useState<string | null>(null);
  const [cancellingRun, setCancellingRun] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const drivingRun = useRef<string | null>(null);
  const resumedRun = useRef<string | null>(null);
  const callStartedAt = useRef(0);
  const callController = useRef<AbortController | null>(null);
  const cancelling = useRef(false);
  const starting = useRef(false);

  const load = useCallback(
    () =>
      api.getAssignment(id).then(
        (data) => {
          setDetail(data);
          // Keep the run being driven on screen, but take the API's counters: deleting a submission
          // removes its job rows, so the counts on display are not the ones the run started with.
          setRun((current) =>
            current?.id === data.latest_run?.id ? { ...current, ...data.latest_run } : data.latest_run,
          );
        },
        (err: unknown) => setError(err instanceof Error ? err.message : "Gagal memuat tugas."),
      ),
    [id],
  );

  useEffect(() => {
    void load();
  }, [load]);

  /**
   * A provider call reports nothing until it returns, so elapsed time is the only honest liveness
   * signal the page can show while one submission is being judged.
   */
  useEffect(() => {
    if (!calling) return;
    const timer = setInterval(() => {
      setElapsed(Math.round((Date.now() - callStartedAt.current) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [calling]);

  // Naming what is being graded needs a second look while the call is open: by the time the process
  // response arrives the job it claimed is already finished, so `in_flight` is only populated mid-call.
  useEffect(() => {
    if (!calling || drivenRunId === null) return;
    const poll = setInterval(() => {
      api.getRun(drivenRunId).then(setRun, () => {});
    }, IN_FLIGHT_POLL_MS);
    return () => clearInterval(poll);
  }, [calling, drivenRunId]);

  /**
   * Drive a run to completion. Each call evaluates a bounded chunk; the run itself lives in the
   * database, so closing this tab loses only the loop, and a reload resumes it from `jobs`.
   */
  const drive = useCallback(
    async (runId: string) => {
      if (drivingRun.current === runId) return;
      drivingRun.current = runId;
      setDrivenRunId(runId);
      setDriving(true);
      setError(null);
      setNote(null);
      let stalled = 0;
      let finished = -1;

      try {
        for (;;) {
          const controller = new AbortController();
          const timeout = setTimeout(() => controller.abort(), PROCESS_TIMEOUT_MS);
          callController.current = controller;
          callStartedAt.current = Date.now();
          setElapsed(0);
          setCalling(true);
          try {
            await api.processRun(runId, PROCESS_CHUNK, controller.signal);
          } finally {
            clearTimeout(timeout);
            callController.current = null;
            setCalling(false);
          }
          const current = await api.getRun(runId);
          setRun(current);
          const { done, failed, queued } = jobTotals(current.jobs);
          if (queued === 0) break;
          if (done + failed === finished) {
            stalled += 1;
            if (stalled >= MAX_STALLED) {
              setNote("Penilaian berhenti sebelum seluruh kiriman selesai. Tekan lanjutkan untuk mencoba lagi.");
              break;
            }
          } else {
            stalled = 0;
            finished = done + failed;
          }
        }
      } catch (err) {
        // A cancel from this page aborts the call on purpose; the cancel control reports the outcome.
        if (!cancelling.current) {
          if (err instanceof DOMException && err.name === "AbortError") {
            setNote("Permintaan penilaian melewati batas waktu tunggu. Penilaian dapat dilanjutkan.");
          } else {
            setError(err instanceof Error ? err.message : "Penilaian gagal dijalankan.");
          }
        }
      } finally {
        drivingRun.current = null;
        setDrivenRunId(null);
        setDriving(false);
        await load();
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
    liveRuns.find(
      (item) => !TERMINAL_RUN_STATUS.includes(item.status) && pendingJobs(item.jobs) > 0,
    )?.id ?? null;
  const inFlightNames = (run?.in_flight ?? []).map((item) => item.pseudonym);
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
      if (run && !window.confirm("Jalankan penilaian lagi? Layar hasil akan menampilkan penilaian terbaru.")) {
        return;
      }
      setError(null);
      const created = await api.createRun(id);
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
    const stillFinishing = calling || grading.length > 0;
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
      // Dropping this page's request stops the waiting; the server finishes the submission it holds.
      callController.current?.abort();
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

  return (
    <AppShell>
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
            </div>
            <Link href={`/tugas/${id}/hasil`} className="underline underline-offset-4 hover:text-foreground">
              Lihat hasil penilaian
            </Link>
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
                  {imported.map((file) => (
                    <li key={file.filename} className="flex flex-wrap items-center gap-2 text-sm">
                      <span className="font-medium">{file.filename}</span>
                      <StatusBadge
                        tone={file.status === "imported" ? "green" : "red"}
                        label={file.status === "imported" ? "Berhasil" : "Gagal"}
                      />
                      {file.pseudonym ? <span className="text-muted-foreground">{file.pseudonym}</span> : null}
                      {file.status === "failed" ? <span>Berkas ini gagal dibaca.</span> : null}
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
                Penilaian berjalan di latar belakang dan dapat dilanjutkan setelah halaman dimuat ulang.
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
                  {calling && inFlightNames.length > 0 ? (
                    <p className="text-sm">
                      Sedang menilai <span className="font-medium">{inFlightNames.join(", ")}</span>
                    </p>
                  ) : null}
                  <p className="text-sm text-muted-foreground">
                    {calling
                      ? `Menilai… ${duration(elapsed)}`
                      : "Menilai… menyiapkan kiriman berikutnya."}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Penilaian berjalan per kiriman, jadi waktu per tahap tidak dilaporkan.
                  </p>
                </div>
              ) : null}

              <div className="flex flex-wrap items-center gap-3">
                <Button
                  onClick={unfinishedRunId !== null ? () => void drive(unfinishedRunId) : onStart}
                  disabled={driving || (unfinishedRunId === null && submissions.length === 0)}
                >
                  {driving
                    ? "Penilaian sedang berjalan…"
                    : unfinishedRunId !== null
                      ? "Lanjutkan penilaian"
                      : "Jalankan penilaian"}
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
                  <table className="w-full border-collapse text-left">
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
                              {submission.pseudonym}
                            </Link>
                          </td>
                          <td className="py-2 pr-4">
                            <StatusBadge {...segmentationStatus(submission.segmentation_status)} />
                          </td>
                          <td className="py-2 pr-4">
                            {submission.review_flags?.length ? (
                              <div className="flex flex-col gap-1">
                                <StatusBadge tone="amber" label="Perlu Ditinjau" className="self-start" />
                                <span className="text-muted-foreground">
                                  {flagSentences(submission.review_flags).join(" ")}
                                </span>
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
    </AppShell>
  );
}
