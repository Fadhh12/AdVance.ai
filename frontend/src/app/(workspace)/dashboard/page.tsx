import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-2">
      <h1 className="font-display text-2xl text-ink">Dashboard</h1>
      <p className="max-w-md text-sm text-ink-muted">
        Belum ada konten.{" "}
        <Link href="/media" className="text-rec hover:underline">
          Upload foto produk pertamamu
        </Link>{" "}
        lalu buka{" "}
        <Link href="/generate" className="text-rec hover:underline">
          Generate Studio
        </Link>{" "}
        untuk mulai bikin video.
      </p>
    </div>
  );
}
