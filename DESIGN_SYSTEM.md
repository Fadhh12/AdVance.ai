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
[📤 Upload] ╾╌╮  ╭╌╾[✨ Generate] ╾╌╮  ╭╌╾[✂ Edit] ╾╌╮  ╭╌╾[🚀 Publish]
   selesai       sedang proses          belum            belum
```

Tiap node punya **ikon fungsional + nama tahap** (bukan cuma dot polos), dihubungkan
**kabel melengkung** (bezier, seperti patch cable ruang broadcast) — bukan garis lurus
datar (`pipeline-connector.tsx`). Ini beda dengan canvas node ala automation-tool
generik (n8n/Zapier): tetap linear sesuai alur produk asli, tidak ada kotak melayang
bebas, tidak ada avatar bot, tidak ada percabangan yang dipalsukan.

Sebuah node **tambahan** boleh muncul di antara node inti kalau project memang benar-
benar memakainya (mis. node "Motion: <nama preset>" muncul hanya kalau
`project.motion_preset` terisi) — jangan tambahkan node dekoratif yang tidak
mencerminkan state asli. Tahap **Publish** boleh bercabang jadi beberapa node kecil di
bawahnya, satu per platform (`PipelineBranch`), begitu `posts` untuk project itu sudah
disiapkan — cabang ini nyata dari data (satu `Post` per platform), bukan diagram
keputusan if/else yang dikarang.

### 5.2 Status pakai "Tally Light", bukan Badge Generik
Dot kecil berdenyut (pulse) warna `--accent-rec` untuk "processing", solid `--accent-signal` untuk "published/success", solid `--accent-alert` untuk "failed" — ditaruh presisi di depan nama item, bukan badge rounded penuh warna yang menumpuk jadi "confetti UI".

### 5.3 Dashboard: Bukan Grid Kartu Seragam
Media Library dan Content Calendar sebaiknya pakai **daftar/list dengan thumbnail video kecil di kiri + info di kanan** (mirip bin/media pool di software edit), bukan grid kartu rounded-shadow identik seperti produk SaaS pada umumnya. Reserve kartu besar hanya untuk item yang sedang aktif dikerjakan (1 fokus utama di layar, bukan semua item sama besar).

### 5.4 Preview Multi-Platform
Saat preview hasil ke 3 platform (IG/TikTok/YouTube), tampilkan **3 frame video 9:16 berjajar horizontal** dengan crop/caption masing-masing — device-frame minimalis tipis, bukan mockup HP 3D dekoratif.

---

### 5.5 Halaman Marketing Publik (Phase 6R-7)

Landing page publik (`/`) pakai tema terang: `bg-paper` (`#F7F6F2`) sebagai
background, dengan `--color-paper-ink` (`#1B1D28`) dan `--color-paper-ink-muted`
(`#5B5E6E`) sebagai token teks khusus tema terang ini — **jangan** pakai `text-ink`/
`text-ink-muted` di atas `bg-paper`, keduanya dituning untuk latar gelap dan nyaris
tidak terbaca di atas latar terang (kontras gagal WCAG AA).

Pola yang dipakai:
- Nav sticky (`bg-paper/90 backdrop-blur`), anchor link dalam satu halaman (bukan
  halaman terpisah) — landing page tetap satu halaman panjang, sama seperti
  workspace satu-canvas.
- Hero pakai `PhoneFrame` (sudah ada, `ui/phone-frame.tsx`) berisi mockup UI abstrak
  (bentuk play button + pill caption) — **bukan** mockup akun media sosial dengan
  username/foto profil/angka like-comment fiktif. Itu adalah social proof palsu,
  dilarang di materi publik manapun.
- Section "cara kerja" me-reuse `TimelinePipeline`/`TallyDot` yang sama persis
  dipakai di workspace (di dalam panel gelap `bg-canvas`/`bg-panel-raised` sebagai
  "jendela" produk asli di tengah halaman terang) — bukan ilustrasi terpisah yang
  diciptakan khusus untuk marketing.
- **Tidak ada** section testimoni/nama pelanggan, tidak ada tabel harga dengan tier
  yang belum benar-benar ada (cek `Plan` di backend dulu sebelum menulis harga apa
  pun), tidak ada nama fitur yang belum dibangun (cek
  `adVance-AI-Spesifikasi-Proyek.md` dan `PROGRESS.md` dulu).
- Badge/klaim dukungan model AI pihak ketiga (mis. "Google Veo", "Seedance") harus
  mencerminkan status implementasi ASLI — pakai kata kerja roadmap ("dirancang untuk
  mendukung", "segera") kalau providernya belum benar-benar disambungkan
  (`get_video_provider()` masih return provider lain), jangan "Didukung oleh" yang
  menyiratkan sudah aktif.

### 5.6 Pengecualian §5.3 untuk Galeri Konten/Template

§5.3 melarang "grid kartu seragam" untuk **dashboard data** (Media Library, Content
Calendar) karena semua item di situ setara pentingnya — list lebih jujur. Tapi
**galeri template/konten** (dashboard hub, lihat `dashboard/page.tsx`) boleh berupa
grid dengan cover art, karena secara fungsi memang mirip pustaka aset visual (stock
footage library), bukan data operasional. Syaratnya:
- Cover art tidak boleh seragam shadow/radius generik tanpa hierarki — variasi warna
  gradient per item boleh (asal dari token warna kita sendiri, bukan foto stok/AI-
  generated image acak), dan ukuran kartu bisa berbeda berdasarkan hierarki (kartu
  "Buat Baru" lebih besar dari kartu template).
- Kalau jumlah item masih sedikit (di bawah ~10), jangan tambah chrome pencarian/
  filter kategori yang keliatan kosong — itu lebih AI-slop daripada grid sederhana.
  Tambahkan filter cuma kalau datanya sudah cukup banyak untuk benar-benar berguna.

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
