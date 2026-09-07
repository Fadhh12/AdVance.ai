import Link from "next/link";

// Minimal — no fabricated social links (DESIGN_SYSTEM.md §5.5).
export function MarketingFooter() {
  return (
    <footer className="border-t border-paper-ink/10 bg-paper">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-6 py-8 text-sm text-paper-ink-muted md:flex-row">
        <span>© {new Date().getFullYear()} adVance.AI</span>
        <div className="flex gap-5">
          <Link href="/login" className="hover:text-paper-ink">
            Masuk
          </Link>
          <Link href="/register" className="hover:text-paper-ink">
            Daftar
          </Link>
        </div>
      </div>
    </footer>
  );
}
