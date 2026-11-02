# Backend - FastAPI Chatbot Pencarian Skripsi

Backend FastAPI untuk sistem pencarian judul dan abstrak skripsi menggunakan **RAG (Retrieval-Augmented Generation)** dan **HyDE (Hypothetical Document Embeddings)** dengan ChromaDB sebagai vector database.

## 🎯 Fitur Utama

- ✅ **RAG Standard**: Pencarian langsung dengan embedding query
- ✅ **HyDE RAG**: Pencarian dengan hypothetical document generation
- ✅ **Rule-Based Extraction**: Ekstraksi judul dan abstrak 100% lokal tanpa API LLM
- ✅ **Anchor-Based Slicing**: Ekstraksi judul yang robust terhadap OCR noise
- ✅ **Deduplication**: Pencegahan dokumen duplikat dengan SHA-256 hash
- ✅ **Multilingual Embedding**: Menggunakan `multilingual-e5-small`
- ✅ **Groq LLM Integration**: Response generation dengan Llama 3 via Groq API

## 📁 Struktur Folder

```
backend/
├── app/
│   ├── api/          # API routes dan endpoints
│   ├── core/         # Konfigurasi dan utilities
│   ├── services/     # Business logic (document, chat, RAG)
│   ├── __init__.py
│   └── main.py       # FastAPI application entry point
├── chroma_db/        # Vector database (auto-generated)
├── data/
│   └── pdf/          # Taruh file PDF skripsi di sini
├── evaluation/       # Script evaluasi performa
├── scripts/
│   └── build_index.py # Script untuk indexing PDF
├── venv/             # Virtual environment
├── .env              # Environment variables (buat dari .env.example)
├── .env.example      # Template environment variables
├── requirements.txt  # Python dependencies
├── render.yaml       # Konfigurasi deployment Render
└── run.sh            # Production startup script
```

## 🚀 Setup & Installation

### 1️⃣ Setup Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2️⃣ Install Dependencies

**Catatan untuk deployment (Render/VPS)**: Install torch CPU terlebih dahulu untuk menghindari download CUDA wheel (~2GB):

```bash
# Opsional (deployment): Install torch CPU
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install semua dependencies
pip install -r requirements.txt
```

**Dependencies Utama:**
- FastAPI 0.135.1 + Uvicorn 0.41.0
- LangChain 1.2.10 (community, core, groq, huggingface)
- ChromaDB 1.5.2
- Sentence Transformers 5.2.3
- PyTorch 2.10.0
- PyMuPDF 1.28.0
- Wordninja 2.0.0

### 3️⃣ Setup Environment Variables

1. Copy file `.env.example` menjadi `.env`
2. Edit file `.env` dan isi dengan konfigurasi Anda:

```env
# API key dari https://console.groq.com (WAJIB)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Development mode (aktifkan uvicorn reload + lazy-load)
# Set "false" untuk production
DEBUG=false

# Jumlah worker uvicorn (Plan Free 512MB RAM = 1)
WORKERS=1

# (Opsional) Custom ChromaDB location
# CHROMA_PERSIST_DIR=/var/data/skripsi/chroma_db
```

### 4️⃣ Siapkan Data PDF

Letakkan file PDF skripsi di folder `data/pdf/`. Sistem akan mengekstrak judul dan abstrak dari halaman pertama.

## 🔧 Menjalankan Aplikasi

### Step 1: Build ChromaDB Index

**PENTING**: Jalankan ini setiap kali menambah PDF baru atau pertama kali setup.

```bash
# Clean build (hapus index lama dan buat dari nol)
python scripts/build_index.py --reset

# Incremental build (hanya proses PDF baru)
python scripts/build_index.py
```

**Proses yang dilakukan:**
1. ✅ Load semua PDF dari `data/pdf/`
2. ✅ Extract judul dengan **Anchor-Based Slicing**
3. ✅ Extract abstrak dengan **Rule-Based Pipeline**
4. ✅ Validasi dengan **Quality Gate** (min 300 karakter abstrak)
5. ✅ Cegah duplikasi menggunakan **SHA-256 File Hash**
6. ✅ Generate embedding dengan `multilingual-e5-small`
7. ✅ Simpan vectors ke ChromaDB di `chroma_db/`
8. ✅ Record processed hashes ke `processed_hashes.json`

### Step 2: Jalankan FastAPI Server

```bash
# Development mode (hot reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Atau gunakan script production
./run.sh  # Linux/Mac
```

**Server URLs:**
- 🌐 API Base: `http://localhost:8000`
- 📚 Swagger Docs: `http://localhost:8000/docs`
- 🔍 ReDoc: `http://localhost:8000/redoc`

## 📡 API Endpoints

### 1. Health Check
```
GET /
```

Response:
```json
{
  "message": "Backend is running",
  "status": "ok"
}
```

### 2. Chat/Search Endpoint
```
POST /api/chat
```

**Request Body:**
```json
{
  "message": "sistem rekomendasi",
  "mode": "rag",
  "chat_history": []
}
```

**Parameters:**
- `message` (string, required): Query pencarian
- `mode` (string, optional): Mode pencarian
  - `"rag"` - Standard RAG (default, lebih cepat)
  - `"hyde"` atau `"HyDE"` - HyDE RAG (lebih baik untuk query luas)
