import Link from "next/link";

import { Button } from "@/components/ui/button";

// Sticky nav for the marketing page (DESIGN_SYSTEM.md §5.5). Both nav links anchor
// within this same page — the landing page is one continuous page, same "no wizard,
// no unnecessary route hops" principle the /studio canvas already follows.
export function MarketingNav() {
  return (
    <header className="sticky top-0 z-10 border-b border-paper-ink/10 bg-paper/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <span className="font-display text-lg text-paper-ink">adVance.AI</span>
        <nav className="hidden items-center gap-6 text-sm text-paper-ink-muted md:flex">
          <a href="#fitur" className="hover:text-paper-ink">
            Fitur
          </a>
          <a href="#cara-kerja" className="hover:text-paper-ink">
            Cara Kerja
          </a>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm text-paper-ink-muted hover:text-paper-ink">
            Masuk
          </Link>
          <Link href="/app">
            <Button size="sm">Mulai Gratis</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
