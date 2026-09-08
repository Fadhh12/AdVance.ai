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

---

## Catatan sesi — Verifikasi manual end-to-end pertama (2026-09-07)

Semua item follow-up infra dari Phase 0-5 **selesai** dan alur produk penuh sudah
dites manual beneran (bukan cuma mock/test otomatis) untuk pertama kali:

- **Docker Desktop terpasang** — sempat kejegal error "WSL needs updating" pas
  pertama start (WSL2 di mesin ini kekunoan buat engine Docker terbaru). Fix:
  `wsl --update` lalu `wsl --shutdown` supaya versi baru kepakai, baru Docker
  Engine bisa nyala. `docker compose up -d` jalan bersih — Postgres, Redis, MinIO
  semua `healthy`.
- **ffmpeg terpasang** (`ffmpeg-9.0.1-full_build`, via winget) — sudah terdeteksi
  di PATH, tidak ada aksi lagi yang perlu dilakukan.
- **`PIP_TARGET` sudah bersih** (User-level env var kosong) — tidak membajak `pip
  install` lagi.
- **`alembic upgrade head` jalan pertama kali ke Postgres asli** — 5 migrasi
  (Phase 1-5) apply bersih, 7 tabel + seed plan "Free" terverifikasi lewat `psql`.
- **Full pipeline dites manual lewat API (bukan browser, tapi request nyata ke
  server nyala)**: register → login → upload foto (MinIO asli) → generate video
  (job `queued`→`success` diproses **Celery worker asli** via **Redis asli**,
  bukan eager mode) → buat `content_project` → render (**ffmpeg asli** dipanggil,
  crop+encode video test jadi `final_video_url` beneran) → `POST .../posts` (3
  post IG/TikTok/YouTube) → export per-platform (crop 9:16 + caption per-platform,
  semua `success`) → generate QR code (PNG valid) → mark-uploaded → `GET /posts`
  flat (Content Calendar) nunjukin status yang benar. Data tes sudah dibersihkan
  dari Postgres dan MinIO setelahnya.
- **`SKIP_AUTH` dicopot dari `frontend/.env.local`** — login gate `(workspace)`
  sudah diverifikasi redirect ke `/login` beneran (bukan lagi bypass) begitu
  Postgres asli jalan.

### Bug kecil ditemukan saat verifikasi (bukan blocker, dicatat aja)
- Tidak ada `ON DELETE CASCADE` di foreign key `media_assets`/`ai_jobs`/
  `content_projects`/`posts` → `users`. Hapus user manual lewat SQL harus urut
  (posts → content_projects → ai_jobs → media_assets → users) atau kena FK
  violation. Belum masalah nyata di alur produk (tidak ada fitur "hapus akun"
  sampai sekarang), tapi kalau fitur itu ditambah nanti, perlu cascade delete atau
  soft-delete eksplisit.

### Cara jalanin sekarang (semua infra nyala)
```bash
docker compose up -d          # Postgres, Redis, MinIO

cd backend && .venv\Scripts\activate
alembic upgrade head          # cuma perlu sekali / tiap ada migrasi baru
uvicorn app.main:app --reload
celery -A app.workers.celery_app worker --loglevel=info --pool=solo   # Windows butuh --pool=solo

cd frontend
npm run dev   # http://localhost:3000 — login/register sekarang beneran butuh akun asli
```

### Untuk sesi berikutnya
Blocker infra lokal **sudah tidak ada lagi**. Yang masih outstanding:
1. Proses developer app Meta/TikTok/YouTube — belum dimulai, paling lama, mulai
   paralel dengan phase-phase berikutnya.
2. Konfirmasi provider AI final (image-to-video, TTS) sebelum implementasi
   konkret ganti `MockVideoProvider`.
3. **Phase 6** (Koneksi Akun & Auto-Publish) masih menunggu approval developer
   app — jangan mulai sampai user bilang approval sudah turun.
4. Uji coba manual lewat **browser sungguhan** (bukan cuma API via curl/Python
   seperti verifikasi sesi ini) masih worth dilakukan user sendiri untuk cek UI
   nyata — backend & data path sudah terbukti jalan.

---

## Catatan sesi (belum jadi phase sendiri) — Register stuck "Failed to fetch"

User coba register manual, backend sudah jalan (`uvicorn`) tapi Postgres belum (Docker
Desktop masih belum terpasang — installer-nya ada di root repo, belum dijalankan).
`/auth/register` 500 karena `psycopg2.OperationalError: connection refused`, tapi
browser cuma menampilkan `TypeError: Failed to fetch` tanpa detail apapun. Dua fix:

1. **Bug nyata, bukan cuma gara-gara Docker** (`backend/app/main.py`): FastAPI/Starlette
   punya quirk — handler yang didaftarkan untuk `Exception`/500 via
   `@app.exception_handler` otomatis dikabel ke `ServerErrorMiddleware`, yang posisinya
   **di luar** `CORSMiddleware` di stack. Jadi response 500 dari exception yang gak
   ketangkep gak pernah dapat header CORS → browser nolak baca response-nya →
   `fetch()` di frontend cuma bilang "Failed to fetch", bukan pesan error asli. Fix:
   tangkap exception lewat middleware biasa (`CatchUnhandledErrorsMiddleware`,
   `BaseHTTPMiddleware`) yang didaftarkan **sebelum** `CORSMiddleware` (jadi lebih ke
   dalam di stack, di dalam wrapping CORS) supaya response error tetap lewat CORS.
   Sudah diverifikasi logikanya benar (skrip TestClient terpisah, cek header
   `access-control-allow-origin` muncul di response 500) — **belum diverifikasi di
   proses uvicorn yang lagi jalan**, karena proses itu jalan di luar sandbox agent ini
   dan gak bisa di-restart dari sini. **User perlu restart backend
   (`Ctrl+C` lalu `uvicorn app.main:app --reload` lagi) supaya fix ini kepakai.**
2. **Dev bypass sementara** (sesuai request user): `frontend/.env.local` sekarang punya
   `SKIP_AUTH=true` (didokumentasikan di `.env.example`, default off). Kalau di-set,
   `(workspace)/layout.tsx` skip cek session & redirect ke `/login` — halaman workspace
   bisa diakses tanpa login. **Bukan solusi penuh**: hampir semua fitur produk (Media
   Library, Generate Studio, Editor, Publish) tetap butuh Postgres buat data beneran,
   jadi tanpa Docker jalan, halaman-halaman itu cuma nunjukin empty state (gak crash,
   tapi juga gak ada data). Perlu restart `npm run dev` biar env var baru kebaca.
   **Hapus/comment `SKIP_AUTH` dari `.env.local` begitu Docker + Postgres beneran
   jalan** — jangan biarkan nempel, itu literally mematikan auth check.

---

## Catatan sesi — Bug "video stuck" di editor (fixed) + kickoff Phase 6R

User coba alur penuh lewat browser sungguhan (Docker/Celery/ffmpeg semua sudah jalan,
diverifikasi ulang: `advance-postgres`/`advance-redis`/`advance-minio` healthy,
`uvicorn --reload` dan `celery worker --pool=solo` sama-sama jalan). Laporan: preview di
editor tidak muncul, video terasa "stuck".

**Root cause** (bukan masalah infra): `MockVideoProvider` (`backend/app/services/ai_providers/mock.py`)
selama ini cuma echo URL foto sumber sebagai `result_url`. Begitu ffmpeg beneran ada,
`trim_video`/`export_for_platform` memproses foto itu sebagai video 1-frame nyaris tanpa
durasi — itu yang di browser terlihat sebagai video beku.

**Fix**: `synthesize_placeholder_video()` baru di `backend/app/services/video_render.py`
me-render foto jadi klip MP4 pendek (4 detik, efek zoom pelan, framing 9:16) via ffmpeg;
`MockVideoProvider` upload hasilnya ke storage dan itu yang jadi `result_url`. Fallback ke
perilaku lama (echo URL foto) kalau ffmpeg tidak ada atau gambar tidak valid (CI, test
fixture pakai bytes fake) — 36/36 test lama tetap hijau tanpa diubah. Diverifikasi manual
(bukan cuma unit test): output MP4 nyata, `ffprobe` konfirmasi durasi 4.0 detik.
**Aksi yang perlu user lakukan**: restart Celery worker (`Ctrl+C` lalu jalankan ulang) —
proses itu tidak auto-reload seperti `uvicorn`, jadi masih pakai kode lama sampai di-restart.

**Setelah itu**, user minta arah desain besar terinspirasi dari Dreamina (CapCut AI
tool): workspace satu-tab (bukan 4 halaman terpisah), AI chat agent yang benar-benar
mengeksekusi aksi (bukan cuma saran), dan galeri template. Ini scope besar di luar
Task Breakdown `adVance-AI-Spesifikasi-Proyek.md` saat ini, jadi dikonfirmasi dulu ke
user sebelum dikerjakan (lihat rules CLAUDE.md soal tidak boleh diam-diam menambah
scope). User konfirmasi: kerjakan ketiganya, LLM provider untuk agent = **Claude
(Anthropic API)** (tetap diabstraksi lewat interface seperti `AI_VIDEO_PROVIDER` —
lihat rencana lengkap di plan file sesi ini), halaman lama (`/generate`,
`/editor/[id]`, `/publish/[id]`) dihapus langsung begitu `/studio` menggantikannya
(bukan dipertahankan sebagai rollback path — histori git cukup).

