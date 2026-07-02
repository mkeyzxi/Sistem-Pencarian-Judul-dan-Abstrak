# DESIGN.md — Redesign Antarmuka Sistem Pencarian Skripsi (RAG vs HyDE)

**Codename:** Laci Katalog — _Digital Card Catalog_
**Versi:** 1.0
**Status:** Draft desain — siap diimplementasikan

---

## 1. Ringkasan & Latar Belakang

Sistem saat ini menampilkan hasil pencarian dalam bentuk **chatbot** (bubble percakapan), padahal secara fungsional ini bukan chatbot — ini adalah **mesin pencari akademik** yang membandingkan dua strategi retrieval (Standard RAG vs HyDE) terhadap koleksi judul & abstrak skripsi.

Masalah dengan tampilan chatbot untuk kasus ini:

- Bubble chat menyembunyikan struktur hasil (skor, metode, rank) di balik teks naratif.
- Chatbot menyiratkan _percakapan satu arah berurutan_, padahal yang sebenarnya terjadi adalah **pencarian → daftar hasil terstruktur** yang idealnya bisa dibandingkan berdampingan.
- Sulit menonjolkan perbedaan hasil RAG vs HyDE — dua hal yang justru menjadi inti dari skripsi ini.

**Keputusan desain besar:** buang total metafora chatbot. Ganti dengan metafora **laci katalog perpustakaan digital** — satu bidang pencarian seperti "slip pencarian", hasil ditampilkan sebagai **kartu indeks (index card)** yang bisa dibandingkan berdampingan antara laci RAG dan laci HyDE, lengkap dengan elemen khas katalog: nomor panggil, stempel relevansi, dan label metode.

Ini bukan sekadar tema visual — strukturnya secara langsung merepresentasikan apa yang sedang dievaluasi: dua metode retrieval, dibandingkan berdampingan, per query.

---

## 2. Filosofi Desain

1. **Pencarian, bukan percakapan.** Tidak ada bubble, tidak ada avatar, tidak ada "typing indicator" ala chat. Yang ada: input pencarian → grid hasil.
2. **Perbandingan adalah warga kelas satu.** RAG dan HyDE harus selalu bisa dilihat berdampingan, bukan bergantian di satu thread.
3. **Kejujuran data.** Skor kemiripan, latency, dan rank ditampilkan apa adanya — desain tidak boleh menyembunyikan angka yang menjadi inti evaluasi skripsi ini.
4. **Minimalis dengan kepribadian.** Minimalis bukan berarti generik. Satu elemen signature (kartu indeks bertekstur + stempel relevansi) menjadi identitas visual yang tidak akan tertukar dengan produk lain.
5. **Presisi akademik.** Tipografi, spacing, dan angka disusun rapi seperti dokumen ilmiah — bukan playful, bukan corporate SaaS generik.

---

## 3. Sistem Token Desain

### 3.1 Palet Warna

Terinspirasi dari kertas manila folder arsip dan tinta stempel perpustakaan lama — bukan cream+serif+terracotta yang sudah terlalu umum dipakai desain AI-generated, dan bukan juga tema gelap generik.

| Token                  | Hex       | Penggunaan                                               |
| ---------------------- | --------- | -------------------------------------------------------- |
| `--color-kraft-bg`     | `#EDE6D6` | Latar belakang utama (warna kertas kraft/manila)         |
| `--color-card-surface` | `#FFFDF8` | Permukaan kartu indeks & elemen terangkat                |
| `--color-ink`          | `#1B2432` | Teks utama, judul (tinta gelap hampir hitam-navy)        |
| `--color-ink-muted`    | `#5C6472` | Teks sekunder, metadata, caption                         |
| `--color-stamp-red`    | `#B5432B` | Aksen utama: skor relevansi tinggi, CTA, highlight aktif |
| `--color-index-teal`   | `#2F6E5D` | Label metode HyDE, aksen sekunder, status sukses         |
| `--color-rule`         | `#C9C0AC` | Garis pembatas, perforasi kartu, border tipis            |
| `--color-rag-tag`      | `#4A5A8C` | Label metode Standard RAG (biru arsip/dusty navy)        |

> Catatan: `stamp-red` dipakai **sangat sedikit** — hanya untuk elemen yang benar-benar butuh perhatian (skor tertinggi, tombol utama). Ini bukan warna dekoratif.

### 3.2 Tipografi

Dua peran font yang sengaja kontras dengan pasangan serif+sans yang umum dipakai:

| Peran                               | Font                                   | Alasan                                                                                                       |
| ----------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Display / Judul & Label Katalog** | `JetBrains Mono` (700/500)             | Meniru mesin tik pada kartu katalog lama — memberi nuansa "arsip terindeks" tanpa jatuh ke klise serif mewah |
| **Body / Konten & Abstrak**         | `Inter` (400/500)                      | Sans humanis, sangat terbaca untuk teks panjang (abstrak skripsi)                                            |
| **Utility / Angka & Metadata**      | `IBM Plex Mono` (400, tabular numbers) | Skor, latency, rank, nomor panggil — angka harus sejajar rapi                                                |

**Skala tipe:**

```
Display XL   36px / 44px   JetBrains Mono 700   — Judul halaman
Display M    22px / 28px   JetBrains Mono 600   — Judul kartu hasil
Body L       16px / 26px   Inter 400            — Abstrak, deskripsi
Body M       14px / 22px   Inter 400            — Teks umum UI
Label        11px / 14px   JetBrains Mono 500   — Label kategori (UPPERCASE, letter-spacing 0.06em)
Mono Data    13px / 18px   IBM Plex Mono 400    — Skor, latency, ID
```

### 3.3 Layout Concept

Bukan drawer chat vertikal — melainkan **dua laci berdampingan** (desktop) yang bisa ditumpuk (mobile).

```
DESKTOP (≥1024px)
┌──────────────────────────────────────────────────────────────┐
│  LACI KATALOG           [query: "sistem rekomendasi..."]  🔍  │  ← search slip
├──────────────────────────────────────────────────────────────┤
│  LACI A — STANDARD RAG      │   LACI B — HYDE                │
│  ┌────────────────────┐     │   ┌────────────────────┐       │
│  │ ⌐ kartu indeks #1  │     │   │ ⌐ kartu indeks #1  │       │
│  │ skor 0.842  ⧉RAG   │     │   │ skor 0.891  ⧉HyDE  │       │
│  └────────────────────┘     │   └────────────────────┘       │
│  ┌────────────────────┐     │   ┌────────────────────┐       │
│  │ ⌐ kartu indeks #2  │     │   │ ⌐ kartu indeks #2  │       │
│  └────────────────────┘     │   └────────────────────┘       │
│  ...                        │   ...                          │
├──────────────────────────────────────────────────────────────┤
│  ringkasan metrik: Hit@5 · MRR · Latency rata-rata (footer)   │
└──────────────────────────────────────────────────────────────┘

MOBILE (<768px)
┌───────────────────────┐
│  [query...........] 🔍│
├───────────────────────┤
│  [ RAG ] [ HyDE ]  ← tab pemisah laci (bukan dropdown)
├───────────────────────┤
│  ⌐ kartu indeks #1    │
│  ⌐ kartu indeks #2    │
│  ...                  │
└───────────────────────┘
```

### 3.4 Signature Element — Kartu Indeks (Index Card)

Elemen paling khas & satu-satunya tempat "keberanian visual" dihabiskan:

- Bentuk kartu meniru kartu katalog fisik: sudut sedikit membulat (2px), tepi kiri bergaris tebal 3px sesuai warna metode (biru = RAG, teal = HyDE).
- Pojok kanan atas ada **"stempel" skor relevansi** — lingkaran/oval tipis berputar -6°, seperti stempel tanggal kembali buku perpustakaan, berisi angka skor (contoh: `0.891`). Warna stempel merah (`stamp-red`) hanya jika skor termasuk 1 tertinggi di antara hasil yang ditampilkan.
- Nomor panggil sintetis di pojok kiri bawah, format mono: `TI.2024.0142` (disusun dari tahun + hash id dokumen) — memberi rasa "terindeks", bukan sekadar list hasil generik.
- Garis putus-putus horizontal tipis (meniru garis perforasi kartu) memisahkan judul dari cuplikan abstrak.

Ini satu-satunya dekorasi yang diperbolehkan mencolok. Semua elemen lain (search bar, tab, footer) tetap datar dan tenang.

---

## 4. Spesifikasi Komponen

### 4.1 Search Slip (Pengganti Input Chat)

- Satu baris input lebar penuh, background `--color-card-surface`, border bawah tebal 2px `--color-ink` (bukan border penuh kotak — meniru garis tanda tangan di slip kertas).
- Placeholder: `Cari judul, topik, atau kata kunci skripsi…`
- Tidak ada bubble "Anda: ..." setelah submit. Query yang aktif ditampilkan sebagai **label kecil di atas hasil**, format: `HASIL UNTUK "sistem rekomendasi berbasis konten"` (mono, uppercase, label style).
- Tombol cari: ikon kaca pembesar sederhana, tanpa gradient, warna `--color-ink`, berubah `--color-stamp-red` saat hover.
- Tidak ada riwayat percakapan menumpuk ke bawah. Setiap pencarian baru **mengganti** tampilan hasil (state pencarian tunggal), sesuai sifat sistem retrieval — bukan histori obrolan.

