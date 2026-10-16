"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { StatusBadge, runStatus } from "@/components/status-badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { API_BASE, api, type AssignmentDetail, type RunResults } from "@/lib/api";
import { levelLabel, scoreLevel } from "@/lib/labels";

type SortKey = "pseudonym" | "level" | "review";

type Row = {
  id: string;
  pseudonym: string;
  level: string | null;
  indicators: Record<string, string>;
  flagged: boolean;
};

export default function HasilPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [detail, setDetail] = useState<AssignmentDetail | null>(null);
  const [results, setResults] = useState<RunResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("pseudonym");
  const [ascending, setAscending] = useState(true);
  const [levelFilter, setLevelFilter] = useState("");

  const load = useCallback(
    () =>
      api
        .getAssignment(id)
        .then(async (data) => {
          setDetail(data);
          // FR-09 reads the newest run; an older run stays available through the export of its own id.
          const newest = data.runs[0];
          setResults(newest ? await api.getRunResults(newest.id) : null);
        })
        .catch((err: unknown) => setError(err instanceof Error ? err.message : "Gagal memuat hasil.")),
    [id],
  );

  useEffect(() => {
    void load();
  }, [load]);

  const run = detail?.runs[0] ?? null;
  const scores = results?.submissions ?? [];
  const levelNames = results?.level_names ?? {};

  const rows: Row[] = scores.map((submission) => {
    const indicators: Record<string, string> = {};
    for (const score of submission.scores) {
      if (score.dimension === "metacognitive") indicators[score.indicator ?? "Indikator lain"] = score.level;
    }
    return {
      id: submission.submission_id,
      pseudonym: submission.pseudonym,
      level: submission.scores.find((score) => score.dimension === "cognitive")?.level ?? null,
      indicators,
      flagged: (submission.review_flags ?? []).length > 0,
    };
  });

  const indicatorColumns: string[] = [];
  for (const row of rows) {
    for (const indicator of Object.keys(row.indicators)) {
      if (!indicatorColumns.includes(indicator)) indicatorColumns.push(indicator);
    }
  }

  const levels: string[] = [];
  for (const row of rows) {
    if (row.level !== null && !levels.includes(row.level)) levels.push(row.level);
  }

  const visible = rows
    .filter((row) => levelFilter === "" || row.level === levelFilter)
    .sort((a, b) => {
      const direction = ascending ? 1 : -1;
      if (sortKey === "pseudonym") return a.pseudonym.localeCompare(b.pseudonym, "id") * direction;
      if (sortKey === "review") return (Number(a.flagged) - Number(b.flagged)) * direction;
      // Sorting stays on the code: the codes are the rubric's own order, while the displayed name is prose.
      return (a.level ?? "").localeCompare(b.level ?? "", "id", { numeric: true }) * direction;
    });

  function toggleSort(key: SortKey) {
    if (key === sortKey) setAscending((previous) => !previous);
    else {
      setSortKey(key);
      setAscending(true);
    }
  }

  const sortState = (key: SortKey) =>
    key === sortKey ? (ascending ? "ascending" : "descending") : ("none" as const);

  const sortableHeader = (key: SortKey, label: string) => (
    <th scope="col" aria-sort={sortState(key)} className="py-2 pr-4 font-medium">
      <button
        type="button"
        onClick={() => toggleSort(key)}
        className="inline-flex items-center gap-1 rounded underline-offset-4 hover:underline focus-visible:ring-3 focus-visible:ring-ring/50"
      >
        {label}
        <span aria-hidden className="text-muted-foreground">
          {key === sortKey ? (ascending ? "▲" : "▼") : "↕"}
        </span>
      </button>
    </th>
  );

  return (
    <AppShell>
      {detail === null ? (
        <p className="text-muted-foreground">Memuat…</p>
      ) : (
        <>
          <header className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold">Hasil penilaian</h1>
              <p className="text-muted-foreground">
                {detail.title} · {detail.course}
              </p>
            </div>
            <Link href={`/tugas/${id}`} className="underline underline-offset-4 hover:text-foreground">
              Kembali ke tugas
            </Link>
          </header>

          {error ? (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : null}

          {run === null ? (
            <Card>
              <CardContent>
                <p>Belum ada penilaian untuk tugas ini. Jalankan penilaian dari halaman tugas.</p>
              </CardContent>
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Ekspor hasil</CardTitle>
                  <CardDescription>
                    Berkas memuat nilai, kutipan bukti, catatan tinjauan, dan umpan balik per kiriman.
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  <div className="flex flex-wrap gap-3">
                    <Button asChild variant="outline">
                      <a href={`${API_BASE}/runs/${run.id}/export.csv`}>Ekspor CSV</a>
                    </Button>
                    <Button asChild variant="outline">
                      <a href={`${API_BASE}/runs/${run.id}/export.xlsx`}>Ekspor XLSX</a>
                    </Button>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Status penilaian: <StatusBadge {...runStatus(run.status)} />
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Nilai per kiriman</CardTitle>
                  <CardDescription>
                    Kolom setelah Tingkat Kognitif adalah indikator metakognitif. Klik baris untuk membaca
                    bukti dan meninjau nilainya.
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  <div className="flex flex-col gap-2 sm:max-w-xs">
                    <Label htmlFor="level_filter">Saring tingkat kognitif</Label>
                    <select
                      id="level_filter"
                      value={levelFilter}
                      onChange={(event) => setLevelFilter(event.target.value)}
                      className="h-8 w-full rounded-lg border border-input bg-transparent px-2 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                    >
                      <option value="">Semua tingkat</option>
                      {levels.map((level) => (
                        <option key={level} value={level}>
                          {levelLabel(level, levelNames)}
                        </option>
                      ))}
                    </select>
                  </div>

                  {visible.length === 0 ? (
                    <p className="text-muted-foreground">
                      {rows.length === 0
                        ? "Penilaian ini belum menghasilkan nilai."
                        : "Tidak ada kiriman pada tingkat kognitif yang dipilih."}
                    </p>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse text-left">
                        <thead>
                          <tr className="border-b">
                            {sortableHeader("pseudonym", "Pseudonim")}
                            {sortableHeader("level", "Tingkat Kognitif")}
                            {indicatorColumns.map((indicator) => (
                              <th key={indicator} scope="col" className="py-2 pr-4 font-medium">
                                {indicator}
                              </th>
                            ))}
                            {sortableHeader("review", "Tinjauan")}
                          </tr>
                        </thead>
                        <tbody>
                          {visible.map((row) => (
                            <tr
                              key={row.id}
                              onClick={() => router.push(`/kiriman/${row.id}`)}
                              className="cursor-pointer border-b last:border-0 hover:bg-muted/60"
                            >
                              <td className="py-2 pr-4">
                                <Link
                                  href={`/kiriman/${row.id}`}
                                  className="underline underline-offset-4 hover:text-foreground"
                                >
                                  {row.pseudonym}
                                </Link>
                              </td>
                              <td className="py-2 pr-4">
                                {row.level === null ? "—" : levelLabel(scoreLevel(row.level), levelNames)}
                              </td>
                              {indicatorColumns.map((indicator) => (
                                <td key={indicator} className="py-2 pr-4">
                                  {row.indicators[indicator] === undefined
                                    ? "—"
                                    : scoreLevel(row.indicators[indicator])}
                                </td>
                              ))}
                              <td className="py-2 pr-4">
                                {row.flagged ? (
                                  <StatusBadge tone="amber" label="Perlu Ditinjau" />
                                ) : (
                                  <span className="text-muted-foreground">Sesuai</span>
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
        </>
      )}
    </AppShell>
  );
}