Ini jadi **Phase 6R**, 7 sub-fase (6R-1..6R-7), berjalan independen dari Phase 6
"Koneksi Akun & Auto-Publish" yang masih diblokir approval developer app (area kode
beda, tidak konflik — tool "publish" di agent tetap cuma manggil Publish Manual Assist
yang sudah ada, tidak pernah posting asli).

## Phase 6R-1 — Backend: service extraction + LLM provider interface — Status: selesai

### Dibangun
- **Refactor murni, tanpa ubah behavior/response contract**: logic yang tadinya inline
  di route handler dipindah ke service functions supaya AI chat agent (6R-3) bisa
  manggil fungsi yang sama persis, bukan duplikasi logic:
  - `app/services/generation_service.py`: `create_generate_video_job()` — dari
    `app/api/ai.py`'s `generate_video` handler (cek media, cek kuota, bikin `AIJob`,
    enqueue). Raise `MediaNotFoundError`/`QuotaExceededError` (bukan `HTTPException`
    langsung) — `app/api/ai.py` yang translate ke status code.
  - `app/services/project_service.py`: `get_owned_project()`, `create_project_from_job()`,
    `enqueue_render()` — dari `app/api/projects.py`. `get_owned_project()` sekarang jadi
    satu-satunya tempat lookup project ter-scope-kepemilikan, dipakai ulang di semua
    route `projects.py` (sebelumnya ada `_get_owned_project` privat yang diduplikasi).
  - `app/services/publish_service.py`: `enqueue_publish_manual()` — dari
    `create_posts` handler. Docstring eksplisit: Manual Assist saja, tidak pernah
    posting asli.
  - `app/services/errors.py`: exception domain baru (`MediaNotFoundError`,
    `QuotaExceededError`, `JobNotFoundError`, `JobNotReadyError`,
    `ProjectNotFoundError`, `RenderNotReadyError`) — router translate ke
    `HTTPException` dengan status/pesan yang **persis sama** seperti sebelum refactor.
- **LLM provider interface** (`app/services/llm_providers/`), mirroring pola
  `app/services/ai_providers/` persis: `base.py` (`ToolSpec`, `ToolCallRequest`,
  `LLMResponse` dataclass, `LLMProvider` ABC dengan method `complete()`), `factory.py`
  (`get_llm_provider()` baca `AI_LLM_PROVIDER` dari settings, `"mock"` →
  `MockLLMProvider`, selain itu `NotImplementedError` — fail loud, sama seperti
  `get_video_provider()`), `mock.py` (`MockLLMProvider` — keyword matching
  deterministik ke nama tool, tanpa network, default provider supaya test/CI tidak
  pernah butuh API key asli).
- `app/core/config.py` + `.env.example`: `AI_LLM_PROVIDER=mock` (default),
  `ANTHROPIC_API_KEY=` (kosong), `ANTHROPIC_MODEL=claude-sonnet-5`.

### Keputusan teknis
- Provider LLM asli untuk agent **sudah dikonfirmasi user: Claude (Anthropic API)** —
  tapi implementasi konkretnya (`anthropic_provider.py`) baru masuk di Phase 6R-3
  bareng tools-nya. `factory.py` di fase ini sengaja **belum** menyebut "anthropic"
  sebagai opsi valid (masih fail loud kalau di-set) — biar konsisten dengan pola
  `ai_video_provider` yang cuma daftar provider yang benar-benar sudah ada kodenya.
- `MockLLMProvider` tetap default (`AI_LLM_PROVIDER=mock`) — sama seperti
  `MockVideoProvider`, ini implementasi lokal asli yang bisa menjalankan seluruh
  pipeline (bukan stub kosong), supaya seluruh Phase 6R bisa dibangun & dites tanpa
  butuh API key Anthropic sampai user benar-benar mau memakainya.

### Cara jalanin / verifikasi
```bash
cd backend && .venv\Scripts\activate
pytest -q        # 53/53 pass (36 lama + 17 baru: generation/project service + LLM provider)
ruff check .      # clean
```
Tidak ada perubahan frontend di fase ini. Tidak ada perubahan response API — endpoint
`/ai/generate-video`, `/projects/*` tetap sama persis dari sisi klien.

### Item follow-up / aksi manual user
- Untuk benar-benar pakai Claude nanti (begitu 6R-3 selesai): isi `ANTHROPIC_API_KEY`
  di `backend/.env` dan set `AI_LLM_PROVIDER=anthropic`. Sampai saat itu semuanya
  (termasuk test 6R-3 sendiri) jalan di atas `MockLLMProvider`, tidak butuh key.
- Sama seperti sebelumnya: proses developer app Meta/TikTok/YouTube belum dimulai.

### Untuk sesi berikutnya (sudah dilanjut — lihat Phase 6R-2 di bawah)

## Phase 6R-2 — Backend: template gallery — Status: selesai

### Dibangun
- `app/models/template.py`: model `Template` (global, tidak per-user) —
  `name`, `description`, `mode`, `prompt_preset`, `thumbnail_url` (nullable, belum ada
  pipeline seed gambar), `is_active`. Didaftarkan di `app/models/__init__.py`.
- Migrasi `8b124fa99bc5_create_templates_table.py` (revisi setelah `d87a7503cb38`) —
  dibuat via `alembic revision --autogenerate` lalu dirapikan manual (autogenerate juga
  mendeteksi drift index/constraint `users.email` yang tidak berhubungan dan sudah ada
  dari sebelumnya — sengaja **tidak** disertakan di migrasi ini, di luar scope Phase
  6R). Seed 4 template starter via `op.bulk_insert`: Unboxing Produk, Testimoni
  Pelanggan, Before/After, Demo Produk Close-up.
- `app/schemas/template.py` (`TemplateOut`), `app/api/templates.py`
  (`GET /templates`, filter opsional `?mode=`, selalu `is_active=True`, tetap butuh
  login tapi bukan data per-user), didaftarkan di `app/api/router.py`.
- **Pemetaan ke Generate Studio** (tidak ada field baru): memilih template hanya
  mengisi field `prompt` yang sudah ada (tetap bisa diedit) + pre-select `mode` untuk
  `POST /projects` nanti — tidak ada apapun baru yang dikirim ke
  `POST /ai/generate-video`.

### Keputusan teknis
- Nama/isi 4 template starter di migrasi adalah placeholder yang gampang diedit
  langsung di tabel nanti — tidak dianggap keputusan final, tidak ada UI admin untuk
  ini sekarang (di luar scope Phase 6R).

### Cara jalanin / verifikasi
```bash
cd backend && .venv\Scripts\activate
pytest -q        # 56/56 pass (53 lama + 3 baru: list/filter/auth templates)
ruff check .      # clean
alembic upgrade head   # dijalankan ke Postgres asli — sukses, 4 baris ter-seed
                        # (diverifikasi manual lewat query SQL langsung)
```

### Untuk sesi berikutnya (sudah dilanjut — lihat Phase 6R-3 di bawah)

## Phase 6R-3 — Backend: chat agent (tool-calling + conversation persistence) — Status: selesai

### Dibangun
- `app/models/chat.py`: `ChatConversation` (per user, `project_id` opsional) +
  `ChatMessage` (`role`: user/assistant/tool, `content`, `tool_name`/`tool_args`/
  `tool_result` JSON — diisi cuma di pesan `role="tool"`). Migrasi
  `1038d694248b_create_chat_tables.py`.
- `app/services/agent_tools/`: satu file per tool, masing-masing cuma wrapper tipis di
  atas service dari 6R-1/6R-2 (tidak reimplement logic):
  `select_media_tool` (resolve foto dari `media_asset_id` atau default foto terbaru —
  **tidak** meng-upload apapun, LLM tidak bisa membawa file; upload tetap lewat
  `POST /media/upload` asli, lihat 6R-6), `generate_video_tool` →
  `generation_service`, `create_project_tool` → `project_service` (default: job sukses
  terbaru), `render_project_tool` → `project_service` (default: project terbaru),
  `prepare_publish_tool` → `publish_service` (default: project ter-render sukses
  terbaru; deskripsi tool eksplisit bilang "TIDAK memposting otomatis"),
  `apply_template_tool` (baca `Template`, tidak ada mutasi). Registry di
  `agent_tools/__init__.py` (`TOOLS: dict[str, AgentTool]`).
- `app/services/chat_agent.py`: orkestrator `handle_turn()` — simpan pesan user, panggil
  `get_llm_provider().complete()`, jalankan tool kalau diminta (maks 3x per giliran,
  supaya tidak infinite loop kalau provider "nyasar"), suntik `media_asset_id` dari
  request ke argumen tool manapun yang punya parameter itu (lihat poin lampiran chat di
  atas), loop lagi sampai provider balas teks biasa. Exception domain
  (`app/services/errors.py`) ditangkap jadi pesan `role="tool"` biasa, bukan 500.
