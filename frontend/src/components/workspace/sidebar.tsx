import Link from "next/link";

// Bagian yang belum dibangun ditandai "Segera" — bukan link mati tanpa penjelasan.
// Urutan mengikuti alur produk (Task Breakdown Phase 1-7), bukan alfabetis.
// "Generate Studio"/"Editor"/"Publish" digabung jadi satu "Studio" (Phase 6R-4) —
// alurnya sekarang satu workspace berkelanjutan, bukan lagi 3 halaman terpisah.
const SECTIONS: Array<{ label: string; href: string; available: boolean }> = [
  { label: "Dashboard", href: "/dashboard", available: true },
  { label: "Studio", href: "/studio", available: true },
  { label: "Media Library", href: "/media", available: true },
  { label: "Content Calendar", href: "/calendar", available: true },
  { label: "Connected Accounts", href: "#", available: false },
  { label: "Analytics", href: "#", available: false },
  { label: "Billing", href: "#", available: false },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <aside className="flex h-full w-64 shrink-0 flex-col gap-6 overflow-y-auto bg-panel px-4 py-6 lg:w-56">
      <span className="font-display text-lg text-ink">adVance.AI</span>
      <nav className="flex flex-col gap-1">
        {SECTIONS.map((section) =>
          section.available ? (
            <Link
              key={section.label}
              href={section.href}
              onClick={onNavigate}
              className="rounded-md px-3 py-2 text-sm text-ink transition-colors hover:bg-panel-raised"
            >
              {section.label}
            </Link>
          ) : (
            <span
              key={section.label}
              className="flex items-center justify-between rounded-md px-3 py-2 text-sm text-ink-muted"
            >
              {section.label}
              <span className="text-xs">Segera</span>
            </span>
          ),
        )}
      </nav>
    </aside>
  );
}
