# 📚 Sistem Pencarian Judul & Abstrak Skripsi

README ini menjelaskan cara menjalankan dan mengembangkan project Pencarian Judul & Abstrak Skripsi (FastAPI backend + frontend).

**Ringkasan singkat**

- **Tujuan**: Menyediakan eksperimen retrieval dokumen (RAG, HyDE, & Hybrid) untuk mencari judul dan abstrak skripsi, plus mode chatbot interaktif.
- **Stack**: Python (FastAPI, LangChain, ChromaDB) untuk backend; React + Vite (frontend utama, frontend-v2) dan Vue 3 (frontend legacy) untuk frontend.

---

## Overview

- **Backend**: [backend/app/main.py](file:///c:/belajarku/semester%207/Sistem%20Pencarian%20Judul%20dan%20Abstrak%20Skripsi/backend/app/main.py) — FastAPI sebagai API server. Logika RAG di [backend/app/services/rag_service.py](file:///c:/belajarku/semester%207/Sistem%20Pencarian%20Judul%20dan%20Abstrak%20Skripsi/backend/app/services/rag_service.py).
- **Frontend utama**: [frontend-v2/](file:///c:/belajarku/semester%207/Sistem%20Pencarian%20Judul%20dan%20Abstrak%20Skripsi/frontend-v2) — UI React + Vite, berkomunikasi dengan endpoint `/api/chat`. Lihat detail di `frontend-v2/README.md`.
- **Frontend legacy**: [frontend/](file:///c:/belajarku/semester%207/Sistem%20Pencarian%20Judul%20dan%20Abstrak%20Skripsi/frontend) — UI minimal berbasis Vue 3.
- **Indexing**: Script `backend/scripts/build_index.py` membuat vector store di `backend/chroma_db/`.

### Struktur Direktori

```
Sistem Pencarian Judul dan Abstrak Skripsi/
├── backend/                  # FastAPI + RAG/HyDE/Hybrid + ChromaDB
│   ├── app/
│   │   ├── main.py           # Entry point FastAPI
│   │   ├── api/chat.py       # Endpoint /api/chat, /api/chatbot, /api/health, /api/info
│   │   ├── core/config.py    # Konfigurasi (env, model, path)
│   │   └── services/         # rag_service, embedding_service, document_service,
│   │                         # hybrid_utils, suggestion_service, chatbot_service
│   ├── scripts/build_index.py# Bangun indeks (hashing + checkpoint + --reset)
│   ├── data/pdf/             # Tempatkan file PDF skripsi di sini
│   ├── chroma_db/            # Vector store (dibuat saat build index)
│   └── evaluation/           # Dataset query & hasil evaluasi (Hit@K, MRR, dll.)
├── frontend-v2/              # UI React + Vite (utama)
├── frontend/                 # UI Vue 3 (legacy)
└── readme.md
```

---

## Fitur Utama

- **4 Mode Retrieval** di endpoint `/api/chat`:
  - `rag` — Standard RAG (embed query → pencarian vektor → LLM menyusun jawaban).
  - `hyde` — HyDE murni: LLM menyusun satu paragraf abstrak fiktif murni, kemudian di-embed untuk semantic search yang presisi.
  - `hybrid` — Hybrid Search (BM25 + ChromaDB + Metadata Filter) via `hybrid_utils.py`.
  - Mode ke-4 (asisten interaktif): endpoint terpisah `POST /api/chatbot` — Agentic RAG + Tool Calling dengan Gemini API untuk merekomendasikan judul baru, analisis research gap, dan diskusi ide penelitian.
- **100% Rule-Based Extraction**: Ekstraksi deterministik murni (Regex _Anchor-Based Slicing_ + _Word Splitting_ via `wordninja`) untuk memproses ribuan PDF tanpa batas kuota API LLM.
- **Anti-Duplikasi Vektor**: Hashing SHA-256 file PDF sebagai `ids` mutlak di ChromaDB + registry `data/processed_hashes.json`, sehingga re-index tidak menduplikasi data (dengan checkpointing per file).
- **Clean Build (Hard Reset)**: `python scripts/build_index.py --reset` menghapus basis data vektor dan registry hash untuk memulai dari nol.
- **Domain Filter & Quality Gate**: Kueri di luar domain Teknik Informatika ditolak; dokumen dengan abstrak < 300 karakter atau judul gagal slicing otomatis di-skip.

---

## Prerequisites

- Python 3.10+ (direkomendasikan)
- Node.js 20+ dan pnpm (atau npm/yarn)

---

## Backend — Setup & Run

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

Buat file `.env` di folder `backend/`:

```text
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here   # opsional, hanya untuk mode chatbot
# GEMINI_MODEL=gemini-flash-latest        # opsional
```

- `GROQ_API_KEY` — wajib untuk mode `hyde`/`hybrid` (LLM HyDE & sintesis jawaban RAG). Ekstraksi indeks tetap bebas LLM.
- `GEMINI_API_KEY` — hanya diperlukan jika memakai endpoint `/api/chatbot` (asisten interaktif).

**4) Bangun index (WAJIB sebelum server)**

Letakkan file PDF skripsi di `backend/data/pdf/` lalu jalankan:

```bash
cd backend
python scripts/build_index.py --reset
```

Proses ini mengekstrak teks, membuat embedding dengan model `intfloat/multilingual-e5-small`, dan menyimpan vektor ke `backend/chroma_db/`.

**5) Jalankan server**

```bash
cd backend
uvicorn app.main:app --reload
```

Endpoint dokumentasi tersedia di `http://localhost:8000/docs`.

---

## Frontend — Setup & Run

**Frontend utama (React, frontend-v2)** — lihat [`frontend-v2/README.md`](frontend-v2/README.md):

```bash
cd frontend-v2
pnpm install
pnpm dev
```

**Frontend legacy (Vue 3)**

```bash
cd frontend
pnpm install
pnpm dev
```

Default Vite dev server akan berjalan di `http://localhost:5173`. Pastikan backend sudah aktif di `http://127.0.0.1:8000` (URL di-hardcode di frontend).

---

## API — Ringkasan

- **POST /api/chat** — Endpoint utama pencarian. Request JSON:

```json
{
  "message": "kata kunci atau judul skripsi",
  "mode": "rag",
  "chat_history": []
}
```

  - `mode`: `"rag"` | `"hyde"` | `"hybrid"`
  - Response: `message` (narasi), `documents[]` (judul, abstrak, skor), `suggestion` (jika query berupa judul lengkap), `hypothetical_document` (khusus HyDE).

- **POST /api/chatbot** — Asisten interaktif (Agentic RAG + Tool Calling, Gemini). Request:

```json
{ "message": "Rekomendasikan ide skripsi tentang AI", "chat_history": [] }
```

  Response hanya teks narasi markdown (`message`), tanpa field `documents`.

- **GET /api/health** — Status server + jumlah vektor di ChromaDB.
- **GET /api/info** — Info sistem (model embedding, LLM, jumlah vektor).
- **GET /api/status** — Status & versi API.

---

## Evaluasi

Dataset query dan hasil evaluasi (Hit@K, MRR, perbandingan RAG vs HyDE) tersedia di `backend/evaluation/`. Script bantuan:

```bash
cd backend
python scripts/run_evaluation.py      # Jalankan evaluasi
python scripts/compare_hyde_prompts.py # Bandingkan prompt HyDE
python scripts/check_db.py            # Inspeksi isi ChromaDB
```

---

## Troubleshooting & Tips

- **GROQ_API_KEY not found**: pastikan `.env` ada di folder `backend/` dan berisi kunci. (Diperlukan untuk mode HyDE/Hybrid & sintesis jawaban; ekstraksi indeks bebas LLM).
- **No vectors found**: Pastikan Anda sudah menjalankan `python scripts/build_index.py` di dalam folder `backend`.
- **Ekstraksi Cacat/Gagal**: Sistem memiliki _Quality Gate_ ketat. Jika panjang abstrak kurang dari 300 karakter atau judul tidak lulus _Anchor-Based Slicing_, dokumen otomatis di-skip (tidak di-embed).
- **Frontend tidak bisa menghubungi backend**: backend harus aktif di `http://127.0.0.1:8000` (URL hardcoded di `frontend-v2/src/hooks/useSearch.js` dan `ChatContainer.jsx`).
- **Mode chatbot tidak berfungsi**: isi `GEMINI_API_KEY` di `backend/.env`.

---

## License & Contact

Project ini disiapkan sebagai eksperimen akademik. Untuk pertanyaan, hubungi penulis proyek.

<!-- struktur branch
- chatbot (uji coba chatbot skripsi pendukung mahasiswa)
- hybrid  (presentasikan jika diminta)
- rev (presentasi di hasil)-->
