# PROGRESS.md — adVance.AI

Living doc, satu section per phase (lihat Task Breakdown di
`adVance-AI-Spesifikasi-Proyek.md` §5). **Mulai sesi baru dari sini** — jangan re-scan
histori chat. Tiap section: apa yang dibangun, keputusan teknis, cara jalanin/verifikasi,
item follow-up manual untuk user.

---

## Phase 0 — Setup & Fondasi — Status: selesai

### Dibangun
- **Repo & git**: `git init`, remote `origin` → https://github.com/Fadhh12/AdVance.ai.git,
  branch `main` tracking `origin/main`. Identity commit: `Nabil <nabilbiel12@gmail.com>`
  (sama dengan commit awal repo, supaya kontribusi kehitung).
- **Infra lokal** (`docker-compose.yml`): Postgres 16, Redis 7, MinIO (S3-compatible,
  bucket `media-assets` **privat** — bukan public bucket, sesuai SDD §3.6). Belum bisa
  `docker compose up` karena **Docker Desktop belum terpasang** di mesin ini.
- **Backend** (`backend/`): FastAPI, struktur folder persis SDD §3.5
  (`app/api|core|models|schemas|services/{ai_providers,social_publishers}|workers`,
  `alembic/`, `tests/`). Config via `pydantic-settings` (`app/core/config.py`), DB
  session setup (`app/models/base.py`), endpoint `/health`. Interface
  `VideoGenerationProvider` dan `SocialPublisher` didefinisikan (`services/*/base.py`)
  tapi **belum ada implementasi konkret** — provider AI belum final dipilih, publisher
  platform diblokir sampai developer app approved (lihat CLAUDE.md).
  Venv Python 3.11.9 di `backend/.venv` (lihat catatan PIP_TARGET di bawah).
- **Frontend** (`frontend/`): Next.js 16 (App Router) + TypeScript + Tailwind v4, di-
  scaffold via `create-next-app`. Token warna/font dari `DESIGN_SYSTEM.md` §3-4 ditaruh
  di `src/app/globals.css` (`@theme`): `bg-canvas/panel/panel-raised`,
  `text-rec/signal/alert` (tally light), `font-display` (Space Grotesk) + `font-sans`
  (Inter) — **bukan** palet/font default Tailwind. Halaman/komponen produk (login,
  dashboard, dst) belum dibuat — itu mulai Phase 1.
- **CI** (`.github/workflows/ci.yml`): job lint+test backend (ruff, pytest) dan
  lint+build frontend (eslint, `next build`), jalan otomatis di push/PR ke `main`.
- **Riset** (`docs/research/`):
  - `developer-app-registration.md` — checklist syarat & langkah daftar developer app
    Meta/TikTok/YouTube + item aksi manual untuk user (business verification, domain,
    privacy policy page, dst).
  - `ai-providers-comparison.md` — perbandingan Runway/Kling/Pika/Luma/Veo (image-to-
    video), ElevenLabs vs Google/Azure (TTS), Whisper (STT). Rekomendasi awal ditulis,
    **belum keputusan final** — perlu konfirmasi user sebelum di-hardcode.

### Keputusan teknis (dikonfirmasi user)
- Cakupan sesi: Phase 0→5 berturut-turut, commit kecil per checkpoint + push tiap commit
  (bukan satu commit besar di akhir).
- Infra lokal: Docker Desktop (compose-ready, user install sendiri) — bukan cloud dev
  services atau native install.
- Backend Python: 3.11.9 (venv terpisah dari Python 3.14 default di mesin, lebih stabil
  untuk ekosistem FastAPI/SQLAlchemy/Celery).
- `openai-whisper` **sengaja tidak** ditaruh di `requirements.txt` (dependency ML berat,
  butuh torch) — STT masih interface/stub sampai Phase 3 memutuskan hosted API vs
  self-hosted (lihat `ai-providers-comparison.md`).

