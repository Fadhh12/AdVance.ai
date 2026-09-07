"use client";

import { useSession } from "next-auth/react";

import { CreateNewCard } from "@/components/dashboard/create-new-card";
import { RecentProjectsList } from "@/components/dashboard/recent-projects-list";
import { TemplateHubGrid } from "@/components/dashboard/template-hub-grid";

// Phase 6R-7: Dashboard becomes the "hub" (qreed.ai-inspired) — pick a template or
// start blank, land in /studio (the editing canvas, unchanged) either way. Was a
// placeholder empty-state since Phase 1, from before Media Library/Studio existed.
export default function DashboardPage() {
  const { data: session } = useSession();
  const isGuest = Boolean(session?.user?.email?.endsWith("@guest.advanceai.app"));
  const greetingName = isGuest ? "Kreator" : (session?.user?.name ?? "Kreator");
  const accessToken = session?.accessToken;

  return (
    <div className="flex flex-col gap-10">
      <div>
        <h1 className="font-display text-2xl text-ink">Halo, {greetingName}</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Mulai dari template, atau langsung buat dari kosong.
        </p>
      </div>

      <CreateNewCard />
      <TemplateHubGrid accessToken={accessToken} />
      <RecentProjectsList accessToken={accessToken} />
    </div>
  );
}