- **`AnthropicLLMProvider`** (`app/services/llm_providers/anthropic_provider.py`) —
  implementasi nyata pakai Anthropic Messages API + tool-calling, dependency
  `anthropic==1.4.0` ditambah ke `requirements.txt`. `factory.py` sekarang mendukung
  `AI_LLM_PROVIDER=anthropic` (import lazy, jadi install `anthropic` tidak wajib
  selama masih pakai `mock`) — **tapi default tetap `mock`**, provider asli baru aktif
  kalau user isi `ANTHROPIC_API_KEY` sendiri.
- `app/schemas/chat.py` (`ChatMessageIn`, `ChatMessageOut`, `ChatTurnOut`),
  `app/api/chat.py` (`POST /chat/messages`, `GET /chat/conversations/{id}/messages`),
  didaftarkan di `router.py`.

### Keputusan teknis
- **`MockLLMProvider` diperbaiki supaya tidak infinite-loop/berulang memanggil tool
  yang sama**: karena orkestrator memanggil `complete()` lagi setelah tiap tool
  selesai (supaya provider asli *bisa* chaining beberapa tool dalam 1 giliran), versi
  awal mock yang murni keyword-match akan mencocokkan pesan user yang sama berulang
  kali dan memanggil tool yang sama berkali-kali (bisa menghabiskan kuota AI generation
  ganda per 1 pesan chat!). Fix: mock berhenti begitu melihat pesan terakhir di
  histori adalah hasil tool — langsung balas teks penutup, tidak mencocokkan keyword
  lagi. Diverifikasi lewat test khusus
  (`test_mock_llm_provider_stops_after_one_tool_call_per_turn`).
- **Setiap tool punya default "paling baru"** (foto/job/project terbaru milik user)
  kalau argumen id tidak disebut — supaya `MockLLMProvider` yang tidak bisa membawa
  id antar-tool-call tetap bisa menjalankan alur end-to-end (upload → "generate video"
  → "siapkan publish" di 3 pesan terpisah, tanpa perlu menyebut id manapun secara
  eksplisit). Provider asli (Claude) tetap bisa mengirim id eksplisit lewat argumen
  tool kalau perlu.
- **Simplifikasi di `AnthropicLLMProvider`**: histori percakapan yang dilempar lewat
  interface `LLMProvider.complete()` cuma `{role, content}` generik (bukan struktur
  `tool_use`/`tool_result` asli Anthropic) — pesan `role="tool"` dipetakan jadi pesan
  `"user"` berisi teks deskriptif hasil tool, bukan tool_result block asli yang terikat
  `tool_use_id`. Ini sengaja supaya interface tetap provider-agnostic (provider lain
  nanti tidak perlu tahu bentuk block Anthropic), trade-off-nya Claude melihat hasil
  tool sebagai teks biasa. **Belum pernah dites dengan API key asli** — lihat item
  follow-up.

### Cara jalanin / verifikasi
```bash
cd backend && .venv\Scripts\activate
pytest -q        # 62/62 pass (56 lama + 6 baru: chat agent end-to-end via MockLLMProvider)
ruff check .      # clean
alembic upgrade head   # dijalankan ke Postgres asli — sukses
```
Smoke test manual lewat `uvicorn`/`celery` yang sedang jalan **belum bisa** dilakukan
dari sesi ini — kedua proses itu jalan di luar sandbox agent (sama seperti catatan
"Register stuck" sebelumnya) dan `uvicorn --reload` sepertinya gagal reload otomatis di
tengah rentetan perubahan file Phase 6R-3 (endpoint baru `/templates` dan `/chat/...`
masih 404 saat dicoba dari sesi ini, padahal `/health` tetap 200 — tanda proses lama
masih yang jalan, bukan kode baru).

### Item follow-up / aksi manual user
- **Restart `uvicorn` DAN `celery worker`** (`Ctrl+C` lalu jalankan ulang keduanya)
  supaya endpoint baru (`/templates`, `/chat/messages`, dst) benar-benar aktif — semua
  perubahan Phase 6R-1/6R-2/6R-3 belum pernah dimuat proses yang sedang jalan.
- Untuk benar-benar pakai Claude: isi `ANTHROPIC_API_KEY` di `backend/.env`, set
  `AI_LLM_PROVIDER=anthropic`, restart backend. Belum pernah dites dengan key asli dari
  sesi manapun — kalau ada masalah format request/response ke Anthropic API, kemungkinan
  perlu penyesuaian kecil di `anthropic_provider.py` begitu dites nyata.

### Untuk sesi berikutnya (sudah dilanjut — lihat "Catatan sesi" di bawah)

---

## Catatan sesi — LLM diganti ke Gemini (gratis), mode guest, akun Unlimited, AI Image/Audio

Setelah Phase 6R-3, user memutuskan 3 hal tambahan:

1. **LLM agent pakai Gemini, bukan Claude** — karena Claude API berbayar dan produk
   belum ada penghasilan ("nanti kalau udah ada yang akses banyak dan menghasilkan
   uang, baru upgrade"). Google Gemini API punya tier gratis (Google AI Studio, tanpa
   billing) dengan function-calling yang solid.
2. **Mode guest** — begitu pertama buka app, langsung masuk kayak tamu (tanpa isi
   form login), tapi sistem akun tetap ada di backend (dibutuhkan buat kuota/
   kepemilikan data). Ditambah: akun khusus milik user sendiri dengan kuota unlimited.
3. **Skill AI baru** — user pilih opsi "beneran tambah kemampuan baru" (bukan cuma
   pola interaksi), terinspirasi dari Dreamina yang punya AI Image, AI Audio, dst.

### Dibangun

**LLM provider — Gemini jadi provider gratis, Claude tetap ada sebagai upgrade path**
- `app/services/llm_providers/gemini_provider.py`: `GeminiLLMProvider` — pakai SDK
  resmi `google-genai` (`pip install google-genai`, versi 2.22.0), function-calling
  lewat `types.FunctionDeclaration`/`types.Tool`. Konstruktor gagal jelas kalau
  `GEMINI_API_KEY` kosong (sama seperti `AnthropicLLMProvider`).
- `factory.py` sekarang dukung 3 nama: `mock` (default), `gemini` (direkomendasikan,
  gratis), `anthropic` (upgrade berbayar nanti) — keduanya lazy-import biar SDK-nya
  tidak wajib terpasang kalau masih pakai mock.
- `app/core/config.py` + `.env`/`.env.example`: `GEMINI_API_KEY`, `GEMINI_MODEL`
  (`gemini-2.5-flash`) ditambah, `anthropic_*` tetap ada.
- **Efek samping**: `pip install google-genai` menaikkan `pydantic` (2.10.4 → 2.13.5)
  karena dependency SDK-nya. Sudah diverifikasi kompatibel (77/77 test tetap hijau) —
  `requirements.txt` di-update ke versi yang benar-benar terpasang.

**Mode guest + akun Unlimited**
- `app/api/auth.py`: endpoint baru `POST /auth/guest` — bikin akun anonim
  (`guest+<uuid>@guest.advanceai.app`, plan Free) tanpa perlu isi form, buat frontend
  langsung "masuk" begitu dibuka (pemakaian nyata di 6R-4, belum dikerjakan sesi ini).
  Helper `_plan_id_for_email()`: kalau email yang register/login cocok dengan
  `OWNER_EMAIL` di `.env` (case-insensitive), otomatis dapat plan **"Unlimited"**
  (bukan "Free") — tidak self-serve, hanya lewat env var yang saya set langsung di
  `backend/.env` (gitignored, tidak pernah masuk repo).
- Migrasi `b7b7f3d31c32_seed_unlimited_plan.py`: seed 1 plan "Unlimited"
  (`ai_generation_quota=1_000_000`).
- `backend/.env` (lokal, bukan `.env.example`): `OWNER_EMAIL=nabilbiel12@gmail.com`
  sudah diisi langsung — akun dengan email itu otomatis dapat plan Unlimited begitu
  daftar/login.

**AI Image + AI Audio (skill baru, di luar spec awal — dikonfirmasi user)**
- `app/services/ai_providers/image.py` (interface baru, pola sama seperti video) +
  `mock_image.py`: `MockImageProvider` — belum ada provider gambar asli, mock-nya
  gambar placeholder beneran (kartu warna panel + teks prompt, pakai Pillow yang
  sudah jadi dependency lewat `qrcode[pil]`), diupload ke storage, jadi `MediaAsset`
  baru bertipe `photo` — **bisa langsung dipakai lagi sebagai sumber generate video**.
- `app/services/ai_providers/voiceover.py` (interface lama Phase 0, baru sekarang
  disambung) + `mock_voiceover.py`: `MockVoiceoverProvider` — belum ada TTS asli,
  mock-nya generate klip audio bisu berdurasi wajar (perkiraan dari jumlah kata) via
  ffmpeg, jadi `MediaAsset` baru bertipe `audio` (tipe baru, tidak perlu migrasi
  karena kolom `type` cuma string bebas, bukan enum DB).
- Tool agent baru: `generate_image_tool` (prompt → gambar), `generate_voiceover_tool`
  (teks → audio) — didaftarkan di registry, `MockLLMProvider` dapat keyword baru
  ("gambar"/"generate image" → image, "voiceover"/"text-to-speech"/"suara ai" → audio)
  yang otomatis meneruskan pesan user apa adanya sebagai isi prompt/teks.
