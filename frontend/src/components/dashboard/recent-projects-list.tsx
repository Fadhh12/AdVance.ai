"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { TallyDot, type TallyStatus } from "@/components/ui/tally-dot";
import { apiFetch } from "@/lib/api-client";
import { MODE_LABEL } from "@/lib/template-cover";
import type { ContentProject } from "@/lib/types";

function renderStatusDot(project: ContentProject): TallyStatus {
  if (project.render_status === "success") return "success";
  if (project.render_status === "failed") return "failed";
  if (project.render_status) return "processing";
  return "idle";
}

// List style, not a grid (DESIGN_SYSTEM.md §5.3) — same pattern as the old
// editor/page.tsx this replaces as the primary way back into an existing project.
export function RecentProjectsList({ accessToken }: { accessToken: string | undefined }) {
  const [projects, setProjects] = useState<ContentProject[] | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    let ignore = false;
    apiFetch<ContentProject[]>("/projects", { token: accessToken })
      .then((data) => {
        if (!ignore) setProjects(data);
      })
      .catch(() => {
        if (!ignore) setProjects([]);
      });
    return () => {
      ignore = true;
    };
  }, [accessToken]);

  if (!projects || projects.length === 0) return null;

  return (
    <div>
      <h2 className="font-display text-lg text-ink">Project Terbaru</h2>
      <ul className="mt-4 flex flex-col divide-y divide-panel">
        {projects.slice(0, 8).map((project) => (
          <li key={project.id}>
            <Link
              href={`/studio/${project.id}`}
              className="flex items-center gap-3 py-3 text-sm transition-colors hover:bg-panel-raised"
            >
              <TallyDot status={renderStatusDot(project)} />
              <span className="flex-1 text-ink">{project.title}</span>
              <span className="text-xs text-ink-muted">{MODE_LABEL[project.mode]}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
