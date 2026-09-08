import { CloudUpload, Rocket, Scissors, Sparkles } from "lucide-react";

import { TimelinePipeline, type PipelineStage } from "@/components/workspace/timeline-pipeline";

// Fixed, illustrative stage statuses — not live data (this is a marketing page, no
// session/job exists here). The point is to reuse the exact same component the
// in-app pipeline header renders (DESIGN_SYSTEM.md §5.1), inside a dark panel that
// mirrors the workspace's own palette, so this is a preview of the real UI rather
// than a separate illustration invented for marketing.
const STAGES: PipelineStage[] = [
  { key: "s1", label: "Upload", icon: CloudUpload, status: "success", caption: "foto produk" },
  { key: "s2", label: "Generate", icon: Sparkles, status: "processing", caption: "AI bikin video" },
  { key: "s3", label: "Edit", icon: Scissors, status: "idle", caption: "trim, caption, musik" },
  { key: "s4", label: "Publish", icon: Rocket, status: "idle", caption: "siap per platform" },
];

export function PipelineExplainer() {
  return (
    <section id="cara-kerja" className="mx-auto max-w-6xl px-6 py-16 md:py-24">
      <h2 className="font-display text-3xl text-paper-ink md:text-4xl">Cara kerjanya</h2>
      <p className="mt-3 max-w-xl text-paper-ink-muted">
        Empat tahap yang sama persis dengan yang kamu lihat di dalam workspace — bukan
        ilustrasi terpisah.
      </p>
      <div className="mt-8 rounded-lg border border-panel-raised bg-canvas p-6 md:p-8">
        <TimelinePipeline stages={STAGES} />
      </div>
    </section>
  );
}