### Cara jalanin / verifikasi
```bash
# Infra (butuh Docker Desktop terpasang — lihat item follow-up)
docker compose up -d

# Backend — sudah diverifikasi: pytest pass, uvicorn serve /health (200 OK), ruff clean
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
# alembic upgrade head — BELUM dites jalan (butuh Postgres via docker compose up, pending)

# Frontend — sudah diverifikasi: npm run build clean, npm run lint clean
cd frontend
npm run dev   # http://localhost:3000
```

### Item follow-up / aksi manual user
- [ ] **Install Docker Desktop** — supaya `docker compose up -d` bisa jalan (Postgres/
      Redis/MinIO). Tanpa ini, Phase 1+ backend tidak bisa connect DB.
- [ ] **Install ffmpeg** di mesin dev (dibutuhkan Phase 4/5 untuk trim/crop video).
      Belum terpasang saat Phase 0 dicek.
- [ ] **Bersihkan environment variable `PIP_TARGET`** (User-level Windows env var,
      isinya `D:\TrashDetection\venv\Lib\site-packages`) — ini leftover dari proyek lain
      dan diam-diam membajak `pip install` di semua venv Python di mesin ini, termasuk
      punya adVance.AI. Workaround yang dipakai sekarang: `$env:PIP_TARGET = $null` per
      sesi PowerShell sebelum `pip install`. Sebaiknya dihapus permanen lewat System
      Properties → Environment Variables (bisa saya bantu kalau diminta).
- [ ] Mulai proses developer app Meta/TikTok/YouTube (lihat checklist di
      `docs/research/developer-app-registration.md`) — paling lama, mulai sedini
      mungkin, paralel dengan Phase 1-5.
- [ ] Konfirmasi provider AI final (image-to-video, TTS) — lihat
      `docs/research/ai-providers-comparison.md`, isi keputusan sebelum Phase 3 lanjut
      ke implementasi konkret (sekarang masih mock).

### Untuk sesi berikutnya (sudah dilanjut — lihat Phase 1 di bawah)

---

## Phase 1 — Auth & Core Infra — Status: selesai

### Dibangun
- **Backend auth** (FR-01): model `User` + `Plan` (`app/models/`), migrasi Alembic
  pertama (`856f311546c8_create_plans_and_users_tables.py`, seed 1 plan default
  "Free" — 5 quota AI generation, 1 akun sosmed). `app/core/security.py` (hash
  password bcrypt, JWT issue/verify), `app/api/auth.py`:
  `POST /auth/register`, `POST /auth/login`, `POST /auth/oauth/google`,
  `GET /auth/me`. Google id_token diverifikasi lewat endpoint `tokeninfo` Google
  (`app/services/google_oauth.py`) — cukup untuk skala MVP, upgrade ke verifikasi
  JWKS lokal kalau traffic login naik.
- **Celery skeleton**: `app/workers/celery_app.py` (instance Celery ke Redis dari
  settings) + `app/workers/tasks.py` (task `ping` no-op untuk tes wiring nanti).
- **Frontend auth**: NextAuth v4 (`next-auth@4.24.15` — dipilih stabil, v5 masih
  beta di registry). `src/lib/auth-options.ts`: Credentials provider manggil
  backend `/auth/login`, Google provider forward `id_token` ke backend
  `/auth/oauth/google` — backend tetap source of truth akun, NextAuth cuma layer
  session/cookie. JWT backend disimpan di `session.accessToken` (lihat
  `src/types/next-auth.d.ts` untuk type augmentation-nya).
- **Halaman**: `/login`, `/register` (form panel gelap, CTA warna `--accent-rec`,
  bukan kartu rounded generik). Route group `(workspace)` — `layout.tsx` cek
  session server-side (redirect ke `/login` kalau belum login), `Sidebar` dengan
  section yang belum dibangun ditandai "Segera" (bukan link mati tanpa
  penjelasan), `/dashboard` placeholder empty-state jujur (belum ada Media
  Library/Generate Studio — itu Phase 2-3).

### Keputusan teknis
- **next-auth v4** (bukan v5/Auth.js beta) — v5 masih beta di npm registry saat
  dicek, v4.24.15 stabil dan sudah declare peer support `next ^16`.
  - **Verifikasi Google id_token via endpoint `tokeninfo`** (bukan library JWKS
  terpisah) — cukup untuk volume MVP, hemat dependency; didokumentasikan di kode
  supaya upgrade path jelas kalau perlu.
