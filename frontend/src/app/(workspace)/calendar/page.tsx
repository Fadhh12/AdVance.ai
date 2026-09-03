"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { TallyDot, type TallyStatus } from "@/components/ui/tally-dot";
import { API_BASE_URL } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { Platform, Post } from "@/lib/types";

const PLATFORM_LABELS: Record<Platform, string> = {
  instagram: "Instagram Reels",
  tiktok: "TikTok",
  youtube: "YouTube Shorts",
};

function statusLabel(post: Post): { text: string; tally: TallyStatus } {
  if (post.status === "manual_uploaded") return { text: "Sudah saya upload", tally: "success" };
  if (post.status === "manual_ready") return { text: "Siap diupload manual", tally: "idle" };
  if (post.export_status === "failed") return { text: "Export gagal", tally: "failed" };
  return { text: "Menyiapkan…", tally: "processing" };
}

export default function ContentCalendarPage() {
  const { data: session } = useSession();
  const accessToken = session?.accessToken;
  const [posts, setPosts] = useState<Post[] | null>(null);

  useEffect(() => {
    let ignore = false;
    (async () => {
      if (!accessToken) return;
      const response = await fetch(`${API_BASE_URL}/posts`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!ignore && response.ok) setPosts(await response.json());
    })();
    return () => {
      ignore = true;
    };
  }, [accessToken]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl text-ink">Content Calendar</h1>
        <p className="text-sm text-ink-muted">
          Status semua post per platform, dari semua proyek.
        </p>
      </div>

      {posts === null ? (
        <p className="text-sm text-ink-muted">Memuat…</p>
      ) : posts.length === 0 ? (
        <p className="text-sm text-ink-muted">
          Belum ada post disiapkan.{" "}
          <Link href="/editor" className="text-rec hover:underline">
            Buka Editor
          </Link>{" "}
          untuk render lalu siapkan publish.
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-panel">
          {posts.map((post) => {
            const { text, tally } = statusLabel(post);
            return (
              <li key={post.id} className="flex items-center gap-4 py-3 text-sm">
                <TallyDot status={tally} />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-ink">{post.project_title ?? "(tanpa judul)"}</p>
                  <p className="text-xs text-ink-muted">{PLATFORM_LABELS[post.platform]}</p>
                </div>
                <span className="w-40 shrink-0 text-right text-xs text-ink-muted">{text}</span>
                <span className="w-36 shrink-0 text-right text-xs text-ink-muted">
                  {formatDateTime(post.created_at)}
                </span>
                <Link
                  href={`/publish/${post.project_id}`}
                  className="shrink-0 text-xs text-rec hover:underline"
                >
                  Buka
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