- Exception baru `GenerationFailedError` di `app/services/errors.py` buat skill ini.
- Rename kecil biar bisa dipakai lintas modul: `video_render._ensure_ffmpeg_available`
  → `ensure_ffmpeg_available` (public).

### Keputusan teknis
- **Gemini dipilih sebagai provider gratis "terbaik"** dibanding alternatif gratis
  lain (mis. Groq+Llama) karena kualitas reasoning/function-calling-nya lebih baik
  untuk agent yang manggil tool berulang kali. **Belum pernah dites dengan API key
  asli** — user perlu daftar sendiri di https://aistudio.google.com/apikey (gratis,
  tanpa kartu kredit) lalu isi `GEMINI_API_KEY` + `AI_LLM_PROVIDER=gemini` di `.env`.
- **Mode guest baru setengah jalan**: endpoint backend-nya sudah ada dan dites, tapi
  **frontend belum dipakaikan** — itu bagian dari 6R-4 (workspace shell), supaya tidak
  ngerjain UI auth 2x (sekali sekarang untuk halaman lama yang segera dihapus, sekali
  lagi nanti untuk `/studio`).
- **AI Image/Audio scope-nya dijaga kecil**: cuma dua skill yang relevan ke tujuan
  produk (foto/gambar & suara buat video iklan) yang dikerjakan, bukan replikasi penuh
  Dreamina (AI Avatar, 3D, Clay Renderer, Mimic Motion sengaja **tidak** dibangun —
  di luar tujuan produk "video iklan dari foto produk", akan jadi scope tak terbatas
  kalau semua ditiru).
- `MediaAsset.size_bytes=0` untuk hasil AI Image/Audio (bukan file upload asli, tidak
  ada ukuran byte yang bermakna untuk ditampilkan) — kosmetik saja, tidak dipakai untuk
  validasi apapun.

### Cara jalanin / verifikasi
```bash
cd backend && .venv\Scripts\activate
pytest -q        # 77/77 pass (68 lama + 9 baru: LLM factory gemini/anthropic,
                  # AI Image/Audio providers + tools end-to-end lewat chat)
ruff check .      # clean
alembic upgrade head   # migrasi Unlimited plan diverifikasi ke Postgres asli
```

### Item follow-up / aksi manual user
- **Restart `uvicorn` dan `celery worker` lagi** — perubahan `.env` (OWNER_EMAIL,
  provider settings) baru kebaca kalau backend di-restart (`pydantic-settings` di-cache
  sekali per proses).
- Daftar API key Gemini gratis di https://aistudio.google.com/apikey kalau mau agent
  beneran jalan pakai AI (bukan `MockLLMProvider`), isi `GEMINI_API_KEY` +
  `AI_LLM_PROVIDER=gemini` di `backend/.env`.
- Kalau sebelumnya sudah pernah register akun pakai email `nabilbiel12@gmail.com`
  SEBELUM `OWNER_EMAIL` ini diisi, akun itu masih ke-assign plan "Free" (plan cuma
  di-assign saat akun dibuat, bukan diupdate otomatis) — perlu register ulang (kalau
  belum ada data penting) atau bilang ke saya untuk update `plan_id`-nya manual lewat
  SQL.

### Untuk sesi berikutnya
Semua kerjaan backend Phase 6R (6R-1, 6R-2, 6R-3, + tambahan LLM/guest/AI skills di
atas) **selesai dan hijau** (77/77 test, migrasi terverifikasi). **Frontend masih
belum disentuh sama sekali** — ini beban kerja terbesar yang tersisa: 6R-4 (workspace
shell + mode guest di UI + hapus halaman lama), 6R-5 (galeri template), 6R-6 (panel
chat), plus sekarang juga perlu slot UI untuk skill AI Image/Audio yang baru dan
tampilan yang match referensi Dreamina (warna/font/animasi ikut DESIGN_SYSTEM.md,
bukan AI-slop). Rencana arsitektur dasarnya masih sama seperti di plan file sesi ini
(`warm-knitting-journal.md`), tapi perlu diperluas dikit buat 3 penambahan ini.

---

## Phase 6R-4/5/6 — Frontend: unified workspace shell, template gallery, chat panel — Status: selesai

Dikerjakan sekaligus dalam satu sesi (bukan 3 commit terpisah seperti rencana awal) —
ketiganya saling menyambung erat (canvas butuh context; template gallery & chat panel
sama-sama slot ke canvas itu) sehingga membangun terpisah cuma menambah overhead tanpa
manfaat nyata. Verifikasi tetap dilakukan menyeluruh di akhir (lihat "Cara jalanin").

### Dibangun

**Mode guest di UI** (backend-nya sudah ada dari catatan sesi sebelumnya):
- `src/lib/auth-options.ts`: provider `CredentialsProvider({ id: "guest" })` baru —
  `authorize()` selalu memanggil `POST /auth/guest` (baru), tidak menerima form apapun.
- `src/app/page.tsx` (ditulis ulang): begitu dibuka, panggil `signIn("guest")` otomatis
  kalau belum ada sesi, lalu redirect ke `/studio` — tidak ada form login di depan.
  Guard `useRef` mencegah StrictMode memanggil dua kali; sesi NextAuth sendiri yang
  mencegah panggilan ulang di kunjungan berikutnya (tiap panggil `/auth/guest`
  menghabiskan satu akun+kuota baru — lihat komentar di `app/api/auth.py`).
  Fallback: kalau guest sign-in gagal (mis. backend mati), tampilkan link Masuk/Daftar.
- `(workspace)/layout.tsx`: redirect ke `/` (bukan lagi `/login`) kalau belum ada sesi.
- `components/workspace/user-menu.tsx`: badge "Mode Tamu" + link "Simpan sebagai akun"
  (ke `/register`) untuk guest — email guest (`guest+<uuid>@guest.advanceai.app`) tidak
  pernah ditampilkan mentah ke user.
- `/login` dapat tambahan link "Lanjut sebagai tamu" (ke `/`); redirect setelah
  login/register diarahkan ke `/studio`, bukan `/dashboard` lagi.

**Workspace shell (6R-4)** — satu canvas berkelanjutan menggantikan
`/generate`, `/editor/[id]`, `/publish/[id]` (dihapus outright):
- `src/lib/api-client.ts` (baru): `apiFetch`/`apiFetchBlob` generik, ganti pola
  `fetch(..., {headers:{Authorization}})` yang tadinya diduplikasi di tiap halaman.
- `components/workspace/workspace-context.tsx`: `WorkspaceProvider`/`useWorkspace()` —
  state di React Context + `useState` (bukan `useReducer` seperti draf plan awal; untuk
  ukuran state ini beberapa `useState` lebih sederhana dan sama efektifnya, tanpa
  menambah dependency). Menyatukan: pilih/upload foto, prompt+mode+template, job
  generate, project (create/save draft/render), posts (prepare publish/mark uploaded).
  **Satu** effect polling terpusat (ganti 3 `setInterval` yang tadinya terpisah di
  masing-masing halaman lama) — jalan tiap 2.5 detik hanya kalau job/render/export ada
  yang masih in-flight. `applyToolResult(toolName, result)`: jembatan dari chat agent
  (6R-6) — tiap hasil tool dipetakan ke state yang sama persis yang dipakai tombol UI,
  jadi aksi lewat chat vs lewat klik memperbarui canvas dengan cara yang sama.
- `components/workspace/pipeline-header.tsx` + `timeline-pipeline.tsx` (diperbarui,
  tambah `onStageClick`): strip pipeline persisten, klik satu stage men-scroll ke
  section-nya di canvas (bukan navigasi halaman lain — workspace-nya memang satu
  halaman panjang, bukan wizard).
- `components/workspace/workspace-canvas.tsx` + `panels/{upload,generate,edit,publish}
  -panel.tsx`: 4 section ditumpuk vertikal (upload → generate → edit → publish),
  dipisah garis tipis (`divide-y`), bukan kartu terpisah. Auto-scroll halus (satu-
  satunya motion "disengaja" di luar respons klik langsung, sesuai DESIGN_SYSTEM.md
  §6) saat project baru dibuat (→ section Edit) dan saat render sukses (→ section
  Publish).
- `components/workspace/shell.tsx` (baru): sidebar jadi off-canvas drawer di bawah
  breakpoint `lg` (tombol hamburger di header) — sebelumnya sidebar `w-56` fixed tidak
  responsif sama sekali. `(workspace)/layout.tsx` didelegasikan ke sini.
- `sidebar.tsx`: "Generate Studio"/"Editor"/"Publish" digabung jadi satu link "Studio".
  Halaman index lama (`editor/page.tsx`, `publish/page.tsx`, `calendar/page.tsx`) tetap
  ada (tidak di-link dari sidebar lagi) — link-nya diarahkan ke `/studio/[id]`.
- `app/(workspace)/studio/layout.tsx` + `studio/[[...projectId]]/page.tsx`
  (catch-all opsional): `/studio` (belum ada project) dan `/studio/<id>` (bookmark)
  sama-sama merender canvas yang sama; `createProject`/tool `create_project_tool`
  memanggil `window.history.replaceState` ke `/studio/<id>` begitu project dibuat,
  tanpa navigasi penuh.