- **bcrypt dipin ke `4.0.1`** — passlib 1.7.4 (masih versi paling stabil untuk
  hashing) salah deteksi backend di bcrypt ≥4.1 (`AttributeError` saat
  `detect_wrap_bug`), issue dikenal di ekosistem passlib/bcrypt.
- Test backend jalan pakai **SQLite in-memory** (dependency override `get_db`) —
  bukan berarti migrasi Postgres sudah tervalidasi, cuma logika endpoint yang
  tervalidasi. Ini tetap **pending**: `alembic upgrade head` ke Postgres asli
  belum pernah dijalankan (blocker sama seperti Phase 0: Docker belum
  terpasang).

### Cara jalanin / verifikasi
```bash
# Backend — 6/6 test pass (SQLite), ruff clean
cd backend && .venv\Scripts\activate
pytest -q
ruff check .
# BELUM dites: alembic upgrade head (butuh Postgres via docker compose up -d)

# Frontend — build + lint clean
cd frontend
npm run build
npm run lint
```
Untuk coba alur login manual end-to-end: butuh Postgres jalan (Docker) +
`backend/.env` terisi + `frontend/.env.local` terisi (`NEXTAUTH_SECRET` bebas
random, `GOOGLE_OAUTH_CLIENT_ID/SECRET` boleh kosong — tombol Google saja yang
belum berfungsi).

### Item follow-up / aksi manual user
- Sama seperti Phase 0 (Docker Desktop, ffmpeg, bersihkan `PIP_TARGET`) — **masih
  belum dilakukan**, jadi migrasi Postgres & test login manual end-to-end masih
  pending sampai itu selesai.
- [ ] Isi `GOOGLE_OAUTH_CLIENT_ID`/`SECRET` (backend `.env` **dan** frontend
      `.env.local`) begitu Google Cloud OAuth consent screen dibuat (lihat
      `docs/research/developer-app-registration.md` §3) — tanpa ini tombol
      "Masuk dengan Google" tidak akan berfungsi.

### Untuk sesi berikutnya (sudah dilanjut — lihat Phase 2 di bawah)

---

## Phase 2 — Media & Upload — Status: selesai

### Dibangun
- **Backend**: model `MediaAsset` (`app/models/media_asset.py`) — `file_url` menyimpan
  **S3 object key**, bukan URL publik (bucket privat, SDD §3.6); URL bertanda tangan
  (signed) selalu dibuat baru saat dibaca, tidak pernah disimpan. Migrasi
  `1e41fea2ddea_create_media_assets_table.py`. `app/services/storage.py`: wrapper
  boto3 generik S3-compatible (ganti MinIO→R2/S3 cuma ubah `.env`).
  `POST /media/upload`, `GET /media`, `DELETE /media/{id}` (`app/api/media.py`) —
  validasi tipe & ukuran **server-side** (SRS §2.2: foto ≤20MB jpg/png/webp, video
  mentah ≤500MB mp4/mov), stream ke `SpooledTemporaryFile` (spool ke disk setelah
  10MB) supaya upload video besar tidak membebani RAM.
- **Frontend**: halaman `/media` (Media Library) — list bergaya **bin/media pool**
  (thumbnail kecil kiri + kolom tipe/ukuran/tanggal terpisah, **bukan** grid kartu
  atau caption "A · B · C" — DESIGN_SYSTEM §5.3 & Anti-Slop Checklist), dropzone
  drag-and-drop + klik untuk upload, empty state actionable. Sidebar diupdate:
  "Media Library" sudah aktif (bukan "Segera" lagi).

### Keputusan teknis
- Test backend media pakai **moto** (mock S3/AWS) — bukan MinIO asli. Catatan
  penting: moto **hanya** intercept request ke endpoint AWS asli, jadi test
  sementara meng-override `settings.s3_endpoint_url` ke `None` di dalam fixture
  (lihat `tests/test_media.py::s3_bucket`) supaya boto3 diarahkan ke endpoint yang
  di-mock moto, bukan ke `localhost:9000` (MinIO) yang belum jalan.
