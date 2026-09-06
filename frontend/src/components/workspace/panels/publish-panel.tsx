"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { PhoneFrame } from "@/components/ui/phone-frame";
import { TallyDot, type TallyStatus } from "@/components/ui/tally-dot";
import { useWorkspace } from "@/components/workspace/workspace-context";
import { apiFetchBlob } from "@/lib/api-client";
import type { Platform, Post } from "@/lib/types";

const PLATFORM_LABELS: Record<Platform, string> = {
  instagram: "Instagram Reels",
  tiktok: "TikTok",
  youtube: "YouTube Shorts",
};

const PLATFORM_ORDER: Platform[] = ["instagram", "tiktok", "youtube"];

function statusDot(post: Post): TallyStatus {
  if (post.export_status === "failed") return "failed";
  if (post.export_status === "success") return "success";
  if (post.export_status) return "processing";
  return "idle";
}

export function PublishPanel() {
  const { accessToken, project, posts, preparePublish, isPreparingPublish, markUploaded } =
    useWorkspace();
  const [qrUrls, setQrUrls] = useState<Record<string, string>>({});

  async function handleShowQr(postId: string) {
    if (!accessToken || qrUrls[postId]) return;
    try {
      const blob = await apiFetchBlob(`/posts/${postId}/qr`, { token: accessToken });
      setQrUrls((current) => ({ ...current, [postId]: URL.createObjectURL(blob) }));
    } catch {
      // QR is a convenience, not essential — download link still works without it
    }
  }

  if (!project || project.render_status !== "success") {
    return (
      <section id="stage-publish" className="flex flex-col gap-2 scroll-mt-24">
        <h2 className="font-display text-lg text-ink">4. Publish</h2>
        <p className="text-sm text-ink-muted">
          Render video dulu di langkah Edit sebelum bisa disiapkan untuk publish.
        </p>
      </section>
    );
  }

  return (
    <section id="stage-publish" className="flex flex-col gap-4 scroll-mt-24">
      <div>
        <h2 className="font-display text-lg text-ink">4. Publish — {project.title}</h2>
        <p className="text-sm text-ink-muted">
          Video di-crop dan caption disesuaikan otomatis per platform. Upload manual ke
          masing-masing app — auto-post menyusul setelah developer app disetujui.
        </p>
      </div>

      {posts === null ? (
        <p className="text-sm text-ink-muted">Memuat…</p>
      ) : posts.length === 0 ? (
        <Button onClick={preparePublish} disabled={isPreparingPublish} className="w-fit">
          {isPreparingPublish ? "Menyiapkan…" : "Siapkan untuk Publish"}
        </Button>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {PLATFORM_ORDER.map((platform) => {
            const post = posts.find((p) => p.platform === platform);
            if (!post) return null;

            return (
              <div key={post.id} className="flex flex-col gap-2">
                <div className="flex items-center gap-2 text-sm text-ink">
                  <TallyDot status={statusDot(post)} />
                  {PLATFORM_LABELS[platform]}
                </div>

                <PhoneFrame>
                  {post.video_url ? (
                    <video src={post.video_url} controls className="h-full w-full object-cover" />
                  ) : (
                    <div className="flex h-full items-center justify-center text-xs text-ink-muted">
                      {post.export_status === "failed" ? "Export gagal" : "Menyiapkan…"}
                    </div>
                  )}
                </PhoneFrame>

                {post.export_status === "failed" && (
                  <p className="text-xs text-alert">{post.export_error_message}</p>
                )}

                {post.caption && (
                  <div className="text-xs text-ink-muted">
                    {platform === "youtube" && post.youtube_title && (
                      <p className="mb-1 text-ink">{post.youtube_title}</p>
                    )}
                    <p className="line-clamp-3">{post.caption}</p>
                  </div>
                )}

                {post.video_url && (
                  <div className="flex flex-wrap items-center gap-3 text-xs">
                    <a
                      href={post.video_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-rec hover:underline"
                    >
                      Download
                    </a>
                    <button
                      type="button"
                      onClick={() => handleShowQr(post.id)}
                      className="text-rec hover:underline"
                    >
                      Bagikan ke HP
                    </button>
                  </div>
                )}

                {qrUrls[post.id] && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={qrUrls[post.id]} alt="QR code download" className="h-24 w-24" />
                )}

                {post.status === "manual_ready" && (
                  <Button
                    variant="ghost"
                    onClick={() => markUploaded(post.id)}
                    className="w-fit"
                  >
                    Tandai sudah saya upload
                  </Button>
                )}
                {post.status === "manual_uploaded" && (
                  <p className="flex items-center gap-1.5 text-xs text-signal">
                    <TallyDot status="success" /> Sudah kamu upload
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
