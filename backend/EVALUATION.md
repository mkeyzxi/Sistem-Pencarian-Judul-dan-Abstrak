# EVALUATION.md — Sistem Evaluasi Chatbot Pencarian Skripsi

Dokumen ini mendefinisikan skenario, desain query, arsitektur, parameter generatif HyDE, parameter ruang vektor, dan kriteria relevansi yang digunakan dalam evaluasi perbandingan **Standard RAG vs. HyDE (Prompt 1 vs. Prompt 2)** secara lokal.

---

## 1. Skenario & Desain Query Uji

### Sumber Query
Sebanyak **50 query** disusun secara sintetis berdasarkan topik skripsi Teknik Informatika pada repositori UIN Alauddin Makassar. 

### Alasan Menggunakan Query Sintetis
Belum tersedia data riwayat pencarian pengguna yang terstruktur secara langsung. Oleh karena itu, query sintetis digunakan untuk menghasilkan variasi kondisi pencarian yang terkontrol, representatif, dan mencakup berbagai tingkat kompleksitas pencarian.

### Karakteristik Query
Seluruh query dirancang sebagai **query pendek**, yang didefinisikan secara ketat sebagai query dengan panjang **1–5 kata**. Batasan ini mencerminkan kebiasaan pencarian pengguna riil pada sistem pencarian dokumen akademik.

### Distribusi Skenario Query (50 Query)
Untuk menguji performa retrieval secara komprehensif, 50 query dibagi menjadi 6 kategori skenario berikut:

| Kategori Skenario | Porsi | Jumlah | Penjelasan / Tujuan Uji |
| ----------------- | ----- | ------ | ----------------------- |
| **Leksikal Tematik** | 30% | 15 Query | Menguji keyword bias dengan kata kunci umum. Menargetkan sekumpulan dokumen sejenis. |
| **Query Semantic Gap** | 20% | 10 Query | Menguji pemahaman intensi pencarian (search intent) di mana terdapat perbedaan istilah query dengan bahasa dokumen. |
| **Query Spesifik** | 20% | 10 Query | Menguji presisi mutlak sistem terhadap satu dokumen target spesifik. |
| **Query Typo/Noisy** | 10% | 5 Query | Menguji ketahanan representasi ruang vektor terhadap noise atau salah ketik kata kunci. |
| **Query Metadata** | 10% | 5 Query | Menguji kemampuan model embedding dalam memisahkan konteks topik dengan angka tahun dokumen. |
| **Query Kasual** | 10% | 5 Query | Menguji responsivitas sistem terhadap query percakapan informal sehari-hari. |

---

## 2. Desain Prompt & Konfigurasi Generatif HyDE

Pencarian berbasis HyDE (Hypothetical Document Embeddings) menggunakan LLM untuk men-generate dokumen/abstrak hipotetis dari query sebelum dilakukan embedding dan retrieval. Sistem ini mengevaluasi dua jenis prompt generatif:

### Desain Prompt

#### Prompt 1: Strict Abstract Components
Prompt ini menginstruksikan model secara ketat untuk menyusun abstrak berdasarkan struktur komponen formal abstrak skripsi (masalah, metode, hasil).
```
Tugas: Tulis satu paragraf abstrak skripsi Teknik Informatika dalam Bahasa Indonesia berdasarkan topik berikut.
Struktur abstrak harus mengikuti komponen berikut secara ketat:
1. Masalah: Masalah penelitian yang diselesaikan.
2. Metode: Metode, algoritma, atau teknologi yang digunakan.
3. Hasil: Hasil atau tujuan akhir yang ingin dicapai.

Topik: {query}
```

#### Prompt 2: Explicit Constraints (Pembatasan Eksplisit)
Prompt ini dirancang menggunakan pembatasan (constraint) ketat untuk mengurangi ambiguitas dan menghindari halusinasi agar model menghasilkan konteks yang lebih fokus dan deterministik.
```
Tugas: Tulis satu paragraf abstrak skripsi Teknik Informatika dalam Bahasa Indonesia berdasarkan topik berikut.

Aturan ketat:
- Panjang: 2–3 kalimat saja.
- Hanya sebutkan metode, algoritma, atau teknologi yang TERSEBUT SECARA EKSPLISIT atau TERSIRAT LANGSUNG dari topik. Jangan tambahkan metode lain untuk mengurangi ambiguitas dan halusinasi.
- Jika topik menggunakan bahasa sehari-hari (misal: 'aplikasi absensi pakai muka'), terjemahkan ke istilah akademis yang tepat (misal: 'Penelitian ini membangun sistem absensi berbasis pengenalan wajah...').
- Jika ada typo, koreksi otomatis ke istilah baku yang paling mendekati dalam bidang Teknik Informatika.
- Output hanya teks abstrak. Tanpa salam, tanpa label, tanpa tanda kutip pembuka/penutup.

Topik: {query}
```