**Template gallery (6R-5)**:
- `components/workspace/template-gallery.tsx`: filmstrip horizontal-scroll (bukan grid
  kartu seragam — DESIGN_SYSTEM.md §5.3), fetch `GET /templates` sekali per mount.
  Pilih template → `context.applyTemplate()` → prefill prompt+mode di Generate panel
  (tetap bisa diedit manual).

**Chat panel (6R-6)**:
- `components/workspace/chat-panel.tsx`: satu instance (bukan dua — lihat komentar di
  kode) yang berubah bentuk lewat CSS breakpoint saja: docked column di `lg+`, tombol
  mengambang + drawer full-screen di bawah `lg`. Ini penting karena kalau di-mount dua
  kali (satu untuk mobile, satu untuk desktop, disembunyikan via `hidden`/`lg:hidden`),
  riwayat percakapan akan bercabang jadi dua — sudah dites dan dihindari sejak awal.
  Lampirkan foto → `POST /media/upload` asli langsung dari sini (bukan LLM yang
  "meng-upload" — LLM tidak bisa membawa bytes), lalu id-nya dikirim sebagai
  `media_asset_id` di `POST /chat/messages` berikutnya.
  Render pesan `role="tool"` sebagai tally dot + label (bukan log teks polos).
  Markdown ringan dari balasan Gemini (`**bold**`, `*italic*`, list `- `/`1. `)
  dirender jadi elemen React manual (bukan `dangerouslySetInnerHTML`, dan sengaja tidak
  menambah dependency markdown-renderer untuk kasus sekecil ini).

### Bug ditemukan & diperbaiki lewat smoke test browser nyata

Sesi ini diverifikasi dengan smoke test Playwright asli (Chrome sistem, karena
`playwright install` tidak bisa download browser sendiri di sandbox ini — lihat
"Keputusan teknis") terhadap stack yang benar-benar jalan (Docker Postgres/Redis/MinIO,
`GEMINI_API_KEY` asli). Ini menemukan bug nyata yang lolos dari `build`/`lint`:
**pesan user muncul dobel di chat** — `handle_turn` (backend) selalu mengembalikan
pesan user yang baru saja disimpan sebagai elemen pertama `messages[]`, sementara
frontend juga menambahkannya secara optimistik sebelum memanggil API. Diperbaiki
dengan membuang elemen pertama respons server sebelum di-merge (kontrak
`handle_turn` menjamin urutan ini, lihat komentar di `chat_agent.py`).

### Keputusan teknis

- **`useState` majemuk, bukan `useReducer`**, untuk `WorkspaceProvider` — deviasi kecil
  dari draf plan (`warm-knitting-journal.md`). Bentuk state-nya flat, tidak ada
  transisi kompleks yang butuh reducer; `useState` lebih mudah dibaca untuk ukuran ini.
- **6R-4/5/6 dikerjakan sebagai satu unit**, bukan 3 commit/verifikasi terpisah seperti
  urutan di plan awal — canvas, template gallery, dan chat panel saling bergantung
  erat sejak awal (semua butuh `WorkspaceContext` yang sama), jadi memisahkannya
  hanya menambah overhead tanpa manfaat integrasi bertahap yang nyata.
- **Smoke test pakai Chrome sistem (`executablePath`) via `playwright-core`**, bukan
  `chromium-cli` (tidak tersedia) atau browser bundled Playwright (gagal download —
  sandbox ini tidak bisa akses `cdn.playwright.dev`). Dependency `playwright-core`
  diinstal di scratchpad sesi, **bukan** ditambahkan ke `frontend/package.json` —
  murni alat verifikasi sesi ini, bukan bagian dari aplikasi.
- **Markdown balasan chat dirender manual** (regex `**bold**`/`*italic*`/list), bukan
  lewat library (`react-markdown` dll.) — cakupannya kecil (cuma pola yang benar-benar
  muncul dari Gemini), menambah dependency untuk ini belum sepadan.
- Kode lampiran chat di atas mengonfirmasi poin desain dari plan awal: intent "generate
  video dari foto ini" lewat chat betul-betul memanggil `generate_video_tool` →
  `AIJob` asli (`status: queued`) — bukan simulasi UI semata.

### Cara jalanin / verifikasi

```bash
cd frontend
npm run build   # clean
npm run lint    # clean
```
Manual/otomatis, terhadap stack nyata (Docker Postgres/Redis/MinIO healthy, ffmpeg
terpasang, `GEMINI_API_KEY` asli terisi):
- Buka `http://localhost:3000` → otomatis masuk sebagai tamu → landing di `/studio`
  dengan pipeline header, template gallery, upload panel, chat panel — dikonfirmasi
  lewat screenshot Playwright, nol error console.
- Upload foto → tally dot Upload jadi solid teal ("selesai").
- Klik "Generate video" → tally dot Generate jadi amber pulsing ("sedang proses") lalu
  solid teal ("selesai") lewat polling terpusat, tanpa reload halaman.
- Chat: "generate video dari foto ini" → `generate_video_tool` beneran jalan (job
  `queued` sungguhan, dikonfirmasi lewat network response `/chat/messages`), balasan
  Gemini tampil dengan bold/list ter-render, tanpa pesan dobel.
- Resize ke 390×844 (mobile): hamburger drawer + tombol mengambang chat AI keduanya
  muncul dan berfungsi.

### Item follow-up / aksi manual user

- **Coba sendiri end-to-end di browser biasa** (bukan cuma screenshot headless) —
  terutama alur "Lanjut ke Edit" → render → "Siapkan untuk Publish" yang belum sempat
  diklik di smoke test sesi ini (sudah diverifikasi lewat kode/lint/build, tapi belum
  lewat klik nyata sampai ke ujung pipeline).
- Halaman `editor/page.tsx`/`publish/page.tsx` (daftar riwayat project) tidak lagi ada
  di sidebar (sesuai plan) — kalau ternyata masih dibutuhkan sebagai navigasi utama,
  beri tahu supaya ditambahkan lagi sebagai link (bukan cuma reachable via `/editor`
  langsung).
- Tombol chat mengambang di mobile menumpuk di pojok kanan-bawah secara permanen
  (pola FAB umum) — kalau terasa mengganggu konten di bawahnya, bisa disesuaikan.

---

## Phase 6R-7 — Marketing landing page + Dashboard hub (redesign visual, bagian 1) — Status: selesai

User menunjukkan qreed.ai sebagai referensi tampilan yang ingin ditiru gayanya, plus
minta beberapa fitur baru besar (AI Influencer, motion graphics/effects, provider
Google Veo & Seedance). Karena itu penambahan scope besar di luar
`adVance-AI-Spesifikasi-Proyek.md`, dikonfirmasi dulu ke user urutan kerjanya lewat
`AskUserQuestion` sebelum ada kode ditulis:
1. **Redesign visual dulu** (fase ini) — fitur & backend yang sudah ada tetap, tidak
   ada API/data baru yang dijanjikan ke user produk.
2. Provider Veo/Seedance: **badge tampilan saja** sekarang (dicek dulu harganya —
   Veo3 ~$0.75/detik, Seedance $0.04-0.78/detik — mahal & belum ada pemasukan produk
   untuk nanggung itu). Generation asli tetap `MockVideoProvider`.
3. Motion graphics: AI auto-apply preset **nanti**, phase terpisah.
4. AI Influencer: **ditunda**, phase terpisah.

### Dibangun

**Routing — pisahkan marketing (publik) dari workspace (butuh sesi)**:
- `frontend/src/app/page.tsx` ditulis ulang total jadi landing page publik (server
  component murni, tanpa next-auth sama sekali) — sebelumnya `/` cuma logic
  auto-guest-signin+redirect, tidak ada konten marketing apapun.
- **Baru** `frontend/src/app/app/page.tsx` (`/app`) — logic guest-bootstrap yang
  dulu ada di `/` dipindah ke sini (redirect tujuan diganti ke `/dashboard`, bukan
  lagi `/studio`). Semua CTA "Mulai Gratis"/"Lanjut sebagai tamu" di landing/login
  arahkan ke `/app`, bukan `/`.
- `(workspace)/layout.tsx`: redirect no-session diganti dari `/` → `/app`.
- `login/page.tsx`, `register/page.tsx`: redirect sukses diganti ke `/dashboard`
  (dari `/studio`), tambah link kecil kembali ke `/` di atas form.

**Landing page baru** (`components/marketing/`): `nav.tsx` (sticky, anchor scroll
`#fitur`/`#cara-kerja`), `hero.tsx` (headline + `PhoneFrame` berisi mockup UI abstrak
— play icon + pill caption, BUKAN mockup akun sosmed dengan username/like/comment
fiktif), `pipeline-explainer.tsx` (reuse `TimelinePipeline`/`TallyDot` yang sama
persis dipakai di workspace, di dalam panel gelap di tengah halaman terang),
`feature-grid.tsx` (list fitur nyata yang sudah ada — Media Library, Generate
Studio, AI Chat Agent, AI Image/Audio, Editor Ringan, Publish Manual Assist, dengan
copy jujur soal auto-post belum ada), `model-badges.tsx` (badge Veo/Seedance ditulis
sebagai **roadmap** — "dirancang untuk mendukung ... segera menyusul", bukan
"didukung oleh" yang menyiratkan sudah aktif), `cta-band.tsx`, `footer.tsx` (minimal,
tanpa link sosmed palsu). **Sengaja tidak ada**: section testimoni/nama pelanggan
fiktif, tabel harga dengan tier berbayar yang belum ada (cuma plan "Free" nyata di
backend), section "Akademi"/fitur qreed.ai lain yang tidak match produk kita.

