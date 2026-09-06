"use client";

import { useEffect, useRef } from "react";

import { EditPanel } from "@/components/workspace/panels/edit-panel";
import { GeneratePanel } from "@/components/workspace/panels/generate-panel";
import { PublishPanel } from "@/components/workspace/panels/publish-panel";
import { UploadPanel } from "@/components/workspace/panels/upload-panel";
import { useWorkspace } from "@/components/workspace/workspace-context";

// The one deliberate motion DESIGN_SYSTEM.md §6 allows beyond direct user response:
// auto-scrolling to the section that just became relevant when a stage completes
// (new project created -> Edit; render finishes -> Publish) — not a scroll-reveal
// effect applied to everything.
export function WorkspaceCanvas() {
  const { project, error, clearError } = useWorkspace();
  const knownProjectId = useRef<string | null>(null);
  const knownRenderStatus = useRef<string | null>(null);

  useEffect(() => {
    if (project && project.id !== knownProjectId.current) {
      knownProjectId.current = project.id;
      requestAnimationFrame(() => {
        document.getElementById("stage-edit")?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }, [project]);

  useEffect(() => {
    const status = project?.render_status ?? null;
    if (status === "success" && knownRenderStatus.current !== "success") {
      requestAnimationFrame(() => {
        document.getElementById("stage-publish")?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
    knownRenderStatus.current = status;
  }, [project?.render_status]);

  return (
    <div className="flex flex-col gap-10 divide-y divide-panel">
      {error && (
        <p
          role="alert"
          className="flex items-center justify-between gap-3 rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert"
        >
          {error}
          <button type="button" onClick={clearError} className="shrink-0 text-alert/80 hover:text-alert">
            Tutup
          </button>
        </p>
      )}
      <div className="pt-10 first:pt-0">
        <UploadPanel />
      </div>
      <div className="pt-10">
        <GeneratePanel />
      </div>
      <div className="pt-10">
        <EditPanel />
      </div>
      <div className="pt-10">
        <PublishPanel />
      </div>
    </div>
  );
}
