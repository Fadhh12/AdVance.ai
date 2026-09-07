import { Play } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { PhoneFrame } from "@/components/ui/phone-frame";

// Abstract "screen" content for the hero's phone mockups — a play glyph + two pill
// bars standing in for a caption, nothing more. Deliberately NOT a fake social-media
// mockup with usernames/like counts/comments (that's fabricated social proof, see
// DESIGN_SYSTEM.md §5.5) — just shapes that read as "this is a vertical video app".
function AbstractScreen({ accent }: { accent: "rec" | "signal" | "alert" }) {
  const accentClass = { rec: "text-rec", signal: "text-signal", alert: "text-alert" }[accent];
  return (
    <PhoneFrame>
      <div className="relative flex h-full flex-col justify-end bg-gradient-to-b from-panel-raised to-canvas p-4">
        <Play
          className={`absolute top-1/2 left-1/2 h-9 w-9 -translate-x-1/2 -translate-y-1/2 ${accentClass}`}
          aria-hidden
        />
        <div className="h-2 w-2/3 rounded-full bg-ink/20" />
        <div className="mt-2 h-2 w-1/3 rounded-full bg-ink/10" />
      </div>
    </PhoneFrame>
  );
}

export function Hero() {
  return (
    <section className="mx-auto flex max-w-6xl flex-col gap-12 px-6 py-16 md:flex-row md:items-center md:py-24">
      <div className="flex-1">
        <h1 className="font-display text-4xl leading-[1.05] tracking-tight text-paper-ink md:text-6xl">
          Dari foto produk, jadi video siap tayang.
        </h1>
        <p className="mt-5 max-w-lg text-base text-paper-ink-muted md:text-lg">
          Upload foto, biarkan AI generate videonya, edit ringan, lalu siapkan caption
          per platform — Instagram, TikTok, dan YouTube.
        </p>
        <div className="mt-8 flex flex-wrap items-center gap-6">
          <Link href="/app">
            <Button size="lg">Mulai Gratis</Button>
          </Link>
          <Link
            href="/login"
            className="text-sm font-medium text-paper-ink underline decoration-paper-ink/30 underline-offset-4 hover:decoration-paper-ink"
          >
            Masuk ke akun
          </Link>
        </div>
        <p className="mt-4 text-xs text-paper-ink-muted">
          Tanpa kartu kredit — langsung coba sebagai tamu.
        </p>
      </div>
      <div className="grid flex-1 grid-cols-3 gap-4">
        <div className="translate-y-6">
          <AbstractScreen accent="signal" />
        </div>
        <AbstractScreen accent="rec" />
        <div className="translate-y-6">
          <AbstractScreen accent="alert" />
        </div>
      </div>
    </section>
  );
}
