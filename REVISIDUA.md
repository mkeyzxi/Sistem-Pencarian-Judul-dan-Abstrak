# PROMPT PERBAIKAN: METADATA DARI NAMA FILE (BACKEND) & FITUR COPY (FRONTEND)

Bertindaklah sebagai Senior Fullstack Engineer (FastAPI & Vue.js). RAG Skripsi saya mengalami 2 masalah:

1. Backend kadang mengekstrak nama penulis dengan keliru (memasukkan gelar "Sarjana" dll). Padahal, nama file PDF sudah memiliki format yang sangat rapi: `TAHUN_NAMA_PENULIS.pdf` (contoh: `2023_RINI_AMALIAH.pdf`).
2. Frontend gagal menjalankan fitur "Salin Abstrak" karena referensi variabelnya keliru.

Selesaikan perbaikan ini dalam 2 fase:

### FASE 1: PERBAIKAN BACKEND (File `document_service.py`)

Fokus pada metode `load_documents_from_folder(folder_path)`.

- Ganti logika pengambilan `tahun` dan `nama`. JANGAN gunakan hasil ekstrak teks dari regex untuk `nama` jika format nama file sudah memenuhi standar.
- Ekstrak langsung dari nama `file` (variabel nama file PDF).
- Logika:
  1. Buang ekstensi `.pdf` (kasus abaikan / case-insensitive).
  2. Split string berdasarkan underscore `_`.
  3. Indeks pertama `parts[0]` pasti TAHUN.
  4. Gabungan indeks sisanya `" ".join(parts[1:])` pasti NAMA MAHASISWA. Jangan lupa gunakan `.title()` agar namanya menjadi huruf kapital di setiap awal kata (Contoh: "RINI AMALIAH" -> "Rini Amaliah").
- Timpa/Overwrite `doc_meta["nama"]` dan `doc_meta["tahun"]` menggunakan hasil ekstraksi dari nama file ini sebelum objek `Document` dibuat. Terapkan fallback ke regex lama HANYA jika nama file tidak mengandung underscore.

### FASE 2: PERBAIKAN FRONTEND (Komponen `MainChat.vue` / Card UI)

Fokus pada tombol "Salin Abstrak" di komponen Card UI.

- Saat ini tombol mencoba menyalin `doc.full_content || doc.content`. Padahal, backend RAG kita mengirimkan teks abstrak murni di dalam variabel `doc.page_content`.
- Buat sebuah fungsi di `<script setup>` bernama `copyToClipboard(text, event)` yang menggunakan `navigator.clipboard.writeText(text)`.
- Jika berhasil disalin, ubah teks tombol tersebut sementara menjadi "Tersalin!" (atau ganti iconnya menjadi `check`) selama 2 detik untuk memberikan visual feedback kepada user.
- Pastikan event `@click` pada tombol memanggil `copyToClipboard(doc.page_content, $event)`. DILARANG propagation event (gunakan `.stop` jika perlu).

Berikan saya revisi blok kode untuk `document_service.py` (khusus di bagian perulangan `for file in pdf_files:` sebelum pembuatan `Document`) dan revisi kode script/template Vue 3 untuk tombol Copy-nya.
