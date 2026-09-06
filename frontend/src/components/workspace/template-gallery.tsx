"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api-client";
import type { Template } from "@/lib/types";
import { useWorkspace } from "@/components/workspace/workspace-context";

const MODE_LABELS: Record<Template["mode"], string> = {
  product_ad: "Iklan Produk",
  affiliate: "Affiliate",
};

// DESIGN_SYSTEM.md §5.3: a filmstrip row, not a uniform rounded-card grid — each tile
// keeps its own thumbnail-placeholder + name + mode, scrolling horizontally instead of
// wrapping into identical cards.
export function TemplateGallery() {
  const { accessToken, applyTemplate } = useWorkspace();
  const [templates, setTemplates] = useState<Template[] | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

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

  if (templates === null) {
    return <p className="text-sm text-ink-muted">Memuat template…</p>;
  }
  if (templates.length === 0) {
    return null;
  }

  return (
    <div className="flex gap-3 overflow-x-auto pb-1">
      {templates.map((template) => {
        const isSelected = selectedId === template.id;
        return (
          <button
            key={template.id}
            type="button"
            onClick={() => {
              setSelectedId(template.id);
              applyTemplate(template);
            }}
            className={`flex w-44 shrink-0 flex-col gap-2 rounded-md border p-3 text-left transition-colors ${
              isSelected
                ? "border-rec bg-panel-raised"
                : "border-panel-raised bg-panel hover:bg-panel-raised"
            }`}
          >
            <div className="flex h-20 items-center justify-center rounded-sm bg-canvas text-xs text-ink-muted">
              {template.thumbnail_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={template.thumbnail_url}
                  alt={template.name}
                  className="h-full w-full rounded-sm object-cover"
                />
              ) : (
                MODE_LABELS[template.mode]
              )}
            </div>
            <p className="text-sm text-ink">{template.name}</p>
            {template.description && (
              <p className="line-clamp-2 text-xs text-ink-muted">{template.description}</p>
            )}
          </button>
        );
      })}
    </div>
  );
}
