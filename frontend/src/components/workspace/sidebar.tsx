import {
  BarChart3,
  CalendarDays,
  Clapperboard,
  CreditCard,
  Image as ImageIcon,
  LayoutGrid,
  Link2,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";

// Bagian yang belum dibangun ditandai "Segera" — bukan link mati tanpa penjelasan.
// Urutan mengikuti alur produk (Task Breakdown Phase 1-7), bukan alfabetis.
// "Generate Studio"/"Editor"/"Publish" digabung jadi satu "Studio" (Phase 6R-4) —
// alurnya sekarang satu workspace berkelanjutan, bukan lagi 3 halaman terpisah.
// Icons (Phase 6R-7) are a small legibility aid, not decoration — same links/behavior.
const SECTIONS: Array<{ label: string; href: string; icon: LucideIcon; available: boolean }> = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutGrid, available: true },
  { label: "Studio", href: "/studio", icon: Clapperboard, available: true },
  { label: "Media Library", href: "/media", icon: ImageIcon, available: true },
  { label: "Content Calendar", href: "/calendar", icon: CalendarDays, available: true },
  { label: "Connected Accounts", href: "#", icon: Link2, available: false },
  { label: "Analytics", href: "#", icon: BarChart3, available: false },
  { label: "Billing", href: "#", icon: CreditCard, available: false },
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
              className="flex items-center gap-2.5 rounded-md px-3 py-2 text-sm text-ink transition-colors hover:bg-panel-raised"
            >
              <section.icon className="h-4 w-4 shrink-0 text-ink-muted" aria-hidden />
              {section.label}
            </Link>
          ) : (
            <span
              key={section.label}
              className="flex items-center gap-2.5 rounded-md px-3 py-2 text-sm text-ink-muted"
            >
              <section.icon className="h-4 w-4 shrink-0" aria-hidden />
              <span className="flex-1">{section.label}</span>
              <span className="text-xs">Segera</span>
            </span>
          ),
        )}
      </nav>
    </aside>
  );
}