### 4.2 Toggle Laci (Method Switch — Mobile) / Kolom Ganda (Desktop)

- Desktop: dua kolom tetap terlihat bersamaan, masing-masing berjudul `LACI A — STANDARD RAG` dan `LACI B — HYDE`, dipisah garis vertikal putus-putus `--color-rule`.
- Mobile: dua tab berdampingan gaya "label folder gantung" (bukan pill rounded generik) — bentuk trapesium kecil di atas, aktif = terangkat & warna solid metode; nonaktif = warna kraft pudar.
- Opsional (power-user): toggle "Overlay" yang menumpuk kedua laci jadi satu daftar terurut skor, dengan badge warna metode di tiap kartu — untuk analisis cepat mana yang menang per query.

### 4.3 Kartu Indeks (Result Card)

Struktur konten per kartu, top to bottom:

1. **Baris label metode + rank** — mono kecil, contoh: `RAG · #1`
2. **Judul skripsi** — Display M, maksimal 2 baris, ellipsis jika lebih panjang
3. **Metadata baris tipis** — penulis · tahun · program studi (Body M, `--color-ink-muted`)
4. **Garis perforasi** (dashed, 1px, `--color-rule`)
5. **Cuplikan abstrak** — Body M, maksimal 3 baris, kata kunci hasil highlight tipis (underline, bukan background block mencolok)
6. **Footer kartu**: skor relevansi (stempel), latency retrieval (mono kecil, opsional expand), tombol "Lihat detail →"

State interaksi:

- **Hover**: kartu terangkat 4px (`box-shadow` halus, bukan glow), miring 0.5° seperti diangkat tangan.
- **Klik "Lihat detail"**: buka panel slide-in dari kanan (bukan modal tengah generik) berisi abstrak penuh, metadata lengkap, dan breakdown skor per komponen (jika ada).

### 4.4 Ringkasan Metrik (Footer Perbandingan)

Ditampilkan sebagai strip tipis di bawah hasil, bukan dashboard terpisah — supaya konteks evaluasi selalu terlihat saat membandingkan:

```
Hit@5   RAG 0.78  ·  HyDE 0.84        MRR   RAG 0.61 · HyDE 0.69        Latency avg   RAG 412ms · HyDE 890ms
```

- Format mono, tabular, dengan metode pemenang per metrik ditandai underline `--color-stamp-red`, bukan warna latar block.
- Bisa diklik untuk expand ke tabel metrik lengkap (Precision@K dsb.) dalam panel slide-up.

### 4.5 Empty, Loading, Error States

- **Loading**: kartu skeleton meniru bentuk kartu indeks (bukan spinner generik) — garis-garis tipis muncul berurutan seolah kartu sedang "ditarik dari laci", durasi singkat (~400–600ms), stagger 60ms antar kartu.
- **Empty (belum ada pencarian)**: ilustrasi minimal garis (laci kosong terbuka), teks: `Laci masih kosong — mulai ketik untuk mencari skripsi.`
- **Empty (hasil tidak ditemukan)**: `Tidak ada kartu yang cocok untuk pencarian ini. Coba kata kunci lain atau periksa ejaan.` — nada lugas, bukan permintaan maaf berlebihan.
- **Error (LLM/API gagal)**: kartu tunggal warna `--color-stamp-red` tipis di border: `Pencarian gagal diproses. Coba lagi dalam beberapa saat.` + tombol "Coba lagi".

---

## 5. Interaksi & Motion

Motion dipakai untuk memperkuat metafora katalog, bukan hiasan random:

| Momen                | Animasi                                                                                                               |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Submit pencarian     | Search slip sedikit "menekan" (scale 0.98 → 1), lalu kartu-kartu lama fade-out cepat (150ms) sebelum kartu baru masuk |
| Kartu hasil muncul   | Slide-up 8px + fade-in, stagger 60ms per kartu (maks 6 kartu pertama distagger, sisanya langsung)                     |
| Hover kartu          | Elevasi halus + rotasi 0.5° (transform saja, tidak reflow)                                                            |
| Buka detail          | Panel slide-in dari kanan, 220ms, easing standar (ease-out)                                                           |
| Toggle laci (mobile) | Konten laci fade+slide horizontal 150ms searah tab yang dipilih                                                       |

