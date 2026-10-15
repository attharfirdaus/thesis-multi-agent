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
import { api, type AssignmentDetail, type ImportedFile, type RunSummary } from "@/lib/api";
import { flagSentence, warningSentence } from "@/lib/labels";

/** Jobs per request: one call must not sit on the whole batch, and the page shows progress between calls. */
const PROCESS_CHUNK = 2;

/** Consecutive calls that finished no job mean the batch is stuck; stop driving and let the lecturer decide. */
const MAX_STALLED = 2;

const ACCEPTED_FILES = ".pdf,.docx,.txt,.zip";

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
  return { done, failed, queued: counts.queued ?? 0, total: Object.values(counts).reduce((s, n) => s + n, 0) };
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
  const fileInput = useRef<HTMLInputElement>(null);
  const drivingRun = useRef<string | null>(null);
  const resumedRun = useRef<string | null>(null);

  const load = useCallback(
    () =>
      api.getAssignment(id).then(
        (data) => {
          setDetail(data);
          // Keep the run being driven on screen; anything else shows the newest run the API reports.
          setRun((current) => (current?.id === data.latest_run?.id ? current : data.latest_run));
        },
        (err: unknown) => setError(err instanceof Error ? err.message : "Gagal memuat tugas."),
      ),
    [id],
  );

  useEffect(() => {
    void load();
  }, [load]);

  /**
   * Drive a run to completion. Each call evaluates a bounded chunk; the run itself lives in the
   * database, so closing this tab loses only the loop, and a reload resumes it from `jobs`.
   */
  const drive = useCallback(
    async (runId: string) => {
      if (drivingRun.current === runId) return;
      drivingRun.current = runId;
      setDriving(true);
      setError(null);
      setNote(null);
      let stalled = 0;
      let finished = -1;

      try {
        for (;;) {
          await api.processRun(runId, PROCESS_CHUNK);
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
        setError(err instanceof Error ? err.message : "Penilaian gagal dijalankan.");
      } finally {
        drivingRun.current = null;
        setDriving(false);
        await load();
      }
    },
    [load],
  );

  const latest = detail?.latest_run ?? null;
  useEffect(() => {
    if (!latest || latest.status === "done" || latest.status === "failed") return;
    if ((latest.jobs?.queued ?? 0) === 0) return;
    if (resumedRun.current === latest.id) return;
    resumedRun.current = latest.id;
    void drive(latest.id);
  }, [latest, drive]);

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
    if (run && !window.confirm("Jalankan penilaian lagi? Layar hasil akan menampilkan penilaian terbaru.")) {
      return;
    }
    setError(null);
    try {
      const created = await api.createRun(id);
      setRun(created);
      resumedRun.current = created.id;
      await drive(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal memulai penilaian.");
    }
  }

  const submissions = detail?.submissions ?? [];
  const totals = run ? jobTotals(run.jobs) : null;

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
                          {file.warnings.map(warningSentence).join(" ")}
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
                      {totals.done} selesai · {totals.queued} menunggu
                      {totals.failed > 0 ? ` · ${totals.failed} gagal` : ""} dari {totals.total} kiriman
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

              <div>
                <Button
                  onClick={onStart}
                  disabled={driving || submissions.length === 0}
                >
                  {driving ? "Menilai…" : totals && totals.queued > 0 ? "Lanjutkan penilaian" : "Jalankan penilaian"}
                </Button>
                {submissions.length === 0 ? (
                  <p className="mt-2 text-sm text-muted-foreground">
                    Unggah minimal satu kiriman sebelum menilai.
                  </p>
                ) : null}
              </div>
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
                                  {submission.review_flags.map(flagSentence).join(" ")}
                                </span>
                              </div>
                            ) : (
                              <span className="text-muted-foreground">—</span>
                            )}
                          </td>
                          <td className="py-2 text-muted-foreground">
                            {submission.import_warnings?.length ? (
                              <div className="flex flex-col gap-1">
                                <span>{submission.import_warnings.map(warningSentence).join(" ")}</span>
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
