# EVALUATION.md — Sistem Evaluasi Chatbot Pencarian Skripsi

Dokumen ini mendefinisikan arsitektur, skema data, dan prosedur lengkap untuk menjalankan evaluasi perbandingan **Standard RAG vs. HyDE** secara lokal menggunakan infrastruktur backend yang sama (ChromaDB + `multilingual-e5-small`) — bukan lingkungan Google Colab — sehingga hasil yang diperoleh mencerminkan performa sistem yang sesungguhnya.

---

## 1. Tujuan & Filosofi

| Tujuan                 | Penjelasan                                                                                                                             |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Reprodusibilitas**   | Evaluasi dijalankan di atas stack yang identik dengan produksi (ChromaDB lokal, model embedding yang sama, Groq API yang sama)         |
| **Isolasi Lingkungan** | Menghindari gap performa antara Colab (GPU/CPU berbeda, model dimuat ulang setiap sesi) vs. server lokal                               |
| **Automasi Penuh**     | Satu perintah → semua query dijalankan → satu file JSON output dihasilkan                                                              |
| **Traceability**       | Setiap baris result bisa ditelusuri ke query, metode, rank, skor, file sumber, dan (untuk HyDE) dokumen hipotetis yang di-generate LLM |

---

## 2. Struktur File & Direktori

```
backend/
├── scripts/
│   ├── build_index.py          # (existing) build ChromaDB index
│   └── run_evaluation.py       # ← FILE BARU: script evaluasi utama
├── evaluation/
│   ├── queries.json            # ← FILE BARU: master list semua query
│   └── results/
│       └── eval_YYYYMMDD_HHMMSS.json   # output hasil evaluasi
├── app/
│   ├── services/
│   │   └── document_service.py
│   └── ...
└── EVALUATION.md               # dokumen ini
```

---

## 3. Skema `queries.json`

File ini adalah **sumber kebenaran tunggal** untuk semua query evaluasi. Script `run_evaluation.py` membaca file ini dan mengiterasi setiap query.

```json
[
  {
    "ID": "Q01",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum. RAG standar seharusnya unggul karena mengandalkan pencocokan token langsung.",
    "Query_Text": "sistem pendukung keputusan metode",
    "Ground_Truth_File": null
  }
]
```

### Kolom `queries.json`

| Kolom               | Tipe             | Keterangan                                                                                    |
| ------------------- | ---------------- | --------------------------------------------------------------------------------------------- |
| `ID`                | `string`         | Identifier unik query, format `Q01`, `Q02`, dst.                                              |
| `Tipe`              | `string`         | Kategori query (lihat §4)                                                                     |
| `Deskripsi_Tipe`    | `string`         | Penjelasan singkat tujuan uji kategori ini                                                    |
| `Query_Text`        | `string`         | Teks query yang dikirim ke sistem                                                             |
| `Ground_Truth_File` | `string \| null` | Nama file PDF target (hanya untuk kategori **Leksikal Spesifik**); `null` untuk kategori lain |

---

## 4. Master Daftar Query

Isi lengkap untuk `evaluation/queries.json`:

