"use client";

import { useSession } from "next-auth/react";
import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { API_BASE_URL, readApiError } from "@/lib/api";
import { formatBytes, formatDateTime } from "@/lib/format";
import type { MediaAsset } from "@/lib/types";

const ACCEPTED_TYPES = "image/jpeg,image/png,image/webp,video/mp4,video/quicktime";

export default function MediaLibraryPage() {
  const { data: session } = useSession();
  const accessToken = session?.accessToken;
  const [assets, setAssets] = useState<MediaAsset[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadAssets = useCallback(async () => {
    if (!accessToken) return;
    const response = await fetch(`${API_BASE_URL}/media`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (response.ok) setAssets(await response.json());
  }, [accessToken]);

  // Initial fetch on mount/session-ready — guarded so a stale response from an
  // unmounted/re-run effect never overwrites newer state (react-hooks/set-state-in-effect).
  useEffect(() => {
    let ignore = false;
    (async () => {
      if (!accessToken) return;
      const response = await fetch(`${API_BASE_URL}/media`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!ignore && response.ok) setAssets(await response.json());
    })();
    return () => {
      ignore = true;
    };
  }, [accessToken]);

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0 || !accessToken) return;
    setError(null);
    setIsUploading(true);

    for (const file of Array.from(files)) {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE_URL}/media/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
        body: formData,
      });
      if (!response.ok) {
        setError(await readApiError(response));
        break;
      }
    }

    setIsUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
    loadAssets();
  }

  async function handleDelete(id: string) {
    if (!accessToken) return;
    await fetch(`${API_BASE_URL}/media/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    setAssets((current) => current?.filter((asset) => asset.id !== id) ?? current);
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl text-ink">Media Library</h1>
          <p className="text-sm text-ink-muted">
            Foto dan video mentah yang siap di-generate jadi video.
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <Button onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
          {isUploading ? "Mengunggah…" : "Upload media"}
        </Button>
      </div>

      {error && (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          {error}
        </p>
      )}

      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFiles(e.dataTransfer.files);
        }}
        className="rounded-md border border-dashed border-panel-raised p-6 text-center text-sm text-ink-muted"
      >
        Tarik &amp; lepas foto atau video ke sini, atau klik &quot;Upload media&quot;.
      </div>

      {assets === null ? (
        <p className="text-sm text-ink-muted">Memuat…</p>
      ) : assets.length === 0 ? (
        <p className="text-sm text-ink-muted">
          Belum ada media. Upload foto produk pertamamu untuk mulai.
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-panel">
          {assets.map((asset) => (
            <li key={asset.id} className="flex items-center gap-4 py-3">
              <div className="h-14 w-14 shrink-0 overflow-hidden rounded-md bg-panel">
                {asset.type === "photo" ? (
                  // Signed URLs vary per environment/render — next/image's remote
                  // allowlist doesn't fit here, plain <img> is the pragmatic choice.
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={asset.url}
                    alt={asset.original_filename}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-xs text-ink-muted">
                    Video
                  </div>
                )}
              </div>

              <div className="min-w-0 flex-1">
                <p className="truncate text-sm text-ink">{asset.original_filename}</p>
                <p className="text-xs text-ink-muted">
                  {asset.type === "photo" ? "Foto" : "Video mentah"}
                </p>
              </div>

              <span className="w-20 shrink-0 text-right text-xs text-ink-muted">
                {formatBytes(asset.size_bytes)}
              </span>
              <span className="w-36 shrink-0 text-right text-xs text-ink-muted">
                {formatDateTime(asset.uploaded_at)}
              </span>

              <button
                type="button"
                onClick={() => handleDelete(asset.id)}
                className="shrink-0 text-xs text-ink-muted transition-colors hover:text-alert"
              >
                Hapus
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
