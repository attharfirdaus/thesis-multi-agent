/**
 * Browser-side API client.
 *
 * Every call to the backend happens in the browser, never in a server component: the Next.js
 * server then never touches student data, which keeps the hosting decision free of privacy
 * consequences (see DECISIONS.md, O-5 and O-7).
 *
 * The session cookie is httpOnly and set by the API; the CSRF cookie is readable and echoed
 * back in a header (double submit).
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export type User = { id: string; email: string; name: string; role: "lecturer" | "admin" };

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function csrfToken(): string {
  const match = document.cookie.match(/(?:^|;\s*)ta_csrf=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

/**
 * The API speaks English; the interface speaks Bahasa Indonesia (PRD §9).
 * Message codes would be cleaner and arrive with the language toggle (FR-18); until then this
 * map is the whole translation layer.
 */
const MESSAGES_ID: Record<string, string> = {
  "Invalid email or password.": "Email atau kata sandi salah.",
  "Email already registered.": "Email ini sudah terdaftar.",
  "Not signed in.": "Anda belum masuk.",
  "Session expired.": "Sesi berakhir. Silakan masuk kembali.",
  "Session not found.": "Sesi tidak ditemukan. Silakan masuk kembali.",
  "CSRF check failed.": "Permintaan ditolak. Muat ulang halaman lalu coba lagi.",
  "Too many login attempts. Try again later.": "Terlalu banyak percobaan masuk. Coba lagi nanti.",
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken(),
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = "Terjadi kesalahan. Coba lagi.";
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") message = MESSAGES_ID[body.detail] ?? message;
    } catch {
      // non-JSON error body; keep the generic message
    }
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  me: () => request<{ user: User }>("/auth/me"),

  login: (email: string, password: string) =>
    request<{ user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  signup: (email: string, name: string, password: string) =>
    request<{ user: User }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, name, password }),
    }),

  logout: () => request<void>("/auth/logout", { method: "POST" }),
};
