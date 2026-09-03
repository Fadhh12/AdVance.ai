import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import { Sidebar } from "@/components/workspace/sidebar";
import { UserMenu } from "@/components/workspace/user-menu";
import { authOptions } from "@/lib/auth-options";

// Dev-only escape hatch (see frontend/.env.example): lets the workspace render without
// a login/register round trip while Postgres/Docker isn't set up locally yet, per user
// request. Pages that fetch data still guard on a missing access token and degrade to
// their empty state — nothing here fakes a real session. Must stay off (unset) in any
// deployed environment; never wire this to a real user identity.
const skipAuth = process.env.SKIP_AUTH === "true";

export default async function WorkspaceLayout({ children }: { children: ReactNode }) {
  const session = skipAuth ? null : await getServerSession(authOptions);
  if (!skipAuth && !session) {
    redirect("/login");
  }

  return (
    <div className="flex flex-1">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-end border-b border-panel px-6 py-4">
          {skipAuth ? (
            <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-1.5 text-sm text-alert">
              Mode dev — login dilewati (SKIP_AUTH=true). Data yang butuh akun tidak akan
              muncul sampai backend beneran jalan.
            </p>
          ) : (
            <UserMenu name={session?.user?.name} email={session?.user?.email} />
          )}
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
