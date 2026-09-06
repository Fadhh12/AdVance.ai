"use client";

import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { TemplateGallery } from "@/components/workspace/template-gallery";
import { useWorkspace } from "@/components/workspace/workspace-context";
import type { ProjectMode } from "@/lib/types";

const MODES: Array<{ value: ProjectMode; label: string }> = [
  { value: "product_ad", label: "Iklan Produk" },
  { value: "affiliate", label: "Affiliate" },
];

export function GeneratePanel() {
  const {
    selectedAssetId,
    prompt,
    setPrompt,
    generate,
    isGenerating,
    job,
    projectTitle,
    setProjectTitle,
    projectMode,
    setProjectMode,
    createProject,
    isCreatingProject,
  } = useWorkspace();

  return (
    <section id="stage-generate" className="flex flex-col gap-4 scroll-mt-24">
      <div>
        <h2 className="font-display text-lg text-ink">2. Generate video</h2>
        <p className="text-sm text-ink-muted">
          Pilih template gaya (opsional), tulis gaya referensi, lalu generate.
        </p>
      </div>

      <TemplateGallery />

      <div className="max-w-sm">
        <TextField
          id="prompt"
          label="Gaya referensi (opsional)"
          placeholder="Contoh: close-up produk, latar dapur minimalis"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </div>

      <Button onClick={generate} disabled={!selectedAssetId || isGenerating} className="w-fit">
        {isGenerating ? "Mengirim…" : "Generate video"}
      </Button>

      {!selectedAssetId && (
        <p className="text-xs text-ink-muted">Pilih foto dulu di langkah 1.</p>
      )}

      {job && job.status !== "success" && job.status !== "failed" && (
        <p className="text-sm text-ink-muted">Sedang diproses AI — bisa beberapa saat…</p>
      )}

      {job?.status === "failed" && (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          Generate gagal: {job.error_message}
        </p>
      )}

      {job?.status === "success" && (
        <section className="flex max-w-sm flex-col gap-3 rounded-md border border-signal/40 bg-signal/10 p-4">
          <p className="text-sm text-signal">Video berhasil dibuat. Lanjut ke Edit?</p>
          <TextField
            id="project-title"
            label="Judul proyek"
            placeholder="Contoh: Sepatu lari — konten Q3"
            value={projectTitle}
            onChange={(e) => setProjectTitle(e.target.value)}
          />
          <fieldset className="flex flex-col gap-1.5 text-sm">
            <legend className="text-ink-muted">Mode</legend>
            <div className="flex gap-4">
              {MODES.map((option) => (
                <label key={option.value} className="flex items-center gap-1.5 text-ink">
                  <input
                    type="radio"
                    name="mode"
                    checked={projectMode === option.value}
                    onChange={() => setProjectMode(option.value)}
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </fieldset>
          <Button
            onClick={createProject}
            disabled={!projectTitle.trim() || isCreatingProject}
            className="w-fit"
          >
            {isCreatingProject ? "Membuat…" : "Lanjut ke Edit"}
          </Button>
        </section>
      )}
    </section>
  );
}
