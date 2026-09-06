"use client";

import { signIn, useSession } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

// Guest mode (Phase 6R catatan sesi): "begitu pertama buka app, langsung masuk kayak
// tamu" — no login form on first visit. This page's only job is to get a session (a
// real one if it already exists, a fresh guest one if not) and hand off to /studio.
// `signIn("guest")` is guarded by a ref so React StrictMode's double-effect in dev
// can't spend two guest accounts for one visit; next-auth's own session cookie is
// what actually prevents a repeat guest sign-in on the *next* visit.
export default function EntryPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [failed, setFailed] = useState(false);
  const attempted = useRef(false);

  useEffect(() => {
    if (status === "loading") return;

    if (session) {
      router.replace("/studio");
      return;
    }

    if (attempted.current) return;
    attempted.current = true;

    signIn("guest", { redirect: false }).then((result) => {
      if (result?.ok) {
        router.replace("/studio");
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
        <p className="mt-2 text-sm text-ink-muted">Menyiapkan studio…</p>
      )}
    </main>
  );
}
