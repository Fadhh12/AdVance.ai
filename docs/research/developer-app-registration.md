# Checklist Developer App: Meta, TikTok, YouTube

> Ini dokumen riset & checklist untuk **aksi manual user** — Claude/agent tidak bisa mendaftarkan akun developer atas nama kamu (butuh verifikasi bisnis, nomor telepon, kepemilikan domain, dsb). Mulai proses ini **paralel sedini mungkin** (SDD §Rekomendasi Urutan Kerja) karena approval bisa memakan waktu berminggu-minggu, dan baru bisa diajukan setelah ada domain + produk berjalan.

Status: belum diajukan (per catatan CLAUDE.md — jangan asumsikan token/API ini sudah aktif di kode manapun).

---

## 1. Meta (Instagram Content Publishing API / Graph API)

**Prasyarat sebelum bisa submit:**
- Akun Instagram harus **Business** atau **Creator**, terhubung ke sebuah **Facebook Page**.
- Punya **Meta Business Account** terverifikasi (Business Manager).
- App terdaftar di [developers.facebook.com](https://developers.facebook.com/), dengan **Business Verification** selesai (upload dokumen legal bisnis).
- **Privacy Policy URL** dan **Terms of Service URL** yang live (bukan localhost) — ini kenapa domain harus sudah jalan dulu.
- App harus punya use case jelas saat submit App Review: `instagram_content_publish`, `instagram_basic`, `pages_show_list`, `pages_read_engagement`.

**Langkah:**
1. Buat App di Meta for Developers → tipe "Business".
2. Tambahkan produk "Instagram Graph API".
3. Lengkapi Business Verification (bisa makan waktu 1–2 minggu, kadang lebih).
4. Isi App Review dengan screencast alur pemakaian (submission harus menunjukkan app benar-benar berfungsi — artinya Phase 1–5 harus sudah live/deployed sebelum submit ini).
5. Setelah approved: baru boleh implementasi Phase 6 (OAuth flow IG).

**Rate limit & policy penting:** batasi frekuensi post per akun (Meta punya limit publish per 24 jam per IG Business account), wajib comply Platform Policy soal konten & spam.

---

## 2. TikTok (Content Posting API)

**Prasyarat:**
- Daftar sebagai TikTok Developer di [developers.tiktok.com](https://developers.tiktok.com/).
- Untuk Content Posting API scope publik (bukan sandbox), butuh **audit aplikasi** oleh TikTok — perlu deskripsi use case, demo video, privacy policy URL.
- Direct Post ke akun publik butuh approval terpisah dari sekadar akses sandbox/testing.

**Langkah:**
1. Register developer account + buat app.
2. Tambah produk "Content Posting API".
3. Isi form audit: nama app, deskripsi, demo video alur upload, privacy policy & ToS URL live.
4. Selama menunggu approval, app hanya bisa dites dengan akun TikTok milik developer sendiri (sandbox/unaudited scope) — cocok untuk internal testing tapi belum untuk user publik.

---

## 3. YouTube (YouTube Data API v3)

**Prasyarat:**
- Google Cloud Project + aktifkan "YouTube Data API v3" di Google Cloud Console.
- OAuth consent screen harus diisi lengkap (nama app, logo, privacy policy URL, scope yang diminta: `youtube.upload`).
- Untuk quota production penuh (bukan quota testing default 10,000 unit/hari yang cepat habis untuk resumable upload), ajukan **API quota increase request** — ini juga butuh app sudah live & privacy policy jelas.
- Kalau app dipakai banyak user eksternal (bukan cuma testing), OAuth consent screen kemungkinan butuh **Google verification** (terutama scope sensitif seperti upload video).

**Langkah:**
1. Buat project di Google Cloud Console, aktifkan YouTube Data API v3.
2. Setup OAuth consent screen (external, isi semua field wajib).
3. Buat OAuth Client ID (Web application) — redirect URI mengarah ke domain produksi.
4. Submit untuk verification (kalau butuh scope sensitif) + quota increase.

---

## Ringkasan Aksi untuk User (bisa mulai sekarang, tidak perlu tunggu Phase 1–5 selesai)
- [ ] Siapkan domain untuk adVance.AI (kalau belum ada) — semua 3 platform butuh Privacy Policy/ToS URL live.
- [ ] Buat halaman Privacy Policy + Terms of Service sederhana (bisa halaman statis dulu).
- [ ] Buat Meta Business Account, mulai Business Verification.
- [ ] Register TikTok Developer account.
- [ ] Buat Google Cloud Project, aktifkan YouTube Data API v3.
- [ ] Setelah Phase 1–5 live di domain publik → submit App Review ke ketiganya sekaligus (butuh demo video alur pakai produk asli).

Sampai semua approved, produk tetap 100% terpakai lewat **Publish Manual Assist** (Phase 5) — auto-post (Phase 6) baru dikerjakan setelah approval turun.
