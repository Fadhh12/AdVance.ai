export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
      <span className="h-2 w-2 rounded-full bg-rec" aria-hidden />
      <h1 className="font-display text-4xl tracking-tight text-ink">adVance.AI</h1>
      <p className="max-w-md text-sm text-ink-muted">
        Workspace produksi konten belum mulai dibangun di sini — mulai dari Phase 1
        (Auth &amp; Core Infra) sesuai Task Breakdown di adVance-AI-Spesifikasi-Proyek.md.
      </p>
    </main>
  );
}