- Thumbnail video belum ada generate preview asli (masih placeholder teks "Video")
  — generate thumbnail dari frame video itu tugas ffmpeg, masuk akal digabung nanti
  saat ffmpeg dipakai di Phase 4/5, bukan di-generate sekarang supaya tidak
  menambah dependency ffmpeg lebih awal dari yang direncanakan.

### Cara jalanin / verifikasi
```bash
cd backend && .venv\Scripts\activate
pytest -q        # 12/12 pass (moto S3 mock)
ruff check .      # clean

cd frontend
npm run build     # clean
npm run lint      # clean
```
Upload/list/delete manual end-to-end via browser **belum dites** — butuh MinIO asli
jalan (`docker compose up -d`, masih pending Docker Desktop) + backend+frontend jalan
bersamaan dengan `.env`/`.env.local` terisi.

### Item follow-up / aksi manual user
Sama seperti Phase 0/1 — Docker Desktop, ffmpeg, `PIP_TARGET` — belum ada yang
berubah statusnya, jadi ini masih daftar yang sama (lihat Phase 0 di atas).

### Untuk sesi berikutnya (sudah dilanjut — lihat Phase 3 di bawah)

---

## Phase 3 — AI Generation Integration — Status: selesai

### Dibangun
- **Backend**: `MockVideoProvider` (`app/services/ai_providers/mock.py`) — provider
  default selama provider asli belum dipilih (CLAUDE.md); **tidak** menghasilkan video
  sungguhan, cuma echo `source_image_url` balik sebagai `result_url` supaya seluruh
  pipeline job (queued→processing→success/failed) bisa dites end-to-end tanpa API key.
  Ada test hook: `prompt` mengandung `"trigger-failure"` → provider sengaja gagal, buat
  nguji jalur error. `factory.py` (`get_video_provider()`) baca `AI_VIDEO_PROVIDER` dari
  `.env`, provider baru tinggal ditambah di sini. `TransientProviderError` dipisah dari
  kegagalan permanen (SRS §2.3: hanya error transient yang di-retry).
  Model `AIJob` + migration `61abd86fc8b2`. `generate_video_task` (Celery, retry max 3x
  dengan backoff, cuma untuk `TransientProviderError`) — buka session DB sendiri lewat
  `models_base.SessionLocal()` (bukan import langsung) supaya bisa di-patch saat test.
  `POST /ai/generate-video` (cek + potong kuota SEBELUM enqueue — SRS §2.2, 402 kalau
  habis), `GET /ai/jobs/{id}`. Interface `SpeechToTextProvider` dan `VoiceoverProvider`
  ditambah (`app/services/ai_providers/stt.py`, `voiceover.py`) — **stub kontrak saja**,
  belum disambung ke endpoint manapun (provider belum final, dan pemakaiannya baru
  masuk akal begitu UI caption/musik Phase 4 ada).
- **Frontend**: `TallyDot` (`components/ui/tally-dot.tsx`) dan `TimelinePipeline`
  (`components/workspace/timeline-pipeline.tsx`) — elemen visual pertama yang benar-benar
  mengikuti motif "timeline pipeline"/"tally light" di DESIGN_SYSTEM §5.1-5.2 (bukan
  badge rounded/step 01-02-03). Halaman `/generate` (Generate Studio): pilih foto dari
  Media Library, isi gaya referensi opsional, trigger generate, polling status job,
  notifikasi in-app inline saat sukses/gagal (bukan toast global — belum ada sistem
  notifikasi terpusat di app ini). Sidebar & dashboard diupdate, "Generate Studio" aktif.

