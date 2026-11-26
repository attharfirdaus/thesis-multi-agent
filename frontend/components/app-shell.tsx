"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { GraduationCap, LayoutDashboard, Loader2, LogOut, ShieldCheck } from "lucide-react";

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
        <p className="flex items-center gap-2 text-muted-foreground" role="status">
          <Loader2 className="size-4 animate-spin" aria-hidden="true" />
          Memuat…
        </p>
      </main>
    );
  }

  const links = [
    { href: "/dasbor", label: "Dasbor", icon: LayoutDashboard, show: true },
    { href: "/admin", label: "Admin", icon: ShieldCheck, show: user?.role === "admin" },
  ];

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="bg-sidebar text-sidebar-foreground md:sticky md:top-0 md:h-screen md:w-64 md:shrink-0">
        <div className="flex h-full flex-wrap items-center gap-x-4 gap-y-3 p-4 md:flex-col md:flex-nowrap md:items-stretch md:gap-8 md:p-6">
          <Link
            href="/dasbor"
            className="flex w-full items-center gap-3 rounded-lg outline-none focus-visible:ring-3 focus-visible:ring-sidebar-ring md:w-auto"
          >
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
              <GraduationCap className="size-5" aria-hidden="true" />
            </span>
            <span className="font-heading text-lg leading-tight font-semibold text-white">
              Penilaian Kedalaman Analisis
            </span>
          </Link>
          <nav aria-label="Navigasi utama" className="flex gap-1 md:flex-col">
            {links
              .filter((link) => link.show)
              .map(({ href, label, icon: Icon }) => {
                // Assignments and submissions are reached from the dashboard, so they keep it highlighted.
                const active = href === "/dasbor" ? !pathname.startsWith("/admin") : pathname.startsWith(href);
                return (
                  <Link
                    key={href}
                    href={href}
                    aria-current={active ? "page" : undefined}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-base transition-colors duration-200 outline-none focus-visible:ring-3 focus-visible:ring-sidebar-ring ${
                      active
                        ? "bg-sidebar-accent font-bold text-sidebar-accent-foreground"
                        : "text-sidebar-foreground/85 hover:bg-sidebar-accent/60 hover:text-white"
                    }`}
                  >
                    <Icon className="size-[18px]" aria-hidden="true" />
                    {label}
                  </Link>
                );
              })}
          </nav>
          <div className="ml-auto flex items-center gap-3 md:mt-auto md:ml-0 md:flex-col md:items-stretch md:border-t md:border-sidebar-border md:pt-5">
            <div className="min-w-0">
              <p className="truncate text-sm font-bold text-white">{user?.name}</p>
              <p className="text-xs text-sidebar-foreground/80">
                {user?.role === "admin" ? "Admin peneliti" : "Dosen"}
              </p>
            </div>
            <button
              type="button"
              onClick={onLogout}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-sidebar-foreground/90 transition-colors duration-200 outline-none hover:bg-sidebar-accent hover:text-white focus-visible:ring-3 focus-visible:ring-sidebar-ring"
            >
              <LogOut className="size-4" aria-hidden="true" />
              Keluar
            </button>
          </div>
        </div>
      </aside>
      <main className="min-w-0 flex-1 px-4 py-6 md:px-10 md:py-10">
        <UserContext.Provider value={user}>
          <div className="mx-auto flex max-w-6xl flex-col gap-6">{children}</div>
        </UserContext.Provider>
      </main>
    </div>
  );
}

/**
 * The title block every signed-in screen opens with: an optional eyebrow (where the lecturer is), the
 * serif title, one sentence of purpose, and the screen's primary action on the right.
 */
export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4 border-b border-border pb-6">
      <div className="flex min-w-0 flex-col gap-1.5">
        {eyebrow ? (
          <div className="text-sm font-bold tracking-wide text-primary uppercase">{eyebrow}</div>
        ) : null}
        <h1>{title}</h1>
        {description ? <p className="max-w-2xl text-muted-foreground">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-3">{actions}</div> : null}
    </header>
  );
}
