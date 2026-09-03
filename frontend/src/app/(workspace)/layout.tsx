import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import { Sidebar } from "@/components/workspace/sidebar";
import { UserMenu } from "@/components/workspace/user-menu";
import { authOptions } from "@/lib/auth-options";

export default async function WorkspaceLayout({ children }: { children: ReactNode }) {
  const session = await getServerSession(authOptions);
  if (!session) {
    redirect("/login");
  }

  return (
    <div className="flex flex-1">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-end border-b border-panel px-6 py-4">
          <UserMenu name={session.user?.name} email={session.user?.email} />
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