```json
[
  {
    "ID": "Q01",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "sistem pendukung keputusan metode",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q02",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "aplikasi media pembelajaran android",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q03",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "algoritma convolutional neural network",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q04",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "sistem kontrol berbasis iot",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q05",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "sistem pakar diagnosa penyakit",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q06",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "sistem question answering chatbot",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q07",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "analisis sentimen word embedding",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q08",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "penerapan progressive web application",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q09",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "algoritma k-nearest neighbor",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q10",
    "Tipe": "Leksikal Tematik",
    "Deskripsi_Tipe": "Menguji keyword bias. Menargetkan sekumpulan dokumen umum.",
    "Query_Text": "metode full-text indexing",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q11",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "klasifikasi kematangan buah cabai cnn",
    "Ground_Truth_File": "2024_AZIZAH_SALSABILA.pdf"
  },
  {
    "ID": "Q12",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "vehicle routing problem logistik waktu",
    "Ground_Truth_File": "2025_ANDI_ANI_NURDIANINGRAT.pdf"
  },
  {
    "ID": "Q13",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "kualitas sarang burung walet vgg16",
    "Ground_Truth_File": "2023_ASHABUL_KAHFI_ASH_SHIDDIQ.pdf"
  },
  {
    "ID": "Q14",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "pakan lele otomatis iot",
    "Ground_Truth_File": "2025_ULFA_RAHMAYANI.pdf"
  },
  {
    "ID": "Q15",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "pengenalan jenis kulit wajah vgg16",
    "Ground_Truth_File": "2024_NUR_AISYA_HERI.pdf"
  },
  {
    "ID": "Q16",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "klasifikasi fertilitas telur ayam yolov8",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q17",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "water resistant perkebunan karet mikrokontroler",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q18",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "sentimen ulasan wisata pantai losari lstm",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q19",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "animasi struktur bumi augmented reality",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q20",
    "Tipe": "Leksikal Spesifik",
    "Deskripsi_Tipe": "Menguji presisi mutlak. Satu dokumen target wajib berada di Rank 1.",
    "Query_Text": "deteksi kelelawar mikrokontroler android",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q21",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "cara otomatis pisahin telur bagus",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q22",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "alat biar motor gak gampang dicuri",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q23",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "bikin aplikasi donasi untuk pelosok",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q24",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "aplikasi buat hafalan quran santri",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q25",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "gimana cara siram bawang otomatis",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q26",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "website buat cari info kos",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q27",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "alat biar sapi tidak dicuri",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q28",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "bantu tunanetra tahu nominal uang",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q29",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "aplikasi lapor fasilitas publik rusak",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q30",
    "Tipe": "Semantik Tematik",
    "Deskripsi_Tipe": "Menguji pemahaman intensi (Search Intent). HyDE dirancang unggul di sini.",
    "Query_Text": "cara cek tugas akhir plagiat",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q31",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "klasifiaksi",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q32",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "mikrokntroler",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q33",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "yolo",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q34",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "androdi",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q35",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "algorimta",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q36",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "k-menas",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q37",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "naiv bayes",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q38",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "blokchain",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q39",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "frameowrk",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q40",
    "Tipe": "Typo Stress Test",
    "Deskripsi_Tipe": "Menguji ketahanan vector space terhadap noise. RAG rentan gagal, HyDE rentan berhalusinasi.",
    "Query_Text": "pwa",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q41",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "sistem pakar android 2018",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q42",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "internet of things 2024",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q43",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "augmented reality 2017",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q44",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "sistem pendukung keputusan 2020",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q45",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "convolutional neural network 2025",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q46",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "aplikasi rumah sakit 2021",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q47",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "progressive web app 2022",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q48",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "algoritma k-means 2024",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q49",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "mikrokontroler arduino 2019",
    "Ground_Truth_File": null
  },
  {
    "ID": "Q50",
    "Tipe": "Metadata Query",
    "Deskripsi_Tipe": "Menguji apakah model embedding bisa memisahkan konteks topik dari angka tahun absolut.",
    "Query_Text": "sistem pakar web 2017",
    "Ground_Truth_File": null
  }
]
```

---

## 5. Skema Output `eval_YYYYMMDD_HHMMSS.json`

Setiap record dalam array `results` merepresentasikan **satu dokumen yang di-retrieve** untuk satu kombinasi (query × metode × rank).

```json
{
  "metadata": {
    "timestamp": "2026-02-15T14:30:00",
    "top_k": 5,
    "embedding_model": "intfloat/multilingual-e5-small",
    "llm_model": "llama3-8b-8192",
    "chroma_collection": "skripsi_docs",
    "total_queries": 50,
    "methods": ["Standard RAG", "HyDE"]
  },
  "results": [
    {
      "ID": "Q01",
      "Tipe": "Leksikal Tematik",
      "Query_Text": "sistem pendukung keputusan metode",
      "Ground_Truth_File": null,
      "Metode": "Standard RAG",
      "Rank": 1,
      "Skor_Similarity": 0.8752,
      "File_Source": "2025_BAHRUL_ULLUNG.pdf",
      "Tahun": 2025,
      "Judul_Skripsi": "IMPLEMENTASI ANALYTICAL HIERARCHY PROCESS ...",
      "Abstrak": "Program Keluarga Harapan ...",
      "Dokumen_Hipotetikal_LLM": null,
      "Hit_Ground_Truth": null,
      "Rank_Ground_Truth": null
    },
    {
      "ID": "Q11",
      "Tipe": "Leksikal Spesifik",
      "Query_Text": "klasifikasi kematangan buah cabai cnn",
      "Ground_Truth_File": "2024_AZIZAH_SALSABILA.pdf",
      "Metode": "Standard RAG",
      "Rank": 1,
      "Skor_Similarity": 0.9123,
      "File_Source": "2024_AZIZAH_SALSABILA.pdf",
      "Tahun": 2024,
      "Judul_Skripsi": "...",
      "Abstrak": "...",
      "Dokumen_Hipotetikal_LLM": null,
      "Hit_Ground_Truth": true,
      "Rank_Ground_Truth": 1
    },
    {
      "ID": "Q21",
      "Tipe": "Semantik Tematik",
      "Query_Text": "cara otomatis pisahin telur bagus",
      "Ground_Truth_File": null,
      "Metode": "HyDE",
      "Rank": 1,
      "Skor_Similarity": 0.8612,
      "File_Source": "2024_AZIZAH_SALSABILA.pdf",
      "Tahun": 2024,
      "Judul_Skripsi": "...",
      "Abstrak": "...",
      "Dokumen_Hipotetikal_LLM": "Penelitian ini mengembangkan sistem otomatis untuk mengklasifikasikan kualitas telur berdasarkan parameter visual menggunakan computer vision ...",
      "Hit_Ground_Truth": null,
      "Rank_Ground_Truth": null
    }
  ]
}
```

