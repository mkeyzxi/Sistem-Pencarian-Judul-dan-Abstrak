# PROMPT PERBAIKAN BACKEND RAG: EKSTRAKSI & SKORING

Bertindaklah sebagai Senior Backend Engineer yang ahli dalam NLP dan Information Retrieval (LangChain & FastAPI). Sistem RAG Skripsi saya mengalami dua kecacatan logika fatal yang harus Anda perbaiki sekarang juga.

## MASALAH 1: Kalkulasi Skor Relevansi Selalu 0%

Saat melakukan pencarian (Standard RAG maupun HyDE) menggunakan ChromaDB, nilai `distance` tidak dikonversi dengan benar, sehingga frontend menerima skor 0 atau format yang salah.
**TUGAS 1:**
Perbaiki fungsi retrieval (misal: `retrieve_standard_rag` dan `retrieve_hyde`). Tangkap nilai `distance` dari `similarity_search_with_score`.
Konversi menjadi persentase dengan rumus `similarity_score = round((1.0 - distance) * 100, 2)`. Pastikan nilai ini masuk ke dalam `doc.metadata['similarity_score']` agar terbaca oleh frontend. Dilarang mereturn nilai 0 jika dokumen memang ditemukan.

## MASALAH 2: Sampah Metadata di Badan Abstrak (Garbage In, Garbage Out)

Fungsi ekstraksi PDF saat ini menangkap semua teks setelah kata "ABSTRAK". Akibatnya, format identitas (Judul, Nama, NIM, Pembimbing 1, Pembimbing 2) yang sering ditulis ulang oleh mahasiswa di halaman abstrak ikut masuk menjadi vektor dan merusak tampilan frontend.
**TUGAS 2:**
Tulis ulang fungsi `extract_metadata_and_abstract(text)`. Buat logika ekstraksi yang **fault-tolerant** (tahan banting) dengan alur berikut:

1. **Ekstraksi Fleksibel:** Gunakan Regex untuk mengekstrak entitas berikut dari halaman PDF (jika tidak ada, kembalikan string "Tidak diketahui" / None, jangan sampai error):
   - `Judul`: Ambil dari halaman pertama atau awal halaman abstrak.
   - `Nama Mahasiswa`: Cari pola "Nama[:\s]" atau "Nama Penulis[:\s]".
   - `NIM`: Cari pola "NIM[:\s]".
   - `Pembimbing`: Cari pola "Pembimbing 1" dan "Pembimbing 2", atau sekadar "Pembimbing[:\s]".

2. **Pembersihan Ekstrem (Scrubbing):**
   Setelah variabel metadata di atas berhasil diekstrak (atau tidak ditemukan), **HAPUS/STRIP** teks-teks identitas tersebut dari string `raw_abstract`.
3. **Pencarian Titik Awal Abstrak yang Sebenarnya:**
   Cari di mana esai abstrak benar-benar dimulai. Biasanya dimulai dengan kalimat yang mengandung kata-kata seperti: _"Penelitian ini"_, _"Masalah yang melatarbelakangi"_, _"Kemajuan teknologi"_, _"Tujuan dari"_, dll. Buang semua teks sampah sebelum titik mula ini.

4. **Sanitasi Paragraf:**
   PDF sering memutus kalimat dengan `\n`. Ubah `\n` tunggal menjadi spasi `" "`. Pertahankan `\n\n` ganda sebagai paragraf baru. Hapus spasi ganda.

**HASIL AKHIR YANG DIHARAPKAN (RETURN OBJECT):**
Keluarkan dictionary atau struktur data yang sangat rapi untuk disimpan ke dalam `ChromaDB metadata` dan payload API, formatnya:

```json
{
  "page_content": "[MURNI ESAI ABSTRAK, TANPA NAMA, TANPA NIM, TANPA KATA PEMBIMBING]",
  "metadata": {
    "source": "nama_file.pdf",
    "judul": "Judul Skripsi...",
    "nama": "Nama Penulis",
    "nim": "123456",
    "pembimbing": "Nama Dosen 1 & Nama Dosen 2",
    "tahun": 2024,
    "similarity_score": 85.5
  }
}
```
