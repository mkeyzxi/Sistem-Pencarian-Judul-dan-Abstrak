# Design System & UI Improvement

## Chatbot Skripsi Teknik Informatika

Dokumen ini berfungsi sebagai **panduan desain (design guideline)** untuk memperbaiki tampilan UI/UX aplikasi *Chatbot Skripsi Teknik Informatika*. Fokus utama: **lebih rapi, lebih bernapas, lebih akademik namun tetap ramah**, serta **sidebar yang muncul dari kiri (slide-in)**.

---

## 1. Masalah Visual Saat Ini (Observasi Jujur)

Berdasarkan tampilan saat ini:

* UI **terlalu gelap dan padat**, kurang ruang napas
* Hierarki visual belum tegas (judul, isi, aksi terasa sejajar)
* Area tengah terasa kosong namun berat
* Sidebar terasa permanen → kurang fleksibel
* Chat belum terasa sebagai *fokus utama*

Tujuan perbaikan:

> *Mengubah kesan dari “panel sistem” menjadi “ruang dialog akademik”.*

---

## 2. Prinsip Desain Utama

Gunakan 5 prinsip ini sebagai kompas desain:

1. **Focus First** – Chat adalah pusat segalanya
2. **Academic Calm** – Tenang, tidak mencolok
3. **Readable Always** – Teks > dekorasi
4. **Progressive Disclosure** – Kontrol muncul saat dibutuhkan
5. **Mobile & Small Screen Aware** – Sidebar tidak selalu terlihat

---

## 3. Struktur Layout Final (1 Page)

```
┌───────────────────────────────┐
│ Header (fixed, slim)          │
├───────────────────────────────┤
│                               │
│   Main Chat Area (focus)      │
│                               │
├───────────────────────────────┤
│ Input Chat (sticky bottom)   │
└───────────────────────────────┘

Sidebar → hidden by default
Appears from LEFT when toggled
```

Sidebar **bukan layout utama**, tapi **overlay drawer**.

---

## 4. Sidebar (Drawer dari Kiri)

### 4.1 Perilaku Sidebar

* Posisi: `fixed left`
* Default: **hidden**
* Muncul dengan animasi `translateX(-100%) → 0`
* Background overlay semi-transparan

**Trigger:**

* Tombol ☰ di Header
* Shortcut (opsional): `Ctrl + B`

### 4.2 Isi Sidebar (Urutan Wajib)

1. **Identitas Sistem**

   * Logo kecil
   * Nama sistem

2. **Tombol Obrolan Baru**

   * Primary button
   * Ikon + teks

3. **Mode Pencarian**

   * RAG (default)
   * HyDE
   * Deskripsi singkat di bawah toggle

4. **Riwayat Obrolan**

   * List sederhana
   * Aktif chat → highlight
   * Hover actions (hapus)

---

## 5. Header (Lebih Tipis, Lebih Tenang)

### Spesifikasi

* Tinggi: 56–64px
* Posisi: fixed
* Background: gelap solid (tanpa gradasi)

### Isi Header

Kiri:

* ☰ Toggle Sidebar
* Judul: *Chatbot Skripsi TI*

Kanan:

* Status sistem (Online)
* Mode aktif (RAG / HyDE)

> Header hanya sebagai penunjuk arah, bukan pusat perhatian.

---

## 6. Area Chat Utama

### 6.1 Empty State (Sangat Penting)

Saat belum ada chat:

* Icon besar (ringan)
* Judul: *Selamat Datang*
* Subteks: penjelasan singkat
* Contoh prompt (chip / card)

Gunakan **vertical center**, jangan rata atas.

---

### 6.2 Bubble Chat

#### User Message

* Posisi: kanan
* Warna: hijau tua lembut
* Border radius besar

#### Bot Message

* Posisi: kiri
* Warna: abu / hijau sangat muda
* Konten terstruktur:

  * Judul
  * Abstrak ringkas
  * Metadata (tahun, bidang)

Gunakan **max-width 70%** agar mudah dibaca.

---

## 7. Input Chat Area

### Spesifikasi

* Posisi: sticky bottom
* Tinggi: ±72px
* Background solid (kontras ringan)

### Isi

* Textarea auto-grow
* Placeholder edukatif
* Tombol kirim jelas

Opsional:

* Enter = kirim
* Shift+Enter = baris baru

---

## 8. Warna & Mood

### Palet Utama

* Hijau tua → identitas & amanah
* Putih / abu terang → ruang napas
* Oranye kecil → aksi (optional)

### Aturan

* ❌ Jangan terlalu banyak gradasi
* ❌ Jangan hijau terlalu gelap di area teks
* ✅ Prioritaskan kontras teks

---

## 9. Tipografi

### Hierarki

* Judul halaman → font besar, tegas
* Konten chat → normal, readable
* Metadata → kecil & muted

Gunakan **sans-serif modern** dengan rounded feel.

---

## 10. Animasi (Halus & Fungsional)

* Sidebar slide-in: 200–300ms
* Hover state: opacity / background
* ❌ Hindari animasi berlebihan

Animasi hanya untuk **membantu orientasi**, bukan pamer.

---

## 11. Komponen yang Perlu Disesuaikan

Prioritas refactor:

1. `Sidebar.vue` → Drawer
2. `Header.vue` → lebih slim
3. `ChatArea.vue` → max-width & spacing
4. `InputArea.vue` → sticky & clean
5. `TheWelcome.vue` → empty state fokus

---

## 12. Rasa Akhir yang Diharapkan

Ketika mahasiswa membuka aplikasi ini, yang dirasakan:

> “Tenang. Fokus. Saya bisa cari skripsi tanpa stres.”

Bukan seperti dashboard admin.
Bukan seperti chatbot main-main.

Tapi seperti **perpustakaan digital yang bisa diajak bicara**.

---

*Dokumen ini adalah fondasi. Desain boleh berkembang, tapi prinsipnya jangan runtuh.*