### Penjelasan Kolom Output

| Kolom                     | Tipe             | Keterangan                                                                                                                            |
| ------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `ID`                      | `string`         | ID query dari `queries.json`                                                                                                          |
| `Tipe`                    | `string`         | Kategori query                                                                                                                        |
| `Query_Text`              | `string`         | Teks query asli                                                                                                                       |
| `Ground_Truth_File`       | `string \| null` | File target (dari `queries.json`)                                                                                                     |
| `Metode`                  | `string`         | `"Standard RAG"` atau `"HyDE"`                                                                                                        |
| `Rank`                    | `int`            | Posisi dokumen dalam hasil retrieve (1–top_k)                                                                                         |
| `Skor_Similarity`         | `float`          | Cosine similarity dari ChromaDB (range ~0.7–1.0)                                                                                      |
| `File_Source`             | `string`         | Nama file PDF yang di-retrieve                                                                                                        |
| `Tahun`                   | `int \| null`    | Tahun skripsi (dari metadata ChromaDB)                                                                                                |
| `Judul_Skripsi`           | `string`         | Judul skripsi yang di-retrieve                                                                                                        |
| `Abstrak`                 | `string`         | Abstrak skripsi yang di-retrieve                                                                                                      |
| `Dokumen_Hipotetikal_LLM` | `string \| null` | Dokumen fiktif yang di-generate oleh LLM (hanya untuk HyDE, `null` untuk Standard RAG)                                                |
| `Hit_Ground_Truth`        | `bool \| null`   | `true` jika `File_Source == Ground_Truth_File`; `null` jika tidak ada ground truth                                                    |
| `Rank_Ground_Truth`       | `int \| null`    | Rank di mana ground truth ditemukan (untuk query dengan `Ground_Truth_File`); `null` jika tidak ditemukan atau tidak ada ground truth |

---

## 6. Implementasi `scripts/run_evaluation.py`

