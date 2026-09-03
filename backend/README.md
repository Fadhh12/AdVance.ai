# backend — FastAPI

Struktur folder mengikuti SDD §3.5:
```
app/
├── api/            # routers per domain (auth, media, ai, projects, posts)
├── core/           # config, security, dependencies
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
├── services/
│   ├── ai_providers/       # wrapper tiap provider AI (base.py = interface)
│   └── social_publishers/  # wrapper tiap platform (base.py = interface, Phase 6)
├── workers/        # celery tasks
└── main.py
alembic/            # migrations
tests/
```

## Setup
```bash
py -3.11 -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # isi sesuai docker-compose.yml kamu
```

> **Catatan mesin ini:** ada environment variable `PIP_TARGET` (User-level Windows env
> var) yang mengarah ke folder proyek lain (`D:\TrashDetection\venv\...`) dan diam-diam
> membajak SEMUA `pip install` di semua venv di mesin ini. Kalau `pip install` terasa
> "berhasil" tapi package tidak kebaca dari venv, jalankan dulu:
> `$env:PIP_TARGET = $null` (PowerShell, per-sesi) sebelum `pip install`, atau hapus
> env var itu permanen lewat System Properties → Environment Variables kalau memang
> sudah tidak dipakai proyek lain.

## Menjalankan
```bash
alembic upgrade head            # butuh Postgres jalan (docker compose up -d)
uvicorn app.main:app --reload
pytest -q
ruff check .
```

## Provider AI (Phase 3+)
Jangan panggil SDK/HTTP provider AI langsung dari router atau task Celery — selalu lewat
interface di `app/services/ai_providers/base.py`. Provider final belum dipilih, lihat
`/docs/research/ai-providers-comparison.md`. Default `.env`: `AI_VIDEO_PROVIDER=mock`.
