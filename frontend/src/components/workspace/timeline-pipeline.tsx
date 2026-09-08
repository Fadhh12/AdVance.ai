"use client";

import type { LucideIcon } from "lucide-react";

import { PipelineConnector } from "@/components/workspace/pipeline-connector";
import { TallyDot, type TallyStatus } from "@/components/ui/tally-dot";

// DESIGN_SYSTEM.md §5.1 "Timeline Pipeline" motif — a functional strip showing where
// the current project actually is (Upload -> Generate -> Edit -> Publish), not a
// decorative 01/02/03 step list. Phase 6R-4: rendered once, persistently, above the
// single continuous Studio canvas — `onStageClick` scrolls the canvas to that stage's
// section instead of navigating to a different page.
// "use client" (Phase 6R-7): the button below always attaches an onClick, even when
// `onStageClick` isn't passed — a Server Component (e.g. the marketing page's
// pipeline-explainer.tsx, which renders this with no handler at all) can't send an
// event handler function across the server/client boundary without this directive.
//
// Phase 6R-12: nodes gained an icon + curved cable connectors (was a flat divider
// line) so the strip reads as one connected chain rather than a flat step list, and a
// stage can carry `branches` — extra sub-nodes that only appear when the project
// actually has more than one of that stage's output (e.g. Publish fans out into one
// node per platform once posts exist). `branches` reflects real per-project data, it
// is never fabricated just to look busier (DESIGN_SYSTEM.md anti-slop checklist).
export type PipelineBranch = { key: string; label: string; status: TallyStatus };

export type PipelineStage = {
  key: string;
  label: string;
  status: TallyStatus;
  caption: string;
  icon: LucideIcon;
  /** Element id to scroll to on click, if different from `key` (e.g. an extra node
   * that lives inside another stage's section, like Motion inside Edit). */
  targetId?: string;
  branches?: PipelineBranch[];
};

export function TimelinePipeline({
  stages,
  onStageClick,
}: {
  stages: PipelineStage[];
  onStageClick?: (key: string) => void;
}) {
  return (
    <ol className="flex items-start overflow-x-auto pb-1">
      {stages.map((stage, index) => {
        const Icon = stage.icon;
        return (
          <li key={stage.key} className="flex flex-1 items-start last:flex-none">
            <div className="flex shrink-0 flex-col gap-2">
              <button
                type="button"
                onClick={() => onStageClick?.(stage.targetId ?? stage.key)}
                disabled={!onStageClick}
                className={`flex min-h-14 w-36 flex-col justify-center gap-1 rounded-lg border px-3 py-2 text-left transition-colors disabled:cursor-default ${
                  stage.status === "idle"
                    ? "border-panel-raised bg-panel"
                    : "border-panel-raised bg-panel-raised hover:border-ink-muted/40"
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <Icon className="h-3.5 w-3.5 shrink-0 text-ink-muted" aria-hidden />
                  <span className="truncate text-xs text-ink">{stage.label}</span>
                  <TallyDot status={stage.status} />
                </div>
                <span className="truncate text-[11px] text-ink-muted">{stage.caption}</span>
              </button>

              {stage.branches && stage.branches.length > 0 && (
                <ul className="flex flex-col gap-1 border-l border-panel-raised py-1 pl-3">
                  {stage.branches.map((branch) => (
                    <li
                      key={branch.key}
                      className="flex items-center gap-1.5 text-[11px] text-ink-muted"
                    >
                      <TallyDot status={branch.status} />
                      {branch.label}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {index < stages.length - 1 && <PipelineConnector state={stage.status} />}
          </li>
        );
      })}
    </ol>
  );
}
