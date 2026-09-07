"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api-client";
import type { MotionPreset } from "@/lib/types";
import { useWorkspace } from "@/components/workspace/workspace-context";

// Same filmstrip motif as TemplateGallery (DESIGN_SYSTEM.md §5.3/§5.6) — a small style
// gallery, not an operational dashboard, so a horizontal row of tiles is fine. No
// thumbnails (presets are ffmpeg recipes, not media with cover art) — duration/aspect
// ratio stand in as the at-a-glance info instead.
export function MotionPresetPicker() {
  const { accessToken, motionPreset, setMotionPreset } = useWorkspace();
  const [presets, setPresets] = useState<MotionPreset[] | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    let ignore = false;
    apiFetch<MotionPreset[]>("/motion-presets", { token: accessToken })
      .then((data) => {
        if (!ignore) setPresets(data);
      })
      .catch(() => {
        if (!ignore) setPresets([]);
      });
    return () => {
      ignore = true;
    };
  }, [accessToken]);

  if (presets === null) {
    return <p className="text-sm text-ink-muted">Memuat motion preset…</p>;
  }
  if (presets.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-sm text-ink-muted">Motion preset (opsional)</h3>
      <div className="flex gap-3 overflow-x-auto pb-1">
        <button
          type="button"
          onClick={() => setMotionPreset("")}
          className={`w-40 shrink-0 rounded-md border p-3 text-left transition-colors ${
            motionPreset === ""
              ? "border-rec bg-panel-raised"
              : "border-panel-raised bg-panel hover:bg-panel-raised"
          }`}
        >
          <p className="text-sm text-ink">Tanpa preset</p>
          <p className="text-xs text-ink-muted">Trim polos seperti biasa.</p>
        </button>
        {presets.map((preset) => {
          const isSelected = motionPreset === preset.id;
          return (
            <button
              key={preset.id}
              type="button"
              onClick={() => setMotionPreset(preset.id)}
              className={`w-52 shrink-0 flex-col gap-1 rounded-md border p-3 text-left transition-colors ${
                isSelected
                  ? "border-rec bg-panel-raised"
                  : "border-panel-raised bg-panel hover:bg-panel-raised"
              }`}
            >
              <p className="text-sm text-ink">{preset.name}</p>
              <p className="line-clamp-3 text-xs text-ink-muted">{preset.description}</p>
              <p className="mt-1 text-[11px] text-ink-muted">
                {preset.aspect_ratio} · {preset.min_duration_seconds}-{preset.max_duration_seconds}s
              </p>
            </button>
          );
        })}
      </div>
      {motionPreset && (
        <p className="text-xs text-ink-muted">
          Preset menggantikan pengaturan trim di atas — durasi &amp; gaya motion ditentukan
          preset. Klik &quot;Simpan draft&quot; dulu sebelum render supaya pilihan ini tersimpan.
        </p>
      )}
    </div>
  );
}
