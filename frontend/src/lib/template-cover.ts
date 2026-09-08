import {
  ArrowLeftRight,
  Camera,
  Megaphone,
  MessageCircleHeart,
  PackageOpen,
  ShoppingBag,
  type LucideIcon,
} from "lucide-react";

import type { ProjectMode, Template } from "@/lib/types";

// Deterministic "cover art" for template cards that don't have a real thumbnail yet
// (thumbnail_url stays null until real generation ships — see PROGRESS.md Phase
// 6R-2). Rather than a broken <img> or a random color per render, each template gets
// one of a small set of on-brand gradients (built from our own design tokens, never
// stock photos or AI-generated imagery) picked deterministically from its id — the
// same template always renders the same cover, and a re-render never flickers.
const GRADIENTS = [
  "from-rec/25 via-panel to-panel-raised",
  "from-signal/25 via-panel to-panel-raised",
  "from-alert/15 via-panel to-panel-raised",
  "from-rec/15 via-signal/10 to-panel-raised",
] as const;

export function templateGradient(id: string): string {
  let hash = 0;
  for (let index = 0; index < id.length; index += 1) {
    hash = (hash * 31 + id.charCodeAt(index)) >>> 0;
  }
  return GRADIENTS[hash % GRADIENTS.length];
}

// Mode is the only real categorization the Template model has today (see
// backend/app/schemas/template.py) — no separate `category` field exists, and this
// redesign deliberately doesn't add one (DESIGN_SYSTEM.md §5.5) rather than invent
// categories the data doesn't back up.
export const MODE_ICON: Record<ProjectMode, LucideIcon> = {
  product_ad: ShoppingBag,
  affiliate: Megaphone,
};

export const MODE_LABEL: Record<ProjectMode, string> = {
  product_ad: "Iklan Produk",
  affiliate: "Affiliate",
};

// Per-template icon, keyed by name (see the seed rows in
// alembic/versions/8b124fa99bc5_create_templates_table.py) — every seeded product_ad
// template used to fall back to the same ShoppingBag icon, so 3 of the 4 cards in the
// hub read as visually identical. A real per-template mark (grounded in each one's
// actual style, not invented) reads as a real gallery instead of one card repeated.
// Anything not in this map (a template added later straight in the DB) still gets a
// sensible icon via MODE_ICON, it just won't be individually distinct until added here.
const TEMPLATE_ICON: Record<string, LucideIcon> = {
  "Unboxing Produk": PackageOpen,
  "Testimoni Pelanggan": MessageCircleHeart,
  "Before/After": ArrowLeftRight,
  "Demo Produk Close-up": Camera,
};

export function templateIcon(template: Template): LucideIcon {
  return TEMPLATE_ICON[template.name] ?? MODE_ICON[template.mode];
}
