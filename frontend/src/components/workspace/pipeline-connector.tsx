import type { TallyStatus } from "@/components/ui/tally-dot";

// A curved "patch cable" connector between two Timeline Pipeline nodes
// (DESIGN_SYSTEM.md §5.1) — replaces the flat divider line so the strip reads as a
// connected production chain (broadcast patch bay), not a disconnected step list.
// Deliberately not a literal automation-canvas wire (drop shadow, arrowhead, floating
// free-form routing) — see the anti-slop checklist in DESIGN_SYSTEM.md §2. Color/pulse
// mirror the same tally-light states TallyDot uses: muted while idle, pulsing amber
// mid-transfer, solid teal once the left-hand node has actually finished, brick-red if
// it failed.
export function PipelineConnector({ state }: { state: TallyStatus }) {
  const strokeClass =
    state === "success"
      ? "stroke-signal"
      : state === "processing"
        ? "stroke-rec"
        : state === "failed"
          ? "stroke-alert"
          : "stroke-panel-raised";

  return (
    <div className="flex h-14 min-w-10 flex-1 items-center" aria-hidden>
      <svg viewBox="0 0 100 24" preserveAspectRatio="none" className="h-6 w-full">
        <path
          d="M0,4 C25,4 25,20 50,20 C75,20 75,4 100,4"
          fill="none"
          strokeWidth={2}
          strokeLinecap="round"
          strokeDasharray={state === "idle" ? "2 6" : undefined}
          className={`${strokeClass} ${state === "processing" ? "animate-pulse" : ""}`}
        />
      </svg>
    </div>
  );
}
