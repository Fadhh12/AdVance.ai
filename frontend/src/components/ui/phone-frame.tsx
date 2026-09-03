import type { ReactNode } from "react";

// DESIGN_SYSTEM.md §5.4: "device-frame minimalis tipis, bukan mockup HP 3D dekoratif" —
// just a thin 9:16 border, not a decorative 3D phone shell.
export function PhoneFrame({ children }: { children: ReactNode }) {
  return (
    <div className="aspect-[9/16] w-full overflow-hidden rounded-lg border border-panel-raised bg-panel">
      {children}
    </div>
  );
}
