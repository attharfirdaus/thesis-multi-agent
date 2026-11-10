"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

import { AppShell } from "@/components/app-shell";
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
    <AppShell>
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Dasbor</h1>
          <p className="text-muted-foreground">Tugas yang Anda kelola beserta status penilaiannya.</p>
        </div>
        {formOpen ? null : (
          <Button onClick={() => setFormOpen(true)}>Buat tugas</Button>
        )}
      </header>

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
                  className="w-full rounded-lg border border-input bg-transparent px-2.5 py-1.5 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
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
        <p className="text-muted-foreground">Memuat…</p>
      ) : assignments.length === 0 ? (
        <Card>
          <CardContent>
            <p>Belum ada tugas. Buat tugas pertama untuk mulai mengunggah pekerjaan mahasiswa.</p>
          </CardContent>
        </Card>
      ) : (
        <ul className="flex flex-col gap-3">
          {assignments.map((assignment) => {
            const jobs = assignment.latest_run?.jobs ?? {};
            const total = Object.values(jobs).reduce((sum, count) => sum + count, 0);
            const done = jobs.done ?? 0;
            return (
              <li key={assignment.id}>
                <Link
                  href={`/tugas/${assignment.id}`}
                  className="block rounded-xl bg-card p-4 ring-1 ring-foreground/10 transition-colors hover:bg-muted/60 focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="font-medium">{assignment.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {assignment.course} · {assignment.submission_count} kiriman · dibuat{" "}
                        {new Date(assignment.created_at).toLocaleDateString("id-ID", {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                        })}
                      </p>
                    </div>
                    {assignment.latest_run ? (
                      <div className="flex items-center gap-2">
                        <StatusBadge {...runStatus(assignment.latest_run.status)} />
                        <span className="text-sm text-muted-foreground">
                          {done} dari {total} kiriman
                        </span>
                      </div>
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
    </AppShell>
  );
}