### Keputusan teknis
- **Celery `task_always_eager=True` di test session** (`tests/conftest.py`) — karena
  Redis belum ada (Docker pending), `.delay()` di test dijalankan sinkron di proses yang
  sama alih-alih butuh broker asli. Konsekuensinya: task butuh DB session yang sama
  dengan request test, jadi `models_base.SessionLocal` di-patch sementara ke session
  factory test juga. Endpoint `POST /ai/generate-video` melakukan `db.refresh(job)`
  setelah `.delay()` supaya response selalu merefleksikan state DB terbaru — no-op di
  production (worker asli belum sempat proses), tapi perlu di mode eager test.
  **Belum diverifikasi** dengan Celery worker + Redis sungguhan.
  - Timeline pipeline **belum** jadi header persisten workspace-wide — ditaruh khusus di
  halaman Generate Studio, terikat ke job aktif. Alasan: Upload/Edit/Publish di luar
  konteks generate belum punya state nyata untuk direfleksikan sampai `content_projects`
  (Phase 4) ada — motif ini "naik level" jadi header per-project begitu itu dibangun.
- Mode konten ("Iklan Produk"/"Affiliate" dari PRD flow) **sengaja tidak** ada di
  Generate Studio — field itu milik `content_projects` (Phase 4), dan checklist Task
  Breakdown Phase 3 sendiri tidak menyebutkannya, jadi tidak ditambahkan sekarang untuk
  hindari field yang belum ada tempat penyimpanannya di backend.

### Cara jalanin / verifikasi
```bash
cd backend && .venv\Scripts\activate
pytest -q        # 17/17 pass (Celery eager mode, moto S3 mock)
ruff check .      # clean

cd frontend
npm run build     # clean
npm run lint      # clean
```
Alur generate manual end-to-end via browser **belum dites** — sama seperti Phase 0-2,
butuh Postgres+Redis (`docker compose up -d`, masih pending Docker Desktop). Tanpa Redis,
job dari UI akan tersangkut di status "queued" selamanya (perilaku yang diharapkan
selama tidak ada worker asli yang jalan, bukan bug).

### Item follow-up / aksi manual user
Sama seperti Phase 0-2 — Docker Desktop, ffmpeg, `PIP_TARGET` — masih daftar yang sama.

### Untuk sesi berikutnya (sudah dilanjut — lihat Phase 4 di bawah)

---

## Phase 4 — Editor Ringan — Status: selesai

### Dibangun
- **Backend**: model `ContentProject` + migration `470511c8fd3d`
  (`app/models/content_project.py`). `status` tetap terbatas ke nilai SDD
  (`draft/ready/scheduled/published`); state render ffmpeg ditaruh di kolom terpisah
  `render_status`/`render_error_message` (bukan numpuk ke `status`). `source_job_id`
  nunjuk ke **satu** baris `ai_jobs` — belum ada "reorder klip" karena memang belum ada
  data multi-klip untuk di-reorder (lihat keputusan teknis).
  `app/services/video_render.py`: wrapper `ffmpeg` (subprocess), lempar
  `FFmpegNotAvailableError` yang actionable kalau binary tidak ada di PATH — **memang
  belum terpasang** di mesin ini sekarang.
  `render_project_task` (Celery): download video sumber, trim, upload hasil ke storage.
  Endpoint: `POST /projects` (dari job generate yang sukses), `GET /projects`,
  `GET /projects/{id}`, `PATCH /projects/{id}` (caption/music_track/trim),
  `POST /projects/{id}/render`.
- **Frontend**: Generate Studio — setelah job sukses, muncul form kecil (judul + mode)
  buat langsung lanjut ke editor. `/editor` (index, list proyek + tally-dot status
  render). `/editor/[projectId]`: trim (start/end detik), caption, pilih musik (daftar
  stub, belum ada katalog audio asli), simpan draft (PATCH), render (POST render +
  polling). Preview pakai elemen `<video>` asli dengan fallback `onError` yang jujur
  ("provider AI masih mock, hasil belum berupa video sungguhan") — bukan player rusak
  yang dibiarkan begitu saja.

