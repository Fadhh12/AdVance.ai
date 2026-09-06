"use client";

import { useParams } from "next/navigation";
import { useEffect, useRef } from "react";

import { WorkspaceCanvas } from "@/components/workspace/workspace-canvas";
import { useWorkspace } from "@/components/workspace/workspace-context";

// Optional catch-all so both `/studio` (fresh session, no project yet) and
// `/studio/<id>` (bookmarked/shared, or landed on via router.replace after creating a
// project — see workspace-context.tsx's `createProject`) render the same canvas.
export default function StudioPage() {
  const params = useParams<{ projectId?: string[] }>();
  const projectId = params.projectId?.[0];
  const { project, loadProject } = useWorkspace();
  const loadedFor = useRef<string | null>(null);

  useEffect(() => {
    if (projectId && projectId !== loadedFor.current && projectId !== project?.id) {
      loadedFor.current = projectId;
      loadProject(projectId);
    }
  }, [projectId, project?.id, loadProject]);

  return <WorkspaceCanvas />;
}
