import type { ReactNode } from "react";
import { GraduationCap, Quote, ShieldCheck, UserCheck } from "lucide-react";

/** What the system promises a lecturer, stated once, on the screens they see before signing in. */
const PRINCIPLES = [
  {
    icon: Quote,
    title: "Setiap nilai punya bukti",
    body: "Tingkat kognitif dan indikator metakognitif selalu disertai kutipan dari tulisan mahasiswa.",
  },
  {
    icon: UserCheck,
    title: "Dosen tetap memutuskan",
    body: "Nilai sistem dapat diterima, dikoreksi, atau dikomentari tanpa menimpa nilai aslinya.",
  },
  {
    icon: ShieldCheck,
    title: "Identitas mahasiswa terlindungi",
    body: "Nama, NIM, dan kontak dihapus sebelum teks dikirim ke model bahasa.",
  },
];

/**
 * The two-column frame of the public screens: the system's purpose on the left, the task on the right.
 * Below `lg` the task comes first, so a lecturer on a narrow screen does not scroll past prose to sign in.
 */
export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)]">
      <section className="order-2 flex flex-col gap-10 bg-sidebar lg:order-1 px-6 py-10 text-sidebar-foreground md:px-12 lg:py-14">
        <div className="flex items-center gap-3">
          <span className="flex size-10 items-center justify-center rounded-lg bg-white text-sidebar">
            <GraduationCap className="size-5" aria-hidden="true" />
          </span>
          <span className="text-sm font-bold tracking-wide text-white uppercase">
            Penilaian Kedalaman Analisis
          </span>
        </div>
        <div className="flex max-w-lg flex-col gap-4">
          <h1 className="text-4xl leading-tight text-white md:text-5xl">
            Seberapa dalam mahasiswa menganalisis keluaran AI?
          </h1>
          <p className="text-lg text-sidebar-foreground/90">
            Sistem multi-agen untuk tugas yang mengizinkan AI: menilai dimensi kognitif (Taksonomi Bloom) dan
            metakognitif dari analisis mahasiswa terhadap keluaran AI.
          </p>
        </div>
        <ul className="flex max-w-lg flex-col gap-5">
          {PRINCIPLES.map(({ icon: Icon, title, body }) => (
            <li key={title} className="flex gap-4">
              <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-sidebar-accent text-white">
                <Icon className="size-5" aria-hidden="true" />
              </span>
              <div>
                <p className="font-bold text-white">{title}</p>
                <p className="text-sidebar-foreground/85">{body}</p>
              </div>
            </li>
          ))}
        </ul>
        <p className="mt-auto text-sm text-sidebar-foreground/75">
          Artefak penelitian tesis Magister Sistem dan Teknologi Informasi, Institut Teknologi Bandung.
        </p>
      </section>
      <main className="order-1 flex items-center justify-center px-6 py-10 lg:order-2">
        <div className="w-full max-w-md">{children}</div>
      </main>
    </div>
  );
}
