"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { MotionPresetPicker } from "@/components/workspace/motion-preset-picker";
import { useWorkspace } from "@/components/workspace/workspace-context";

// No real music catalog yet — just enough to exercise "pilih musik" (FR-05). Wiring an
// actual audio library/licensing is out of scope until a provider decision is made.
const MUSIC_TRACKS = [
  { value: "", label: "Tidak ada musik" },
  { value: "upbeat-pop", label: "Upbeat Pop" },
  { value: "chill-lofi", label: "Chill Lo-fi" },
  { value: "energetic-corporate", label: "Energetic Corporate" },
];

export function EditPanel() {
  const {
    project,
    caption,
    setCaption,
    musicTrack,
    setMusicTrack,
    trimStart,
    setTrimStart,
    trimEnd,
    setTrimEnd,
    saveDraft,
    isSavingDraft,
    render,
    isRendering,
  } = useWorkspace();
  const [previewFailed, setPreviewFailed] = useState(false);

  if (!project) {
    return (
      <section id="stage-edit" className="flex flex-col gap-2 scroll-mt-24">
        <h2 className="font-display text-lg text-ink">3. Edit</h2>
        <p className="text-sm text-ink-muted">
          Selesaikan langkah Generate dulu untuk membuka editor.
        </p>
      </section>
    );
  }

  return (
    <section id="stage-edit" className="flex flex-col gap-5 scroll-mt-24">
      <div>
        <h2 className="font-display text-lg text-ink">3. Edit — {project.title}</h2>
        <p className="text-sm text-ink-muted">
          {project.mode === "product_ad" ? "Iklan Produk" : "Affiliate"}
        </p>
      </div>

      <div className="flex flex-col gap-2">
        <h3 className="text-sm text-ink-muted">Preview</h3>
        {previewFailed ? (
          <p className="max-w-md text-sm text-ink-muted">
            Preview tidak bisa ditampilkan — provider AI masih mode mock, hasil generate
            saat ini belum berupa video sungguhan (lihat PROGRESS.md Phase 3).
          </p>
        ) : (
          <video
            src={project.final_video_url ?? project.source_video_url}
            controls
            className="max-h-80 w-full max-w-sm rounded-md bg-panel"
            onError={() => setPreviewFailed(true)}
          />
        )}
      </div>

      <MotionPresetPicker />

      <div className="grid max-w-sm grid-cols-2 gap-3">
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

      <div className="flex max-w-sm flex-col gap-2">
        <label htmlFor="caption" className="text-sm text-ink-muted">
          Caption
        </label>
        <textarea
          id="caption"
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
          rows={4}
          className="rounded-md border border-panel-raised bg-panel px-3 py-2 text-sm text-ink outline-none focus:border-rec"
          placeholder="Tulis caption untuk video ini…"
        />
      </div>

      <div className="flex max-w-sm flex-col gap-2">
        <label htmlFor="music" className="text-sm text-ink-muted">
          Musik
        </label>
        <select
          id="music"
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
      </div>

      {project.render_status === "failed" && project.render_error_message && (
        <p className="max-w-sm rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          Render gagal: {project.render_error_message}
        </p>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <Button variant="ghost" onClick={saveDraft} disabled={isSavingDraft}>
          {isSavingDraft ? "Menyimpan…" : "Simpan draft"}
        </Button>
        <Button onClick={render} disabled={isRendering}>
          {isRendering ? "Merender…" : "Render video"}
        </Button>
        {(project.render_status === "queued" || project.render_status === "processing") && (
          <span className="text-xs text-ink-muted">Sedang merender…</span>
        )}
      </div>
    </section>
  );
}