**Prinsip:** satu momen terorkestrasi (kartu muncul dari "laci") lebih berarti daripada animasi bertebaran di semua elemen. Hormati `prefers-reduced-motion` — semua transisi di atas fallback ke fade sederhana 100ms.

---

## 6. Responsif

| Breakpoint            | Perilaku                                                                             |
| --------------------- | ------------------------------------------------------------------------------------ |
| `≥1024px` (desktop)   | Dua laci berdampingan, footer metrik full-width                                      |
| `768–1023px` (tablet) | Dua laci berdampingan tapi kartu 1 kolom per laci, font sedikit diperkecil           |
| `<768px` (mobile)     | Tab switch RAG/HyDE, satu kolom kartu, footer metrik jadi carousel horizontal scroll |

---

## 7. Aksesibilitas

- Kontras teks `--color-ink` di atas `--color-kraft-bg` ≥ 7:1 (AA/AAA aman).
- Semua kartu fokus dengan outline keyboard jelas (2px `--color-stamp-red`, offset 2px) — bukan hanya mengandalkan hover.
- Label metode (RAG/HyDE) tidak hanya dibedakan warna — selalu disertai teks label, agar tidak bergantung pada persepsi warna.
- Stempel skor punya `aria-label` deskriptif: `Skor relevansi 0.891 dari 1`.
- Animasi menghormati `prefers-reduced-motion: reduce`.
- Struktur heading semantik: `h1` judul halaman, `h2` per laci (RAG/HyDE), `h3` judul tiap kartu.

---

## 8. Catatan Implementasi Teknis

Mengikuti stack yang biasa dipakai (Next.js App Router + Tailwind + Framer Motion):

- Definisikan token warna & font di atas sebagai CSS variables di `globals.css`, lalu extend `tailwind.config` supaya bisa dipakai sebagai utility (`bg-kraft`, `text-ink`, `border-rule`, dst).
- Font: load `JetBrains Mono`, `Inter`, `IBM Plex Mono` via `next/font/google` untuk performa.
- Komponen disarankan:
  - `SearchSlip.tsx` — input + label query aktif
  - `CatalogDrawer.tsx` — wrapper 2 kolom (desktop) / tab switch (mobile)
  - `IndexCard.tsx` — kartu hasil (props: title, author, year, snippet, score, method, rank, latency)
  - `MetricStrip.tsx` — footer ringkasan metrik
  - `DetailPanel.tsx` — slide-in panel detail
- Data skor & metrik tetap dari backend FastAPI/ChromaDB yang sudah ada — desain ini murni lapisan presentasi, tidak mengubah kontrak API. Field tambahan yang dibutuhkan UI: `rank`, `latency_ms` per hasil (jika belum ada di response, tambahkan di endpoint evaluasi/pencarian).
- Gunakan Framer Motion `layout` + `AnimatePresence` untuk transisi ganti hasil pencarian (fade-out lama → fade-in baru).

---

## 9. Yang Sengaja Dihindari

- ❌ Bubble chat & avatar — menyiratkan percakapan, bukan pencarian terstruktur.
- ❌ "Typing indicator" / efek mengetik huruf-per-huruf — tidak relevan untuk hasil yang sudah terkomputasi.
- ❌ Gradient dekoratif besar, glassmorphism, atau warna neon — bertentangan dengan nuansa akademik/arsip yang diinginkan.
- ❌ Angka 01/02/03 sebagai penomoran dekoratif tanpa makna urutan nyata (rank hasil memang berurutan, jadi ini dipakai apa adanya sebagai rank, bukan sebagai hiasan section).

---

## 10. Ringkasan Copy / Microcopy

| Konteks               | Teks                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------ |
| Placeholder pencarian | `Cari judul, topik, atau kata kunci skripsi…`                                              |
| Label hasil aktif     | `HASIL UNTUK "…"`                                                                          |
| Judul laci            | `LACI A — STANDARD RAG` / `LACI B — HYDE`                                                  |
| Tombol detail         | `Lihat detail →`                                                                           |
| Empty awal            | `Laci masih kosong — mulai ketik untuk mencari skripsi.`                                   |
| Empty hasil kosong    | `Tidak ada kartu yang cocok untuk pencarian ini. Coba kata kunci lain atau periksa ejaan.` |
| Error                 | `Pencarian gagal diproses. Coba lagi dalam beberapa saat.` + tombol `Coba lagi`            |

---

_Dokumen ini adalah spesifikasi desain, siap dipakai sebagai acuan implementasi frontend (Next.js/Tailwind/Framer Motion) tanpa mengubah backend RAG/HyDE yang sudah ada._
