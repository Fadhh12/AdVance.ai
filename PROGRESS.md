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

### Untuk sesi berikutnya
Lanjut ke **Phase 4 — Editor Ringan**: model `content_projects` + migration (termasuk
field `mode`: product_ad/affiliate — ini pertama kalinya field itu punya rumah di
backend), `PATCH /projects/{id}` untuk simpan instruksi edit (trim range, urutan klip,
caption, pilihan musik), worker ffmpeg (dibungkus error jelas kalau ffmpeg belum
terpasang), UI Editor (preview, trim/reorder sederhana, edit caption, pilih musik, simpan
draft). Di titik ini juga masuk akal mulai sambungkan `SpeechToTextProvider` stub dari
Phase 3 ke fitur auto-caption di editor.
