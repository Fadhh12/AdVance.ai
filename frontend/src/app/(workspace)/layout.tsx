import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import { WorkspaceShell } from "@/components/workspace/shell";
import { authOptions } from "@/lib/auth-options";

// Dev-only escape hatch (see frontend/.env.example): lets the workspace render without
// a login/register round trip while Postgres/Docker isn't set up locally yet, per user
// request. Pages that fetch data still guard on a missing access token and degrade to
// their empty state — nothing here fakes a real session. Must stay off (unset) in any
// deployed environment; never wire this to a real user identity.
const skipAuth = process.env.SKIP_AUTH === "true";

export default async function WorkspaceLayout({ children }: { children: ReactNode }) {
  const session = skipAuth ? null : await getServerSession(authOptions);
  // No session -> "/app" (guest-bootstrap entry), not "/login" and not "/" anymore:
  // "/" is the public marketing page (Phase 6R-7) and must never touch next-auth.
  // "/app" signs the visitor in as a guest automatically (Phase 6R catatan sesi) and
  // only falls back to showing Masuk/Daftar links if the guest sign-in itself fails.
  if (!skipAuth && !session) {
    redirect("/app");
  }

  const isGuest = Boolean(session?.user?.email?.endsWith("@guest.advanceai.app"));

  return (
    <WorkspaceShell
      name={session?.user?.name}
      email={session?.user?.email}
      isGuest={isGuest}
      devBanner={
        skipAuth ? (
          <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-1.5 text-sm text-alert">
            Mode dev — login dilewati (SKIP_AUTH=true). Data yang butuh akun tidak akan
            muncul sampai backend beneran jalan.
          </p>
        ) : undefined
      }
    >
      {children}
    </WorkspaceShell>
  );
}
