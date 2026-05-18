# 📚 Dokumentasi Sistem Pencarian Judul dan Abstrak Skripsi

> **Chatbot Pencarian Judul & Abstrak Skripsi**  
> Teknik Informatika — UIN Alauddin Makassar  
> Versi: 1.0.0

---

## 📋 Daftar Isi

1. [Gambaran Umum Sistem](#1-gambaran-umum-sistem)
2. [Arsitektur Sistem](#2-arsitektur-sistem)
3. [Technology Stack](#3-technology-stack)
4. [Perangkat Lunak & Library yang Digunakan](#4-perangkat-lunak--library-yang-digunakan)
5. [Spesifikasi AI/ML](#5-spesifikasi-aiml)
6. [Struktur Direktori Proyek](#6-struktur-direktori-proyek)
7. [Detail Backend](#7-detail-backend)
8. [Detail Frontend](#8-detail-frontend)
9. [Alur Kerja Sistem (Pipeline)](#9-alur-kerja-sistem-pipeline)
10. [API Endpoints](#10-api-endpoints)
11. [Konfigurasi Sistem](#11-konfigurasi-sistem)
12. [Cara Menjalankan](#12-cara-menjalankan)

---

## 1. Gambaran Umum Sistem

Sistem ini adalah **chatbot berbasis web** yang membantu mahasiswa Teknik Informatika UIN Alauddin Makassar dalam mencari judul dan abstrak skripsi yang relevan dengan topik penelitian mereka. Sistem menggunakan pendekatan **RAG (Retrieval-Augmented Generation)** untuk menggabungkan pencarian dokumen berbasis vektor dengan kemampuan generasi teks dari LLM (Large Language Model).

### Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **Pencarian Semantik** | Mencari skripsi berdasarkan kesamaan makna (bukan keyword exact match) |
| **Dua Mode Pencarian** | Standard RAG dan HyDE (Hypothetical Document Embeddings) |
| **Chatbot Natural Language** | Respon dalam bahasa Indonesia yang natural dan informatif |
| **Saran Akademik** | Memberikan saran berdasarkan judul skripsi yang diajukan |
| **Riwayat Percakapan** | Memahami konteks dari percakapan sebelumnya (follow-up question) |
| **Rendering Markdown** | Menampilkan tabel, bold, list, dan format lainnya di chat |
| **Responsive UI** | Mendukung desktop (sidebar) dan mobile (drawer) |
| **Dark Mode Ready** | Tema gelap diimplementasikan melalui Tailwind CSS |

---

## 2. Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Vue.js 3)                        │
│  ┌──────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │
│  │ InputChat│  │  MainChat  │  │  Sidebar   │  │  DrawerMenu    │  │
│  │  .vue    │  │   .vue     │  │   .vue     │  │    .vue        │  │
│  └────┬─────┘  └─────┬──────┘  └─────┬──────┘  └───────┬────────┘  │
│       │              │               │                  │           │
│  ┌────▼──────────────▼───────────────▼──────────────────▼────────┐  │
│  │              Composables (useChatbot.js, useSearchMode.js)    │  │
│  └─────────────────────────────┬────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────┘
                                 │ HTTP POST /api/chat
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                             │
│  ┌───────────┐                                                      │
│  │  chat.py  │ ◄── API Router (endpoint /api/chat)                 │
│  └─────┬─────┘                                                      │
│        │                                                            │
│  ┌─────▼──────────────────────────────────────────────────────────┐ │
│  │                     RAG Service                                │ │
│  │  ┌──────────────────┐    ┌──────────────────────────────────┐  │ │
│  │  │  Standard RAG    │    │  HyDE RAG                       │  │ │
│  │  │  (MMR Search)    │    │  (Hypothetical Doc + Embedding) │  │ │
│  │  └────────┬─────────┘    └─────────────┬────────────────────┘  │ │
│  └───────────┼────────────────────────────┼───────────────────────┘ │
│              │                            │                         │
│  ┌───────────▼────────────────────────────▼───────────────────────┐ │
│  │                    ChromaDB (Vector Store)                     │ │
│  │              Menyimpan embedding dokumen skripsi               │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                     │
│  ┌───────────────────────────▼───────────────────────────────────┐ │
│  │              Embedding Service (HuggingFace)                  │ │
│  │          Model: intfloat/multilingual-e5-small                │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │               Suggestion Service (Groq LLM)                  │ │
│  │          Generasi respon chatbot + saran akademik             │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │ build_index.py
                                 │ (Preprocessing & Indexing)
                                 │
┌────────────────────────────────┴────────────────────────────────────┐
│                     DATA SOURCE                                     │
│              Folder: backend/data/pdf/                              │
│              File PDF skripsi mahasiswa                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### Backend

| Teknologi | Versi/Detail | Fungsi |
|-----------|-------------|--------|
| **Python** | 3.x | Bahasa pemrograman utama backend |
| **FastAPI** | Latest | Web framework untuk REST API |
| **Uvicorn** | Standard | ASGI server untuk menjalankan FastAPI |
| **LangChain** | Latest | Framework orkestrasi LLM & RAG pipeline |
| **LangChain-Groq** | Latest | Integrasi LangChain dengan Groq API |
| **LangChain-HuggingFace** | Latest | Integrasi LangChain dengan HuggingFace Embeddings |
| **LangChain-Community** | Latest | Extension komunitas LangChain (termasuk ChromaDB loader) |
| **ChromaDB** | Latest | Vector database untuk menyimpan embedding |
| **Sentence-Transformers** | ≥ 2.6.0 | Library untuk embedding model |
| **PyPDF** | Latest | Parser/loader untuk file PDF |
| **PyTorch (Torch)** | Latest | Backend untuk model embedding |
| **python-dotenv** | Latest | Memuat environment variables dari file `.env` |

### Frontend

| Teknologi | Versi/Detail | Fungsi |
|-----------|-------------|--------|
| **Vue.js** | 3.5.28 | Framework JavaScript reaktif (Composition API) |
| **Vite** | Beta | Build tool & dev server |
| **Vue Router** | 5.0.2 | Client-side routing |
| **Pinia** | 3.0.4 | State management |
| **Tailwind CSS** | 4.2.0 | Utility-first CSS framework |
| **Marked** | 17.0.3 | Library parser Markdown ke HTML |
| **pnpm** | — | Package manager |
| **Vitest** | 4.0.18 | Unit testing framework |
| **Prettier** | 3.8.1 | Code formatter |
| **Google Fonts (Lexend)** | — | Font utama UI |
| **Material Symbols Outlined** | — | Icon set |

---

## 4. Perangkat Lunak & Library yang Digunakan

### 4.1 LangChain (Ya, Digunakan ✅)

Sistem ini **menggunakan LangChain** sebagai framework orkestrasi utama. Berikut package LangChain yang digunakan:

```
langchain                  → Core framework LangChain
langchain-community        → Integrasi komunitas (ChromaDB vectorstore, PyPDFLoader)
langchain-core             → Core abstractions (Document, dll)
langchain-groq             → Wrapper LLM untuk Groq API (ChatGroq)
langchain-huggingface      → Wrapper embedding HuggingFace (HuggingFaceEmbeddings)
```

**Penggunaan LangChain dalam sistem:**

| Komponen LangChain | Digunakan Di | Fungsi |
|---------------------|-------------|--------|
| `PyPDFLoader` | `document_service.py` | Memuat dan mengekstrak teks dari file PDF |
| `Document` | `document_service.py` | Representasi dokumen dengan metadata |
| `HuggingFaceEmbeddings` | `embedding_service.py` | Mengubah teks menjadi vektor embedding |
| `Chroma` | `rag_service.py`, `build_index.py` | Vector store untuk menyimpan dan query embedding |
| `ChatGroq` | `rag_service.py`, `suggestion_service.py` | LLM client untuk generasi teks via Groq API |

### 4.2 ChromaDB

- **Tipe:** Vector database lokal (persistent storage)
- **Lokasi penyimpanan:** `backend/chroma_db/`
- **Fungsi:** Menyimpan embedding vektor dari dokumen skripsi dan melakukan similarity search

### 4.3 PyPDF

- Digunakan melalui `PyPDFLoader` dari LangChain Community
- Memuat file PDF halaman per halaman
- Mengekstrak teks dari halaman sampul (cover) untuk judul dan identitas, serta halaman isi untuk abstrak

---

## 5. Spesifikasi AI/ML

### 5.1 Large Language Model (LLM)

| Parameter | Detail |
|-----------|--------|
| **Provider** | **Groq** (Cloud API — [https://console.groq.com](https://console.groq.com)) |
| **Model** | `openai/gpt-oss-20b` |
| **Temperature** | `0.2` (RAG Service), `0.3` (Suggestion Service — sedikit lebih kreatif) |
| **API Key** | Disimpan di file `backend/.env` (`GROQ_API_KEY`) |
| **Wrapper** | `ChatGroq` dari package `langchain-groq` |

> **Catatan:** Meskipun di endpoint `/api/info` tertulis `meta-llama/llama-3-70b-versatile`, konfigurasi aktual di `config.py` menggunakan model `openai/gpt-oss-20b`. Ini kemungkinan merupakan ketidakkonsistenan yang belum diperbarui.

**Fungsi LLM dalam sistem:**
1. **HyDE RAG** — Menghasilkan abstrak hipotetikal berdasarkan query user untuk pencarian semantik yang lebih baik
2. **Chat Response** — Menghasilkan respon chatbot yang natural dan informatif dalam bahasa Indonesia
3. **Saran Akademik** — Memberikan saran akademik (relevansi judul, pengembangan metode, rekomendasi dataset, dll.)

### 5.2 Embedding Model

| Parameter | Detail |
|-----------|--------|
| **Model** | `intfloat/multilingual-e5-small` |
| **Provider** | HuggingFace (Sentence Transformers) |
| **Device** | `cpu` (default), bisa diubah ke `cuda` untuk GPU |
| **Normalisasi** | `normalize_embeddings: True` |
| **Wrapper** | `HuggingFaceEmbeddings` dari package `langchain-huggingface` |
| **Pattern** | Singleton (hanya di-load sekali) |

**Mengapa model ini dipilih:**
- `multilingual-e5-small` mendukung **bahasa Indonesia** (multilingual)
- Ukuran kecil (`small`) sehingga ringan dijalankan di CPU
- Cocok untuk tugas semantic similarity dan retrieval

### 5.3 Retrieval Configuration

| Parameter | Nilai | Deskripsi |
|-----------|-------|-----------|
| `K_RETRIEVAL` | 5 | Jumlah dokumen yang dikembalikan ke user |
| `FETCH_K` | 20 | Jumlah dokumen kandidat untuk filtering awal (digunakan oleh MMR) |

### 5.4 Mode Pencarian

#### a. Standard RAG Mode
- Menggunakan **Max Marginal Relevance (MMR) Search**
- Query user langsung di-embed dan dicocokkan dengan vektor di ChromaDB
- MMR memastikan hasil yang relevan sekaligus beragam (menghindari duplikasi)

#### b. HyDE Mode (Hypothetical Document Embeddings)
- LLM terlebih dahulu menghasilkan **abstrak hipotetikal** berdasarkan query user
- Abstrak hipotetikal tersebut yang di-embed (bukan query asli)
- Vektor dari abstrak hipotetikal digunakan untuk **similarity search** di ChromaDB
- Cocok untuk query yang samar atau umum karena menghasilkan representasi yang lebih kaya

---

## 6. Struktur Direktori Proyek

```
Sistem Pencarian Judul dan Abstrak Skripsi/
├── backend/
│   ├── .env                          # Environment variables (API key Groq)
│   ├── requirements.txt              # Daftar dependensi Python
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Entry point FastAPI
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── chat.py               # Endpoint /api/chat, /api/health, /api/info
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py             # Konfigurasi (model, path, Groq key)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── document_service.py   # Preprocessing & ekstraksi PDF
│   │       ├── embedding_service.py  # Singleton embedding model
│   │       ├── rag_service.py        # Standard RAG & HyDE RAG logic
│   │       └── suggestion_service.py # Chatbot response & saran akademik
│   ├── scripts/
│   │   └── build_index.py            # Script membuat index ChromaDB
│   ├── data/
│   │   └── pdf/                      # Folder berisi file PDF skripsi
│   └── chroma_db/                    # Persistent ChromaDB storage
│
├── frontend/
│   ├── index.html                    # Entry HTML
│   ├── package.json                  # Dependensi Node.js
│   ├── vite.config.js                # Konfigurasi Vite
│   ├── tailwind.config.js            # Konfigurasi Tailwind CSS
│   ├── src/
│   │   ├── main.js                   # Entry point Vue.js
│   │   ├── App.vue                   # Root component
│   │   ├── assets/
│   │   │   └── main.css              # Global CSS + Tailwind theme
│   │   ├── composables/
│   │   │   ├── useChatbot.js         # Logic chatbot (send/receive message)
│   │   │   ├── useSearchMode.js      # State mode pencarian (rag/hyde)
│   │   │   └── useData.js            # (Kosong — belum diimplementasi)
│   │   ├── components/
│   │   │   ├── MainChat.vue          # Area chat utama (bubble + markdown)
│   │   │   ├── InputChat.vue         # Input pesan + auto-resize textarea
│   │   │   ├── HeaderChat.vue        # Header dengan status online
│   │   │   ├── Sidebar.vue           # Panel kontrol desktop (mode pencarian)
│   │   │   ├── DrawerMenu.vue        # Drawer mobile (panel kontrol)
│   │   │   ├── ChatArea.vue          # (Versi lama, tidak aktif digunakan)
│   │   │   ├── InputArea.vue         # (Versi lama, tidak aktif digunakan)
│   │   │   ├── Header.vue            # (Versi lama, tidak aktif digunakan)
│   │   │   └── Drawer.vue            # (Versi lama, tidak aktif digunakan)
│   │   ├── layouts/
│   │   │   ├── ChatLayout.vue        # Layout aktif (Sidebar + Header + Main + Input)
│   │   │   └── MainLayout.vue        # (Layout lama, tidak aktif)
│   │   ├── views/
│   │   │   ├── HomeView.vue          # (Tidak aktif digunakan, App.vue langsung ke ChatLayout)
│   │   │   └── AboutView.vue         # (Halaman About, belum diimplementasi)
│   │   ├── stores/
│   │   │   └── counter.js            # (Default Pinia store, belum digunakan)
│   │   └── router/
│   │       └── index.js              # Vue Router (rute / dan /about)
│   └── dist/                         # Build output
│
├── .gitignore
└── readme.md
```

---

## 7. Detail Backend

### 7.1 Entry Point — `main.py`

- Menggunakan **FastAPI** sebagai web framework
- CORS middleware di-enable untuk semua origin (`*`) agar frontend bisa berkomunikasi
- Server dijalankan via **Uvicorn** di `host=0.0.0.0`, `port=8000`
- Mode debug aktif (hot-reload) saat development
- Endpoint root (`/`) menampilkan welcome message dan link ke docs

### 7.2 API Layer — `chat.py`

File ini mendefinisikan endpoint-endpoint API menggunakan `APIRouter` dengan prefix `/api`.

**Request/Response Model (Pydantic):**

```python
# Request
class ChatRequest:
    message: str                    # Pesan dari user
    mode: str = "rag"              # Mode pencarian: "rag" atau "hyde"
    chat_history: list = []         # Riwayat percakapan (max 10 terakhir)

# Response
class ChatResponse:
    success: bool                   # Berhasil/gagal
    message: str                    # Respon chatbot (format markdown)
    query: str                      # Query asli user
    mode: str                       # Mode yang digunakan
    documents: list = []            # List dokumen yang ditemukan
    suggestion: str | None = None   # Saran akademik (jika ada)
```

### 7.3 Document Service — `document_service.py`

Service ini bertanggung jawab untuk **memuat dan memproses file PDF skripsi**:

1. **`load_documents_from_folder()`** — Scan semua PDF di folder `data/pdf/`
2. **`extract_title()`** — Mengekstrak judul dari halaman sampul (cover) menggunakan stop words
3. **`extract_identity()`** — Mengekstrak Nama dan NIM menggunakan regex
4. **`extract_abstract()`** — Mengekstrak abstrak menggunakan regex pattern
5. **`clean_text()`** — Membersihkan noise (nama universitas, keterangan sampul, dll.)

**Validasi dokumen:**
- PDF harus minimal 2 halaman (cover + isi)
- Abstrak harus minimal 100 karakter
- Judul dibatasi maksimal 150 karakter

**Format output per dokumen:**
```
Judul: [Judul Skripsi]
Nama: [Nama Mahasiswa] | NIM: [NIM]

Abstrak:
[Isi Abstrak]
```

### 7.4 Embedding Service — `embedding_service.py`

- Mengimplementasikan **Singleton Pattern** — model hanya di-load sekali
- Memuat model `intfloat/multilingual-e5-small` dari HuggingFace
- Menyediakan fungsi:
  - `get_embedding_function()` — Mengembalikan embedding function untuk ChromaDB
  - `embed_text(text)` — Embed satu teks ke vektor
  - `embed_texts(texts)` — Embed batch teks ke vektor

### 7.5 RAG Service — `rag_service.py`

Service inti yang menangani **retrieval dokumen**:

#### Standard RAG (`standard_rag()`)
```
User Query → Embed Query → MMR Search di ChromaDB → Return Top-K Dokumen
```
- Menggunakan `max_marginal_relevance_search` untuk hasil yang relevan dan beragam
- Parameter: `k=5`, `fetch_k=20`

#### HyDE RAG (`hyde_rag()`)
```
User Query → LLM Generate Hypothetical Abstract → Embed Hypothetical → Similarity Search → Return Top-K Dokumen
```
- LLM menghasilkan abstrak fiktif 3-4 kalimat berdasarkan topik
- Abstrak fiktif di-embed ke vektor
- Vektor digunakan untuk similarity search di ChromaDB

### 7.6 Suggestion Service — `suggestion_service.py`

Menangani dua fungsi utama menggunakan LLM:

#### a. `generate_chat_response()` — Respon Chatbot
- Menerima query, dokumen hasil retrieval, mode, dan riwayat percakapan
- Memformat respon dalam **tabel Markdown** (No, Judul, Sumber, Ringkasan)
- Mendukung **follow-up question** berdasarkan riwayat percakapan (max 10 pesan terakhir)
- Berbahasa Indonesia yang ramah dan natural

#### b. `generate_suggestion()` — Saran Akademik
- Di-trigger jika pesan user > 50 karakter DAN mengandung keyword tertentu (`sistem`, `aplikasi`, `implementasi`, dll.)
- Memberikan 3-5 poin saran meliputi:
  1. Relevansi judul dengan penelitian sebelumnya
  2. Potensi pengembangan metode/algoritma
  3. Saran dataset atau tools
  4. Kelebihan dan kekurangan judul
  5. Rekomendasi modifikasi judul

### 7.7 Build Index Script — `build_index.py`

Script CLI untuk membangun ChromaDB index **sebelum menjalankan server**:

```
1. Scan folder data/pdf/ untuk file PDF
2. Proses setiap PDF (extract judul, identitas, abstrak)
3. Bersihkan teks dari noise
4. Buat Document objects dengan metadata
5. Hapus ChromaDB lama (jika ada)
6. Buat ChromaDB baru
7. Embed dokumen dalam batch (batch_size=5)
8. Persist ke disk
9. Verifikasi jumlah vektor tersimpan
```

---

## 8. Detail Frontend

### 8.1 Arsitektur Frontend

Frontend menggunakan **Vue.js 3 Composition API** dengan struktur:

```
App.vue → ChatLayout.vue → Sidebar + HeaderChat + MainChat + InputChat
```

### 8.2 Layout — `ChatLayout.vue` (Aktif)

Layout utama yang menggabungkan semua komponen:
- **Desktop (lg+):** Sidebar di kiri + konten utama di kanan
- **Mobile:** DrawerMenu (slide dari kiri) + HeaderChat (tombol hamburger)

### 8.3 Komponen Utama

#### `MainChat.vue` (330 baris)
Komponen terbesar — menampilkan area chat:
- **Empty State:** Icon animasi, teks selamat datang, contoh pencarian (clickable)
- **Chat Messages:** User bubble (kanan, warna primary) + Bot bubble (kiri, putih, dengan avatar)
- **Loading Indicator:** Tiga titik bouncing saat menunggu respon
- **Markdown Rendering:** Menggunakan library `marked` untuk render tabel, bold, list, code, dll.
- **Auto-scroll:** Otomatis scroll ke bawah saat pesan baru masuk

#### `InputChat.vue`
- Textarea auto-resize (maks 120px)
- Tombol kirim dengan state disabled/active
- Enter untuk kirim, Shift+Enter untuk baris baru
- Visual feedback: glow effect saat fokus

#### `Sidebar.vue` (Desktop)
- Panel kontrol di kiri layar (280px)
- Pilihan mode pencarian: RAG Mode atau HyDE Mode (radio button)
- Riwayat obrolan (saat ini masih di-comment-out / placeholder)
- Footer versi sistem (v1.0.4)

#### `DrawerMenu.vue` (Mobile)
- Drawer slide-in dari kiri (85% lebar layar, maks 320px)
- Pilihan mode pencarian: RAG Mode atau HyDE Mode
- Riwayat obrolan (placeholder)
- Animasi backdrop blur + slide transition

#### `HeaderChat.vue`
- Brand "Chatbot Skripsi TI" + "UIN Alauddin Makassar"
- Hamburger menu (mobile) untuk membuka DrawerMenu
- Status indikator "Online" dengan animasi ping

### 8.4 Composables

#### `useChatbot.js`
```javascript
// Shared state (Singleton pattern)
const messages = ref([])      // Array pesan [{role, content}]
const isLoading = ref(false)  // Status loading
const error = ref(null)       // Error state

// Fungsi
sendMessage(message, mode)    // Kirim pesan ke API backend
clearMessages()               // Hapus semua pesan
```

**Alur `sendMessage()`:**
1. Push pesan user ke `messages[]`
2. Bangun `chat_history` dari 10 pesan terakhir
3. POST ke `http://127.0.0.1:8000/api/chat` dengan body `{message, mode, chat_history}`
4. Terima respon, push pesan bot ke `messages[]`
5. Jika error, push pesan error fallback

#### `useSearchMode.js`
```javascript
const searchMode = ref('rag')  // Default: 'rag'
setMode(mode)                  // Ganti mode: 'rag' atau 'hyde'
```
- State bersifat **global singleton** (di-share antar komponen)

### 8.5 Styling & Design System

**Warna utama:**
| Variabel | Hex | Penggunaan |
|----------|-----|-----------|
| `--color-primary` | `#14b866` | Warna aksen utama (hijau) |
| `--color-primary-light` | `#1dd975` | Warna hover/aktif |
| `--color-primary-dark` | `#0f9a54` | Gradient dan shadow |
| `--color-background-light` | `#f6f8f7` | Background mode terang |
| `--color-background-dark` | `#112119` | Background mode gelap |

**Font:** Lexend (Google Fonts) — `font-family-display`

**CSS Utilities kustom:**
- `.hide-scrollbar` — Hide scrollbar (WebKit + Firefox)
- `.thin-scrollbar` — Scrollbar tipis 4px untuk area chat
- `.interactive` — Hover translateY effect
- `.glow-primary` — Glow shadow hijau pada tombol
- `.gradient-text` — Teks gradient hijau
- `.glass` — Glassmorphism (backdrop-blur 16px)
- `.animate-fade-up` — Animasi fade-in dari bawah
- `.animate-pulse-subtle` — Pulse opacity halus

**Markdown di Chat (prose-chat):**
- Style heading h1-h3
- Bold text menggunakan warna primary
- Tabel dengan header gradient primary
- Code block dengan background slate
- Blockquote dengan border kiri primary

---

## 9. Alur Kerja Sistem (Pipeline)

### 9.1 Pipeline Indexing (Persiapan — Jalankan Sekali)

```
┌──────────┐     ┌──────────────────┐     ┌────────────────────┐
│ File PDF │────▶│ Document Service │────▶│ Extract:           │
│ Skripsi  │     │ (PyPDFLoader)    │     │ - Judul (cover)    │
└──────────┘     └──────────────────┘     │ - Nama & NIM       │
                                           │ - Abstrak (body)   │
                                           └────────┬───────────┘
                                                    │
                                           ┌────────▼───────────┐
                                           │ Clean & Validate   │
                                           │ - Hapus noise      │
                                           │ - Min 100 char     │
                                           └────────┬───────────┘
                                                    │
                                           ┌────────▼───────────┐
                                           │ Embedding Service  │
                                           │ (multilingual-e5)  │
                                           └────────┬───────────┘
                                                    │
                                           ┌────────▼───────────┐
                                           │ ChromaDB           │
                                           │ (Persistent Store) │
                                           └────────────────────┘
```

### 9.2 Pipeline Pencarian (Runtime — Setiap Query)

```
┌──────────┐     ┌──────────────┐     ┌─────────────────────────────────┐
│ User     │────▶│ Frontend     │────▶│ POST /api/chat                  │
│ Query    │     │ (useChatbot) │     │ {message, mode, chat_history}   │
└──────────┘     └──────────────┘     └─────────────┬───────────────────┘
                                                    │
                                          ┌─────────▼──────────┐
                                          │ Mode = "rag" ?     │
                                          └──┬─────────────┬───┘
                                     Ya     │             │   Tidak (hyde)
                               ┌────────────▼──┐   ┌─────▼────────────────┐
                               │ MMR Search    │   │ LLM: Generate        │
                               │ (langsung)    │   │ Hypothetical Abstract│
                               └────────┬──────┘   └──────────┬───────────┘
                                        │                     │
                                        │              ┌──────▼───────────┐
                                        │              │ Embed Hypothetical│
                                        │              │ → Similarity     │
                                        │              │   Search         │
                                        │              └──────┬───────────┘
                                        │                     │
                                  ┌─────▼─────────────────────▼───────┐
                                  │ Top-K Dokumen Relevan (k=5)       │
                                  └────────────────┬──────────────────┘
                                                   │
                                  ┌────────────────▼──────────────────┐
                                  │ Suggestion Service                │
                                  │ → generate_chat_response()        │
                                  │ → generate_suggestion() (opsional)│
                                  └────────────────┬──────────────────┘
                                                   │
                                  ┌────────────────▼──────────────────┐
                                  │ Response: {message, documents,    │
                                  │            suggestion}            │
                                  └────────────────┬──────────────────┘
                                                   │
                                  ┌────────────────▼──────────────────┐
                                  │ Frontend: Render Markdown +       │
                                  │ tampilkan di chat bubble          │
                                  └───────────────────────────────────┘
```

---

## 10. API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/` | Root — welcome message & link dokumentasi |
| `GET` | `/api/status` | Status server (running, version, app_name) |
| `GET` | `/api/health` | Health check — status ChromaDB & jumlah vektor |
| `GET` | `/api/info` | Info sistem (model embedding, LLM, mode retrieval) |
| `POST` | `/api/chat` | **Endpoint utama** — kirim pesan dan dapatkan respon |
| `GET` | `/docs` | Swagger UI (auto-generated oleh FastAPI) |
| `GET` | `/redoc` | ReDoc API documentation |

### Contoh Request `/api/chat`

```json
{
  "message": "sistem rekomendasi",
  "mode": "rag",
  "chat_history": [
    {"role": "user", "content": "cari skripsi tentang AI"},
    {"role": "bot", "content": "Berikut beberapa skripsi..."}
  ]
}
```

### Contoh Response

```json
{
  "success": true,
  "message": "Halo! Saya menemukan beberapa skripsi...\n\n| No | Judul | Sumber | Ringkasan |\n|...|...|...|...|",
  "query": "sistem rekomendasi",
  "mode": "rag",
  "documents": [
    {
      "title": "Implementasi Sistem Rekomendasi...",
      "source": "skripsi_001.pdf",
      "content": "Judul: ... Abstrak: ...",
      "score": null
    }
  ],
  "suggestion": null
}
```

---

## 11. Konfigurasi Sistem

### 11.1 Environment Variables (`backend/.env`)

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxx    # API key Groq
# EMBEDDING_DEVICE=cuda            # Uncomment untuk GPU
```

### 11.2 Settings (`backend/app/core/config.py`)

```python
# API
API_TITLE = "Sistem Pencarian Judul & Abstrak Skripsi"
API_VERSION = "1.0.0"

# Paths
DATA_DIR = backend/data/pdf/            # Lokasi file PDF
CHROMA_DB_DIR = backend/chroma_db/      # Lokasi ChromaDB

# Embedding
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
EMBEDDING_DEVICE = "cpu"

# RAG
K_RETRIEVAL = 5       # Jumlah dokumen hasil
FETCH_K = 20          # Jumlah kandidat untuk MMR

# LLM (Groq)
GROQ_MODEL = "openai/gpt-oss-20b"
LLM_TEMPERATURE = 0.2

# Server
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
```

### 11.3 Frontend Configuration

```javascript
// useChatbot.js
const baseURL = "http://127.0.0.1:8000"  // Alamat backend API

// tailwind.config.js
primary: "#14b866"                       // Warna utama (hijau)
background-light: "#f6f8f7"             // Background terang
background-dark: "#112119"              // Background gelap
font-display: "Lexend"                  // Font utama
```

---

## 12. Cara Menjalankan

### 12.1 Persiapan Backend

```bash
# 1. Masuk ke folder backend
cd backend

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependensi
pip install -r requirements.txt

# 5. Buat file .env dan masukkan API key Groq
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx

# 6. Letakkan file PDF skripsi di folder data/pdf/

# 7. Build index (jalankan sekali)
python scripts/build_index.py

# 8. Jalankan server
uvicorn app.main:app --reload
# atau
python -m app.main
```

Server akan berjalan di: `http://localhost:8000`

### 12.2 Persiapan Frontend

```bash
# 1. Masuk ke folder frontend
cd frontend

# 2. Install dependensi
pnpm install

# 3. Jalankan development server
pnpm dev
```

Frontend akan berjalan di: `http://localhost:5173` (default Vite)

### 12.3 Urutan Menjalankan

1. **Build index** (`python scripts/build_index.py`) — Cukup sekali saat pertama kali atau saat ada PDF baru
2. **Jalankan backend** (`uvicorn app.main:app --reload`) — Port 8000
3. **Jalankan frontend** (`pnpm dev`) — Port 5173
4. Buka browser di `http://localhost:5173`

---

> **Catatan:** Dokumentasi ini dihasilkan berdasarkan analisis kode sumber pada tanggal 27 April 2026.
