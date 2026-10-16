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

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

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
  "No rubric version is seeded for this account; run scripts/seed_rubric.py first.":
    "Rubrik belum tersedia untuk akun ini. Hubungi pengelola sistem untuk menyiapkan rubrik.",
  "Assignment not found.": "Tugas tidak ditemukan.",
  "Submission not found.": "Kiriman tidak ditemukan.",
  "Run not found.": "Penilaian tidak ditemukan.",
  "Score not found.": "Nilai tidak ditemukan.",
  "An override needs a new level and a reason.":
    "Perubahan nilai memerlukan tingkat baru dan alasan singkat.",
  "new_level must be one of the rubric's levels.": "Tingkat yang dipilih tidak ada di dalam rubrik.",
  "No feedback has been generated for this submission yet.":
    "Umpan balik belum tersedia untuk kiriman ini.",
  "The student's analysis cannot be empty.": "Analisis mahasiswa tidak boleh kosong.",
  "This submission is still queued or being graded; stop the run first.":
    "Kiriman ini masih menunggu atau sedang dinilai. Hentikan penilaian terlebih dahulu.",
  "Every submission in this assignment has already been graded.":
    "Semua kiriman pada tugas ini sudah dinilai.",
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      // A multipart body carries its own boundary; setting the JSON type here would break it.
      ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
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

/** Job counts per status (`queued`, `running`, `done`, `failed`) — PRD §10 `Job`. */
export type JobCounts = Record<string, number>;

export type RunInFlight = { submission_id: string; pseudonym: string };

/**
 * A run. The list endpoint's `latest_run` carries only the id, status and counters; the run endpoints
 * add `in_flight`, which names the submissions being graded right now.
 */
export type RunSummary = {
  id: string;
  status: string;
  jobs: JobCounts;
  in_flight?: RunInFlight[];
};

export type AssignmentSummary = {
  id: string;
  title: string;
  course: string;
  prompt_text: string | null;
  created_at: string;
  submission_count: number;
  /** How many of its submissions any run has already scored; the rest is what `only_ungraded` covers. */
  graded_count: number;
  latest_run: RunSummary | null;
};

/** Fields the frozen contract does not pin down are optional, so a shape change cannot crash a page. */
export type SubmissionSummary = {
  id: string;
  pseudonym: string;
  segmentation_status: string;
  review_flags?: string[];
  import_warnings?: string[];
};

export type AssignmentDetail = AssignmentSummary & {
  submissions: SubmissionSummary[];
  runs: RunSummary[];
};

export type Rubric = {
  version: string;
  levels: string[];
  indicators: string[];
  /** The rubric's own name per level code (`{"C4": "Analyze"}`); empty when the frozen rubric had none. */
  level_names: Record<string, string>;
};

export type Evidence = { quote: string; start_offset: number; end_offset: number };

export type Score = {
  id: string;
  dimension: "cognitive" | "metacognitive";
  indicator: string | null;
  level: string;
  rationale: string | null;
  evidence: Evidence[];
};

export type Feedback = {
  generated_text: string | null;
  edited_text: string | null;
  edited_by: string | null;
  exported_at: string | null;
};

export type Review = {
  system_score_id: string;
  action: "accept" | "override";
  new_level: string | null;
  reason: string | null;
  reviewed_at: string;
};

export type SubmissionDetail = {
  id: string;
  assignment_id: string;
  pseudonym: string;
  segmentation_status: string;
  review_flags?: string[];
  import_warnings?: string[];
  created_at?: string;
  ai_output_text: string | null;
  student_analysis_text: string | null;
  rubric: Rubric | null;
  run: { id: string; status: string; mode: string } | null;
  scores: Score[];
  feedback: Feedback | null;
  reviews: Review[];
};

export type ImportedFile = {
  filename: string;
  status: "imported" | "failed";
  pseudonym?: string | null;
  warnings?: string[];
  error?: string | null;
};

export type ImportResult = { assignment_id: string; files: ImportedFile[] };

export type RunResults = {
  run_id: string;
  status: string;
  /** The run's frozen rubric levels, by code. Empty for a rubric that carried no names. */
  level_names: Record<string, string>;
  submissions: {
    submission_id: string;
    pseudonym: string;
    review_flags?: string[];
    /** Exactly the text the export writes: `coalesce(edited_text, generated_text)`. */
    feedback_text: string | null;
    /** Whether that text is the lecturer's edit rather than the generated one. */
    feedback_edited: boolean;
    scores: {
      id: string;
      dimension: "cognitive" | "metacognitive";
      indicator: string | null;
      level: string;
      rationale: string | null;
      evidence: Evidence[];
      /** The newest lecturer review of this score, or null while nobody has judged it. */
      review: Review | null;
    }[];
  }[];
};

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

  listAssignments: () => request<AssignmentSummary[]>("/assignments"),

  createAssignment: (body: { title: string; course: string; prompt_text?: string }) =>
    request<AssignmentSummary>("/assignments", { method: "POST", body: JSON.stringify(body) }),

  getAssignment: (id: string) => request<AssignmentDetail>(`/assignments/${id}`),

  uploadSubmissions: (assignmentId: string, files: File[]) => {
    const form = new FormData();
    for (const file of files) form.append("files", file);
    return request<ImportResult>(`/assignments/${assignmentId}/submissions`, {
      method: "POST",
      body: form,
    });
  },

  getSubmission: (id: string) => request<SubmissionDetail>(`/submissions/${id}`),

  deleteSubmission: (id: string) => request<void>(`/submissions/${id}`, { method: "DELETE" }),

  patchSegmentation: (id: string, analysisStart: number) =>
    request<unknown>(`/submissions/${id}/segmentation`, {
      method: "PATCH",
      body: JSON.stringify({ analysis_start: analysisStart }),
    }),

  /** `onlyUngraded` queues jobs for submissions no run has scored; false re-grades everything (PRD §11). */
  createRun: (assignmentId: string, mode = "multi_agent", onlyUngraded = false) =>
    request<RunSummary>(`/assignments/${assignmentId}/runs?mode=${mode}&only_ungraded=${onlyUngraded}`, {
      method: "POST",
    }),

  processRun: (runId: string, limit: number, signal?: AbortSignal) =>
    request<RunSummary>(`/runs/${runId}/process?limit=${limit}`, { method: "POST", signal }),

  getRun: (runId: string) => request<RunSummary>(`/runs/${runId}`),

  cancelRun: (runId: string) => request<RunSummary>(`/runs/${runId}/cancel`, { method: "POST" }),

  getRunResults: (runId: string) => request<RunResults>(`/runs/${runId}/results`),

  reviewScore: (
    scoreId: string,
    body: { action: "accept" | "override"; new_level?: string; reason?: string },
  ) =>
    request<Review>(`/system_scores/${scoreId}/review`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  patchFeedback: (submissionId: string, editedText: string) =>
    request<Feedback>(`/submissions/${submissionId}/feedback`, {
      method: "PATCH",
      body: JSON.stringify({ edited_text: editedText }),
    }),
};
