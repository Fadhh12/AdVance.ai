"use client";

import { useCallback } from "react";
import { Clapperboard, CloudUpload, Mic, Rocket, Scissors, Sparkles } from "lucide-react";

import type { TallyStatus } from "@/components/ui/tally-dot";
import {
  TimelinePipeline,
  type PipelineBranch,
  type PipelineStage,
} from "@/components/workspace/timeline-pipeline";
import { useWorkspace } from "@/components/workspace/workspace-context";
import type { AIJob, ContentProject, Platform, Post } from "@/lib/types";

function generateStatus(job: AIJob | null): { status: TallyStatus; caption: string } {
  if (!job) return { status: "idle", caption: "belum" };
  if (job.status === "success") return { status: "success", caption: job.provider };
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

// "editorial-newspaper" -> "Editorial Newspaper" — the preset id doubles as its label
// here so the node doesn't need its own fetch to /motion-presets just to show a name.
function motionLabel(presetId: string): string {
  return presetId
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

const PLATFORM_LABEL: Record<Platform, string> = {
  instagram: "Instagram",
  tiktok: "TikTok",
  youtube: "YouTube",
};

function branchStatus(post: Post): TallyStatus {
  if (post.export_status === "failed") return "failed";
  if (post.export_status === "success") return "success";
  if (post.export_status) return "processing";
  return "idle";
}

function publishStatus(posts: Post[] | null): TallyStatus {
  if (!posts || posts.length === 0) return "idle";
  if (posts.some((p) => p.export_status === "failed")) return "failed";
  if (posts.some((p) => p.export_status === "queued" || p.export_status === "processing")) {
    return "processing";
  }
  return "success";
}

// Persistent pipeline strip (DESIGN_SYSTEM.md §5.1), rendered once above the
// continuous /studio canvas. Clicking a stage scrolls to its section instead of
// navigating — the workspace is one page, not four. The 4 core stages always show;
// "Motion" and the per-platform Publish branches only appear once the project
// actually has that data (motion_preset set / posts prepared) — real state, not a
// fixed decorative node count (see timeline-pipeline.tsx for why).
export function PipelineHeader() {
  const { selectedAssetId, job, project, posts } = useWorkspace();

  const generate = generateStatus(job);
  const edit = editStatus(project);

  const stages: PipelineStage[] = [
    {
      key: "stage-upload",
      label: "Upload",
      icon: CloudUpload,
      status: selectedAssetId ? "success" : "idle",
      caption: selectedAssetId ? "foto siap" : "belum",
    },
    {
      key: "stage-generate",
      label: "Generate",
      icon: Sparkles,
      status: generate.status,
      caption: generate.caption,
    },
    {
      key: "stage-edit",
      label: "Edit",
      icon: Scissors,
      status: edit.status,
      caption: edit.caption,
    },
  ];

  if (project?.motion_preset) {
    stages.push({
      key: "stage-motion",
      targetId: "stage-edit",
      label: motionLabel(project.motion_preset),
      icon: Clapperboard,
      status: edit.status,
      caption: "motion preset",
    });
  }

  if (project?.voiceover_text) {
    stages.push({
      key: "stage-voiceover",
      targetId: "stage-edit",
      label: "Voice-over",
      icon: Mic,
      status: edit.status,
      caption: "AI baca naskah",
    });
  }

  const branches: PipelineBranch[] | undefined = posts?.length
    ? posts.map((post) => ({
        key: post.id,
        label: PLATFORM_LABEL[post.platform],
        status: branchStatus(post),
      }))
    : undefined;

  stages.push({
    key: "stage-publish",
    label: "Publish",
    icon: Rocket,
    status: publishStatus(posts),
    caption: posts?.length ? `${posts.length} platform` : "belum",
    branches,
  });

  const handleStageClick = useCallback((key: string) => {
    document.getElementById(key)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  return <TimelinePipeline stages={stages} onStageClick={handleStageClick} />;
}
