# CLAUDE.md — Konteks Proyek adVance.AI

Dokumen ini adalah konteks wajib-baca untuk AI coding agent (Claude Code, Antigravity, atau agent lain) yang mengerjakan repo ini. Tujuannya: agent langsung paham proyek ini apa, tanpa menebak-nebak atau berhalusinasi soal fitur/arsitektur yang belum disepakati.

## Apa Proyek Ini
**adVance.AI** adalah web platform otomasi produksi konten video untuk satu orang (solo creator, UMKM, affiliate marketer). Alurnya: **upload foto → AI generate video → edit ringan → publish ke Instagram/TikTok/YouTube**. Tujuan pemakaian: iklan produk dan video ala-affiliate untuk monetisasi.

Dokumen sumber kebenaran (baca semua sebelum mulai kerja):
- `adVance-AI-Spesifikasi-Proyek.md` — PRD, SRS, SDD, UI/UX Flow, Task Breakdown lengkap.
- `DESIGN_SYSTEM.md` — aturan visual wajib, termasuk daftar hal yang **dilarang** (lihat "Anti-Slop Checklist").

Jangan mendesain ulang arsitektur atau alur produk dari nol — semua sudah diputuskan di dokumen di atas. Kalau ada gap/kontradiksi antara kode dan dokumen, dokumen yang menang, tanyakan ke user sebelum menyimpang.

## Status Fase Saat Ini (PENTING — jangan berasumsi lebih maju)
Proyek ini **baru mulai dari nol**, belum ada kode berjalan. Urutan kerja yang disepakati:

1. **Fase sekarang (bisa dikerjakan tanpa dependency eksternal):** auth, media upload/library, integrasi AI video generation, editor ringan, dan fitur **"Publish Manual Assist"** (export video + caption per-platform untuk diupload manual oleh user).
2. **Belum boleh diasumsikan tersedia:** auto-posting langsung ke Instagram/TikTok/YouTube via API. Developer app ke Meta/TikTok/YouTube **belum disetujui** — jangan tulis kode yang mengasumsikan token/akses API tersebut sudah ada atau berfungsi. Fitur auto-publish dirancang (lihat SDD Phase 6) tapi **diimplementasi belakangan**, setelah approval turun.
3. Provider AI video generation (Runway/Kling/Pika/dll) dan provider voice/TTS **belum final dipilih** — jangan hardcode ke satu provider tanpa konfirmasi; abstraksikan lewat interface/wrapper (`services/ai_providers/`) supaya provider bisa diganti tanpa mengubah kode di luar wrapper itu.

## Tech Stack (yang direkomendasikan di SDD — pakai ini kecuali user bilang lain)
- Frontend: Next.js (React) + TypeScript + Tailwind CSS
- Backend: FastAPI (Python)
- Job queue: Celery + Redis (untuk proses async: AI generation & publishing)
- Database: PostgreSQL
- Object storage: Cloudflare R2 / AWS S3
- Auth: NextAuth.js/Auth.js (frontend) + JWT (backend)

Jangan ganti stack ini secara sepihak. Kalau menurutmu ada alternatif lebih baik untuk satu bagian spesifik, jelaskan trade-off ke user dulu, jangan langsung ganti.

## Aturan Desain
Semua UI **wajib** ikut `DESIGN_SYSTEM.md`. Poin paling penting:
- Jangan pakai palet default AI-generated (krem+terracotta, hitam+neon, kartu rounded seragam, chrome template ALL-CAPS/eyebrow/angka 01-02-03 tanpa makna sekuensial).
- Gunakan token warna, tipografi, dan motif layout ("timeline pipeline", "tally light status") yang sudah didefinisikan di `DESIGN_SYSTEM.md`.
- Motion hanya untuk merespons aksi user atau satu momen transisi status yang disengaja — bukan scroll-reveal generik di semua section.

## Aturan Umum untuk Agent
- **Jangan berhalusinasi fitur** yang tidak ada di `adVance-AI-Spesifikasi-Proyek.md`. Kalau user minta sesuatu di luar dokumen itu, tanyakan dulu apakah itu penambahan scope, jangan diam-diam diasumsikan sudah bagian dari rencana.
- **Jangan berasumsi API pihak ketiga (Meta/TikTok/YouTube) sudah bisa dipakai** sampai user secara eksplisit bilang approval sudah turun.
- Struktur folder backend mengikuti pola di SDD §3.5 (`app/api`, `app/core`, `app/models`, `app/schemas`, `app/services`, `app/workers`).
- Semua proses AI generation & publishing bersifat **asynchronous** (job queue) — jangan buat implementasi yang blocking/synchronous untuk proses ini.
- Validasi file (tipe, ukuran) selalu di sisi server, bukan cuma di frontend.
- Token OAuth harus dienkripsi saat disimpan — jangan pernah simpan/tampilkan token mentah.
- Kalau ragu antara beberapa pendekatan implementasi, pilih yang paling sesuai SDD dan sebutkan alasannya secara singkat ke user — jangan diam-diam mengambil jalan pintas yang menyimpang dari dokumen.

## Yang TIDAK Dikerjakan di Fase Ini (Out of Scope Sekarang)
- Live streaming
- Editor video kompleks setara Premiere/CapCut penuh
- Manajemen ads spend/budget iklan berbayar
- Auto-posting nyata ke platform (sampai approval API disetujui — lihat status fase di atas)
