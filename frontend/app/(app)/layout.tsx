"use client";

import type { ReactNode } from "react";

import { AppShell } from "@/components/app-shell";

/**
 * Every signed-in screen shares this layout, so the shell — and its session check — mounts once and
 * stays while the lecturer moves between screens, instead of re-asking who is signed in on each one.
 */
export default function AppLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
