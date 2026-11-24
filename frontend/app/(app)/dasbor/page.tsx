"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

import { CheckCircle2, ChevronRight, FileText, FolderOpen, Plus } from "lucide-react";

import { PageHeader } from "@/components/app-shell";
import { StatusBadge, runStatus } from "@/components/status-badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type AssignmentSummary } from "@/lib/api";

export default function DasborPage() {
  const [assignments, setAssignments] = useState<AssignmentSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [course, setCourse] = useState("");
  const [promptText, setPromptText] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(
    () =>
      api.listAssignments().then(
        (data) => setAssignments(data),
        (err: unknown) => {
          setError(err instanceof Error ? err.message : "Gagal memuat daftar tugas.");
          setAssignments([]);
        },
      ),
    [],
  );

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const created = await api.createAssignment({
        title: title.trim(),
        course: course.trim(),
        // An empty prompt is left out rather than sent blank; the field is optional in the API.
        ...(promptText.trim() ? { prompt_text: promptText.trim() } : {}),
      });
      setAssignments((previous) => (previous ? [created, ...previous] : [created]));
      setTitle("");
      setCourse("");
      setPromptText("");
      setFormOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal membuat tugas.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Dasbor"
        title="Tugas Anda"
        description="Buat tugas, unggah kiriman mahasiswa, lalu tinjau tingkat kognitif dan indikator metakognitif beserta kutipan buktinya."
        actions={
          formOpen ? null : (
            <Button onClick={() => setFormOpen(true)}>
              <Plus data-icon="inline-start" aria-hidden="true" />
              Buat tugas
            </Button>
          )
        }
      />

      {assignments && assignments.length > 0 ? (
        <dl className="grid grid-cols-3 gap-3 sm:gap-4">
          {[
            { label: "Tugas", value: assignments.length, icon: FolderOpen },
            {
              label: "Kiriman mahasiswa",
              value: assignments.reduce((sum, a) => sum + a.submission_count, 0),
              icon: FileText,
            },
            {
              label: "Kiriman sudah dinilai",
              value: assignments.reduce((sum, a) => sum + a.graded_count, 0),
              icon: CheckCircle2,
            },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="flex items-center gap-4 rounded-xl border border-border bg-card p-3 sm:p-5">
              <span className="hidden size-11 shrink-0 items-center justify-center rounded-lg bg-surface text-primary sm:flex">
                <Icon className="size-5" aria-hidden="true" />
              </span>
              <div>
                <dt className="text-xs text-muted-foreground sm:text-sm">{label}</dt>
                <dd className="font-heading text-3xl leading-none font-semibold tabular-nums">{value}</dd>
              </div>
            </div>
          ))}
        </dl>
      ) : null}

      {error ? (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      {formOpen ? (
        <Card>
          <CardHeader>
            <CardTitle>Tugas baru</CardTitle>
            <CardDescription>
              Judul dan mata kuliah dipakai pada berkas hasil ekspor.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={onCreate} className="flex flex-col gap-4" noValidate>
              <div className="flex flex-col gap-2">
                <Label htmlFor="title">Judul tugas</Label>
                <Input
                  id="title"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="course">Mata kuliah</Label>
                <Input
                  id="course"
                  required
                  value={course}
                  onChange={(e) => setCourse(e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="prompt_text">Teks tugas (opsional)</Label>
                <textarea
                  id="prompt_text"
                  rows={4}
                  value={promptText}
                  onChange={(e) => setPromptText(e.target.value)}
                  className="w-full rounded-lg border border-input bg-card px-3 py-2 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                />
              </div>
              <div className="flex gap-3">
                <Button type="submit" disabled={busy || !title.trim() || !course.trim()}>
                  {busy ? "Menyimpan…" : "Simpan tugas"}
                </Button>
                <Button type="button" variant="ghost" onClick={() => setFormOpen(false)}>
                  Batal
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : null}

      {assignments === null ? (
        <p className="text-muted-foreground" role="status">
          Memuat…
        </p>
      ) : assignments.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-input bg-card px-6 py-14 text-center">
          <span className="flex size-12 items-center justify-center rounded-full bg-surface text-primary">
            <FolderOpen className="size-6" aria-hidden="true" />
          </span>
          <h2 className="text-2xl font-semibold">Belum ada tugas</h2>
          <p className="max-w-md text-muted-foreground">
            Buat tugas pertama untuk mulai mengunggah pekerjaan mahasiswa.
          </p>
        </div>
      ) : (
        <ul className="grid gap-4 md:grid-cols-2">
          {assignments.map((assignment) => {
            const jobs = assignment.latest_run?.jobs ?? {};
            const total = Object.values(jobs).reduce((sum, count) => sum + count, 0);
            const done = jobs.done ?? 0;
            return (
              <li key={assignment.id}>
                <Link
                  href={`/tugas/${assignment.id}`}
                  className="group flex h-full flex-col gap-4 rounded-xl border border-border bg-card p-5 shadow-[0_1px_2px_rgb(15_23_42/0.04)] transition-[border-color,box-shadow] duration-200 outline-none hover:border-primary/40 hover:shadow-md focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-sm font-bold tracking-wide text-primary uppercase">{assignment.course}</p>
                      <h2 className="mt-1 text-xl leading-snug font-semibold">{assignment.title}</h2>
                    </div>
                    <ChevronRight
                      className="mt-1 size-5 shrink-0 text-muted-foreground transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-primary"
                      aria-hidden="true"
                    />
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {assignment.submission_count} kiriman · dibuat{" "}
                    {new Date(assignment.created_at).toLocaleDateString("id-ID", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })}
                  </p>
                  <div className="mt-auto flex flex-col gap-2 border-t border-border pt-4">
                    {assignment.latest_run ? (
                      <>
                        <div className="flex items-center justify-between gap-2">
                          <StatusBadge {...runStatus(assignment.latest_run.status)} />
                          <span className="text-sm text-muted-foreground tabular-nums">
                            {done} dari {total} kiriman
                          </span>
                        </div>
                        <div
                          className="h-1.5 overflow-hidden rounded-full bg-muted"
                          role="progressbar"
                          aria-label="Kiriman selesai dinilai"
                          aria-valuemin={0}
                          aria-valuemax={total}
                          aria-valuenow={done}
                        >
                          <div
                            className="h-full rounded-full bg-primary transition-[width] duration-300"
                            style={{ width: `${total ? (done / total) * 100 : 0}%` }}
                          />
                        </div>
                      </>
                    ) : (
                      <span className="text-sm text-muted-foreground">Belum dinilai</span>
                    )}
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
