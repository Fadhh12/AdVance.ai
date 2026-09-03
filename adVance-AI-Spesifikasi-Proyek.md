# adVance.AI — Dokumen Spesifikasi Proyek

> **Catatan:** Nama proyek: **adVance.AI**. Scope MVP: **end-to-end** (upload foto → AI generate video → edit → auto-post), target **Instagram, TikTok, dan YouTube** sejak awal, tech stack direkomendasikan bebas.
>
> **Strategi fase awal:** Karena approval developer app Meta/TikTok/YouTube butuh waktu (bisa berminggu-minggu) dan baru bisa diajukan setelah ada produk/domain berjalan, adVance.AI dibangun dengan urutan **"bangun dulu yang bisa dikerjakan sekarang, auto-post menyusul saat approval turun"**:
> - **Sekarang (buildable tanpa nunggu approval siapa pun):** auth, media library, integrasi AI generation (foto→video), editor ringan, export hasil video final.
> - **Interim (sambil menunggu approval):** fitur **"Publish Manual Assist"** — video final + caption per-platform (sudah di-crop/disesuaikan rasio & limit karakter otomatis) bisa **didownload atau di-share ke HP** untuk diupload manual oleh user ke IG/TikTok/YouTube. Ini bikin produk tetap 100% terpakai dari hari pertama walau auto-post belum aktif.
> - **Setelah approval:** fitur "Publish Manual Assist" tinggal disambung ke job auto-publish yang sudah dirancang di SDD — tidak perlu bongkar arsitektur, cukup ganti "download" jadi "kirim ke API platform".

---

## DAFTAR ISI
1. PRD — Product Requirements Document
2. SRS — Software Requirements Specification
3. SDD — System Design Document
4. UI/UX Flow
5. Task Breakdown

---

# 1. PRD — Product Requirements Document

## 1.1 Latar Belakang
Membuat konten profesional untuk media sosial (reels, video pendek, iklan produk) butuh keahlian scripting, editing, motion graphics, dan effort konsisten — sesuatu yang sulit dilakukan sendirian secara konsisten. adVance.AI adalah web platform yang menjadi "tim produksi" virtual untuk satu orang: dari **foto/ide mentah → video jadi → otomatis tayang** di Instagram, TikTok, dan YouTube.

## 1.2 Tujuan Produk
- Memungkinkan satu orang menghasilkan konten video kualitas setara tim kecil, dengan kecepatan produksi tinggi dan biaya marjinal mendekati nol.
- Mengotomasi 3 tahap besar: **Generate** (foto/teks → video via AI) → **Edit** (potong, caption, musik, efek) → **Publish** (auto-post terjadwal ke 3 platform sekaligus).
- Mendukung dua use case utama: **iklan produk** (jualan/promosi) dan **video affiliate/monetisasi konten**.

## 1.3 Target User (Persona)
| Persona | Deskripsi | Kebutuhan Utama |
|---|---|---|
| Solo Creator / Personal Brand | Individu membangun personal brand, tidak punya tim | Konsistensi posting, hemat waktu produksi |
| Pemilik UMKM/Online Shop | Jualan produk di sosmed, foto produk seadanya | Ubah foto produk jadi video iklan menarik cepat |
| Affiliate Marketer | Cari cuan dari video promosi produk orang lain | Produksi video massal, variasi cepat untuk A/B testing |

## 1.4 Value Proposition
"Upload foto atau ide → AI yang generate, edit, dan posting video-nya ke semua platform sekaligus — kamu tinggal approve."

