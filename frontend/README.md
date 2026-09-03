# frontend — Next.js

App Router, TypeScript, Tailwind CSS v4. Token warna/font ada di `src/app/globals.css`
(`@theme`) — **jangan** pakai warna Tailwind default (slate/gray/dsb), selalu lewat token
di sana. Lihat `/DESIGN_SYSTEM.md` untuk aturan lengkap sebelum bikin komponen baru.

```
src/
├── app/          # routes (App Router)
├── components/   # komponen shared
└── lib/          # helper, API client, dsb
```

## Setup
```bash
npm install
copy .env.example .env.local
npm run dev      # http://localhost:3000
npm run build
npm run lint
```
