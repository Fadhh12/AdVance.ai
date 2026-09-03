"use client";

import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { TimelinePipeline, type PipelineStage } from "@/components/workspace/timeline-pipeline";
import { API_BASE_URL, readApiError } from "@/lib/api";
import type { ContentProject } from "@/lib/types";

const POLL_INTERVAL_MS = 2500;

// No real music catalog yet — just enough to exercise "pilih musik" (FR-05). Wiring an
// actual audio library/licensing is out of scope until a provider decision is made.
const MUSIC_TRACKS = [
  { value: "", label: "Tidak ada musik" },
  { value: "upbeat-pop", label: "Upbeat Pop" },
  { value: "chill-lofi", label: "Chill Lo-fi" },
  { value: "energetic-corporate", label: "Energetic Corporate" },
];

export default function EditorPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: session } = useSession();
  const accessToken = session?.accessToken;

  const [project, setProject] = useState<ContentProject | null>(null);
  const [previewFailed, setPreviewFailed] = useState(false);
  const [caption, setCaption] = useState("");
  const [musicTrack, setMusicTrack] = useState("");
  const [trimStart, setTrimStart] = useState("");
  const [trimEnd, setTrimEnd] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isRendering, setIsRendering] = useState(false);

  function applyProject(data: ContentProject) {
    setProject(data);
    setCaption(data.caption ?? "");
    setMusicTrack(data.music_track ?? "");
    setTrimStart(data.trim_start_seconds?.toString() ?? "");
    setTrimEnd(data.trim_end_seconds?.toString() ?? "");
  }

  useEffect(() => {
    let ignore = false;
    (async () => {
      if (!accessToken) return;
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!ignore && response.ok) applyProject(await response.json());
    })();
    return () => {
      ignore = true;
    };
  }, [accessToken, projectId]);

  // Poll while a render is in flight.
  useEffect(() => {
    if (!project || !accessToken) return;
    if (project.render_status !== "queued" && project.render_status !== "processing") return;

    const interval = setInterval(async () => {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (response.ok) applyProject(await response.json());
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [project, accessToken, projectId]);

  async function handleSaveDraft() {
    if (!accessToken) return;
    setError(null);
    setIsSaving(true);

    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        caption: caption || null,
        music_track: musicTrack || null,
        trim_start_seconds: trimStart === "" ? null : Number(trimStart),
        trim_end_seconds: trimEnd === "" ? null : Number(trimEnd),
      }),
    });

    setIsSaving(false);
    if (!response.ok) {
      setError(await readApiError(response));
      return;
    }
    applyProject(await response.json());
  }

  async function handleRender() {
    if (!accessToken) return;
    setError(null);
    setIsRendering(true);

    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/render`, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    setIsRendering(false);
    if (!response.ok) {
      setError(await readApiError(response));
      return;
    }
    applyProject(await response.json());
  }

  if (!project) {
    return <p className="text-sm text-ink-muted">Memuat…</p>;
  }

  const stages: PipelineStage[] = [
    { label: "Upload", status: "success", caption: "selesai" },
    { label: "Generate", status: "success", caption: "selesai" },
    {
      label: "Edit",
      status:
        project.render_status === "success"
          ? "success"
          : project.render_status === "failed"
            ? "failed"
            : project.render_status
              ? "processing"
              : "idle",
      caption:
        project.render_status === "success"
          ? "selesai"
          : project.render_status === "failed"
            ? "gagal"
            : project.render_status
              ? "sedang proses"
              : "draft",
    },
    { label: "Publish", status: "idle", caption: "belum" },
  ];

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="font-display text-2xl text-ink">{project.title}</h1>
        <p className="text-sm text-ink-muted">
          {project.mode === "product_ad" ? "Iklan Produk" : "Affiliate"}
        </p>
      </div>

      <TimelinePipeline stages={stages} />

      <section className="flex flex-col gap-2">
        <h2 className="text-sm text-ink-muted">Preview</h2>
        {previewFailed ? (
          <p className="max-w-md text-sm text-ink-muted">
            Preview tidak bisa ditampilkan — provider AI masih mode mock, hasil generate
            saat ini belum berupa video sungguhan (lihat PROGRESS.md Phase 3).
          </p>
        ) : (
          <video
            src={project.final_video_url ?? project.source_video_url}
            controls
            className="max-h-80 max-w-sm rounded-md bg-panel"
            onError={() => setPreviewFailed(true)}
          />
        )}
      </section>

      <section className="flex max-w-sm flex-col gap-3">
        <h2 className="text-sm text-ink-muted">Trim</h2>
        <div className="flex gap-3">
          <TextField
            id="trim-start"
            label="Mulai (detik)"
            type="number"
            min={0}
            value={trimStart}
            onChange={(e) => setTrimStart(e.target.value)}
          />
          <TextField
            id="trim-end"
            label="Selesai (detik)"
            type="number"
            min={0}
            value={trimEnd}
            onChange={(e) => setTrimEnd(e.target.value)}
          />
        </div>
      </section>

      <section className="flex max-w-sm flex-col gap-3">
        <h2 className="text-sm text-ink-muted">Caption</h2>
        <textarea
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
          rows={4}
          className="rounded-md border border-panel-raised bg-panel px-3 py-2 text-sm text-ink outline-none focus:border-rec"
          placeholder="Tulis caption untuk video ini…"
        />
      </section>

      <section className="flex max-w-sm flex-col gap-3">
        <h2 className="text-sm text-ink-muted">Musik</h2>
        <select
          value={musicTrack}
          onChange={(e) => setMusicTrack(e.target.value)}
          className="rounded-md border border-panel-raised bg-panel px-3 py-2 text-sm text-ink outline-none focus:border-rec"
        >
          {MUSIC_TRACKS.map((track) => (
            <option key={track.value} value={track.value}>
              {track.label}
            </option>
          ))}
        </select>
      </section>

      {error && (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          {error}
        </p>
      )}
      {project.render_status === "failed" && project.render_error_message && (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          Render gagal: {project.render_error_message}
        </p>
      )}

      <div className="flex gap-3">
        <Button variant="ghost" onClick={handleSaveDraft} disabled={isSaving}>
          {isSaving ? "Menyimpan…" : "Simpan draft"}
        </Button>
        <Button onClick={handleRender} disabled={isRendering}>
          {isRendering ? "Merender…" : "Render video"}
        </Button>
      </div>
    </div>
  );
}
