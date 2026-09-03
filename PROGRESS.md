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

### Untuk sesi berikutnya
Lanjut ke **Phase 1 — Auth & Core Infra** (lihat Task Breakdown §5 di
`adVance-AI-Spesifikasi-Proyek.md`): model User/Plan, register/login JWT, Google OAuth
wiring, Celery+Redis skeleton, halaman login/register frontend.
