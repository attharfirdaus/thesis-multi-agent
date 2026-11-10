"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { ApiError, api, type User } from "@/lib/api";

const UserContext = createContext<User | null>(null);

/** The signed-in user, for a screen that shows admin-only controls (Bab III.3). */
export const useCurrentUser = () => useContext(UserContext);

/**
 * Renders its children only for an admin. A component, not a hook, because the screens render the
 * shell themselves: only what sits inside it can read the user.
 */
export function AdminOnly({ children }: { children: ReactNode }) {
  return useCurrentUser()?.role === "admin" ? <>{children}</> : null;
}

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
  const adminActive = pathname === "/admin";
  const linkClass = (active: boolean) =>
    `block rounded-lg px-3 py-2 text-base transition-colors hover:bg-muted ${
      active ? "bg-muted font-medium text-primary" : "text-foreground"
    }`;

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="border-b bg-sidebar md:w-64 md:shrink-0 md:border-r md:border-b-0">
        <div className="flex h-full flex-wrap items-center gap-x-4 gap-y-2 p-3 md:flex-col md:flex-nowrap md:items-stretch md:gap-6 md:p-6">
          <p className="w-full font-heading leading-snug font-semibold text-primary md:w-auto">
            Penilaian Kedalaman Analisis Mahasiswa
          </p>
          <nav aria-label="Navigasi utama" className="flex gap-1 md:block">
            <Link href="/dasbor" aria-current={dashActive ? "page" : undefined} className={linkClass(dashActive)}>
              Dasbor
            </Link>
            {user?.role === "admin" ? (
              <Link href="/admin" aria-current={adminActive ? "page" : undefined} className={linkClass(adminActive)}>
                Admin
              </Link>
            ) : null}
          </nav>
          <div className="ml-auto flex items-center gap-2 md:mt-auto md:ml-0 md:flex-col md:items-start">
            <p className="text-sm text-muted-foreground">{user?.name}</p>
            <Button variant="outline" onClick={onLogout} className="md:self-start">
              Keluar
            </Button>
          </div>
        </div>
      </aside>
      <main className="min-w-0 flex-1 bg-muted/40 px-4 py-6 md:px-6 md:py-8">
        <UserContext.Provider value={user}>
          <div className="mx-auto flex max-w-5xl flex-col gap-6">{children}</div>
        </UserContext.Provider>
      </main>
    </div>
  );
}
