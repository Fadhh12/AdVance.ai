import Link from "next/link";

export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
      <span className="h-2 w-2 rounded-full bg-rec" aria-hidden />
      <h1 className="font-display text-4xl tracking-tight text-ink">adVance.AI</h1>
      <p className="max-w-md text-sm text-ink-muted">
        Upload foto atau ide, AI generate, edit, dan siapkan video untuk Instagram,
        TikTok, dan YouTube.
      </p>
      <div className="mt-2 flex gap-4 text-sm">
        <Link href="/login" className="text-rec hover:underline">
          Masuk
        </Link>
        <Link href="/register" className="text-rec hover:underline">
          Daftar
        </Link>
      </div>
    </main>
  );
}
