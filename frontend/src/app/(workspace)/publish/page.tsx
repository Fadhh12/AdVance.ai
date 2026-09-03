"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { TallyDot, type TallyStatus } from "@/components/ui/tally-dot";
import { API_BASE_URL } from "@/lib/api";
import type { ContentProject } from "@/lib/types";

function renderStatusDot(project: ContentProject): TallyStatus {
  if (project.render_status === "success") return "success";
  if (project.render_status === "failed") return "failed";
  if (project.render_status) return "processing";
  return "idle";
}

export default function PublishIndexPage() {
  const { data: session } = useSession();
  const accessToken = session?.accessToken;
  const [projects, setProjects] = useState<ContentProject[] | null>(null);

  useEffect(() => {
    let ignore = false;
    (async () => {
      if (!accessToken) return;
      const response = await fetch(`${API_BASE_URL}/projects`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!ignore && response.ok) setProjects(await response.json());
    })();
    return () => {
      ignore = true;
    };
  }, [accessToken]);

  const renderedProjects = projects?.filter((p) => p.render_status === "success") ?? null;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl text-ink">Publish</h1>
        <p className="text-sm text-ink-muted">Proyek yang sudah di-render dan siap disiapkan untuk publish.</p>
      </div>

      {renderedProjects === null ? (
        <p className="text-sm text-ink-muted">Memuat…</p>
      ) : renderedProjects.length === 0 ? (
        <p className="text-sm text-ink-muted">
          Belum ada proyek yang sudah di-render.{" "}
          <Link href="/editor" className="text-rec hover:underline">
            Buka Editor
          </Link>{" "}
          untuk render dulu.
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-panel">
          {renderedProjects.map((project) => (
            <li key={project.id}>
              <Link
                href={`/publish/${project.id}`}
                className="flex items-center gap-3 py-3 text-sm transition-colors hover:bg-panel-raised"
              >
                <TallyDot status={renderStatusDot(project)} />
                <span className="flex-1 text-ink">{project.title}</span>
                <span className="text-xs text-ink-muted">
                  {project.mode === "product_ad" ? "Iklan Produk" : "Affiliate"}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
