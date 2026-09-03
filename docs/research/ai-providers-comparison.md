# Perbandingan Provider AI — Image-to-Video, TTS, STT

> **Belum jadi keputusan final.** Sesuai CLAUDE.md, provider tidak boleh di-hardcode — semua integrasi lewat `backend/app/services/ai_providers/` (interface di `base.py`). Dokumen ini rekomendasi awal untuk didiskusikan dengan user; harga & kemampuan provider berubah cepat, **cek ulang harga/API terbaru saat mau implementasi aktual** (knowledge cutoff Januari 2026, sekarang sudah lewat beberapa bulan).

## 1. Image-to-Video

| Provider | Kekuatan | Kelemahan | Model Harga (indikatif, cek ulang) |
|---|---|---|---|
| **Runway (Gen-3/4)** | Kualitas motion tinggi, kontrol kamera bagus, API developer-friendly, dokumentasi matang | Lebih mahal per detik dibanding kompetitor baru | Credit-based, per detik video |
| **Kling AI** | Kualitas visual sangat kompetitif, image-to-video kuat untuk produk, harga umumnya lebih murah dari Runway | API resmi untuk pihak ketiga masih berkembang, dokumentasi bahasa Inggris kadang terbatas | Per-generation/credit |
| **Pika** | Cepat, murah, cocok short-form iterative | Konsistensi motion untuk produk kompleks kadang kurang stabil dibanding Runway/Kling | Subscription + credit |
| **Luma Dream Machine (Ray)** | Kualitas foto→video natural, bagus untuk shot produk | Harga per detik relatif tinggi di tier atas | Credit-based |
| **Google Veo (via Vertex AI/Gemini API)** | Kualitas top-tier, terintegrasi ekosistem Google Cloud (cocok kalau storage/infra lain juga GCP) | Akses API bisa butuh allowlist/kuota terbatas, harga enterprise-leaning | Per detik, tier Vertex AI |

**Rekomendasi awal:** mulai dengan **Runway** atau **Kling** sebagai provider pertama (dokumentasi API paling siap pakai untuk MVP, model harga jelas), diimplementasi di belakang interface `VideoGenerationProvider` sehingga bisa A/B / ganti provider tanpa ubah kode caller. Karena use case utama adVance.AI adalah **foto produk → video iklan pendek**, prioritaskan provider yang scoring bagus untuk *product shot consistency*, bukan cuma kualitas sinematik umum — perlu tes langsung dengan beberapa foto produk asli sebelum memutuskan.

## 2. Voice-over / TTS

| Provider | Kekuatan | Kelemahan |
|---|---|---|
| **ElevenLabs** | Kualitas suara paling natural di kelasnya, banyak pilihan suara/emosi, cloning suara tersedia | Harga per karakter lebih tinggi dari cloud TTS umum |
| **Google Cloud TTS** | Murah, terintegrasi kalau infra lain di GCP, cukup untuk voice-over fungsional | Kualitas ekspresif kalah dari ElevenLabs |
| **Azure TTS** | Bagus untuk multi-bahasa termasuk Bahasa Indonesia, harga kompetitif | Setup/akun Azure terpisah dari stack utama |

**Rekomendasi awal:** **ElevenLabs** untuk kualitas voice-over affiliate/iklan yang terdengar profesional (value proposition produk ini soal *kualitas setara tim kecil*) — kalau budget jadi kendala di awal, fallback ke Google/Azure TTS lewat interface yang sama.

## 3. Speech-to-Text (auto-caption)

- **Whisper (OpenAI)** — sesuai rekomendasi SDD §3.1. Bisa dipakai via OpenAI API (hosted, tanpa infra tambahan) atau self-hosted (`openai-whisper`/`faster-whisper`, butuh GPU untuk performa layak). Untuk MVP, **pakai OpenAI Whisper API (hosted)** dulu — hindari beban infra GPU sendiri di tahap awal; migrasi ke self-hosted kalau volume tinggi dan biaya API jadi masalah.

## Keputusan yang Perlu Dikonfirmasi User Sebelum Implementasi Phase 3 Penuh
- [ ] Provider image-to-video final: Runway / Kling / Pika / Luma / Veo — atau tetap generik multi-provider dari awal?
- [ ] Budget per video (menentukan provider mana yang feasible untuk margin biaya user).
- [ ] TTS: ElevenLabs vs Google/Azure — tergantung budget & bahasa (Indonesia perlu dicek kualitas suara tiap provider).
- [ ] Whisper: hosted API vs self-hosted.

**Sampai dikonfirmasi:** `AI_VIDEO_PROVIDER=mock` di `.env` — backend jalan dengan `MockVideoProvider` (lihat `backend/app/services/ai_providers/`) supaya alur end-to-end (upload → generate → edit → publish manual) tetap bisa dites tanpa API key asli.
