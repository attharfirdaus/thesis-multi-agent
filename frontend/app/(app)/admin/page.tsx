"use client";

import { useCallback, useEffect, useState } from "react";

import { AppShell, useCurrentUser } from "@/components/app-shell";
import { StatusBadge, runStatus } from "@/components/status-badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type AdminRun, type AssignmentSummary, type RubricVersion, type Trace } from "@/lib/api";
import { modeLabel } from "@/lib/labels";

/**
 * The admin area of Bab III.3: model configuration and prompt versions, the rubric editor (KF-12), the
 * research runs — single-agent baseline, R repetitions, final evaluation (KF-11, Bab III.1/III.9) — the
 * run log, and the user list. Technical terms are allowed here and nowhere else.
 */
export default function AdminPage() {
  return (
    <AppShell>
      <AdminArea />
    </AppShell>
  );
}

const TEXTAREA_CLASS =
  "w-full rounded-lg border border-input bg-transparent px-2.5 py-1.5 font-mono text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";
const SELECT_CLASS =
  "h-8 w-full rounded-lg border border-input bg-background px-2 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";

const lines = (value: string) =>
  value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

function AdminArea() {
  const user = useCurrentUser();
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [config, setConfig] = useState<Awaited<ReturnType<typeof api.admin.config>> | null>(null);
  const [rubrics, setRubrics] = useState<RubricVersion[]>([]);
  const [runs, setRuns] = useState<AdminRun[]>([]);
  const [users, setUsers] = useState<Awaited<ReturnType<typeof api.admin.users>>>([]);
  const [assignments, setAssignments] = useState<AssignmentSummary[]>([]);
  const [rubricDraft, setRubricDraft] = useState<{ levels: string; indicators: string; descriptors: string } | null>(
    null,
  );
  const [research, setResearch] = useState({ assignment: "", mode: "multi_agent", repetitions: 5, final: false });
  const [progress, setProgress] = useState<string | null>(null);
  const [traces, setTraces] = useState<{ runId: string; rows: Trace[] } | null>(null);

  const load = useCallback(
    () =>
      Promise.all([
        api.admin.config(),
        api.admin.rubrics(),
        api.admin.runs(),
        api.admin.users(),
        api.listAssignments(),
      ]).then(
        ([c, r, ru, u, a]) => {
          setConfig(c);
          setRubrics(r);
          setRuns(ru);
          setUsers(u);
          setAssignments(a);
        },
        (err: unknown) => setError(err instanceof Error ? err.message : "Gagal memuat area admin."),
      ),
    [],
  );

  useEffect(() => {
    if (user?.role === "admin") void load();
  }, [user, load]);

  if (user?.role !== "admin") {
    return <p className="text-muted-foreground">Hanya admin yang dapat membuka bagian ini.</p>;
  }

  const newest = rubrics[0];
  const draft = rubricDraft ?? {
    levels: (newest?.levels ?? []).join("\n"),
    indicators: (newest?.indicators ?? []).join("\n"),
    descriptors: JSON.stringify(newest?.descriptors ?? {}, null, 2),
  };

  async function onSaveRubric(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setNote(null);
    let descriptors: Record<string, unknown>;
    try {
      descriptors = JSON.parse(draft.descriptors || "{}");
    } catch {
      setError("Deskriptor harus berupa JSON yang valid.");
      return;
    }
    try {
      const saved = await api.admin.saveRubric({
        levels: lines(draft.levels),
        indicators: lines(draft.indicators),
        descriptors,
      });
      setRubricDraft(null);
      setNote(`Rubrik versi ${saved.version} tersimpan dan dipakai untuk semua tugas Anda.`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan rubrik.");
    }
  }

  /** Create the R runs together, then drive each to the end, one after another. */
  async function onResearchRun(event: React.FormEvent) {
    event.preventDefault();
    if (!research.assignment) return;
    if (research.final && !window.confirm("Evaluasi akhir membekukan versi rubrik dan prompt. Lanjutkan?")) return;
    setError(null);
    setNote(null);
    try {
      const created = await api.createRun(
        research.assignment,
        research.mode,
        false,
        research.repetitions,
        research.final,
      );
      const ids = created.group_run_ids?.length ? created.group_run_ids : [created.id];
      for (const [index, runId] of ids.entries()) {
        for (;;) {
          const run = await api.processRun(runId, 5);
          setProgress(`Pengulangan ${index + 1} dari ${ids.length}: ${run.jobs.done ?? 0} kiriman selesai`);
          if (!run.jobs.queued && !run.jobs.running) break;
        }
      }
      setNote(`${ids.length} run selesai dijalankan.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menjalankan run penelitian.");
    } finally {
      setProgress(null);
      await load();
    }
  }

  async function onShowTraces(runId: string) {
    try {
      setTraces({ runId, rows: await api.admin.traces(runId) });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal memuat log run.");
    }
  }

  return (
    <>
      <h1 className="text-2xl font-semibold">Admin</h1>
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

      <Card>
        <CardHeader>
          <CardTitle>Run penelitian</CardTitle>
          <CardDescription>
            Baseline single-agent, R pengulangan dengan konfigurasi identik, dan evaluasi akhir. R ditetapkan
            sebelum run pertama dan tidak dapat ditambah setelah hasil dilihat.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onResearchRun} className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="research-assignment">Tugas</Label>
              <select
                id="research-assignment"
                required
                value={research.assignment}
                onChange={(event) => setResearch({ ...research, assignment: event.target.value })}
                className={SELECT_CLASS}
              >
                <option value="">Pilih tugas…</option>
                {assignments.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.title} ({a.submission_count} kiriman)
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="research-mode">Mode</Label>
              <select
                id="research-mode"
                value={research.mode}
                onChange={(event) => setResearch({ ...research, mode: event.target.value })}
                className={SELECT_CLASS}
              >
                <option value="multi_agent">{modeLabel("multi_agent")}</option>
                <option value="single_agent">{modeLabel("single_agent")}</option>
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="research-r">Jumlah pengulangan (R)</Label>
              <Input
                id="research-r"
                type="number"
                min={1}
                max={10}
                value={research.repetitions}
                onChange={(event) => setResearch({ ...research, repetitions: Number(event.target.value) })}
              />
            </div>
            <div className="flex items-center gap-2 pt-6">
              <input
                id="research-final"
                type="checkbox"
                checked={research.final}
                onChange={(event) => setResearch({ ...research, final: event.target.checked })}
              />
              <Label htmlFor="research-final">Evaluasi akhir (bekukan konfigurasi)</Label>
            </div>
            <div className="flex items-center gap-3 sm:col-span-2">
              <Button type="submit" disabled={progress !== null || !research.assignment}>
                {progress !== null ? "Berjalan…" : "Jalankan"}
              </Button>
              {progress ? <span className="text-sm text-muted-foreground">{progress}</span> : null}
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Log run</CardTitle>
          <CardDescription>Masukan, keluaran terstruktur, latensi, dan galat setiap langkah agen.</CardDescription>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b">
                <th className="py-2 pr-3 font-medium">Waktu</th>
                <th className="py-2 pr-3 font-medium">Tugas</th>
                <th className="py-2 pr-3 font-medium">Mode</th>
                <th className="py-2 pr-3 font-medium">Pengulangan</th>
                <th className="py-2 pr-3 font-medium">Status</th>
                <th className="py-2 font-medium" />
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id} className="border-b align-top">
                  <td className="py-2 pr-3 whitespace-nowrap">{new Date(run.created_at).toLocaleString("id-ID")}</td>
                  <td className="py-2 pr-3">{run.assignment_title}</td>
                  <td className="py-2 pr-3">{modeLabel(run.mode)}</td>
                  <td className="py-2 pr-3">
                    {run.repetition_index}/{run.repetitions}
                    {run.final_evaluation ? " · akhir" : ""}
                  </td>
                  <td className="py-2 pr-3">
                    <StatusBadge {...runStatus(run.status)} />
                    {run.model_unavailable ? <StatusBadge tone="red" label="Model tidak tersedia" /> : null}
                  </td>
                  <td className="py-2">
                    <Button variant="ghost" size="sm" onClick={() => void onShowTraces(run.id)}>
                      Lihat log
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {traces ? (
            <div className="mt-4 flex flex-col gap-3">
              <p className="font-medium">Log run {traces.runId}</p>
              {traces.rows.map((trace) => (
                <details key={trace.id} className="rounded-lg bg-muted/60 p-3">
                  <summary className="cursor-pointer">
                    {trace.submission_pseudonym} · {trace.agent_name} · {trace.latency_ms ?? "—"} ms
                    {trace.error ? ` · galat: ${trace.error}` : ""}
                  </summary>
                  <p className="mt-2 text-sm font-medium">Masukan</p>
                  <pre className="max-h-64 overflow-auto text-xs whitespace-pre-wrap">{trace.input_ref ?? "—"}</pre>
                  <p className="mt-2 text-sm font-medium">Keluaran</p>
                  <pre className="max-h-64 overflow-auto text-xs whitespace-pre-wrap">
                    {JSON.stringify(trace.output_json, null, 2)}
                  </pre>
                </details>
              ))}
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Rubrik</CardTitle>
          <CardDescription>
            Disimpan sebagai versi baru; run lama tetap memakai versi yang direkamnya. Versi terbaru:{" "}
            {newest ? `v${newest.version}${newest.frozen_at ? " (dibekukan)" : ""}` : "belum ada"}.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSaveRubric} className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="rubric-levels">Level kognitif (satu per baris)</Label>
              <textarea
                id="rubric-levels"
                rows={6}
                value={draft.levels}
                onChange={(event) => setRubricDraft({ ...draft, levels: event.target.value })}
                className={TEXTAREA_CLASS}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="rubric-indicators">Indikator metakognitif (satu per baris)</Label>
              <textarea
                id="rubric-indicators"
                rows={6}
                value={draft.indicators}
                onChange={(event) => setRubricDraft({ ...draft, indicators: event.target.value })}
                className={TEXTAREA_CLASS}
              />
            </div>
            <div className="flex flex-col gap-2 sm:col-span-2">
              <Label htmlFor="rubric-descriptors">
                Deskriptor (JSON: <code>levels</code> dan <code>indicators</code>, kode → deskripsi)
              </Label>
              <textarea
                id="rubric-descriptors"
                rows={10}
                value={draft.descriptors}
                onChange={(event) => setRubricDraft({ ...draft, descriptors: event.target.value })}
                className={TEXTAREA_CLASS}
              />
            </div>
            <Button type="submit" variant="outline" className="self-start">
              Simpan sebagai versi baru
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Konfigurasi model dan prompt</CardTitle>
          <CardDescription>Yang akan direkam oleh run baru.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <pre className="rounded-lg bg-muted/60 p-3 text-xs whitespace-pre-wrap">
            {JSON.stringify(config?.llm ?? {}, null, 2)}
          </pre>
          <ul className="text-sm">
            {(config?.prompt_versions ?? []).map((prompt) => (
              <li key={prompt.id}>
                {prompt.agent_name} v{prompt.version}
                {prompt.frozen_at ? " (dibekukan)" : ""}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Pengguna</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="text-sm">
            {users.map((u) => (
              <li key={u.id}>
                {u.name} — {u.email} ({u.role})
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </>
  );
}
