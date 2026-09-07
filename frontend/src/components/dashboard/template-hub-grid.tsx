"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api-client";
import { MODE_ICON, MODE_LABEL, templateGradient } from "@/lib/template-cover";
import type { ProjectMode, Template } from "@/lib/types";

const MODES: ProjectMode[] = ["product_ad", "affiliate"];

// Dashboard "hub" template picker (Phase 6R-7) — a real grid with cover art, unlike
// the horizontal filmstrip inside /studio (template-gallery.tsx). Grouped by `mode`
// because that's the only real categorization the Template model has today (no
// fabricated categories — see DESIGN_SYSTEM.md §5.5). Same 4 seeded templates, same
// GET /templates endpoint the in-studio picker already uses.
export function TemplateHubGrid({ accessToken }: { accessToken: string | undefined }) {
  const router = useRouter();
  const [templates, setTemplates] = useState<Template[] | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    let ignore = false;
    apiFetch<Template[]>("/templates", { token: accessToken })
      .then((data) => {
        if (!ignore) setTemplates(data);
      })
      .catch(() => {
        if (!ignore) setTemplates([]);
      });
    return () => {
      ignore = true;
    };
  }, [accessToken]);

  if (!templates || templates.length === 0) return null;

  function openTemplate(template: Template) {
    const params = new URLSearchParams({ mode: template.mode, prompt: template.prompt_preset });
    router.push(`/studio?${params.toString()}`);
  }

  return (
    <div className="flex flex-col gap-8">
      {MODES.map((mode) => {
        const items = templates.filter((template) => template.mode === mode);
        if (items.length === 0) return null;
        const Icon = MODE_ICON[mode];
        return (
          <div key={mode}>
            <h2 className="flex items-center gap-2 font-display text-lg text-ink">
              <Icon className="h-5 w-5 text-rec" aria-hidden />
              {MODE_LABEL[mode]}
            </h2>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((template) => (
                <button
                  key={template.id}
                  type="button"
                  onClick={() => openTemplate(template)}
                  className="flex flex-col overflow-hidden rounded-lg border border-panel-raised bg-panel text-left transition-colors hover:border-rec/60"
                >
                  <div
                    className={`flex h-28 items-center justify-center bg-gradient-to-br ${templateGradient(template.id)}`}
                  >
                    <Icon className="h-8 w-8 text-ink-muted" aria-hidden />
                  </div>
                  <div className="p-4">
                    <p className="text-sm text-ink">{template.name}</p>
                    {template.description && (
                      <p className="mt-1 line-clamp-2 text-xs text-ink-muted">
                        {template.description}
                      </p>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