## 1.5 Fitur Utama (MVP — sesuai scope end-to-end)
1. **Upload & Media Library** — upload foto/video mentah, kelola aset.
2. **AI Video Generation** — foto → video (image-to-video AI), atau teks/skrip → video referensi/awal.
3. **AI Editing Assistant** — auto-caption/subtitle, auto-cut highlight, background music, voice-over AI, watermark/branding.
4. **Manual Editor (ringan)** — trim, reorder klip, ganti teks/caption, ganti musik, preview sebelum publish — supaya user tetap punya kendali akhir.
5. **Connect Social Accounts** — hubungkan akun Instagram, TikTok, YouTube via OAuth resmi masing-masing platform.
6. **Scheduler & Auto-Post** — jadwalkan atau langsung publish ke 3 platform sekaligus, dengan caption/hashtag yang bisa disesuaikan per platform.
7. **Content Calendar & Status Tracking** — lihat status tiap konten (draft/processing/scheduled/published/failed).
8. **Analytics Ringkas** — performa dasar per post (jika API platform mengizinkan) dan riwayat produksi.
9. **Template/Reference Video** — buat video "contoh" sebagai referensi gaya sebelum generate versi final.
10. **Billing/Quota** — karena AI generation berbayar per-use, perlu sistem kuota/paket langganan.

## 1.6 Fitur Lanjutan (Post-MVP / Future)
- A/B testing otomatis untuk video affiliate (banyak varian, lihat mana yang performa terbaik).
- Auto-repurpose 1 video panjang → beberapa short-form.
- Tim/kolaborasi multi-user.
- Integrasi platform lain (Facebook, X, Threads, Pinterest).
- AI product research (cari produk trending untuk affiliate).

## 1.7 User Flow Tingkat Tinggi
```
Daftar/Login → Hubungkan akun sosmed → Upload foto/ide
   → Pilih mode (Iklan Produk / Video Affiliate)
   → AI generate draft video → Edit ringan (opsional)
   → Preview per platform → Approve
   → Jadwalkan / Publish langsung → Tracking status & hasil
```

## 1.8 Success Metrics
- Waktu produksi per konten (turun signifikan dari cara manual).
- Jumlah konten yang berhasil auto-published tanpa gagal per minggu.
- Retensi user (dipakai rutin ≥3x/minggu).
- Rasio quota AI generation terpakai vs berhasil publish (efisiensi).

## 1.9 Out of Scope (MVP)
- Live streaming.
- Editing video kompleks setara Premiere/CapCut penuh (fokus AI-assisted, bukan editor profesional).
- Manajemen ads spend (budget iklan berbayar di platform) — hanya organic auto-post.

---

# 2. SRS — Software Requirements Specification

## 2.1 Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Sistem harus bisa autentikasi user (email/password + OAuth Google) |
| FR-02 | User dapat upload foto (jpg/png/webp) dan video (mp4/mov) ke media library |
| FR-03 | Sistem dapat mengirim foto/prompt ke AI video-generation provider dan menerima hasil video |
| FR-04 | Sistem dapat generate auto-caption/subtitle dari audio video (speech-to-text) |
| FR-05 | User dapat melakukan edit ringan (trim, reorder, ganti teks, ganti musik) pada hasil AI |
| FR-06 | User dapat menghubungkan akun Instagram, TikTok, YouTube via OAuth resmi masing-masing |
| FR-07 | Sistem dapat menjadwalkan post untuk waktu tertentu dan mengeksekusinya otomatis (via job scheduler) |
| FR-08 | Sistem dapat publish langsung (immediate) ke satu atau beberapa platform sekaligus |
| FR-09 | Sistem harus menampilkan status tiap konten: draft, processing, scheduled, published, failed |
| FR-10 | Jika publish gagal, sistem retry sesuai kebijakan dan menampilkan pesan error yang jelas |
| FR-11 | Sistem mencatat quota AI generation per user/paket dan menolak request jika quota habis |
| FR-12 | User dapat melihat riwayat & analitik dasar per post (jika data tersedia dari API platform) |
| FR-13 | **(Interim, sebelum akun developer app disetujui)** Sistem dapat mengekspor video final + caption per-platform (sudah disesuaikan rasio/limit karakter) dalam mode "Publish Manual Assist" — user download/share manual ke HP untuk upload sendiri |
| FR-14 | Sistem dapat menandai per-platform apakah mode publish-nya "Otomatis" (setelah API disetujui) atau "Manual Assist" (sebelum disetujui), tanpa mengubah alur kerja utama user |

