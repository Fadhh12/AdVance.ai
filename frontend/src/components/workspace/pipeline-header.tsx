"use client";

import { useCallback } from "react";

import type { TallyStatus } from "@/components/ui/tally-dot";
import { TimelinePipeline, type PipelineStage } from "@/components/workspace/timeline-pipeline";
import { useWorkspace } from "@/components/workspace/workspace-context";
import type { AIJob, ContentProject, Post } from "@/lib/types";

function generateStatus(job: AIJob | null): { status: TallyStatus; caption: string } {
  if (!job) return { status: "idle", caption: "belum" };
  if (job.status === "success") return { status: "success", caption: "selesai" };
  if (job.status === "failed") return { status: "failed", caption: "gagal" };
  return { status: "processing", caption: "sedang proses" };
}

function editStatus(project: ContentProject | null): { status: TallyStatus; caption: string } {
  if (!project) return { status: "idle", caption: "belum" };
  if (project.render_status === "success") return { status: "success", caption: "selesai" };
  if (project.render_status === "failed") return { status: "failed", caption: "gagal" };
  if (project.render_status) return { status: "processing", caption: "sedang proses" };
  return { status: "idle", caption: "draft" };
}

function publishStatus(posts: Post[] | null): { status: TallyStatus; caption: string } {
  if (!posts || posts.length === 0) return { status: "idle", caption: "belum" };
  if (posts.some((p) => p.export_status === "failed")) return { status: "failed", caption: "gagal" };
  if (posts.some((p) => p.export_status === "queued" || p.export_status === "processing")) {
    return { status: "processing", caption: "sedang proses" };
  }
  return { status: "success", caption: "siap" };
}

// Persistent pipeline strip (DESIGN_SYSTEM.md §5.1), rendered once above the
// continuous /studio canvas. Clicking a stage scrolls to its section instead of
// navigating — the workspace is one page, not four.
export function PipelineHeader() {
  const { selectedAssetId, job, project, posts } = useWorkspace();

  const generate = generateStatus(job);
  const edit = editStatus(project);
  const publish = publishStatus(posts);

  const stages: PipelineStage[] = [
    {
      key: "stage-upload",
      label: "Upload",
      status: selectedAssetId ? "success" : "idle",
      caption: selectedAssetId ? "selesai" : "belum",
    },
    { key: "stage-generate", label: "Generate", status: generate.status, caption: generate.caption },
    { key: "stage-edit", label: "Edit", status: edit.status, caption: edit.caption },
    { key: "stage-publish", label: "Publish", status: publish.status, caption: publish.caption },
  ];

  const handleStageClick = useCallback((key: string) => {
    document.getElementById(key)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  return <TimelinePipeline stages={stages} onStageClick={handleStageClick} />;
}