### Keputusan teknis
- **Tidak ada fitur "reorder klip"** meski disebut di Task Breakdown ("trim/reorder klip
  sederhana") — sengaja diskip karena `content_projects` cuma nunjuk ke SATU AI job
  (satu video), jadi tidak ada beberapa klip nyata untuk di-reorder. Membuat UI reorder
  tanpa data multi-klip di baliknya berarti fitur palsu. Ini beda dari keputusan-
  keputusan sebelumnya karena bukan cuma "belum diverifikasi", tapi **sengaja tidak
  dibangun** — kalau nanti generation menghasilkan beberapa klip per project, ini masuk
  akal ditambahkan.
- Field `mode` (product_ad/affiliate) akhirnya punya rumah di sini (bukan di
  `ai_jobs`/Generate Studio sesuai keputusan Phase 3) — diminta saat user klik "Lanjut
  ke Editor" dari Generate Studio, pas logikanya karena baru di titik itu user
  berkomitmen ke framing iklan-produk vs affiliate.
- Musik masih murni metadata (nama track tersimpan di `music_track`) — **belum**
  di-mixing beneran ke video via ffmpeg, karena belum ada katalog audio asli untuk
  dipakai. Caption juga belum di-burn-in ke video — itu lebih masuk akal jadi bagian
  Phase 5 (export per-platform), bukan di sini.

### Cara jalanin / verifikasi
```bash
cd backend && .venv\Scripts\activate
pytest -q        # 24/24 pass — termasuk 1 test render yang genuinely gagal karena
                  # ffmpeg belum terpasang (dipaksa lewat monkeypatch biar deterministik
                  # di semua environment, bukan cuma kebetulan mesin ini)
ruff check .      # clean

cd frontend
npm run build     # clean
npm run lint      # clean
```
Render manual end-to-end via browser **belum bisa** — butuh ffmpeg **dan** Postgres+Redis
(Docker) terpasang. Tanpa ffmpeg, tombol "Render video" akan selalu balik
`render_status: failed` dengan pesan actionable — ini perilaku yang benar, bukan bug.

### Item follow-up / aksi manual user
Sama seperti Phase 0-3 — Docker Desktop, ffmpeg, `PIP_TARGET` — masih daftar yang sama.
Render video baru bisa dicoba beneran setelah ffmpeg terpasang.

### Untuk sesi berikutnya (sudah dilanjut — lihat Phase 5 di bawah)

---

## Phase 5 — Publish Manual Assist — Status: selesai

### Dibangun
- **Backend**: model `Post` + migration `d87a7503cb38`. Sengaja **tidak** menyertakan
  `social_account_id`/`scheduled_at`/`published_at`/`platform_post_id` dari skema SDD
  penuh — kolom itu baru berarti setelah `social_accounts` (Phase 6) benar-benar ada;
  nambah kolom nganggur sekarang cuma bikin migrasi berat sebelah waktunya.
  `app/services/video_render.export_for_platform`: crop ke 9:16 (scale+crop center) +
  cap durasi per platform (SRS §2.2: IG≤90s, TikTok≤10m, YT≤60s) — auto-adjust, bukan
  cuma nolak. `app/services/caption_adapter.py`: truncate murni (IG/TikTok 2200,
  deskripsi YouTube 5000, judul YouTube 100), fungsi pure jadi gampang dites tanpa
  ffmpeg. `export_post_task` (Celery) jalanin keduanya + upload hasil ke storage.
  Endpoint: `POST /projects/{id}/posts` (bikin 3 post sekaligus, 1 per platform, wajib
  project sudah di-render dulu), `GET /projects/{id}/posts`, `GET /posts` (flat, lintas
  project — buat Content Calendar), `POST /posts/{id}/mark-uploaded` (FR-13/FR-14 self-
  mark), `GET /posts/{id}/qr` (PNG QR code dari signed download URL — "share to phone").
- **Frontend**: `PhoneFrame` (border tipis 9:16, bukan mockup HP 3D — DESIGN_SYSTEM
  §5.4). `/publish` (index, list project yang sudah di-render) dan
  `/publish/[projectId]` — 3 frame IG/TikTok/YouTube berjajar, tiap frame ada
  preview video, caption (+judul untuk YouTube), tombol Download, tombol "Bagikan ke
  HP" (fetch QR pakai header auth di client, bukan `<img src>` polos karena endpoint-nya
  butuh Bearer token), dan tombol self-mark "Tandai sudah saya upload". `/calendar`:
  list flat semua post lintas project, status ditulis eksplisit "Siap diupload manual"
  / "Sudah saya upload" (sesuai istilah di Task Breakdown Phase 5), gaya list kolom
  (bukan caption "A · B · C" — tetap konsisten sama Media Library).

