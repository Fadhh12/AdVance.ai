# DESIGN_SYSTEM.md — adVance.AI

Dokumen ini adalah arahan desain untuk adVance.AI, supaya hasilnya **tidak terlihat seperti template AI generik** (dashboard SaaS kartu-bulat generik, landing page cream+terracotta, dsb). Semua developer/AI agent yang mengerjakan UI proyek ini wajib mengacu ke sini, bukan ke selera "default" masing-masing.

---

## 1. Kenapa Desain Ini Perlu Sudut Pandang Sendiri

adVance.AI bukan "SaaS dashboard" generik — ia adalah **studio produksi virtual untuk satu orang**: dari bahan mentah (foto) sampai video siap tayang. Dunia sumbernya adalah **ruang edit video/broadcast**: timeline, status render, tally light rekam, preview multi-kanal. Bahasa visualnya harus terasa seperti "ruang kerja produksi", bukan seperti dashboard SaaS B2B pada umumnya (invoicing tool, CRM, dll).

**Audiens:** solo creator, pemilik UMKM, affiliate marketer — orang yang butuh alat kerja cepat dan jelas statusnya, bukan orang yang perlu di-"wow"-kan dengan animasi.

---

## 2. Yang Harus Dihindari (Anti-Slop Checklist)

Jangan pakai kombinasi ini kecuali benar-benar dipertimbangkan ulang dan ada alasan spesifik untuk brief ini:
- ❌ Background krem hangat (~#F4F1EA) + serif display kontras tinggi + aksen terracotta (~#D97757) — ini "tanda tangan" tampilan AI-generated, termasuk aksen khas Claude.
- ❌ Background hitam-pekat + satu aksen neon hijau/vermillion tunggal.
- ❌ Semua konten dipotong jadi kartu rounded identik, satu radius dipakai di semua elemen tanpa hierarki, shadow abu-abu lembut generik di bawah tiap kartu, gradient dekoratif tanpa fungsi.
- ❌ "Chrome" template: label eyebrow ALL-CAPS di atas tiap heading, meta info digabung titik tengah ("A · B · C"), label bergaya "WORD — fragment", angka 01/02/03 di konten yang sebenarnya bukan urutan, font monospace untuk label kecil tanpa alasan, tanda panah "→" ditempel di tiap tombol/link.
- ❌ Fade-slide-up di tiap section saat scroll, hover transition seragam di semua kartu — animasi generik yang muncul di mana-mana tanpa maksud.
- ❌ Menebalkan/italic/warna beda hanya pada satu kata dalam headline.

---

## 3. Palet Warna (Token)

Terinspirasi ruang edit video gelap (agar preview video enak dilihat, mata tidak silau) — tapi dengan aksen yang **bukan** neon-hijau atau terracotta generik.

| Token | Hex | Peran |
|---|---|---|
| `--bg-canvas` | `#12131A` | Latar utama workspace (biru-charcoal gelap, bukan hitam pekat #000/#111) |
| `--bg-panel` | `#1B1D28` | Panel/sidebar/card — sedikit lebih terang dari canvas |
| `--bg-panel-raised` | `#242637` | Elemen yang perlu menonjol dari panel (modal, dropdown aktif) |
| `--accent-rec` | `#E8A33D` | Aksen utama — "tally light" amber, dipakai untuk CTA utama & status "processing/live" |
| `--accent-signal` | `#4FBFAE` | Aksen sekunder — teal seperti waveform audio, dipakai untuk status sukses/published |
| `--accent-alert` | `#E2574C` | Status gagal/error — merah bata, bukan merah stop generik |
| `--text-primary` | `#EDEEF3` | Teks utama di atas latar gelap |
| `--text-muted` | `#8A8D9C` | Teks sekunder, label, timestamp |

Untuk halaman marketing (landing) yang butuh mode terang, gunakan `#F7F6F2` (putih hangat pudar, bukan krem #F4F1EA) sebagai background, dengan aksen `--accent-rec` tetap konsisten sebagai satu-satunya warna "berani".

---

## 4. Tipografi

- **Display/Headline:** gunakan grotesk yang agak *condensed* — misal **Archivo Expanded/Condensed**, **Space Grotesk**, atau **General Sans** — kesan "broadcast lower-third" (nama font yang muncul di siaran TV), bukan serif elegan generik.
- **Body/UI:** satu grotesk netral yang gampang dibaca di layar gelap — **Inter** boleh dipakai untuk UI (karena memang dioptimalkan untuk itu), tapi jangan dipakai juga sebagai display/headline supaya tidak terasa "default Inter semua".
- **Data/Angka (durasi video, quota, timestamp):** boleh pakai tabular figures dari font UI yang sama — **tidak perlu font monospace** kecuali menampilkan kode/log mentah.
- Hierarki: headline besar dan tegas (letter-spacing sedikit rapat, bukan tracking lebar ala eyebrow), body maksimal ~75 karakter per baris, label kecil pakai sentence case (bukan ALL CAPS).

---

## 5. Konsep Layout

### 5.1 Motif Utama: "Timeline Pipeline"
Karena alur produk memang benar-benar sekuensial (Upload → Generate → Edit → Publish), tampilkan sebagai **strip timeline horizontal** yang persisten di bagian atas workspace — bukan kartu 01/02/03 generik, tapi elemen fungsional yang menunjukkan posisi project saat ini secara real, mirip timeline editor video sungguhan.

```
[● Upload] ──── [◐ Generating…] ──── [○ Edit] ──── [○ Publish]
   selesai         sedang proses        belum          belum
```

### 5.2 Status pakai "Tally Light", bukan Badge Generik
Dot kecil berdenyut (pulse) warna `--accent-rec` untuk "processing", solid `--accent-signal` untuk "published/success", solid `--accent-alert` untuk "failed" — ditaruh presisi di depan nama item, bukan badge rounded penuh warna yang menumpuk jadi "confetti UI".

### 5.3 Dashboard: Bukan Grid Kartu Seragam
Media Library dan Content Calendar sebaiknya pakai **daftar/list dengan thumbnail video kecil di kiri + info di kanan** (mirip bin/media pool di software edit), bukan grid kartu rounded-shadow identik seperti produk SaaS pada umumnya. Reserve kartu besar hanya untuk item yang sedang aktif dikerjakan (1 fokus utama di layar, bukan semua item sama besar).

### 5.4 Preview Multi-Platform
Saat preview hasil ke 3 platform (IG/TikTok/YouTube), tampilkan **3 frame video 9:16 berjajar horizontal** dengan crop/caption masing-masing — device-frame minimalis tipis, bukan mockup HP 3D dekoratif.

---

## 6. Gerakan (Motion)

Satu momen animasi yang disengaja: **transisi status di timeline pipeline** saat sebuah tahap selesai (dot berubah dari pulsing amber → solid teal, dengan easing halus). Selain itu, motion hanya untuk merespons aksi user (buka panel, expand preview, konfirmasi publish) — bukan scroll-reveal di tiap section landing page.

---

## 7. Gaya Penulisan (Microcopy)

- Bahasa aktif, sesuai aksi: tombol bertuliskan "Generate video", bukan "Submit"; toast setelah sukses bertuliskan "Video berhasil dibuat" — konsisten dengan nama aksinya.
- Status/error bicara dari sudut pandang sistem, jelas dan actionable: *"Token Instagram kadaluarsa — sambungkan ulang"* (dengan tombol langsung), bukan *"Terjadi kesalahan (Error 401)"*.
- Empty state mengarahkan aksi berikutnya: *"Belum ada video. Upload foto pertamamu untuk mulai."* — bukan sekadar ilustrasi kosong.
- Hindari bahasa jualan berlebihan di UI produk (beda dengan landing page) — di dalam workspace, bahasa harus fungsional dan jujur soal status.

---

## 8. Checklist Sebelum Ship UI Apa Pun

- [ ] Apakah kombinasi warna ini benar-benar dipilih untuk adVance.AI, atau ini "default" yang akan sama untuk brief apa pun?
- [ ] Apakah ada label ALL-CAPS/eyebrow/angka 01-02-03 yang dipakai bukan karena kontennya memang urutan?
- [ ] Apakah semua kartu punya radius & shadow identik tanpa alasan hierarki?
- [ ] Apakah animasi yang dipakai merespons aksi user, atau sekadar scroll-reveal generik?
- [ ] Apakah microcopy menyebut aksi dengan nama yang sama dari tombol sampai notifikasi hasil?
