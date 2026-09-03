"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { useEffect, useState } from "react";

import type { TallyStatus } from "@/components/ui/tally-dot";
import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { TimelinePipeline, type PipelineStage } from "@/components/workspace/timeline-pipeline";
import { API_BASE_URL, readApiError } from "@/lib/api";
import type { AIJob, MediaAsset } from "@/lib/types";

const POLL_INTERVAL_MS = 2500;

function stageStatusForJob(job: AIJob | null): TallyStatus {
  if (!job) return "idle";
  if (job.status === "success") return "success";
  if (job.status === "failed") return "failed";
  return "processing";
}

export default function GenerateStudioPage() {
  const { data: session } = useSession();
  const accessToken = session?.accessToken;

  const [photos, setPhotos] = useState<MediaAsset[] | null>(null);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [prompt, setPrompt] = useState("");
  const [job, setJob] = useState<AIJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let ignore = false;
    (async () => {
      if (!accessToken) return;
      const response = await fetch(`${API_BASE_URL}/media`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!ignore && response.ok) {
        const assets: MediaAsset[] = await response.json();
        setPhotos(assets.filter((asset) => asset.type === "photo"));
      }
    })();
    return () => {
      ignore = true;
    };
  }, [accessToken]);

  // Polls while the job is in flight. Note: without a worker actually consuming the
  // queue (Redis/Docker pending — see PROGRESS.md), this can sit at "queued"
  // indefinitely in local dev right now; that's the known environment gap, not a bug
  // in this polling logic.
  useEffect(() => {
    if (!job || !accessToken) return;
    if (job.status === "success" || job.status === "failed") return;

    const interval = setInterval(async () => {
      const response = await fetch(`${API_BASE_URL}/ai/jobs/${job.id}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (response.ok) setJob(await response.json());
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [job, accessToken]);

  async function handleGenerate() {
    if (!accessToken || !selectedAssetId) return;
    setError(null);
    setIsSubmitting(true);

    const response = await fetch(`${API_BASE_URL}/ai/generate-video`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ source_asset_id: selectedAssetId, prompt: prompt || null }),
    });

    setIsSubmitting(false);
    if (!response.ok) {
      setError(await readApiError(response));
      return;
    }
    setJob(await response.json());
  }

  const stages: PipelineStage[] = [
    {
      label: "Upload",
      status: selectedAssetId ? "success" : "idle",
      caption: selectedAssetId ? "selesai" : "belum",
    },
    {
      label: "Generate",
      status: stageStatusForJob(job),
      caption: !job
        ? "belum"
        : job.status === "success"
          ? "selesai"
          : job.status === "failed"
            ? "gagal"
            : "sedang proses",
    },
    { label: "Edit", status: "idle", caption: "belum" },
    { label: "Publish", status: "idle", caption: "belum" },
  ];

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="font-display text-2xl text-ink">Generate Studio</h1>
        <p className="text-sm text-ink-muted">
          Pilih foto produk, tambahkan gaya referensi (opsional), lalu generate.
        </p>
      </div>

      <TimelinePipeline stages={stages} />

      <section className="flex flex-col gap-3">
        <h2 className="text-sm text-ink-muted">1. Pilih foto</h2>
        {photos === null ? (
          <p className="text-sm text-ink-muted">Memuat…</p>
        ) : photos.length === 0 ? (
          <p className="text-sm text-ink-muted">
            Belum ada foto di Media Library.{" "}
            <Link href="/media" className="text-rec hover:underline">
              Upload dulu
            </Link>
            .
          </p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {photos.map((photo) => (
              <button
                key={photo.id}
                type="button"
                onClick={() => setSelectedAssetId(photo.id)}
                className={`h-20 w-20 overflow-hidden rounded-md ring-2 transition-colors ${
                  selectedAssetId === photo.id
                    ? "ring-rec"
                    : "ring-transparent hover:ring-panel-raised"
                }`}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={photo.url}
                  alt={photo.original_filename}
                  className="h-full w-full object-cover"
                />
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="flex max-w-sm flex-col gap-3">
        <h2 className="text-sm text-ink-muted">2. Gaya referensi (opsional)</h2>
        <TextField
          id="prompt"
          label="Gaya referensi"
          placeholder="Contoh: close-up produk, latar dapur minimalis"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </section>

      {error && (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          {error}
        </p>
      )}

      <Button
        onClick={handleGenerate}
        disabled={!selectedAssetId || isSubmitting}
        className="w-fit"
      >
        {isSubmitting ? "Mengirim…" : "Generate video"}
      </Button>

      {job?.status === "success" && (
        <p className="rounded-md border border-signal/40 bg-signal/10 px-3 py-2 text-sm text-signal">
          Video berhasil dibuat.
        </p>
      )}
      {job?.status === "failed" && (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          Generate gagal: {job.error_message}
        </p>
      )}
    </div>
  );
}
