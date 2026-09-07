import Link from "next/link";

import { Button } from "@/components/ui/button";

// A dark band (workspace palette) inside the otherwise light marketing page — a
// deliberate contrast beat before the footer, not decoration for its own sake, and
// it previews the actual in-app color scheme rather than inventing a third palette.
export function CtaBand() {
  return (
    <section className="border-t border-paper-ink/10 bg-canvas">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-5 px-6 py-16 text-center md:py-20">
        <h2 className="font-display text-3xl text-ink md:text-4xl">
          Bikin video pertamamu, gratis.
        </h2>
        <p className="max-w-md text-ink-muted">
          Nggak perlu isi form. Langsung masuk sebagai tamu, upload foto pertamamu.
        </p>
        <Link href="/app">
          <Button size="lg">Mulai Gratis</Button>
        </Link>
      </div>
    </section>
  );
}