## 2.2 Validasi
- Ukuran file upload maksimum (mis. foto ≤ 20MB, video mentah ≤ 500MB — sesuaikan biaya storage/AI).
- Format file: hanya jpg/png/webp untuk foto, mp4/mov untuk video.
- Durasi video hasil generate harus sesuai batas tiap platform (IG Reels ≤ 90 detik, TikTok ≤ 10 menit, YouTube Shorts ≤ 60 detik untuk kategori Shorts) — sistem harus **auto-adjust/crop** atau memberi peringatan bila melebihi batas platform tujuan.
- Caption per platform divalidasi terhadap limit karakter masing-masing (IG ~2200, TikTok ~2200, YouTube title ~100/description ~5000).
- Validasi koneksi OAuth: token expired harus terdeteksi sebelum publish, minta reconnect jika invalid.
- Validasi quota: cek sisa kuota AI generation sebelum job dijalankan, bukan sesudah (hindari biaya sia-sia).

## 2.3 Behavior (Sistem)
- Proses AI generation & publishing **asynchronous** (job queue) — user tidak menunggu di layar, mendapat notifikasi saat selesai.
- Setiap job punya status lifecycle: `queued → processing → success/failed`.
- Jika salah satu platform gagal publish (mis. token IG expired) tapi platform lain sukses, sistem tidak menggagalkan semuanya — status per platform independen.
- Auto-retry maksimum 3x dengan backoff untuk error transient (network/API rate limit); error permanen (mis. konten melanggar policy) tidak di-retry, langsung ditandai failed dengan alasan.
- Notifikasi in-app (dan opsional email) saat job AI generation selesai atau saat post gagal publish.

## 2.4 Aturan Aplikasi / Bisnis
- Setiap paket langganan punya kuota: jumlah AI generation/bulan, jumlah akun sosmed yang bisa dihubungkan, jumlah post terjadwal.
- Konten yang di-generate tetap milik user (hak cipta), platform hanya menyediakan alat.
- Sistem wajib patuh pada **kebijakan resmi tiap platform** (Meta Platform Policy, TikTok Developer Policy, YouTube API Services Terms) — termasuk larangan spam-posting dan rate limit resmi masing-masing API.
- Data token OAuth disimpan terenkripsi, tidak pernah ditampilkan mentah ke frontend.
- User dapat memutus koneksi akun sosmed kapan saja; ini otomatis membatalkan semua post terjadwal ke akun tersebut.

## 2.5 Non-Functional Requirements
- **Performance**: proses generate AI video idealnya selesai < 5 menit per klip pendek (tergantung provider AI, di luar kendali penuh sistem — beri estimasi waktu ke user).
- **Scalability**: job queue harus horizontal-scalable karena beban AI generation & posting bisa spike.
- **Security**: enkripsi token OAuth (at rest), HTTPS semua trafik, rate limiting API internal.
- **Reliability**: uptime scheduler untuk auto-post minimal 99% (post terjadwal tidak boleh "hilang").
- **Auditability**: log semua job (generate & publish) untuk debugging dan billing.

---

# 3. SDD — System Design Document

## 3.1 Rekomendasi Tech Stack