```python
"""
run_evaluation.py — Evaluasi otomatis Standard RAG vs HyDE
Jalankan dari folder backend/:
    python scripts/run_evaluation.py
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Tambahkan root backend ke sys.path agar import app.* bisa bekerja
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.document_service import DocumentService  # sesuaikan import

# ─── Konfigurasi ──────────────────────────────────────────────────────────────

TOP_K = 5                    # Jumlah dokumen yang di-retrieve per query
QUERIES_FILE = Path(__file__).parent.parent / "evaluation" / "queries.json"
OUTPUT_DIR = Path(__file__).parent.parent / "evaluation" / "results"
DELAY_BETWEEN_QUERIES = 1.5  # detik; hindari rate-limit Groq API untuk HyDE

# ─── Helper ───────────────────────────────────────────────────────────────────

def convert_chroma_distance_to_similarity(distance: float) -> float:
    """
    ChromaDB mengembalikan L2 distance atau cosine distance.
    Untuk cosine: similarity = 1 - distance.
    Sesuaikan jika collection kamu pakai metric berbeda.
    """
    return round(1 - distance, 4)


def extract_year_from_filename(filename: str) -> int | None:
    """Ekstrak tahun dari nama file format: 2024_NAMA_PENULIS.pdf"""
    try:
        return int(filename.split("_")[0])
    except (ValueError, IndexError):
        return None


def run_standard_rag(service: DocumentService, query_text: str, top_k: int) -> list[dict]:
    """
    Jalankan Standard RAG: embed query → retrieve dari ChromaDB.
    Kembalikan list of result dicts.

    SESUAIKAN fungsi ini dengan interface DocumentService kamu.
    Contoh di bawah mengasumsikan method `retrieve(query, n_results)` mengembalikan
    ChromaDB query result object.
    """
    chroma_results = service.retrieve(query_text, n_results=top_k)

    results = []
    documents = chroma_results.get("documents", [[]])[0]
    metadatas = chroma_results.get("metadatas", [[]])[0]
    distances = chroma_results.get("distances", [[]])[0]

    for rank_idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        file_source = meta.get("source", meta.get("file_name", "unknown.pdf"))
        results.append({
            "Metode": "Standard RAG",
            "Rank": rank_idx,
            "Skor_Similarity": convert_chroma_distance_to_similarity(dist),
            "File_Source": file_source,
            "Tahun": meta.get("tahun") or extract_year_from_filename(file_source),
            "Judul_Skripsi": meta.get("judul", ""),
            "Abstrak": doc,
            "Dokumen_Hipotetikal_LLM": None,
        })
    return results


def run_hyde(service: DocumentService, query_text: str, top_k: int) -> list[dict]:
    """
    Jalankan HyDE: generate hypothetical doc via LLM → embed hypothetical doc
    → retrieve dari ChromaDB.

    SESUAIKAN fungsi ini dengan interface DocumentService / HyDE pipeline kamu.
    Contoh mengasumsikan:
      - service.generate_hypothetical_document(query) → str
      - service.retrieve(hypothetical_doc, n_results) → chroma result
    """
    hypothetical_doc = service.generate_hypothetical_document(query_text)

    chroma_results = service.retrieve(hypothetical_doc, n_results=top_k)

    results = []
    documents = chroma_results.get("documents", [[]])[0]
    metadatas = chroma_results.get("metadatas", [[]])[0]
    distances = chroma_results.get("distances", [[]])[0]

    for rank_idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        file_source = meta.get("source", meta.get("file_name", "unknown.pdf"))
        results.append({
            "Metode": "HyDE",
            "Rank": rank_idx,
            "Skor_Similarity": convert_chroma_distance_to_similarity(dist),
            "File_Source": file_source,
            "Tahun": meta.get("tahun") or extract_year_from_filename(file_source),
            "Judul_Skripsi": meta.get("judul", ""),
            "Abstrak": doc,
            "Dokumen_Hipotetikal_LLM": hypothetical_doc,
        })
    return results


def compute_ground_truth_fields(results: list[dict], ground_truth_file: str | None) -> list[dict]:
    """
    Tambahkan kolom Hit_Ground_Truth dan Rank_Ground_Truth ke setiap result
    dalam satu grup (query × metode).
    """
    if ground_truth_file is None:
        for r in results:
            r["Hit_Ground_Truth"] = None
            r["Rank_Ground_Truth"] = None
        return results

    # Cari di rank berapa ground truth muncul
    gt_rank = None
    for r in results:
        if r["File_Source"] == ground_truth_file:
            gt_rank = r["Rank"]
            break

    for r in results:
        r["Hit_Ground_Truth"] = (r["File_Source"] == ground_truth_file)
        r["Rank_Ground_Truth"] = gt_rank  # sama untuk semua baris dalam grup ini

    return results


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # 1. Load queries
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        queries = json.load(f)
    print(f"[INFO] Loaded {len(queries)} queries dari {QUERIES_FILE}")

    # 2. Init service
    # Sesuaikan dengan cara kamu inisialisasi DocumentService / RAG service
    service = DocumentService()
    print("[INFO] DocumentService initialized.")

    # 3. Siapkan output dir
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"eval_{timestamp_str}.json"

    all_results = []
    total = len(queries)

    for i, query in enumerate(queries, start=1):
        qid = query["ID"]
        tipe = query["Tipe"]
        query_text = query["Query_Text"]
        ground_truth_file = query.get("Ground_Truth_File")

        print(f"\n[{i}/{total}] {qid} | {tipe} | \"{query_text}\"")

        # — Standard RAG —
        print(f"  → Standard RAG ...", end=" ", flush=True)
        try:
            rag_results = run_standard_rag(service, query_text, TOP_K)
            rag_results = compute_ground_truth_fields(rag_results, ground_truth_file)
        except Exception as e:
            print(f"ERROR: {e}")
            rag_results = []

        for r in rag_results:
            all_results.append({
                "ID": qid,
                "Tipe": tipe,
                "Query_Text": query_text,
                "Ground_Truth_File": ground_truth_file,
                **r
            })
        print(f"OK ({len(rag_results)} results)")

        # — HyDE —
        print(f"  → HyDE ...", end=" ", flush=True)
        try:
            hyde_results = run_hyde(service, query_text, TOP_K)
            hyde_results = compute_ground_truth_fields(hyde_results, ground_truth_file)
        except Exception as e:
            print(f"ERROR: {e}")
            hyde_results = []

        for r in hyde_results:
            all_results.append({
                "ID": qid,
                "Tipe": tipe,
                "Query_Text": query_text,
                "Ground_Truth_File": ground_truth_file,
                **r
            })
        print(f"OK ({len(hyde_results)} results)")

        # Rate-limit delay (Groq API)
        if i < total:
            time.sleep(DELAY_BETWEEN_QUERIES)

    # 4. Susun output final
    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "top_k": TOP_K,
            "embedding_model": "intfloat/multilingual-e5-small",
            "llm_model": "llama3-8b-8192",
            "chroma_collection": "skripsi_docs",
            "total_queries": len(queries),
            "methods": ["Standard RAG", "HyDE"]
        },
        "results": all_results
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] {len(all_results)} records → {output_path}")


if __name__ == "__main__":
    main()
```

