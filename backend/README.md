# Backend - FastAPI Chatbot Pencarian Skripsi

Implementasi backend FastAPI untuk chatbot pencarian judul dan abstrak skripsi dengan menggunakan RAG (Retrieval-Augmented Generation) dan HyDE approach murni.

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

## 🚀 Menjalankan Aplikasi

### Step 1: Build Index ChromaDB

**PENTING**: Jalankan ini ketika menambah PDF baru. Untuk melakukan *clean build* (menghapus index lama dan membuat dari nol), gunakan flag `--reset`.

```bash
python scripts/build_index.py --reset
```

Proses ini akan:
- ✅ Load PDF dari `data/pdf/`
- ✅ Extract judul dengan **Anchor-Based Slicing** dan abstrak dengan **Rule-Based pipeline**
- ✅ Mencegah duplikasi data menggunakan **File Hash**
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

## 🧠 Logika Chatbot

### Standard RAG
- Langsung retrieve dokumen relevan dari database ChromaDB.
- Lebih cepat dan efisien.

### HyDE RAG (Murni)
- Generate sebuah abstrak fiktif murni menggunakan LLM (Llama 3 via Groq API) berdasarkan kueri pengguna.
- Embed teks abstrak fiktif tersebut dan cari kemiripannya (*cosine similarity*) dengan dokumen asli di ChromaDB.
- Lebih baik untuk topik awam atau kueri yang sangat luas.

## ⚙️ Pipeline Pemrosesan PDF & Ekstraksi (100% Rule-Based)

Sistem kini menggunakan pipeline ekstraksi deterministik lokal **tanpa memotong batas API LLM**, ditangani oleh `document_service.py`.

### 1. Pemuatan & Pemisahan Halaman
Menggunakan `PyPDFLoader`, teks dari halaman pertama (cover) digunakan untuk mengekstrak metadata, sedangkan halaman abstrak untuk `page_content`.

### 2. Ekstraksi Metadata (Anchor-Based Slicing)
Pola yang digunakan untuk mengekstrak judul secara beringas dari *newline* dan *OCR noise*:
- **Anchor-Based Slicing**: Judul dipotong dari awal teks sampai ditemukannya kata anchor seperti "SKRIPSI", "DIAJUKAN", atau "TUGAS AKHIR". Seluruh *newline* (\n) dan spasi berlebih diratakan (*flattened*).
- **Spelling Correction**: Menggunakan hardcode dictionary untuk menyatukan kata cacat (misal: "IMPLEMENT ASI" -> "IMPLEMENTASI").
- **Quality Gate Validation**: Judul divalidasi panjang dan komposisi hurufnya. Jika gagal, dokumen akan ditolak.

### 3. Pembersihan Abstrak (Algoritma Guillotine & Wordninja)
- Memotong teks secara tegas tepat setelah ditemukannya kata "Abstrak" dan membuang nama pembimbing menggunakan *Regex*.
- Penggabungan kata yang terputus spasi akibat format PDF diperbaiki secara probabilistik menggunakan librari `wordninja`.

### 4. Pencegahan Duplikasi & Checkpointing
Setiap file PDF akan dihitung hash SHA-256 nya. Hash ini digunakan sebagai `ids` utama dalam ChromaDB dan direkam di `processed_hashes.json`. Dokumen cacat/sampah akan disematkan status hash-nya sehingga eksekusi *script* besok harinya tidak akan pernah memproses dokumen buruk yang sama.

### 5. Embedding
Judul dan Abstrak disatukan (tanpa *chunking* berlebih) menjadi satu blok teks (Contoh: `"Judul: ...\n\nAbstrak:\n..."`) dan diubah menjadi vektor oleh `multilingual-e5-small`.

## 🔧 Troubleshooting

### Error: "No vectors found"
- Jalankan `python scripts/build_index.py --reset` di folder `backend/`
- Pastikan ada PDF di folder `data/pdf/` yang lolos *Quality Gate* (abstrak > 300 karakter).

---
**Last Updated**: February 2026