| Layer | Rekomendasi | Alasan |
|---|---|---|
| Frontend | **Next.js (React) + TypeScript**, Tailwind CSS | SSR/SEO untuk landing, cocok untuk dashboard kompleks, ekosistem besar |
| Backend API | **FastAPI (Python)** | Python memudahkan integrasi AI/ML, async native, cocok untuk job-heavy system |
| Job Queue / Worker | **Celery + Redis** (atau **BullMQ** jika mayoritas Node) | Wajib untuk proses async: generate AI & scheduled posting |
| Database | **PostgreSQL** | Relasional kuat untuk relasi user–akun sosmed–post–job; JSONB untuk metadata fleksibel |
| Object Storage | **Cloudflare R2** atau **AWS S3** | Simpan foto/video mentah & hasil generate, murah untuk file besar |
| Cache | **Redis** | Cache status job & rate-limit counter |
| Auth | **NextAuth.js / Auth.js** (frontend) + JWT (backend) | Standar, support OAuth Google mudah |
| Deployment | **Docker** + VPS/Railway/Fly.io (awal), scale ke AWS/GCP nanti | Mulai murah, scalable ke cloud besar saat traffic naik |
| Monitoring | **Sentry** (error tracking) + log terpusat | Wajib karena banyak proses async yang bisa silent-fail |

### Integrasi AI & Platform Eksternal (kandidat, cek ketersediaan/harga terbaru saat implementasi)
- **Image-to-video AI**: Runway (Gen-3/4), Kling AI, Pika, Luma Dream Machine, atau Google Veo via API — pilih berdasarkan biaya & kualitas saat riset teknis.
- **Voice-over/TTS**: ElevenLabs, atau Google/Azure TTS.
- **Auto-caption/subtitle**: Whisper (OpenAI) untuk speech-to-text.
- **Auto-posting**:
  - Instagram → **Meta Graph API** (Instagram Content Publishing API, butuh Business/Creator account).
  - TikTok → **TikTok Content Posting API**.
  - YouTube → **YouTube Data API v3** (resumable upload untuk Shorts/video).
- Semua integrasi posting ini **butuh approval developer app** dari masing-masing platform sebelum bisa dipakai publik — ini risiko timeline yang harus direncanakan di awal, bukan di akhir.

## 3.2 Arsitektur Tingkat Tinggi (deskripsi)
```
[Next.js Frontend] 
      │ (REST/GraphQL, HTTPS)
[FastAPI Backend] ── auth, CRUD, orchestrasi job
      │
      ├── enqueue → [Redis/Celery Queue] → [Worker: AI Generation]
      │                                          │→ panggil AI provider API
      │                                          │→ simpan hasil ke Object Storage
      │
      ├── enqueue → [Redis/Celery Queue] → [Worker: Scheduler/Publisher]
      │                                          │→ panggil Meta/TikTok/YouTube API
      │                                          │→ update status post
      │
      └── [PostgreSQL] ← semua metadata (user, media, job, post, account)
```

## 3.3 Skema Database (inti)

**users**
`id, email, password_hash, name, plan_id, created_at`

**subscriptions/plans**
`id, name, ai_generation_quota, connected_accounts_limit, price, period`

**social_accounts**
`id, user_id, platform (ig/tiktok/youtube), access_token (encrypted), refresh_token (encrypted), token_expires_at, platform_username, status`

**media_assets**
`id, user_id, type (photo/video_raw), file_url, uploaded_at`

**ai_jobs**
`id, user_id, source_asset_id, type (generate_video/caption/voiceover), status (queued/processing/success/failed), provider, result_url, error_message, created_at, completed_at`

**content_projects**
`id, user_id, title, mode (product_ad/affiliate), status (draft/ready/scheduled/published), final_video_url`

**posts**
`id, project_id, social_account_id, platform, caption, scheduled_at, published_at, status (scheduled/publishing/published/failed), platform_post_id, error_message`

**usage_logs**
`id, user_id, action, quota_used, created_at`

## 3.4 Rancangan API (contoh endpoint utama)
```
POST   /auth/register | /auth/login
GET    /media                 → list media user
POST   /media/upload           → upload foto/video

POST   /ai/generate-video      → kirim job generate video dari foto
GET    /ai/jobs/{id}           → cek status job

POST   /projects               → buat content project baru
PATCH  /projects/{id}          → edit ringan (trim, caption, musik)

GET    /social-accounts        → list akun terhubung
POST   /social-accounts/connect/{platform}   → mulai OAuth flow
DELETE /social-accounts/{id}   → putus koneksi

POST   /posts                  → buat post (langsung/terjadwal) ke 1+ platform
GET    /posts                  → list & status semua post
GET    /posts/{id}/analytics   → data performa dasar (jika tersedia)
```