---

## 7. Cara Menjalankan

```bash
# Pastikan virtual environment aktif dan ChromaDB sudah ter-build
cd backend/
python scripts/run_evaluation.py
```

Output akan tersimpan di `evaluation/results/eval_YYYYMMDD_HHMMSS.json`.

---

## 8. Adaptasi ke Struktur Service Kamu

Script di §6 mengasumsikan dua method pada `DocumentService`:

| Method yang diasumsikan                         | Fungsi                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------- |
| `service.retrieve(text, n_results)`             | Embed `text` lalu query ChromaDB, kembalikan raw chroma result dict |
| `service.generate_hypothetical_document(query)` | Generate hypothetical abstract via Groq API, kembalikan `str`       |

Jika interface `document_service.py` kamu berbeda, sesuaikan hanya dua fungsi `run_standard_rag()` dan `run_hyde()` di script — skema output JSON tidak perlu berubah.

### Tips Adaptasi Umum

Jika RAG pipeline kamu sudah terkapsulasi dalam endpoint `/api/chat`, kamu bisa memanggil endpoint itu secara internal dari script evaluasi menggunakan `httpx` atau `requests`, tanpa perlu import langsung. Contoh:

```python
import httpx

def run_standard_rag_via_api(query_text, top_k):
    resp = httpx.post(
        "http://localhost:8000/api/chat",
        json={"message": query_text, "mode": "rag", "top_k": top_k},
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["retrieved_documents"]  # sesuaikan field
```

---

## 9. Catatan Penting

**Kenapa tidak pakai Colab lagi?**
Perbedaan performa antara Colab dan sistem lokal dapat muncul dari:

- Model embedding yang di-load ke device berbeda (GPU T4 vs CPU lokal)
- Versi library yang berbeda (`chromadb`, `sentence-transformers`)
- State ChromaDB yang tidak identik (index Colab di-rebuild dari nol setiap sesi)

Dengan `run_evaluation.py` ini, semua evaluasi berjalan di atas **ChromaDB dan embedding model yang sama persis** dengan yang digunakan oleh server produksi kamu.

**Rate Limiting Groq API**
HyDE melakukan satu API call per query. Untuk 50 query = 50 Groq calls. Dengan `DELAY_BETWEEN_QUERIES = 1.5` detik, total durasi eksekusi ~4–5 menit. Jika kamu menggunakan Groq free tier, naikkan delay ke 2–3 detik.

**Re-run dengan Index Berbeda**
Setiap kali `build_index.py --reset` dijalankan, output evaluasi bisa berubah. Selalu sertakan `metadata.timestamp` untuk membedakan run antar versi index.
