"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useRef } from "react";

import { WorkspaceCanvas } from "@/components/workspace/workspace-canvas";
import { useWorkspace } from "@/components/workspace/workspace-context";
import type { ProjectMode } from "@/lib/types";

// Optional catch-all so both `/studio` (fresh session, no project yet) and
// `/studio/<id>` (bookmarked/shared, or landed on via router.replace after creating a
// project — see workspace-context.tsx's `createProject`) render the same canvas.
export default function StudioPage() {
  const params = useParams<{ projectId?: string[] }>();
  const searchParams = useSearchParams();
  const projectId = params.projectId?.[0];
  const { project, loadProject, setPrompt, setProjectMode } = useWorkspace();
  const loadedFor = useRef<string | null>(null);
  const appliedTemplateFromQuery = useRef(false);

  useEffect(() => {
    if (projectId && projectId !== loadedFor.current && projectId !== project?.id) {
      loadedFor.current = projectId;
      loadProject(projectId);
    }
  }, [projectId, project?.id, loadProject]);

  // Dashboard hub template cards (Phase 6R-7) hand off the pick via query params
  // instead of re-fetching the template list here or reaching into applyTemplate's
  // contract — cheapest way to prefill the Generate panel without a second fetch.
  useEffect(() => {
    if (appliedTemplateFromQuery.current) return;
    const mode = searchParams.get("mode");
    const prompt = searchParams.get("prompt");
    if (!mode && !prompt) return;
    appliedTemplateFromQuery.current = true;
    if (mode === "product_ad" || mode === "affiliate") {
      setProjectMode(mode as ProjectMode);
    }
    if (prompt) setPrompt(prompt);
  }, [searchParams, setPrompt, setProjectMode]);

  return <WorkspaceCanvas />;
}