## 3.5 Struktur Backend (folder, ilustratif — FastAPI)
```
backend/
├── app/
│   ├── api/            # routers per domain: auth, media, ai, projects, posts
│   ├── core/            # config, security, dependencies
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/
│   │   ├── ai_providers/     # wrapper tiap provider AI (runway.py, elevenlabs.py, whisper.py)
│   │   └── social_publishers/ # wrapper tiap platform (meta.py, tiktok.py, youtube.py)
│   ├── workers/          # celery tasks: generate_video_task, publish_post_task
│   └── main.py
├── alembic/              # migrations
└── tests/
```

## 3.6 Keamanan
- Token OAuth dienkripsi (mis. AES-256) sebelum disimpan di DB.
- Rate limiting di level API gateway untuk cegah abuse.
- Validasi ukuran & tipe file di sisi server, bukan cuma frontend.
- Signed URL untuk akses file di object storage (jangan public bucket langsung).

---

# 4. UI/UX Flow

## 4.1 Peta Halaman (Sitemap)
1. **Landing Page** (marketing, untuk user baru)
2. **Onboarding** — daftar/login → hubungkan minimal 1 akun sosmed
3. **Dashboard** — ringkasan: konten terbaru, status post, sisa quota
4. **Media Library** — upload & kelola foto/video mentah
5. **Create/Generate Studio** — pilih mode (Iklan Produk/Affiliate) → upload foto → pilih gaya/referensi → generate
6. **Editor** — preview hasil AI, trim/reorder, edit caption, ganti musik/voice
7. **Publish/Schedule** — preview per platform (IG/TikTok/YouTube berbeda rasio & caption), pilih jadwal atau publish sekarang
8. **Content Calendar** — tampilan kalender semua post (draft/scheduled/published)
9. **Connected Accounts** — kelola koneksi sosmed, reconnect jika token expired
10. **Analytics** — performa dasar per konten
11. **Billing/Settings** — paket langganan, quota, profil

## 4.2 Flow Utama (Happy Path)
```
1. Login → Dashboard kosong (state baru)
2. CTA "Hubungkan Akun Sosmed" → OAuth IG/TikTok/YouTube
3. CTA "Buat Konten Baru" → pilih mode → upload foto produk
4. Pilih gaya referensi (opsional lihat video contoh) → klik "Generate"
5. Loading state (async) → notifikasi saat selesai
6. Masuk ke Editor → preview video → edit caption/musik jika perlu
7. Klik "Lanjut ke Publish" → preview per platform (crop/caption otomatis disesuaikan)
8. Pilih: Publish Sekarang / Jadwalkan → konfirmasi
9. Redirect ke Content Calendar → lihat status "Scheduled" → nanti berubah "Published"
```

## 4.3 Catatan Desain Penting
- **Preview per-platform wajib terpisah** — rasio IG Reels (9:16), TikTok (9:16), YouTube Shorts (9:16) mirip, tapi caption/hashtag conventions beda; jangan asumsikan satu preview cukup untuk semua.
- **Status job AI generation harus terlihat jelas** (progress indicator/estimasi waktu) — karena prosesnya tidak instan, user gampang bingung/menganggap sistem hang.
- **Error state harus actionable** — misalnya "Token Instagram kadaluarsa" harus punya tombol langsung "Reconnect", bukan cuma pesan error generik.
- **Empty state** di tiap halaman (belum ada media, belum ada post) harus mengarahkan user ke next action, bukan halaman kosong membingungkan.

---

# 5. Task Breakdown

## Phase 0 — Setup & Fondasi
- [ ] Setup repo (frontend Next.js, backend FastAPI), CI/CD dasar
- [ ] Setup database PostgreSQL + migration tool (Alembic)
- [ ] Setup object storage (S3/R2) + Redis
- [ ] Riset & daftar developer app: Meta, TikTok, YouTube (proses approval bisa makan waktu — mulai paling awal)
- [ ] Riset & pilih provider AI video generation + voice + speech-to-text (bandingkan harga/kualitas)