- `chat_history` (array, optional): History percakapan sebelumnya

**Response:**
```json
{
  "response": "Berikut adalah skripsi terkait sistem rekomendasi...",
  "sources": [
    {
      "title": "Sistem Rekomendasi Film Menggunakan Collaborative Filtering",
      "abstract": "Penelitian ini membahas...",
      "metadata": {...}
    }
  ],
  "mode": "rag"
}
```

## 🧠 Cara Kerja

### Standard RAG Mode
1. User query langsung di-embed menggunakan `multilingual-e5-small`
2. Similarity search di ChromaDB untuk menemukan dokumen relevan
3. LLM (Llama 3) generate response berdasarkan context dokumen
4. ⚡ **Keuntungan**: Lebih cepat dan efisien

### HyDE RAG Mode
1. LLM generate hypothetical abstract berdasarkan query user
2. Hypothetical abstract di-embed (bukan query asli)
3. Similarity search menggunakan embedding hypothetical document
4. LLM generate final response dengan context dokumen yang ditemukan
5. ⚡ **Keuntungan**: Lebih baik untuk query awam atau sangat luas

## 🔍 Pipeline Ekstraksi PDF (100% Rule-Based)

Sistem menggunakan pipeline deterministik lokal **tanpa API LLM**, dikelola oleh `document_service.py`.

### 1. Pemuatan & Pemisahan Halaman
- Menggunakan `PyPDFLoader` (LangChain wrapper untuk PyMuPDF)
- Halaman pertama (cover) → ekstrak metadata (judul, penulis, dll)
- Halaman abstrak → `page_content`

### 2. Ekstraksi Judul (Anchor-Based Slicing)
**Algoritma:**
- Ambil teks dari awal hingga kata anchor ("SKRIPSI", "DIAJUKAN", "TUGAS AKHIR")
- Flatten semua `\n` dan spasi berlebih
- Spelling correction dengan hardcoded dictionary (misal: "IMPLEMENT ASI" → "IMPLEMENTASI")
- **Quality Gate Validation**: Validasi panjang (5-200 char) dan komposisi huruf (>30%)

### 3. Ekstraksi Abstrak (Guillotine Algorithm & Wordninja)
- Potong teks tepat setelah kata "Abstrak"
- Buang nama pembimbing dengan Regex
- Perbaiki kata terputus spasi menggunakan `wordninja` (probabilistic word splitting)
- Validasi minimal 300 karakter untuk lolos Quality Gate

### 4. Pencegahan Duplikasi
- Setiap PDF dihitung **SHA-256 hash**-nya
- Hash digunakan sebagai `ids` di ChromaDB
- Hash tersimpan di `processed_hashes.json`
- Dokumen yang gagal Quality Gate juga direcord agar tidak diproses ulang

### 5. Embedding & Storage
- Judul + Abstrak digabung: `"Judul: ...\n\nAbstrak:\n..."`
- Tidak ada chunking berlebih (satu dokumen = satu embedding)
- Embedding menggunakan `multilingual-e5-small` (384 dimensions)
- Vectors disimpan di ChromaDB dengan metadata lengkap

## 🔧 Troubleshooting

### Error: "No vectors found in ChromaDB"
**Solusi:**
```bash
python scripts/build_index.py --reset
```
Pastikan ada PDF di `data/pdf/` yang lolos Quality Gate.

### Error: "GROQ_API_KEY not found"
**Solusi:**
1. Buka file `.env`
2. Pastikan ada baris: `GROQ_API_KEY=gsk_...`
3. Dapatkan API key gratis di https://console.groq.com

### PDF tidak ter-index
**Kemungkinan:**
1. Abstrak terlalu pendek (<300 karakter)
2. Judul tidak terdeteksi (tidak ada anchor keyword)
3. Format PDF tidak standar

**Solusi:**
- Cek log saat menjalankan `build_index.py`
- Cek `processed_hashes.json` untuk status dokumen
- Pastikan PDF memiliki struktur standar (cover page dengan judul + halaman abstrak)

### Server lambat saat startup
**Normal behavior**: Embedding model (`multilingual-e5-small`) perlu di-load ke memory (~400MB). 
Di production dengan `DEBUG=false`, model di-load saat startup. Di development, lazy loading aktif.

## 📊 Evaluasi & Testing

Folder `evaluation/` berisi script untuk mengukur performa:
- Precision, Recall, F1-Score
- Latency pengambilan dokumen
- Kualitas response LLM

## 🚀 Deployment

### Render.com
1. Push repository ke GitHub
2. Connect Render dengan repository
3. Set environment variables di Render Dashboard:
   - `GROQ_API_KEY`
   - `DEBUG=false`
   - `WORKERS=1`
4. Build command: `pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt`
5. Start command: `./run.sh`

### VPS/Server Mandiri
```bash
# Clone repository
git clone <repo-url>
cd backend

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup .env
cp .env.example .env
# Edit .env dengan konfigurasi Anda

# Build index
python scripts/build_index.py --reset

# Run with systemd/supervisor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

## 📝 Lisensi & Contact

Bagian dari proyek akademik **Sistem Pencarian Judul & Abstrak Skripsi** Teknik Informatika.

---
**Last Updated**: November 2026 | FastAPI 0.135.1 | LangChain 1.2.10 | ChromaDB 1.5.2
