cd C:\belajarku\semester 7\Sistem Pencarian Judul dan Abstrak Skripsi\backend
conda activate chatbot-env
uvicorn app.main:app --reload

# Backend - FastAPI Chatbot Pencarian Skripsi

Implementasi backend FastAPI untuk chatbot pencarian judul dan abstrak skripsi dengan menggunakan RAG (Retrieval-Augmented Generation) dan HyDE approach.

## 📋 Setup Awal

### 1️⃣ Install Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Setup Environment Variables

1. Buka file `.env`
2. Ganti `your_groq_api_key_here` dengan API key Anda dari https://console.groq.com

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
```

## 📁 Struktur Folder

```
backend/
├── app/
│   ├── main.py                    # Entry point FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py                # Endpoint chat
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_service.py    # Load & preprocess PDF
│   │   ├── embedding_service.py   # Embedding dengan HuggingFace
│   │   ├── rag_service.py         # RAG & HyDE logic
│   │   └── suggestion_service.py  # Academic suggestions
│   └── core/
│       ├── __init__.py
│       └── config.py              # Configuration
│
├── data/
│   └── pdf/                       # [KOSONG] Letakkan PDF di sini
│
├── scripts/
│   └── build_index.py             # Script untuk embedding (jalankan sekali)
│
├── chroma_db/                     # [AUTO] Vector database
│
├── requirements.txt
├── .env                           # API keys dan configuration
└── README.md
```

## 🚀 Menjalankan Aplikasi

### Step 1: Build Index ChromaDB

**PENTING**: Jalankan ini hanya sekali atau ketika menambah/mengubah PDF baru.

```bash
python scripts/build_index.py
```

Proses ini akan:

- ✅ Load semua PDF dari `data/pdf/`
- ✅ Extract judul, identitas, dan abstrak
- ✅ Membuat embedding dengan multilingual-e5-small
- ✅ Menyimpan vektor ke `chroma_db/`

### Step 2: Jalankan FastAPI Server

```bash
# Development mode (dengan hot reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server akan berjalan di:

- 🌐 API: http://localhost:8000
- 📚 Swagger Docs: http://localhost:8000/docs
- 🔍 ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### 1. Chat Endpoint

**POST** `/api/chat`

Request body:

```json
{
  "message": "sistem rekomendasi",
  "mode": "rag"
}
```

Mode:

- `"rag"` - Standard RAG (default)
- `"hyde"` - HyDE RAG (hypothetical document embeddings)

Response:

```json
{
  "success": true,
  "message": "Halo 👋 Berdasarkan query yang Anda berikan...",
  "query": "sistem rekomendasi",
  "mode": "rag",
  "documents": [
    {
      "title": "Sistem Rekomendasi Dosen Pembimbing...",
      "source": "skripsi_001.pdf",
      "content": "...",
      "score": null
    }
  ],
  "suggestion": "Saran akademik berdasarkan judul..."
}
```

### 2. Health Check

**GET** `/api/health`

Check status server dan vector database.

### 3. System Info

**GET** `/api/info`

Get informasi tentang model, embedding, dan jumlah vektor.

### 4. Server Status

**GET** `/api/status`

Check status server.

## 🔑 Mendapatkan Groq API Key

1. Buka https://console.groq.com
2. Sign up dengan email
3. Di dashboard, generate API key
4. Copy API key ke file `.env`

API gratis Groq:

- ✅ Unlimited requests
- ✅ Fast inference
- ✅ Model: Llama 3 70B

## 📝 Menambah Dataset PDF

1. Pastikan file PDF berisi:
   - ✅ Halaman sampul dengan judul dan identitas
   - ✅ Abstrak minimal 100 karakter

2. Letakkan PDF di folder: `backend/data/pdf/`

3. Jalankan build index ulang:
   ```bash
   python scripts/build_index.py
   ```

## 🧠 Logika Chatbot

### Standard RAG

- Langsung retrieve dokumen relevan dari database
- Lebih cepat dan efisien
- Bagus untuk topik spesifik

### HyDE RAG

- Generate hypothetical abstract menggunakan LLM
- Embed hypothetical doc dan retrieve
- Lebih baik untuk topik umum dan diverse queries
- Sedikit lebih lambat

## ⚙️ Pipeline Pemrosesan PDF & Ekstraksi

Sistem memiliki pipeline khusus untuk memproses PDF mentah (skripsi) menjadi vektor yang bersih dan terstruktur. Hal ini ditangani oleh `document_service.py`.

### 1. Pemuatan & Pemisahan Halaman (PDF Loading)
Menggunakan `PyPDFLoader`, dokumen PDF dibaca per halaman. Teks dari halaman pertama (cover) digunakan sebagai sumber utama ekstraksi metadata, sedangkan halaman berikutnya untuk abstrak.

### 2. Ekstraksi Metadata (Judul & Identitas)
Pola yang digunakan untuk mengekstrak informasi:
- **Judul**: Diekstrak dari baris-baris awal cover. Sistem akan membaca baris per baris dan **berhenti** ketika menemukan *stop words* (seperti "skripsi", "diajukan", "oleh", "nama", "nim"). 
  > *Catatan: Judul seringkali cacat/terpotong jika terdapat kata-kata tersebut di dalam judul itu sendiri, atau format teks PDF berantakan karena letak logo/spasi.*
