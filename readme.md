# 📚 Sistem Pencarian Judul & Abstrak Skripsi

README ini menjelaskan cara menjalankan dan mengembangkan project Chatbot Pencarian Judul & Abstrak Skripsi (FastAPI backend + Vue.js frontend).

**Ringkasan singkat**

- **Tujuan**: Menyediakan eksperimen retrieval dokumen (RAG & HyDE) untuk mencari judul dan abstrak skripsi.
- **Stack**: Python (FastAPI, LangChain, ChromaDB) untuk backend; Vue 3 + Vite untuk frontend.

---

**Overview**

- **Backend**: [backend/app/main.py](file:///c:/belajarku/semester%207/Sistem%20Pencarian%20Judul%20dan%20Abstrak%20Skripsi/backend/app/main.py) — FastAPI sebagai API server, RAG logic di [backend/app/services/rag_service.py](file:///c:/belajarku/semester%207/Sistem%20Pencarian%20Judul%20dan%20Abstrak%20Skripsi/backend/app/services/rag_service.py).
- **Frontend**: [frontend/](file:///c:/belajarku/semester%207/Sistem%20Pencarian%20Judul%20dan%20Abstrak%20Skripsi/frontend) — UI minimal berbasis Vue 3, berkomunikasi dengan endpoint `/api/chat`.
- **Indexing**: Script `backend/scripts/build_index.py` membuat vector store di `backend/chroma_db/`.

---

**Fitur Utama (Terbaru)**

- **100% Rule-Based Extraction**: Menggunakan ekstraksi deterministik murni, Regex _Anchor-Based Slicing_, dan _Word Splitting_ (`wordninja`) untuk memproses ribuan PDF tanpa batas kuota API LLM.
- **HyDE Murni (Hypothetical Document Embeddings)**: Mode HyDE memanggil Groq LLM secara efisien untuk menyusun _satu paragraf abstrak fiktif murni_, lalu mengonversinya menjadi vektor untuk pencarian _semantic search_ yang sangat presisi.
- **Anti-Duplikasi Vektor**: Menggunakan _hashing_ file PDF sebagai `ids` mutlak di ChromaDB sehingga _re-index_ tidak akan pernah menduplikasi data.
- **Clean Build (Hard Reset)**: Tersedia opsi perintah `python scripts/build_index.py --reset` untuk menghapus basis data vektor dan _registry hash_ untuk memulai pembangunan indeks bersih dari nol.

---

**Prerequisites**

- Python 3.10+ (direkomendasikan)
- Node.js 20+ dan pnpm (atau npm/yarn)

---

**Backend — Setup & Run**

**1) Buat virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

**2) Install dependencies**

```bash
pip install -r backend/requirements.txt
```

**3) Konfigurasi environment**
Buat file `.env` di folder `backend/` berisi minimal:

```text
GROQ_API_KEY=your_groq_api_key_here
```

**4) Bangun index (WAJIB sebelum server)**
Letakkan file PDF skripsi di `backend/data/pdf/` lalu jalankan:

```bash
cd backend
python scripts/build_index.py --reset
```

Proses ini akan mengekstrak teks, membuat embedding dengan model `intfloat/multilingual-e5-small`, dan menyimpan vector ke `backend/chroma_db/`.

**5) Jalankan server**

```bash
cd backend
uvicorn app.main:app --reload
```

Endpoint dokumentasi tersedia di `http://localhost:8000/docs`.

---

**Frontend — Setup & Run**

Masuk ke folder `frontend/` lalu install deps dan jalankan dev server:

```bash
cd frontend
pnpm install
pnpm dev
```

Default Vite dev server akan berjalan (biasanya) di `http://localhost:5173`.

---

**API — Ringkasan**

- **POST /api/chat** — Endpoint utama chat. Request JSON:

```json
{
  "message": "kata kunci atau judul skripsi",
  "mode": "rag"    # atau "hyde"
}
```

---

**Troubleshooting & Tips**

- **GROQ_API_KEY not found**: pastikan `.env` ada di folder `backend/` dan berisi kunci. (Hanya diperlukan untuk mode HyDE, ekstraksi kini bebas LLM).
- **No vectors found**: Pastikan Anda sudah menjalankan `python scripts/build_index.py` di dalam folder `backend`.
- **Ekstraksi Cacat/Gagal**: Sistem baru memiliki _Quality Gate_ ketat. Jika panjang abstrak kurang dari 300 karakter atau judul tidak lulus _Anchor-Based Slicing_, dokumen otomatis di-skip (tidak di-embed).

---

**License & Contact**
Project ini disiapkan sebagai eksperimen akademik. Untuk pertanyaan, hubungi penulis proyek.

<!-- struktur branch
- chatbot (uji coba chatbot skripsi pendukung mahasiswa)
- hybrid  (presentasikan jika diminta)
- rev (presentasi di hasil)-->
