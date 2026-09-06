import { TallyDot, type TallyStatus } from "@/components/ui/tally-dot";

// DESIGN_SYSTEM.md §5.1 "Timeline Pipeline" motif — a functional strip showing where
// the current project actually is (Upload -> Generate -> Edit -> Publish), not a
// decorative 01/02/03 step list. Phase 6R-4: rendered once, persistently, above the
// single continuous Studio canvas — `onStageClick` scrolls the canvas to that stage's
// section instead of navigating to a different page.
export type PipelineStage = { key: string; label: string; status: TallyStatus; caption: string };

export function TimelinePipeline({
  stages,
  onStageClick,
}: {
  stages: PipelineStage[];
  onStageClick?: (key: string) => void;
}) {
  return (
    <ol className="flex items-stretch overflow-x-auto">
      {stages.map((stage, index) => (
        <li key={stage.key} className="flex flex-1 items-center last:flex-none">
          <button
            type="button"
            onClick={() => onStageClick?.(stage.key)}
            disabled={!onStageClick}
            className="flex shrink-0 flex-col items-center gap-1.5 px-3 first:pl-0 last:pr-0 disabled:cursor-default"
          >
            <TallyDot status={stage.status} />
            <span className="whitespace-nowrap text-xs text-ink">{stage.label}</span>
            <span className="hidden whitespace-nowrap text-[11px] text-ink-muted sm:block">
              {stage.caption}
            </span>
          </button>
          {index < stages.length - 1 && (
            <div className="h-px flex-1 min-w-6 bg-panel-raised" aria-hidden />
          )}
        </li>
      ))}
    </ol>
  );
}
