import type { Metadata } from "next";

import { CtaBand } from "@/components/marketing/cta-band";
import { FeatureGrid } from "@/components/marketing/feature-grid";
import { MarketingFooter } from "@/components/marketing/footer";
import { Hero } from "@/components/marketing/hero";
import { MarketingNav } from "@/components/marketing/nav";
import { ModelBadges } from "@/components/marketing/model-badges";
import { PipelineExplainer } from "@/components/marketing/pipeline-explainer";

export const metadata: Metadata = {
  title: "adVance.AI — Foto produk jadi video, dibantu AI",
  description:
    "Upload foto produk, biarkan AI generate videonya, edit ringan, lalu siapkan untuk Instagram, TikTok, dan YouTube.",
};

// Public marketing home (Phase 6R-7 — see PROGRESS.md and DESIGN_SYSTEM.md §5.5).
// Pure server component: no next-auth here at all. Guest bootstrap used to live at
// this route ("/") — it moved to /app so simply viewing the marketing page never
// spends a guest account (see frontend/src/app/app/page.tsx).
export default function MarketingHomePage() {
  return (
    <div className="flex min-h-full flex-1 flex-col bg-paper text-paper-ink">
      <MarketingNav />
      <main className="flex-1">
        <Hero />
        <PipelineExplainer />
        <FeatureGrid />
        <ModelBadges />
      </main>
      <CtaBand />
      <MarketingFooter />
    </div>
  );
}
