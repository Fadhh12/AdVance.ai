"use client";

import Link from "next/link";
import { useRef } from "react";

import { Button } from "@/components/ui/button";
import { useWorkspace } from "@/components/workspace/workspace-context";

export function UploadPanel() {
  const { photos, selectedAssetId, selectAsset, uploadFiles, isUploading } = useWorkspace();
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <section id="stage-upload" className="flex flex-col gap-4 scroll-mt-24">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-lg text-ink">1. Pilih foto</h2>
          <p className="text-sm text-ink-muted">
            Pilih dari Media Library, atau upload foto produk baru.
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          className="hidden"
          onChange={(e) => e.target.files && uploadFiles(e.target.files)}
        />
        <Button onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
          {isUploading ? "Mengunggah…" : "Upload foto"}
        </Button>
      </div>

      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files.length > 0) uploadFiles(e.dataTransfer.files);
        }}
        className="rounded-md border border-dashed border-panel-raised p-4 text-center text-sm text-ink-muted"
      >
        Tarik &amp; lepas foto ke sini, atau klik &quot;Upload foto&quot;.
      </div>

      {photos === null ? (
        <p className="text-sm text-ink-muted">Memuat…</p>
      ) : photos.length === 0 ? (
        <p className="text-sm text-ink-muted">
          Belum ada foto.{" "}
          <Link href="/media" className="text-rec hover:underline">
            Buka Media Library
          </Link>{" "}
          untuk melihat semua media, atau upload di sini.
        </p>
      ) : (
        <div className="flex flex-wrap gap-3">
          {photos.map((photo) => (
            <button
              key={photo.id}
              type="button"
              onClick={() => selectAsset(photo.id)}
              className={`h-20 w-20 shrink-0 overflow-hidden rounded-md ring-2 transition-colors ${
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
  );
}
