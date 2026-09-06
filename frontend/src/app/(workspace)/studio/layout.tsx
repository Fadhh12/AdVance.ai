"use client";

import type { ReactNode } from "react";

import { ChatPanel } from "@/components/workspace/chat-panel";
import { PipelineHeader } from "@/components/workspace/pipeline-header";
import { WorkspaceProvider } from "@/components/workspace/workspace-context";

// Phase 6R-4: one continuous workspace instead of separate /generate, /editor/[id],
// /publish/[id] pages. WorkspaceProvider + the pipeline header live here so they're
// shared across the whole /studio route tree (currently just the one catch-all page,
// but this is where a future per-project sub-route would plug in too).
export default function StudioLayout({ children }: { children: ReactNode }) {
  return (
    <WorkspaceProvider>
      <div className="flex flex-col gap-6">
        <PipelineHeader />
        <div className="flex flex-1 flex-col gap-6 lg:flex-row lg:items-start">
          <div className="min-w-0 flex-1">{children}</div>
          <ChatPanel />
        </div>
      </div>
    </WorkspaceProvider>
  );
}