**Dashboard jadi hub** (`(workspace)/dashboard/page.tsx`, sebelumnya placeholder
kosong sejak Phase 1): greeting, `CreateNewCard` (kartu besar "Buat Baru" →
`/studio` kosong), `TemplateHubGrid` (grid template dikelompokkan per `mode` —
"Iklan Produk"/"Affiliate", pakai 4 template asli dari `GET /templates` yang sudah
ada, **tanpa migrasi backend baru** — cover art gradient deterministik dari hash id
template, util baru `lib/template-cover.ts`, ikon `lucide-react` per mode),
`RecentProjectsList` (list bukan grid, reuse pola `GET /projects` dari
`editor/page.tsx` lama). Klik kartu template → `/studio?mode=...&prompt=...` →
`studio/[[...projectId]]/page.tsx` baca query itu sekali (`useSearchParams` + guard
ref) dan panggil `setProjectMode`/`setPrompt` dari `useWorkspace()` — tidak fetch
ulang atau ubah kontrak `applyTemplate`.

**Polish visual (tanpa ubah behavior)**: dependency baru `lucide-react@1.41.0`
(dipin exact). `sidebar.tsx` dapat ikon di depan tiap section (link/behavior tidak
berubah). `ui/button.tsx` dapat prop `size` opsional (`sm|md|lg`, default `md` =
perilaku lama) buat CTA landing yang lebih besar. `globals.css` dapat 2 token baru:
`--color-paper-ink` (`#1B1D28`) dan `--color-paper-ink-muted` (`#5B5E6E`) — teks
khusus tema terang marketing, karena `--color-ink`/`--color-ink-muted` yang ada
dituning untuk latar gelap dan gagal kontras WCAG AA di atas `bg-paper`.

**`DESIGN_SYSTEM.md`**: tambah §5.5 (pola halaman marketing: token teks terang,
aturan mockup abstrak bukan social-proof palsu, aturan badge provider harus
roadmap-honest kalau belum aktif) dan §5.6 (pengecualian §5.3 untuk galeri
template/konten — grid boleh, dengan syarat cover art tidak seragam generik dan
tidak nambah chrome filter/search kalau datanya masih sedikit).

### Keputusan teknis

- **`timeline-pipeline.tsx` ditambah `"use client"`**: build production gagal
  ("Event handlers cannot be passed to Client Component props") karena komponen ini
  selalu attach `onClick` ke tombolnya (meski `onStageClick` tidak diberikan) —
  begitu dipakai dari Server Component murni (`pipeline-explainer.tsx` di landing
  page), fungsi onClick itu tidak bisa diserialisasi lewat batas server/client tanpa
  directive ini. Perubahan minimal, tidak mengubah perilaku di `pipeline-header.tsx`
  (sudah `"use client"` dari awal).
- **Tidak ada migrasi backend baru** untuk grid template di dashboard — dikelompokkan
  pakai field `mode` yang sudah ada (cuma 2 nilai: `product_ad`/`affiliate`), bukan
  nambah kolom `category` — supaya tidak menambah data/skema yang belum benar-benar
  dibutuhkan (baru 4 template ter-seed, lihat Phase 6R-2).
- Halaman `editor/page.tsx`/`publish/page.tsx` (orphaned sejak Phase 6R-4) **masih
  dibiarkan apa adanya** — di luar scope fase ini, bukan dihapus tanpa persetujuan
  eksplisit.

### Cara jalanin / verifikasi

```bash
cd frontend
npm install    # lucide-react baru
npm run build  # clean — "/" sekarang prerender statis
npm run lint   # clean
```

