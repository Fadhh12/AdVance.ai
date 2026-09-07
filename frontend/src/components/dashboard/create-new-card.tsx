import { Plus } from "lucide-react";
import Link from "next/link";

// DESIGN_SYSTEM.md §5.3/§5.5: reserve a big card for the one primary action — not a
// grid of equally-sized cards.
export function CreateNewCard() {
  return (
    <Link
      href="/studio"
      className="group flex items-center gap-4 rounded-lg border border-panel-raised bg-panel px-6 py-8 transition-colors hover:border-rec/60 hover:bg-panel-raised"
    >
      <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-md bg-rec text-canvas">
        <Plus className="h-6 w-6" aria-hidden />
      </span>
      <span>
        <span className="block font-display text-lg text-ink">Buat Baru</span>
        <span className="block text-sm text-ink-muted">
          Mulai dari kosong — upload foto lalu generate video.
        </span>
      </span>
    </Link>
  );
}
