// DESIGN_SYSTEM.md §5.2: a small dot, not a rounded confetti badge. Pulsing amber for
// "processing", solid teal for success, solid brick-red for failed, hollow for idle.
export type TallyStatus = "idle" | "processing" | "success" | "failed";

const STATUS_CLASSES: Record<TallyStatus, string> = {
  idle: "border border-ink-muted/50 bg-transparent",
  processing: "animate-pulse bg-rec",
  success: "bg-signal",
  failed: "bg-alert",
};

export function TallyDot({ status }: { status: TallyStatus }) {
  return (
    <span
      className={`inline-block h-2 w-2 shrink-0 rounded-full ${STATUS_CLASSES[status]}`}
      aria-hidden
    />
  );
}
