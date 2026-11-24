import { cn } from "@/lib/utils";

type Tone = "green" | "amber" | "red" | "neutral";

/** PRD §9: status colours never travel alone, so the label is required, not optional. */
const TONES: Record<Tone, string> = {
  green: "bg-emerald-50 text-emerald-900 ring-emerald-700/30",
  amber: "bg-amber-50 text-amber-900 ring-amber-700/40",
  red: "bg-red-50 text-red-900 ring-red-700/30",
  neutral: "bg-muted text-foreground ring-foreground/15",
};

const DOTS: Record<Tone, string> = {
  green: "bg-emerald-600",
  amber: "bg-amber-600",
  red: "bg-red-600",
  neutral: "bg-slate-500",
};

export function StatusBadge({
  tone = "neutral",
  label,
  className,
}: {
  tone?: Tone;
  label: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-sm font-medium whitespace-nowrap ring-1 ring-inset",
        TONES[tone],
        className,
      )}
    >
      <span aria-hidden="true" className={cn("size-1.5 rounded-full", DOTS[tone])} />
      {label}
    </span>
  );
}

type StatusMeta = { label: string; tone: Tone };

const RUN_STATUS: Record<string, StatusMeta> = {
  queued: { label: "Menunggu", tone: "neutral" },
  running: { label: "Sedang berjalan", tone: "neutral" },
  done: { label: "Selesai", tone: "green" },
  cancelled: { label: "Dibatalkan", tone: "neutral" },
  failed: { label: "Gagal", tone: "red" },
};

const SEGMENTATION_STATUS: Record<string, StatusMeta> = {
  pending: { label: "Belum dipisah", tone: "amber" },
  segmented: { label: "Sudah dipisah otomatis", tone: "green" },
  confirmed: { label: "Sudah dikonfirmasi", tone: "green" },
  failed: { label: "Gagal dipisah", tone: "red" },
};

export const runStatus = (status: string): StatusMeta =>
  RUN_STATUS[status] ?? { label: status, tone: "neutral" };

export const segmentationStatus = (status: string): StatusMeta =>
  SEGMENTATION_STATUS[status] ?? { label: status, tone: "neutral" };
