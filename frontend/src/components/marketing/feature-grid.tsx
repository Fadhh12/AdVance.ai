import { Image, MessageSquare, Scissors, Send, Sparkles, Wand2, type LucideIcon } from "lucide-react";

// Only features that actually ship today (CLAUDE.md: no hallucinated features) — no
// AI Influencer, no motion graphics, no auto-posting. List style with dividers
// (DESIGN_SYSTEM.md §5.3), not a shadow-card grid.
const FEATURES: Array<{ icon: LucideIcon; title: string; description: string }> = [
  {
    icon: Image,
    title: "Media Library",
    description: "Upload dan kelola foto produk, gampang dipilih ulang untuk generate berikutnya.",
  },
  {
    icon: Sparkles,
    title: "Generate Studio",
    description: "AI ubah foto produk jadi video pendek, lengkap dengan status render real-time.",
  },
  {
    icon: MessageSquare,
    title: "AI Chat Agent",
    description:
      'Minta lewat obrolan, misalnya "generate video dari foto ini" — agent yang benar-benar menjalankan aksinya, bukan cuma menyarankan.',
  },
  {
    icon: Wand2,
    title: "AI Image & Audio",
    description: "Butuh gambar atau voiceover tambahan? Generate langsung dari chat, hasilnya masuk ke Media Library.",
  },
  {
    icon: Scissors,
    title: "Editor Ringan",
    description: "Trim, tambah caption, pilih musik — tanpa timeline rumit ala software edit profesional.",
  },
  {
    icon: Send,
    title: "Publish Manual Assist",
    description:
      "Crop otomatis 9:16 + caption per platform (Instagram/TikTok/YouTube), download atau scan QR ke HP untuk upload manual.",
  },
];

export function FeatureGrid() {
  return (
    <section id="fitur" className="border-t border-paper-ink/10 bg-paper-ink/[0.02]">
      <div className="mx-auto max-w-6xl px-6 py-16 md:py-24">
        <h2 className="font-display text-3xl text-paper-ink md:text-4xl">
          Semua yang sudah bisa kamu pakai
        </h2>
        <p className="mt-3 max-w-xl text-paper-ink-muted">
          Fitur yang sudah jalan hari ini — bukan roadmap.
        </p>
        <ul className="mt-10 divide-y divide-paper-ink/10">
          {FEATURES.map((feature) => (
            <li key={feature.title} className="flex gap-4 py-6">
              <feature.icon className="h-6 w-6 shrink-0 text-rec" aria-hidden />
              <div>
                <h3 className="font-display text-lg text-paper-ink">{feature.title}</h3>
                <p className="mt-1 text-sm text-paper-ink-muted">{feature.description}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