### Parameter LLM (Groq API)
Untuk memastikan keluaran LLM bersifat konsisten, fokus, dan meminimalkan variasi generasi (halusinasi), parameter generatif diatur sebagai berikut:

| Parameter | Nilai | Alasan / Justifikasi |
| --------- | ----- | -------------------- |
| **Temperature** | `0.0` | Menghasilkan keluaran yang deterministik, konsisten, dan mengurangi variasi acak generasi. |
| **Top-P** | `1.0` | Mempertahankan batas probabilitas kumulatif penuh (kontrol murni diserahkan ke temperature). |
| **Max Tokens** | `200` | Membatasi panjang teks agar LLM menghasilkan abstrak hipotetis yang ringkas (sesuai target panjang abstrak ±150-300 kata). |
| **Frequency Penalty**| `0` | Tidak memberikan penalti pengulangan kata (menghindari kerusakan istilah teknis berulang). |
| **Presence Penalty** | `0` | Tidak memaksa model memunculkan topik baru secara acak. |

---

## 3. Parameter Embedding & Ruang Vektor

* **Strategi Chunking**: Setiap abstrak direpresentasikan murni sebagai **satu chunk**. Tidak dilakukan splitting paragraf agar kesatuan makna akademis abstrak tetap utuh dalam satu vektor representasi.
* **Panjang Abstrak**: Rata-rata abstrak berkisar antara **150–300 kata**.
* **Penanganan Abstrak Panjang**: Abstrak yang melebihi batas token model embedding (`intfloat/multilingual-e5-small`) secara otomatis dipotong (truncated) sesuai batas token maksimum model (512 token).
* **Distance Metric**: **Cosine Similarity**
  * *Alasan*: Cosine similarity mengukur kedekatan arah/sudut vektor dokumen dibanding besarnya nilai magnitudo vektor. Hal ini sangat cocok untuk *semantic retrieval* karena mengabaikan perbedaan panjang teks pendek/panjang dan lebih berfokus pada kesesuaian topik semantik.
  * *Rumus Konversi*: Cosine Similarity dihitung sebagai `1.0 - Cosine Distance` dari hasil query ChromaDB.

---

## 4. Kriteria Relevansi & Ground Truth

### Pedoman Pelabelan Relevansi (Biner)
Kriteria penilaian kecocokan dokumen yang di-retrieve dengan query uji menggunakan sistem biner:

* **Nilai 1 (Relevan)**:
  * Topik pembahasan utama sesuai dengan query.
  * Metode/algoritma yang dicari berkaitan langsung atau setara.
  * Domain permasalahan serupa.
  * Makna semantik query selaras dengan abstrak yang ditemukan.
* **Nilai 0 (Tidak Relevan)**:
  * Domain permasalahan berbeda secara signifikan.
  * Metode/algoritma tidak berkaitan atau tidak digunakan dalam skripsi tersebut.
  * Makna semantik melenceng jauh.
  * Metadata (seperti tahun atau kata kunci spesifik) tidak sesuai dengan batasan query.

### Pooling Strategy
Untuk menghasilkan Ground Truth yang robust tanpa harus melabeli seluruh dokumen dalam database secara manual:
1. Jalankan **Top-10 hasil retrieval dari Standard RAG**
2. Jalankan **Top-10 hasil retrieval dari HyDE (Prompt 1)**
3. Jalankan **Top-10 hasil retrieval dari HyDE (Prompt 2)**
4. Hasil pencarian digabungkan secara unik (*set union* berdasarkan file source/judul) menjadi daftar kandidat dokumen sebelum dilakukan pelabelan manual.
5. Dokumen kandidat tersebut kemudian diberi label biner (1/0) oleh penilai manual untuk menentukan relevansi sesungguhnya.

