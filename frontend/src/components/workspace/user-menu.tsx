"use client";

import { signOut } from "next-auth/react";
import Link from "next/link";

// Guest mode (Phase 6R catatan sesi): a guest's real backend email
// (`guest+<uuid>@guest.advanceai.app`) is meaningless to show — surface a plain
// "Mode Tamu" badge plus a way to convert to a real account instead of leaking it.
export function UserMenu({
  name,
  email,
  isGuest,
}: {
  name?: string | null;
  email?: string | null;
  isGuest?: boolean;
}) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <div className="text-right">
        <p className="text-ink">{isGuest ? "Mode Tamu" : (name ?? "Creator")}</p>
        {isGuest ? (
          <Link href="/register" className="text-rec hover:underline">
            Simpan sebagai akun
          </Link>
        ) : (
          <p className="text-ink-muted">{email}</p>
        )}
      </div>
      <button
        type="button"
        onClick={() => signOut({ callbackUrl: "/" })}
        className="rounded-md border border-panel-raised px-3 py-1.5 text-ink-muted transition-colors hover:bg-panel-raised hover:text-ink"
      >
        Keluar
      </button>
    </div>
  );
}
