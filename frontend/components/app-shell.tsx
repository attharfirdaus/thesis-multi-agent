"use client";

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { ApiError, api, type User } from "@/lib/api";

/**
 * The frame every signed-in screen shares: left sidebar, wordmark, sign-out.
 *
 * It owns the session check so no screen has to decide what a 401 means — a lost session always
 * lands on the login page.
 */
export function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
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

  const dashActive = pathname === "/dasbor";

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="border-b bg-sidebar md:w-64 md:shrink-0 md:border-r md:border-b-0">
        <div className="flex h-full flex-col gap-6 p-6">
          <p className="font-heading leading-snug font-semibold text-primary">
            Penilaian Kedalaman Analisis Mahasiswa
          </p>
          <nav aria-label="Navigasi utama">
            <Link
              href="/dasbor"
              aria-current={dashActive ? "page" : undefined}
              className={`block rounded-lg px-3 py-2 text-base transition-colors hover:bg-muted ${
                dashActive ? "bg-muted font-medium text-primary" : "text-foreground"
              }`}
            >
              Dasbor
            </Link>
          </nav>
          <div className="mt-auto flex flex-col gap-2">
            <p className="text-sm text-muted-foreground">{user?.name}</p>
            <Button variant="outline" onClick={onLogout} className="self-start">
              Keluar
            </Button>
          </div>
        </div>
      </aside>
      <main className="flex-1 bg-muted/40 px-6 py-8">
        <div className="mx-auto flex max-w-5xl flex-col gap-6">{children}</div>
      </main>
    </div>
  );
}
