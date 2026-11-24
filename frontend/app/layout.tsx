import type { ReactNode } from "react";
import type { Metadata } from "next";
import { Atkinson_Hyperlegible, Crimson_Pro, Geist_Mono } from "next/font/google";
import "./globals.css";

// Academic/Research pairing (ui-ux-pro-max): a scholarly serif for headings, and a typeface designed
// for legibility for everything a lecturer reads at length.
const body = Atkinson_Hyperlegible({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const display = Crimson_Pro({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Penilaian Kedalaman Analisis Mahasiswa",
  description:
    "Sistem multi-agent untuk menilai kedalaman kognitif dan metakognitif analisis mahasiswa pada tugas yang mengizinkan AI.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="id" className={`${body.variable} ${display.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