### Keputusan teknis
- Publish **diblokir** sampai `content_projects.render_status == "success"` — tidak ada
  jalan pintas export dari video yang belum di-render, supaya "final video" yang
  di-crop untuk platform memang benar-benar final (sesuai urutan Timeline Pipeline:
  Upload→Generate→Edit→Publish, bukan Upload→Generate→Publish).
- Caption per platform **bukan** kolom terpisah di `content_projects` — `Post.caption`
  dihitung ulang tiap kali export jalan, dari `project.caption` yang sama, cuma di-
  adapt beda-beda panjangnya per platform. Satu sumber teks, bukan 3 field caption yang
  bisa saling tidak sinkron.
- QR code digenerate di **backend** (paket `qrcode`, sudah disiapkan sejak Phase 0)
  bukan library JS di frontend — alasannya endpoint yang sama juga jadi satu-satunya
  tempat yang tahu signed download URL-nya, tidak perlu expose logic presign ke client.

### Cara jalanin / verifikasi
```bash
cd backend && .venv\Scripts\activate
pytest -q        # 36/36 pass — termasuk export yang genuinely gagal tanpa ffmpeg
                  # (dipaksa deterministik lewat monkeypatch, sama pola kayak Phase 4)
ruff check .      # clean

cd frontend
npm run build     # clean
npm run lint      # clean
```
Publish manual end-to-end via browser **belum bisa dites** — sama seperti render Phase
4, butuh ffmpeg + Postgres/Redis (Docker) terpasang dulu.

### Item follow-up / aksi manual user
Sama seperti Phase 0-4 — Docker Desktop, ffmpeg, `PIP_TARGET` — masih daftar yang sama,
belum ada yang user selesaikan. Proses developer app Meta/TikTok/YouTube (checklist di
`docs/research/developer-app-registration.md`) juga belum dimulai setahu saya — ini yang
paling lama, sebaiknya mulai sekarang secara paralel.

### Untuk sesi berikutnya
**Phase 0-5 (semua yang bisa dikerjakan tanpa approval API pihak ketiga) sudah selesai
semua.** Produk sekarang punya alur lengkap: daftar/login → upload foto → generate
video (AI) → edit ringan (trim/caption/musik) + render → siapkan publish per platform
(crop+durasi+caption otomatis) → download/QR share manual → tandai sudah upload →
terlihat di Content Calendar. Semuanya sudah diverifikasi lewat test otomatis
(backend: alur end-to-end via SQLite+Celery eager+moto S3; frontend: build+lint), tapi
**belum ada satupun yang dites manual lewat browser sungguhan** — itu butuh Docker
Desktop (Postgres+Redis+MinIO) dan ffmpeg terpasang dulu (lihat daftar follow-up di
tiap phase di atas).

Sesi berikutnya, urutan yang masuk akal:
1. **User menyelesaikan item manual**: install Docker Desktop, `docker compose up -d`,
   install ffmpeg, bersihkan env var `PIP_TARGET` yang salah arah, isi `backend/.env` +
   `frontend/.env.local` dari `.env.example`.
2. Begitu itu selesai, jalankan `alembic upgrade head` (baru pertama kali kepakai —
   6 migration menumpuk dari Phase 1-5, belum pernah dijalankan ke DB asli) dan tes
   alur lengkap manual lewat browser — ini akan jadi verifikasi nyata pertama untuk
   semua kode yang sejauh ini cuma tervalidasi lewat mock/test.
3. **Phase 6 — Koneksi Akun & Auto-Publish** baru bisa mulai dikerjakan setelah
   developer app Meta/TikTok/YouTube disetujui (bisa berminggu-minggu) — kalau belum
   disetujui saat sesi berikutnya mulai, jangan mulai Phase 6, cek dulu ke user.
4. Phase 7 (Quota/Billing/Analytics penuh) dan Phase 8 (testing/hardening/launch) masih
   menyusul setelah itu sesuai Task Breakdown.