Smoke test manual lewat `curl` terhadap `npm run dev` (Docker Postgres/Redis/MinIO +
backend `uvicorn` sudah jalan dari sesi sebelumnya):
- `GET /` → 200, judul & hero landing page muncul ("Dari foto produk, jadi video
  siap tayang."), CTA "Mulai Gratis" ada.
- `GET /dashboard` (tanpa cookie sesi) → 307 ke `/app` (bukan lagi `/`).
- `GET /studio` (tanpa cookie sesi) → 307 ke `/app`.
- `GET /app` → 200, render teks "Menyiapkan dashboard…" (target redirect baru).
- `GET /login`, `/register` → 200.

**Klik nyata lewat browser sudah dicoba** (Chrome sistem via `playwright-core`, pola
sama seperti smoke test Phase 6R-4/5/6): `/` → klik "Mulai Gratis" → guest sign-in
otomatis → mendarat di `/dashboard` (grid template per mode + "Buat Baru" muncul,
dikonfirmasi lewat screenshot) → klik kartu "Unboxing Produk" → `/studio?mode=
product_ad&prompt=...` → field "Gaya referensi" di Generate panel ter-prefill
otomatis dari `prompt_preset` template. Nol error console di sepanjang alur ini.
Resize mobile (390px) untuk landing page juga dikonfirmasi rapi lewat screenshot.

### Item follow-up / aksi manual user

- Belum diputuskan: kapan lanjut ke Phase 6R-8+ (AI Influencer, motion graphics auto-
  preset, provider Veo/Seedance asli) — semua ditunda sesuai kesepakatan sesi ini,
  tunggu user yang mulai lagi kapan siap.

---

## Phase 6R-8/9/10/11 — Motion preset engine, voice-over asli, n8n orchestration — Status: selesai

User minta hasil editor benar-benar otomatis (motion, transisi, sound, voice AI) dan
kasih 2 prompt referensi (gaya paper-cutout/newspaper collage dari TikTok, + instruksi
eksplisit "buatkan preset `editorial-newspaper` di modul video-effect generator kita").
Juga minta workflow n8n (via `n8n-mcp`) untuk automation. Scope besar di luar spec awal
— dikonfirmasi dulu lewat `AskUserQuestion` sebelum kode ditulis (lihat plan file sesi
ini kalau perlu detail): **n8n = orkestrasi/notifikasi saja** (auto-posting IG/TikTok/
YouTube masih diblokir approval developer app, CLAUDE.md), **motion = ffmpeg lokal**
(bukan provider AI video berbayar — belum ada budget/provider dipilih), **voice-over =
provider gratis** (edge-tts), **urutan = motion engine dulu** baru redesign visual
lanjutan (redesign visual lanjutan **belum dikerjakan sesi ini** — lihat follow-up).

### Dibangun

**Motion preset engine (6R-8)** — `backend/app/services/motion_presets/`: catalog
code-defined (`registry.py`, `MOTION_PRESETS` dict) — preset adalah render logic bukan
data, pola sama seperti `video_render.PLATFORM_DURATION_LIMITS_SECONDS`. Preset pertama
`editorial-newspaper` (`editorial_newspaper.py`): 3 "shot" Ken-Burns (zoompan) dari 3
still frame source di timestamp berbeda (punch zoom, drift/whip-pan, handheld shake),
digabung via concat demuxer dengan snap cut + 1 frame-flash (klip putih 0.08s), caption
burn-in opsional via drawtext (font Anton — OFL-licensed, dibundel di
`assets/Anton-Regular.ttf`, bukan bergantung fontconfig OS). Output 1080x1920, 5-7 detik
(target 6s). `engine.py`: `apply_motion_preset()`, entrypoint publik pola sama seperti
`video_render.export_for_platform` (download→temp dir→bytes, tidak sentuh storage).
`ContentProject.motion_preset` (kolom baru, migrasi `54d6d000930b`) — kalau diisi,
`render_project_task` pakai preset engine ini menggantikan `trim_video` polos (trim
start/end diabaikan, preset yang tentukan durasi). Endpoint baru `GET /motion-presets`
(katalog, read-only). `render_project_tool` (agent) dapat argumen opsional
`motion_preset`. `video_render._run_ffmpeg` → `run_ffmpeg` (public, dipakai lintas
modul, pola sama seperti rename `ensure_ffmpeg_available` sebelumnya).
**Diverifikasi manual terhadap ffmpeg asli** (bukan cuma test/mock) — output dicek
`ffprobe` (1080x1920/30fps/6.0s persis) dan frame diperiksa visual. Nemu & fix 2 bug
ffmpeg nyata di proses ini: (1) build ffmpeg Windows di mesin ini tidak ada file config
fontconfig sama sekali → `drawtext` butuh `fontfile=` path eksplisit, bukan lookup nama
font; (2) `drawtext` mode `expansion` default menganggap `%` sendirian sebagai awal
format-specifier ("Stray %") → fix pakai `expansion=none` (percobaan escape `%%`/`\%`
duanya TIDAK berhasil di versi ffmpeg ini, meski beberapa dokumentasi online bilang
begitu).

**Voice-over asli (6R-9)** — `EdgeTTSVoiceoverProvider`
(`app/services/ai_providers/edge_tts_voiceover.py`): pakai `edge-tts` (gratis, tanpa
API key, suara neural Microsoft Edge), alasan sama seperti pemilihan Gemini
sebelumnya ("gratis dulu"). Default suara `id-ID-ArdiNeural` (Indonesia, sesuai bahasa
produk). Panggilan network diisolasi di `_synthesize_bytes()` supaya test tidak pernah
hit network asli. `factory.get_voiceover_provider()` dapat cabang `edge_tts` (lazy
import). Default tetap `mock` di `.env.example` — `edge_tts` didokumentasikan sebagai
rekomendasi, tapi opt-in (user isi sendiri).

**n8n orchestration (6R-10)** — **orkestrasi/notifikasi saja, TIDAK PERNAH posting
asli** ke IG/TikTok/YouTube (developer app belum approved, CLAUDE.md). Service `n8n`
baru di `docker-compose.yml` (image `n8nio/n8n`, port 5678). Backend kirim webhook
fire-and-forget (`app/services/n8n_notify.py`, `notify_pipeline_event()`) ke
`N8N_WEBHOOK_URL` saat render/export sukses/gagal (hook di `workers/tasks.py`, di
`render_project_task` & `export_post_task`) — gagal kirim webhook cuma di-log, tidak
pernah melempar exception (notifikasi gagal tidak boleh merusak pipeline video).
Nonaktif default (`N8N_WEBHOOK_URL` kosong). **Belum dibuat**: workflow n8n asli
(Webhook trigger → notifikasi Discord/Slack) — itu langkah lanjutan setelah n8n
container jalan + API key dibuat + `n8n-mcp` di-install sebagai MCP tool + user kasih
URL webhook Discord/Slack-nya (semua butuh aksi manual user, lihat follow-up).
**`n8n-mcp` itu sendiri belum diinstall** sesi ini (baru scaffolding-nya).

**Frontend (6R-11)** — `MotionPresetPicker`
(`components/workspace/motion-preset-picker.tsx`): filmstrip fetch `GET
/motion-presets`, pola visual sama seperti `TemplateGallery` (DESIGN_SYSTEM §5.3/§5.6).
Ditaruh di `edit-panel.tsx` di atas field trim. `WorkspaceContext` dapat
`motionPreset`/`setMotionPreset`, masuk ke body PATCH `saveDraft()` yang sudah ada
(pola sama seperti caption/music_track — user klik "Simpan draft" dulu baru "Render
video", tidak ada endpoint baru).

### Keputusan teknis

- Motion preset **code-defined**, bukan tabel DB — beda filosofi dari `Template`
  (yang memang cuma data/prompt teks). Preset = logika render (filter graph ffmpeg),
  nambah preset baru = nambah modul Python, bukan lewat admin UI/seed data.
- Ken-Burns 3-shot dari 1 sumber (bukan 1 `filter_complex` raksasa) — lebih gampang
  didebug/diverifikasi per langkah (masing-masing panggilan ffmpeg cuma 1 tugas),
  match gaya kode `video_render.py` yang sudah ada (fungsi-fungsi kecil terpisah,
  bukan filter graph kompleks).
- Font dibundel langsung di repo (`motion_presets/assets/`, OFL-licensed) — bukan
  bergantung font sistem/fontconfig, supaya identik di Windows dev machine, Linux CI,
  dan produksi nanti.
- n8n scope **sengaja dibatasi ketat** ke notifikasi — godaan untuk langsung bikin
  node auto-post ditolak eksplisit sesuai konfirmasi user + CLAUDE.md, meski secara
  teknis n8n workflow BISA punya node posting kalau developer app-nya sudah ada
  (belum ada sekarang).

### Cara jalanin / verifikasi

```bash
cd backend && .venv\Scripts\activate
pytest -q        # 89/89 pass
ruff check .      # clean
alembic upgrade head   # migrasi motion_preset diverifikasi ke Postgres asli

cd frontend
npm run build     # clean
npm run lint      # clean
```
Motion preset diverifikasi manual terhadap ffmpeg asli (lihat "Dibangun" di atas) —
**belum dites end-to-end lewat browser** (pilih preset di `/studio` → render → lihat
hasil beneran). `docker compose up -d` (service `n8n` baru) **belum pernah dicoba
jalan** sesi ini — cuma didefinisikan di compose file, belum diverifikasi start bersih.

### Item follow-up / aksi manual user

- [ ] **Coba end-to-end lewat browser**: `/studio` → Edit → pilih preset
      "Editorial Newspaper" → Simpan draft → Render video → cek hasilnya beneran
      punya motion/transisi (bukan cuma trim polos).
- [x] `docker compose up -d` service `n8n`, akun owner dibuat, API key dibuat,
      `n8n-mcp` didaftarkan sebagai MCP server (`claude mcp get n8n-mcp` → Connected).
      Webhook Discord dites langsung (POST → 204).
- [x] Workflow n8n asli dibuat & diaktifkan: **Webhook** (`POST /webhook/advance-ai-notify`)
      → **Code** (format pesan per `event`: `render.success`/`render.failed`/
      `export.success`/`export.failed`) → **HTTP Request** ke webhook Discord channel
      "Advance-AI". Tidak ada node auto-post ke IG/TikTok/YouTube (sesuai CLAUDE.md).
      Dibuat lewat n8n REST API langsung (tool `n8n-mcp` belum ter-load di tool-list
      sesi VSCode ini meski `claude mcp get` bilang Connected — kemungkinan perlu
      reload window, bukan cuma sesi CLI baru; API key sudah di tangan jadi jalan
      pintas ini aman & workflow-nya sama persis). Dites end-to-end: webhook → n8n
      execution `success` → pesan masuk ke Discord.
- [x] `N8N_WEBHOOK_URL=http://localhost:5678/webhook/advance-ai-notify` diisi di
      `backend/.env` — notifikasi render/export sekarang beneran terkirim (bukan
      no-op lagi). Backend (`uvicorn`) & celery worker **sudah dijalankan** (ternyata
      belum pernah jalan sama sekali di mesin ini, bukan cuma perlu restart) — lihat
      Phase 6R-12 di bawah.
- [ ] Kalau mau voice-over AI beneran (bukan cuma dipasang providernya): set
      `AI_VOICEOVER_PROVIDER=edge_tts` di `backend/.env`, restart backend — tidak
      butuh API key.
- Redesign visual/konten lanjutan (qreed.ai lebih dalam: warna/font/animasi/isi
  konten) **masih belum dikerjakan** — disepakati dikerjakan setelah motion engine ini
  (urutan dari `AskUserQuestion` sesi ini), belum mulai.
- Background music bed (`music_track` masih cuma nama string, belum ada file audio
  asli di-mixing) — di luar scope sesi ini, butuh sumber audio royalty-free asli.
- AI video-gen provider berbayar (Veo/Kling/dst, biar `prompt` teks benar-benar
  menggerakkan AI video generation asli) — masih ditunda, butuh keputusan budget.

---

## Phase 6R-12 — Stack dijalankan pertama kali + Timeline Pipeline "kabel" — Status: selesai

User minta cek tampilan frontend nyata (bukan cuma baca kode), lalu kasih feedback
soal pipeline yang "terlalu polos" (referensi screenshot node-canvas ala n8n/Zapier
generik dari hasil googling) dan dashboard yang "kek AI dan kaku". Dikonfirmasi dulu
lewat `AskUserQuestion` karena screenshot referensinya persis pola yang dilarang
`DESIGN_SYSTEM.md` §2 (chrome template, gradient dekoratif, kotak melayang bebas) dan
alur produk kita memang linear (tidak ada percabangan keputusan seperti di n8n) — user
pilih opsi rekomendasi: tetap linear, tapi kabel melengkung + ikon per node, plus
"tambahkan node kalau memang ada tahap ekstra yang dipakai" (bukan node dekoratif).

**Dijalankan (bukan cuma dikode)**: `uvicorn app.main:app --reload` (port 8000) dan
`celery -A app.workers.celery_app worker --pool=solo` — ternyata **belum pernah jalan
sama sekali** di mesin dev ini (bukan soal restart). `npm run dev` frontend juga baru
dijalankan pertama kali (port 3000). Infra docker (postgres/redis/minio/n8n) sudah up
duluan dari sesi 6R-10.

**Timeline Pipeline jadi "kabel"**: `pipeline-connector.tsx` baru — SVG bezier
melengkung (patch-cable broadcast), warna & pulsing ikut status tally-light yang sama
(`stroke-rec` processing, `stroke-signal` success, `stroke-alert` failed), gantikan
divider garis lurus. `timeline-pipeline.tsx`: tiap `PipelineStage` sekarang wajib
`icon` (lucide-react) dan boleh punya `branches` (node cabang, dipakai Publish → satu
node per platform begitu `posts` sudah ada) dan `targetId` (scroll ke section lain,
dipakai node Motion → scroll ke `#stage-edit`). `pipeline-header.tsx`: 4 node inti
(Upload/Generate/Edit/Publish, ikon `CloudUpload`/`Sparkles`/`Scissors`/`Rocket`) +
node "Motion: <nama preset>" (`Clapperboard`) muncul **hanya** kalau
`project.motion_preset` terisi, + cabang per-platform di Publish **hanya** kalau
`posts` sudah disiapkan — tidak ada node/cabang yang dipalsukan untuk terlihat ramai.
`pipeline-explainer.tsx` (landing page, reuse komponen yang sama) ikut dikasih ikon.
`DESIGN_SYSTEM.md` §5.1 diupdate untuk mendokumentasikan motif "kabel + ikon + node
dinamis" ini secara eksplisit (bukan penyimpangan diam-diam dari dokumen).

**Dashboard "kaku"**: akar masalah konkret yang ditemukan — 3 dari 4 template bawaan
(`Unboxing Produk`/`Before/After`/`Demo Produk Close-up`, semuanya `product_ad`) semua
pakai ikon `ShoppingBag` yang sama persis di `TemplateHubGrid`, jadi kelihatan seperti
kartu yang sama diulang. `lib/template-cover.ts` dapat `templateIcon()` — ikon per
nama template (`PackageOpen`/`MessageCircleHeart`/`ArrowLeftRight`/`Camera`, sesuai
gaya masing-masing template asli di seed migration), fallback ke ikon mode kalau ada
template baru yang belum dipetakan. Ikon di kartu dapat hover scale kecil.
**Template bawaan itu sendiri sudah ada sejak awal** (4 baris di
`8b124fa99bc5_create_templates_table.py`, diverifikasi masih ke-seed di Postgres) —
bukan fitur baru, cuma kurang keliatan karena semua kartunya mirip.

**Pertanyaan user soal n8n dijawab** (bukan perubahan kode): n8n itu orkestrasi
backend-only (notifikasi Discord), tidak pernah tampil ke user aplikasi, dan canvas
node n8n **tidak bisa** di-embed ke Next.js — kalau mau tampilan serupa di produk,
itu harus komponen React sendiri (sudah dikerjakan di atas), bukan "ekstrak" dari n8n.

### Item follow-up / aksi manual user

- [ ] **Redesign dashboard lebih lanjut** — perbaikan ikon template ini baru satu titik
      konkret yang ditemukan sendiri (bukan dari feedback spesifik user tentang bagian
      mana yang "kaku"). Kalau masih belum sesuai setelah dilihat langsung di
      `/dashboard`, kasih tahu elemen spesifiknya (warna? kepadatan konten? kurang
      ilustrasi?) supaya nggak nebak-nebak lagi.
- [ ] Coba `/studio` langsung di browser untuk lihat pipeline kabel yang baru — apakah
      lengkungnya/ukuran node sudah pas, atau perlu disetel lagi.
- Backend/celery/frontend dijalankan via `run_in_background` sesi Claude Code ini —
  begitu sesi berakhir atau laptop restart, ketiganya perlu dijalankan manual lagi
  (`uvicorn app.main:app --reload`, `celery -A app.workers.celery_app worker
  --pool=solo`, `npm run dev`) — belum ada script/Procfile yang menyatukan ketiganya.

---

## Phase 6R-13 — Voice-over beneran nyambung ke hasil render — Status: selesai

User lihat hasil render asli di `/studio` (bukan cuma baca kode) dan komplain: video
hasil generate cuma foto diam (nggak kelihatan gerak) dan **nggak ada suara sama
sekali**, padahal dia mau bisa ketik naskah dan AI membacakannya jadi voice-over di
video. Diselidiki dulu sebelum dikerjakan (bukan langsung nebak):

- **Video diam** — `MockVideoProvider` (`synthesize_placeholder_video`) sebenarnya
  sudah pakai efek zoom ("Ken Burns") lewat ffmpeg `zoompan`, tapi zoom-nya sangat
  halus (1.0 → 1.08 selama 4 detik) jadi nyaris tidak kelihatan — bukan bug, memang
  cuma placeholder sampai provider AI video-gen asli (Runway/Kling/dst) dipilih &
  dibayar (CLAUDE.md: belum final, butuh keputusan budget user, sengaja tidak
  di-hardcode). Motion preset "Editorial Newspaper" (Phase 6R-8) sudah kasih gerakan
  jauh lebih dramatis (punch zoom, whip pan, handheld shake) — opsi gratis yang sudah
  ada tapi belum tentu dipakai di tiap project.
- **Tidak ada suara** — ternyata bukan bug tersembunyi, tapi memang **belum pernah
  disambungkan**: `generate_voiceover_tool` (Phase 6R-9, edge-tts) cuma menghasilkan
  `MediaAsset` audio lepas di Media Library, tidak pernah dipakai oleh
  `render_project_task`. `video_render.py` juga sama sekali tidak punya langkah mixing
  audio — `music_track` yang dipilih di Edit panel pun ternyata cuma string tersimpan,
  tidak pernah benar-benar di-mixing (sudah dicatat sebagai gap terpisah di follow-up
  6R-11, di luar scope sesi ini).

**Yang dikerjakan** (voice-over, gratis, tidak butuh keputusan provider baru):
- `ContentProject.voiceover_text` (kolom baru, migration `094c285d71ea`) — naskah
  teks disimpan mentah, **bukan** MediaAsset yang di-generate sekali lalu disimpan;
  setiap render men-sintesis ulang dari teks, jadi edit naskah + render ulang otomatis
  konsisten.
- `video_render.mux_voiceover()` — ffmpeg mux: track audio video (selalu bisu di titik
  ini) diganti audio voice-over. Kalau naskah lebih panjang dari durasi video, frame
  terakhir video di-freeze (`tpad`) supaya suara tidak kepotong di tengah kalimat;
  kalau naskah lebih pendek, video yang dipotong menyesuaikan (`-shortest`) — project
  ber-voice-over dianggap "dipimpin suara", bukan "dipimpin gambar".
  `services/storage.py` dapat `download_object()` (ambil bytes langsung lewat boto3)
  untuk mengambil hasil TTS balik dari MinIO.
- `render_project_task` (`workers/tasks.py`): kalau `voiceover_text` terisi, sintesis
  lewat `get_voiceover_provider()` (default `edge_tts`, provider yang sama dari Phase
  6R-9) lalu `mux_voiceover()` sebelum upload — gagal sintesis/mux bikin
  `render_status="failed"` dengan pesan jelas (pola sama seperti error ffmpeg/motion
  preset lain), bukan diam-diam ship video tanpa suara yang diminta.
- Frontend: `EditPanel` dapat textarea "Naskah voice-over (opsional)" di bawah
  Caption; `WorkspaceContext` dapat `voiceoverText`/`setVoiceoverText`, masuk ke
  `saveDraft()` PATCH body (pola sama seperti caption/motion preset — Simpan draft
  dulu, baru Render). Node **"Voice-over"** (ikon `Mic`) otomatis muncul di Timeline
  Pipeline (Phase 6R-12) begitu `voiceover_text` terisi, sama seperti node Motion.
- Test baru: `test_video_render.py` (mux ffmpeg-missing guard + 1 test ffmpeg asli
  yang benar-benar bikin video 1 detik + audio 3 detik lalu cek hasil mux ~3 detik,
  bukan kepotong 1 detik), `test_voiceover_render.py` (lewat endpoint asli: render
  sukses & voice-over ke-mux, render gagal kalau TTS gagal, langkah voice-over
  di-skip kalau `voiceover_text` kosong). 94 → 97 test lulus total, ruff bersih.

### Keputusan teknis

- **Naskah teks, bukan MediaAsset pre-generated** — beda dari pola motion preset (id
  string yang nunjuk ke logika render), tapi sengaja: voice-over terikat ke *isi*
  (teks), jadi re-render harus ikut teks terbaru tanpa langkah "generate ulang audio"
  manual terpisah.
- **`-shortest` + `tpad` freeze-frame**, bukan mixing di bawah audio asli — karena
  setiap video di titik mux selalu bisu (belum ada satupun sumber audio asli untuk
  di-preserve), replace selalu benar; kalau nanti ada AI video-gen asli yang punya
  audio sendiri, keputusan ini perlu ditinjau ulang.
- **Tidak menyentuh scope AI video-gen berbayar** — user juga minta "video yang
  beneran bergerak" (mis. produk dicelupkan ke cairan), itu butuh provider generative
  image-to-video asli (Runway/Kling/dst), bukan sekadar ffmpeg. Sudah dijelaskan ke
  user, **belum dikerjakan** — nunggu keputusan provider + budget (CLAUDE.md).

### Item follow-up / aksi manual user

- [ ] Coba render ulang project yang sudah ada (isi naskah voice-over di Edit → Simpan
      draft → Render) untuk dengar hasilnya langsung, bukan cuma baca kode.
- [ ] **Keputusan provider AI video-gen berbayar** — kalau mau video yang benar-benar
      menghasilkan gerakan/konten baru (bukan cuma kamera bergerak di atas foto diam),
      ini keputusan besar (biaya API per generate) yang perlu dipilih user dulu
      (lihat `docs/research/ai-providers-comparison.md`) sebelum bisa dikerjakan.
- Background music (`music_track`) masih belum di-mixing beneran — gap lama, belum
  dikerjakan sesi ini (fokus sesi ini voice-over sesuai yang diminta).
