"use client";

import { signOut } from "next-auth/react";

export function UserMenu({ name, email }: { name?: string | null; email?: string | null }) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <div className="text-right">
        <p className="text-ink">{name ?? "Creator"}</p>
        <p className="text-ink-muted">{email}</p>
      </div>
      <button
        type="button"
        onClick={() => signOut({ callbackUrl: "/login" })}
        className="rounded-md border border-panel-raised px-3 py-1.5 text-ink-muted transition-colors hover:bg-panel-raised hover:text-ink"
      >
        Keluar
      </button>
    </div>
  );
}