## Phase 1 — Auth & Core Infra
- [ ] Register/login (email + Google OAuth)
- [ ] Model user, subscription/plan, quota tracking dasar
- [ ] Setup job queue (Celery + Redis) skeleton

## Phase 2 — Media & Upload
- [ ] Upload foto/video ke object storage
- [ ] Media Library UI (list, hapus, preview)
- [ ] Validasi file (tipe, ukuran)

## Phase 3 — AI Generation Integration
- [ ] Integrasi provider image-to-video (kirim job, terima hasil)
- [ ] Worker async untuk job generate video
- [ ] Integrasi speech-to-text untuk auto-caption
- [ ] Integrasi voice-over AI (opsional per project)
- [ ] UI Generate Studio (pilih foto, gaya referensi, trigger generate)
- [ ] Notifikasi saat job selesai/gagal

## Phase 4 — Editor Ringan
- [ ] Preview video hasil AI
- [ ] Fitur trim/reorder klip sederhana
- [ ] Edit teks caption & pilih musik
- [ ] Simpan sebagai draft project

## Phase 5 — Publish Manual Assist (bisa langsung dikerjakan, tidak nunggu approval siapa pun)
- [ ] Preview per-platform di UI (crop rasio, limit karakter caption otomatis per IG/TikTok/YouTube)
- [ ] Fitur export/download video final + caption siap-pakai per platform
- [ ] Fitur "share to phone" (link/QR atau kirim ke storage yang gampang diakses dari HP)
- [ ] Content Calendar UI dengan status "Siap diupload manual" / "Sudah saya upload" (ditandai user sendiri)
- [ ] **Paralel, di luar sprint:** ajukan developer app Meta, TikTok, YouTube (submit begitu ada domain + produk jalan — proses ini yang paling lama, mulai secepatnya)

## Phase 6 — Koneksi Akun & Auto-Publish (dikerjakan setelah developer app disetujui)
- [ ] OAuth flow Instagram (Meta Graph API)
- [ ] OAuth flow TikTok
- [ ] OAuth flow YouTube (Google OAuth + scope YouTube)
- [ ] Penyimpanan token terenkripsi + refresh token handling
- [ ] UI kelola akun terhubung + reconnect flow
- [ ] Wrapper publish ke masing-masing platform (upload video + caption)
- [ ] Fitur jadwalkan post (scheduler worker) & publish langsung
- [ ] Retry & error handling per platform (independen)
- [ ] Ganti tombol "Download/Manual" jadi "Publish Otomatis" per platform begitu API tersambung (tanpa ubah alur utama user)

## Phase 7 — Quota, Billing & Analytics
- [ ] Sistem quota AI generation per plan
- [ ] Halaman billing/paket langganan
- [ ] Analytics dasar per post (tarik data dari API platform jika tersedia)

## Phase 8 — Testing, Hardening & Launch
- [ ] Testing end-to-end: upload → generate → edit → publish ke 3 platform
- [ ] Load testing job queue
- [ ] Security review (enkripsi token, validasi input)
- [ ] Submit app untuk review resmi Meta/TikTok/YouTube (jika belum full-access)
- [ ] Soft launch (internal/beta user) → iterasi

---

## Rekomendasi Urutan Kerja Praktis
Ajukan akses developer API ketiga platform (Meta/TikTok/YouTube) **sedini mungkin di Phase 0**, tapi jangan tunggu approval itu turun untuk mulai kerja — Phase 1–5 (auth, media, AI generation, editor, Publish Manual Assist) semuanya bisa selesai dan **produk sudah bisa dipakai penuh secara manual** sebelum Phase 6 (auto-publish) tersambung. Ini memastikan progres tidak macet menunggu pihak ketiga.
