"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { PhoneFrame } from "@/components/ui/phone-frame";
import { TallyDot, type TallyStatus } from "@/components/ui/tally-dot";
import { API_BASE_URL, readApiError } from "@/lib/api";
import type { ContentProject, Platform, Post } from "@/lib/types";

const POLL_INTERVAL_MS = 2500;

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

export default function PublishPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: session } = useSession();
  const accessToken = session?.accessToken;

  const [project, setProject] = useState<ContentProject | null>(null);
  const [posts, setPosts] = useState<Post[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPreparing, setIsPreparing] = useState(false);
  const [qrUrls, setQrUrls] = useState<Record<string, string>>({});

  useEffect(() => {
    let ignore = false;
    (async () => {
      if (!accessToken) return;
      const [projectResponse, postsResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/projects/${projectId}`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        }),
        fetch(`${API_BASE_URL}/projects/${projectId}/posts`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        }),
      ]);
      if (ignore) return;
      if (projectResponse.ok) setProject(await projectResponse.json());
      if (postsResponse.ok) setPosts(await postsResponse.json());
    })();
    return () => {
      ignore = true;
    };
  }, [accessToken, projectId]);

  // Poll while any export is still in flight.
  useEffect(() => {
    if (!accessToken || !posts) return;
    const stillExporting = posts.some(
      (post) => post.export_status === "queued" || post.export_status === "processing"
    );
    if (!stillExporting) return;

    const interval = setInterval(async () => {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/posts`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (response.ok) setPosts(await response.json());
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [accessToken, posts, projectId]);

  async function handlePrepare() {
    if (!accessToken) return;
    setError(null);
    setIsPreparing(true);

    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/posts`, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    setIsPreparing(false);
    if (!response.ok) {
      setError(await readApiError(response));
      return;
    }
    setPosts(await response.json());
  }

  async function handleMarkUploaded(postId: string) {
    if (!accessToken) return;
    const response = await fetch(`${API_BASE_URL}/posts/${postId}/mark-uploaded`, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (response.ok) {
      const updated: Post = await response.json();
      setPosts((current) =>
        current ? current.map((p) => (p.id === postId ? updated : p)) : current
      );
    }
  }

  async function handleShowQr(postId: string) {
    if (!accessToken || qrUrls[postId]) return;
    const response = await fetch(`${API_BASE_URL}/posts/${postId}/qr`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!response.ok) return;
    const blob = await response.blob();
    setQrUrls((current) => ({ ...current, [postId]: URL.createObjectURL(blob) }));
  }

  if (!project || posts === null) {
    return <p className="text-sm text-ink-muted">Memuat…</p>;
  }

  if (project.render_status !== "success") {
    return (
      <p className="max-w-md text-sm text-ink-muted">
        Render video dulu di{" "}
        <Link href={`/editor/${project.id}`} className="text-rec hover:underline">
          Editor
        </Link>{" "}
        sebelum bisa disiapkan untuk publish.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl text-ink">Publish — {project.title}</h1>
        <p className="text-sm text-ink-muted">
          Video di-crop dan caption disesuaikan otomatis per platform. Upload manual ke
          masing-masing app — auto-post menyusul setelah developer app disetujui.
        </p>
      </div>

      {posts.length === 0 ? (
        <Button onClick={handlePrepare} disabled={isPreparing} className="w-fit">
          {isPreparing ? "Menyiapkan…" : "Siapkan untuk Publish"}
        </Button>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
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
                    onClick={() => handleMarkUploaded(post.id)}
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

      {error && (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          {error}
        </p>
      )}
    </div>
  );
}