- **Identitas (NIM, Nama, Pembimbing)**: Menggunakan pola *Regular Expression (Regex)*.
- **Dynamic Metadata Rescue**: Jika metadata gagal didapatkan dari cover, sistem akan mencoba mencari ulang pola "Judul: ...", "NIM: ..." di dalam teks isi/abstrak.
- **Prioritas File Name**: Untuk tahun dan nama penulis, sistem memprioritaskan pembacaan dari format nama file standar: `TAHUN_NAMA_PENULIS.pdf` (Contoh: `2023_RINI.pdf`).

### 3. Pembersihan Abstrak (Algoritma Guillotine)
Abstrak di PDF skripsi seringkali tercampur dengan nama pembimbing dan header. Sistem menerapkan strategi bertingkat untuk membersihkannya:
- **Explicit Slicing**: Memotong teks secara tegas tepat setelah ditemukannya kata "Abstrak:" atau "Abstract:".
- **Strategi 1 (Academic Title)**: Memotong teks tepat setelah gelar terakhir (seperti M.Kom, Ph.D, S.T, dsb.) karena biasanya isi abstrak dimulai setelah daftar pembimbing.
- **Strategi 2 (Pembimbing Anchor)**: Memotong tepat setelah blok nama pembimbing terdeteksi.
- **Strategi 3 (Narrative Anchor)**: Mencari kata kunci pembuka esai abstrak standar (seperti "Latar belakang", "Penelitian ini", "Seiring perkembangan teknologi", dll.) dan membuang teks di atasnya.
- **Post-Cleaning**: Menghapus sisa-sisa garis bawah yang panjang, spasi ganda, newline, atau teks identitas sisa seperti "Nama : ...".

### 4. Embedding & Vector Database Storage
**Data HANYA akan dimasukkan ke vector database SETELAH semua proses ekstraksi dan pembersihan selesai.**
Setelah teks abstrak dinyatakan bersih (dijadikan sebagai *page_content*) dan semua atribut metadata (judul, nama, NIM, pembimbing, tahun) berhasil diamankan, teks tersebut baru akan diubah menjadi representasi *vector embeddings* menggunakan model `multilingual-e5-small` via HuggingFace. Vektor-vektor ini beserta metadatanya kemudian disimpan secara permanen ke dalam vector database **ChromaDB** (folder `chroma_db/`) agar dapat digunakan untuk proses pencarian semantik (RAG).

### ⚠️ Mengapa ada Judul yang Tidak Terdeteksi / Cacat?
Jika Anda menemukan dokumen dengan judul yang cacat atau kosong, penyebab utamanya adalah:
1. **Format Cover Tidak Standar**: PDF tidak menggunakan letak teks cover konvensional, atau teks menyatu dengan gambar/logo sehingga tidak terbaca sempurna oleh PDF parser (PyPDFLoader).
2. **Terpotong *Stop Words***: Algoritma memotong pengambilan baris judul begitu menemui kata seperti "Oleh" atau "Skripsi". Jika baris judul di file asli mengandung kata-kata ini secara terbalik letaknya, judul bisa terpotong.
3. **Solusi**: Jika data ini krusial, pastikan metadata judul ada pada metadata bawaan file PDF sebelum digenerate, atau Anda bisa mengatur ulang file PDF-nya agar cover-nya dapat diseleksi teksnya secara normal. Format penamaan file `TAHUN_NAMA_PENULIS.pdf` sangat membantu mengamankan sebagian metadata jika covernya benar-benar tidak bisa terbaca.

## 🔧 Troubleshooting

### Error: "GROQ_API_KEY not found"

- Pastikan file `.env` sudah dibuat di folder `backend/`
- Pastikan API key sudah benar di `.env`
- Restart terminal atau server

### Error: "No vectors found"

- Jalankan `python scripts/build_index.py`
- Pastikan ada PDF di folder `data/pdf/`
- Pastikan PDF valid dan berisi abstrak

### Error: "CUDA out of memory"

- Set `EMBEDDING_DEVICE=cpu` di `.env`
- Atau batch size di `config.py` menjadi lebih kecil

## 📊 Performance Tips

1. **Caching**: Services menggunakan singleton pattern untuk caching
2. **Batch Processing**: Document chunking dalam batch di build_index
3. **Vector Search**: Menggunakan max_marginal_relevance_search untuk diversity
4. **Model Size**: multilingual-e5-small (~134MB) - ringan dan cepat

## 🎯 Next Steps

- [ ] Add frontend Vue.js
- [ ] Implement user logging dan history
- [ ] Add evaluation metrics (precision, recall)
- [ ] Optimize retrieval dengan reranking
- [ ] Add more LLM models support
- [ ] Database integration untuk persistence

## 📞 Support

Untuk bantuan lebih lanjut:

- 📖 FastAPI Docs: https://fastapi.tiangolo.com/
- 🦙 Groq Console: https://console.groq.com/
- 🔗 LangChain Docs: https://python.langchain.com/

---

**Version**: 1.0.0  
**Last Updated**: February 2026
