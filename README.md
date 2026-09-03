# AdVance.ai
AI-driven SaaS tool that transforms product photos into engaging video ads and automatically publishes them to Instagram, TikTok, and YouTube Shorts.

## Baca dulu sebelum kerja di repo ini
- [`CLAUDE.md`](./CLAUDE.md) — konteks wajib untuk AI coding agent (Claude Code dkk).
- [`adVance-AI-Spesifikasi-Proyek.md`](./adVance-AI-Spesifikasi-Proyek.md) — PRD/SRS/SDD/UI Flow/Task Breakdown lengkap.
- [`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md) — aturan visual wajib.
- [`PROGRESS.md`](./PROGRESS.md) — progres per phase, mulai sesi baru dari sini.

## Struktur
```
backend/    FastAPI (Python 3.11) — lihat backend/README.md
frontend/   Next.js + TypeScript + Tailwind
docs/       dokumen riset (developer app registration, provider AI)
docker-compose.yml   Postgres + Redis + MinIO untuk dev lokal
```

## Quick start (dev lokal)
```bash
# Infra (butuh Docker Desktop)
docker compose up -d

# Backend
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
copy .env.example .env.local
npm run dev
```