---

## 5. Struktur Direktori & File Evaluasi

```
backend/
├── scripts/
│   ├── build_index.py          # Script pembuatan indeks ChromaDB lokal
│   ├── run_evaluation.py       # Script evaluasi otomatis Standard RAG vs HyDE P1 & P2
│   └── generate_pooling.py     # Helper script untuk membuat kandidat pooling manual
├── evaluation/
│   ├── queries.json            # Master file 50 query uji
│   ├── pooling_candidates.json # File output hasil pooling untuk pelabelan manual
│   └── results/
│       └── eval_YYYYMMDD_HHMMSS.json  # Output log hasil run evaluasi
└── EVALUATION.md               # Dokumen spesifikasi ini
```

---

## 6. Cara Menjalankan

### A. Membuat / Reset Indeks Vektor (Cosine Space)
Pastikan indeks ChromaDB dibuat menggunakan metrik Cosine Similarity:
```bash
python scripts/build_index.py --reset
```

### B. Membuat Kandidat Pooling untuk Pelabelan Manual
Jalankan script pooling untuk menggabungkan hasil Top-10 RAG dan HyDE (P1 & P2) untuk semua 50 query:
```bash
python scripts/generate_pooling.py
```
Output akan disimpan di `evaluation/pooling_candidates.json`. Anda dapat melabeli secara manual dengan mengubah field `"Label_Manual": null` menjadi `1` atau `0`.

### C. Menjalankan Evaluasi Otomatis
Untuk membandingkan performa Standard RAG, HyDE (Prompt 1), dan HyDE (Prompt 2) berdasarkan Ground Truth:
```bash
python scripts/run_evaluation.py
```
Hasil run yang lengkap beserta metrik agregat MRR, Hit Rate@5, Latency, dan Average Score akan disimpan di folder `evaluation/results/`.

---

## 7. Skema Output Evaluasi

Hasil evaluasi disimpan sebagai file JSON dengan metadata, metrik summary agregat per metode, serta detail record per query.

```json
{
  "metadata": {
    "timestamp": "2026-06-30T02:00:00",
    "top_k": 5,
    "embedding_model": "intfloat/multilingual-e5-small",
    "llm_model": "openai/gpt-oss-20b",
    "chroma_collection": "skripsi_docs",
    "total_queries": 50,
    "methods": ["Standard RAG", "HyDE (Prompt 1)", "HyDE (Prompt 2)"]
  },
  "summary": {
    "by_method": {
      "Standard RAG": {
        "n_queries": 5,
        "Hit_Rate@K": 0.8,
        "MRR": 0.7333,
        "Avg_Score_Top1": 89.24,
        "Avg_Latency_ms": 124.5
      },
      "HyDE (Prompt 1)": {
        "n_queries": 5,
        "Hit_Rate@K": 0.9,
        "MRR": 0.85,
        "Avg_Score_Top1": 91.12,
        "Avg_Latency_ms": 1420.2
      },
      "HyDE (Prompt 2)": {
        "n_queries": 5,
        "Hit_Rate@K": 0.95,
        "MRR": 0.92,
        "Avg_Score_Top1": 93.45,
        "Avg_Latency_ms": 1380.8
      }
    },
    "winner_by_MRR": "HyDE (Prompt 2)"
  },
  "results": [
    {
      "ID": "Q26",
      "Tipe": "Spesifik",
      "Query_Text": "klasifikasi kematangan buah cabai cnn",
      "Ground_Truth_File": "2024_AZIZAH_SALSABILA.pdf",
      "Metode": "Standard RAG",
      "Rank": 1,
      "Skor_Similarity": 91.23,
      "File_Source": "2024_AZIZAH_SALSABILA.pdf",
      "File_Source_Basename": "2024_AZIZAH_SALSABILA.pdf",
      "Tahun": 2024,
      "Judul_Skripsi": "KLASIFIKASI KEMATANGAN BUAH CABAI MENGGUNAKAN CNN",
      "Abstrak": "...",
      "Dokumen_Hipotetikal_LLM": null,
      "Latency_ms": 125.1,
      "Hit_GT": true,
      "Rank_GT": 1,
      "RR": 1.0
    }
  ]
}
```
