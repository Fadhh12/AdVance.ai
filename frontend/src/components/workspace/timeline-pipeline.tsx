import { TallyDot, type TallyStatus } from "@/components/ui/tally-dot";

// DESIGN_SYSTEM.md §5.1 "Timeline Pipeline" motif — a functional strip showing where
// the current project actually is (Upload -> Generate -> Edit -> Publish), not a
// decorative 01/02/03 step list. Lives on the Generate Studio page for now, tied to
// the active job; once Phase 4 adds content_projects it belongs in a persistent
// per-project header instead (see PROGRESS.md Phase 3).
export type PipelineStage = { label: string; status: TallyStatus; caption: string };

export function TimelinePipeline({ stages }: { stages: PipelineStage[] }) {
  return (
    <ol className="flex items-stretch">
      {stages.map((stage, index) => (
        <li key={stage.label} className="flex flex-1 items-center last:flex-none">
          <div className="flex flex-col items-center gap-1.5 px-3 first:pl-0 last:pr-0">
            <TallyDot status={stage.status} />
            <span className="text-xs text-ink">{stage.label}</span>
            <span className="text-[11px] text-ink-muted">{stage.caption}</span>
          </div>
          {index < stages.length - 1 && (
            <div className="h-px flex-1 bg-panel-raised" aria-hidden />
          )}
        </li>
      ))}
    </ol>
  );
}
