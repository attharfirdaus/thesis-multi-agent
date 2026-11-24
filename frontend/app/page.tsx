import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { AuthLayout } from "@/components/auth-layout";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <AuthLayout>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-semibold">Mulai menilai</h2>
          <p className="text-muted-foreground">
            Masuk untuk membuat tugas, mengunggah kiriman mahasiswa, dan meninjau hasil penilaian beserta
            kutipan buktinya.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link href="/masuk">
              Masuk
              <ArrowRight data-icon="inline-end" aria-hidden="true" />
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="/daftar">Daftar sebagai dosen</Link>
          </Button>
        </div>
      </div>
    </AuthLayout>
  );
}
