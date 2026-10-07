import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="flex max-w-xl flex-col gap-6">
        <p className="text-sm font-medium tracking-wide text-muted-foreground">
          PENILAIAN KEDALAMAN ANALISIS MAHASISWA
        </p>
        <h1 className="text-3xl font-semibold leading-tight">
          Menilai seberapa dalam mahasiswa menganalisis keluaran AI pada tugas yang mengizinkan AI.
        </h1>
        <p className="text-muted-foreground">
          Setiap nilai disertai kutipan bukti dari tulisan mahasiswa, sehingga dapat ditelusuri dan
          diperiksa ulang oleh dosen.
        </p>
        <div className="flex gap-3">
          <Button asChild>
            <Link href="/masuk">Masuk</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/daftar">Daftar sebagai dosen</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
