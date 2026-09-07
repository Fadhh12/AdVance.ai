"use client";

import { signIn, useSession } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

// Guest bootstrap (moved here from "/" in Phase 6R-7 — see DESIGN_SYSTEM.md §5.5 and
// PROGRESS.md): "/" is now the public marketing page and must never spend a guest
// account just from being viewed. Every "Mulai Gratis" CTA points here instead.
// `signIn("guest")` is guarded by a ref so React StrictMode's double-effect in dev
// can't spend two guest accounts for one visit; next-auth's own session cookie is
// what actually prevents a repeat guest sign-in on the *next* visit.
export default function AppEntryPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [failed, setFailed] = useState(false);
  const attempted = useRef(false);

  useEffect(() => {
    if (status === "loading") return;

    if (session) {
      router.replace("/dashboard");
      return;
    }

    if (attempted.current) return;
    attempted.current = true;

    signIn("guest", { redirect: false }).then((result) => {
      if (result?.ok) {
        router.replace("/dashboard");
      } else {
        setFailed(true);
      }
    });
  }, [session, status, router]);

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
      <span
        className={`h-2 w-2 rounded-full bg-rec ${failed ? "" : "animate-pulse"}`}
        aria-hidden
      />
      <h1 className="font-display text-4xl tracking-tight text-ink">adVance.AI</h1>
      <p className="max-w-md text-sm text-ink-muted">
        Upload foto produk, biarkan AI generate videonya, edit ringan, lalu siapkan untuk
        Instagram, TikTok, dan YouTube.
      </p>

      {failed ? (
        <div className="mt-2 flex flex-col items-center gap-2">
          <p className="text-sm text-alert">
            Tidak bisa masuk sebagai tamu — backend mungkin belum jalan.
          </p>
          <div className="flex gap-4 text-sm">
            <Link href="/login" className="text-rec hover:underline">
              Masuk
            </Link>
            <Link href="/register" className="text-rec hover:underline">
              Daftar
            </Link>
          </div>
        </div>
      ) : (
        <p className="mt-2 text-sm text-ink-muted">Menyiapkan dashboard…</p>
      )}
    </main>
  );
}
