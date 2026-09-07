// Roadmap wording, deliberately not "Didukung oleh" (DESIGN_SYSTEM.md §5.5) — real
// video generation is still MockVideoProvider (see PROGRESS.md). This section must
// never imply Veo/Seedance are already wired in until they actually are. Sentence
// case, not an ALL-CAPS eyebrow (§2 anti-slop checklist).
export function ModelBadges() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-10">
      <p className="text-center text-sm text-paper-ink-muted">
        Dirancang untuk mendukung model video AI terkemuka — segera menyusul
      </p>
      <div className="mt-4 flex flex-wrap items-center justify-center gap-x-8 gap-y-2">
        <span className="text-sm font-medium text-paper-ink-muted">Google Veo</span>
        <span className="text-sm font-medium text-paper-ink-muted">Seedance 2.0</span>
      </div>
    </section>
  );
}
