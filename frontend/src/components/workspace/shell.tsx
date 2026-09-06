"use client";

import { useState } from "react";
import type { ReactNode } from "react";

import { Sidebar } from "@/components/workspace/sidebar";
import { UserMenu } from "@/components/workspace/user-menu";

// Sidebar becomes an off-canvas drawer below `lg` — the fixed 224px rail doesn't fit
// next to a workspace that also needs room for the chat panel (Phase 6R-6) on
// anything narrower than a laptop. `navOpen` state has to live in a client component;
// `(workspace)/layout.tsx` itself stays a server component so the session check there
// doesn't need to ship to the client.
export function WorkspaceShell({
  name,
  email,
  isGuest,
  devBanner,
  children,
}: {
  name?: string | null;
  email?: string | null;
  isGuest: boolean;
  devBanner?: ReactNode;
  children: ReactNode;
}) {
  const [navOpen, setNavOpen] = useState(false);

  return (
    <div className="flex min-h-0 flex-1">
      {navOpen && (
        <button
          type="button"
          aria-label="Tutup menu"
          onClick={() => setNavOpen(false)}
          className="fixed inset-0 z-30 bg-canvas/70 backdrop-blur-sm lg:hidden"
        />
      )}

      <div
        className={`fixed inset-y-0 left-0 z-40 w-64 transform transition-transform duration-200 ease-out lg:static lg:z-auto lg:w-56 lg:shrink-0 lg:translate-x-0 ${
          navOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <Sidebar onNavigate={() => setNavOpen(false)} />
      </div>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-3 border-b border-panel px-4 py-3 md:px-6 md:py-4">
          <button
            type="button"
            onClick={() => setNavOpen(true)}
            aria-label="Buka menu"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-ink-muted transition-colors hover:bg-panel-raised hover:text-ink lg:hidden"
          >
            <span className="flex flex-col gap-1">
              <span className="h-0.5 w-5 bg-current" />
              <span className="h-0.5 w-5 bg-current" />
              <span className="h-0.5 w-5 bg-current" />
            </span>
          </button>
          <div className="flex-1" />
          {devBanner ?? <UserMenu name={name} email={email} isGuest={isGuest} />}
        </header>
        <main className="min-w-0 flex-1 overflow-y-auto px-4 py-5 md:px-6 md:py-6">
          {children}
        </main>
      </div>
    </div>
  );
}
