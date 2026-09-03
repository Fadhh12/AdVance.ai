import Link from "next/link";

// Bagian yang belum dibangun ditandai "Segera" — bukan link mati tanpa penjelasan.
// Urutan mengikuti alur produk (Task Breakdown Phase 1-7), bukan alfabetis.
const SECTIONS: Array<{ label: string; href: string; available: boolean }> = [
  { label: "Dashboard", href: "/dashboard", available: true },
  { label: "Media Library", href: "#", available: false },
  { label: "Generate Studio", href: "#", available: false },
  { label: "Editor", href: "#", available: false },
  { label: "Publish", href: "#", available: false },
  { label: "Content Calendar", href: "#", available: false },
  { label: "Connected Accounts", href: "#", available: false },
  { label: "Analytics", href: "#", available: false },
  { label: "Billing", href: "#", available: false },
];

export function Sidebar() {
  return (
    <aside className="flex w-56 shrink-0 flex-col gap-6 bg-panel px-4 py-6">
      <span className="font-display text-lg text-ink">adVance.AI</span>
      <nav className="flex flex-col gap-1">
        {SECTIONS.map((section) =>
          section.available ? (
            <Link
              key={section.label}
              href={section.href}
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
