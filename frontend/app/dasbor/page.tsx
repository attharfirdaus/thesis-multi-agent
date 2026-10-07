"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError, api, type User } from "@/lib/api";

export default function DasborPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [busy, setBusy] = useState(true);

  useEffect(() => {
    let active = true;
    api
      .me()
      .then(({ user }) => {
        if (active) setUser(user);
      })
      .catch((err) => {
        // 401 means the session is gone; anything else is shown as-is on the login screen.
        if (active && (!(err instanceof ApiError) || err.status === 401)) router.replace("/masuk");
      })
      .finally(() => {
        if (active) setBusy(false);
      });
    return () => {
      active = false;
    };
  }, [router]);

  async function onLogout() {
    try {
      await api.logout();
    } finally {
      router.replace("/masuk");
    }
  }

  if (busy) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <p className="text-muted-foreground">Memuat…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col gap-6 p-6">
      <header className="flex items-center justify-between gap-4 border-b pb-4">
        <div>
          <p className="text-sm text-muted-foreground">Penilaian Kedalaman Analisis Mahasiswa</p>
          <h1 className="text-xl font-semibold">{user?.name}</h1>
        </div>
        <Button variant="outline" onClick={onLogout}>
          Keluar
        </Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Belum ada tugas</CardTitle>
          <CardDescription>
            Buat tugas pertama untuk mulai mengunggah pekerjaan mahasiswa.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button disabled aria-disabled>
            Buat tugas
          </Button>
          <p className="mt-3 text-sm text-muted-foreground">
            Tombol ini aktif pada tahap berikutnya.
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
