# 📚 Sistem Pencarian Judul & Abstrak Skripsi

README ini menjelaskan cara menjalankan dan mengembangkan project Chatbot Pencarian Judul & Abstrak Skripsi (FastAPI backend + Vue.js frontend).

**Ringkasan singkat**
- **Tujuan**: Menyediakan eksperimen retrieval dokumen (RAG & HyDE) untuk mencari judul dan abstrak skripsi.
- **Stack**: Python (FastAPI, LangChain, ChromaDB) untuk backend; Vue 3 + Vite untuk frontend.

---

**Overview**
- **Backend**: [backend/app/main.py](backend/app/main.py#L1) — FastAPI sebagai API server, RAG logic di [backend/app/services/rag_service.py](backend/app/services/rag_service.py#L1).
- **Frontend**: [frontend/](frontend/README.md#L1) — UI minimal berbasis Vue 3, berkomunikasi dengan endpoint `/api/chat`.
- **Indexing**: Script `backend/scripts/build_index.py` membuat vector store di `backend/chroma_db/`.

---

**Fitur Utama**
- **Pencarian dokumen**: retrieve judul & abstrak berdasarkan query.
- **Mode retrieval**: `rag` (standard) dan `hyde` (HyDE hypothetical docs).
- **Saran akademik**: ketika input merupakan judul lengkap, server memberikan saran pengembangan.

---

**Repository Structure (ringkas)**
- **backend/**: kode server, scripts, dan penyimpanan ChromaDB.
- **frontend/**: aplikasi Vue 3 untuk antarmuka pengguna.

Lihat struktur lengkap di file kode, contoh: [backend/app/api/chat.py](backend/app/api/chat.py#L1).

---

**Prerequisites**
- Python 3.10+ (direkomendasikan)
- Node.js 20+ dan pnpm (atau npm/yarn)
- (Opsional) GPU untuk embedding/LLM namun default adalah CPU

---

**Backend — Setup & Run**

- **1) Buat virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

- **2) Install dependencies**

```bash
pip install -r backend/requirements.txt
```

- **3) Konfigurasi environment**

Buat file `.env` di folder `backend/` berisi minimal:

```text
GROQ_API_KEY=your_groq_api_key_here
```

- **4) Bangun index (WAJIB sebelum server)**

Letakkan file PDF skripsi di `backend/data/pdf/` lalu jalankan:

```bash
python backend/scripts/build_index.py
```

Proses ini akan mengekstrak teks, membuat embedding dengan model `intfloat/multilingual-e5-small`, dan menyimpan vector ke `backend/chroma_db/`.

- **5) Jalankan server**

```bash
# Development (hot reload)
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

# Atau dari folder backend
cd backend
uvicorn app.main:app --reload
```

Endpoint dokumentasi tersedia di `http://localhost:8000/docs`.

Referensi kode penting:
- Router utama: [backend/app/api/chat.py](backend/app/api/chat.py#L1)
- RAG logic: [backend/app/services/rag_service.py](backend/app/services/rag_service.py#L1)

---

**Frontend — Setup & Run**

Masuk ke folder `frontend/` lalu install deps dan jalankan dev server:

```bash
cd frontend
pnpm install    # atau: npm install / yarn
pnpm dev
```

Default Vite dev server akan berjalan (biasanya) di `http://localhost:5173`.

Jika backend berjalan di port lain, pastikan CORS dan base URL sesuai (lihat [backend/app/main.py](backend/app/main.py#L1) dan file frontend yang memanggil API).

---

**API — Ringkasan**
- **POST /api/chat** — Endpoint utama chat. Request JSON:

```json
{
  "message": "kata kunci atau judul skripsi",
  "mode": "rag"    # atau "hyde"
}
```

Response berisi fields: `success`, `message`, `query`, `mode`, `documents`, `suggestion`.

- **GET /api/health** — Health check termasuk jumlah vektor di DB.
- **GET /api/info** — Informasi model & vector DB.

Implementasi endpoint ada di [backend/app/api/chat.py](backend/app/api/chat.py#L1).

---

**Menambah Dataset (PDF)**
- Letakkan file PDF di `backend/data/pdf/`.
- Setiap PDF disarankan memiliki halaman sampul (title & identitas) dan abstrak.
- Jalankan ulang `python backend/scripts/build_index.py` untuk memperbarui ChromaDB.

---

**Troubleshooting & Tips**
- **GROQ_API_KEY not found**: pastikan `.env` ada di folder `backend/` dan berisi kunci.
- **No vectors found**: jalankan `python backend/scripts/build_index.py` dan pastikan ada PDF di `backend/data/pdf/`.
- **CUDA out of memory**: set `EMBEDDING_DEVICE=cpu` di `backend/.env` atau gunakan mesin dengan memori GPU lebih besar.
- **CORS**: CORS diizinkan semua asal di development (`allow_origins=["*"]`) pada [backend/app/main.py](backend/app/main.py#L1). Untuk produksi, batasi origin.

---

**Development notes**
- File util & core config: [backend/app/core/config.py](backend/app/core/config.py#L1)
- Build index script: [backend/scripts/build_index.py](backend/scripts/build_index.py#L1)
- Embedding service: [backend/app/services/embedding_service.py](backend/app/services/embedding_service.py#L1)

Jika ingin menambahkan model atau mengubah embedding, lakukan penyesuaian di `config.py`.

---

**Contributing & Next Steps**
- Tambahkan testing, CI, dan dokumentasi API lebih rinci.
- Implementasi pagination / reranking untuk hasil retrieval.
- Tambahkan persistence percakapan (history) dan otentikasi jika diperlukan.

---

**License & Contact**
- Project ini disiapkan sebagai eksperimen akademik. Untuk pertanyaan, hubungi penulis proyek.

---

Jika Anda ingin, saya dapat:
- Menambahkan badge status (build / python / node)
- Menambahkan instruksi Docker untuk menjalankan seluruh stack
- Membuat contoh request `curl` dan Postman collection

Mau saya terapkan salah satu dari opsi di atas sekarang? 

Abstrak:
{abstract}
""".strip()

    documents.append(
        Document(
            page_content=content,
            metadata={"source": file}
        )
    )

print("Jumlah dokumen siap embedding:", len(documents))


from langchain_huggingface import HuggingFaceEmbeddings


embedding = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)


from langchain_community.vectorstores import Chroma


persist_directory = "/content/chroma_db"

if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory)


vectorstore = Chroma(
    embedding_function=embedding,
    persist_directory=persist_directory
)


batch_size = 10
for i in range(0, len(documents), batch_size):
    vectorstore.add_documents(documents[i:i + batch_size])

vectorstore.persist()
print("Jumlah vektor:", vectorstore._collection.count())


from langchain_groq import ChatGroq


import os
# Replace 'YOUR_GROQ_API_KEY' with your actual Groq API key
os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.2,
)

def run_rag(query, k=5):
    docs = vectorstore.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=20
    )

    if not docs:
        return "Tidak ditemukan"

    result = "===== STANDARD RAG =====\n\n"
    for i, doc in enumerate(docs, 1):
        result += f"[{i}] {doc.metadata['source']}\n"
        result += doc.page_content[:1200] + "\n\n"

    return result


def hyde_retrieve(query, k=5):
    prompt = f"""
Tuliskan abstrak skripsi singkat (3–4 kalimat)
yang relevan dengan topik berikut:

Topik: "{query}"
"""

    hypothetical_doc = llm.invoke(prompt).content.strip()
    hypo_vector = embedding.embed_query(hypothetical_doc)

    docs = vectorstore.similarity_search_by_vector(
        hypo_vector, k=k
    )

    return hypothetical_doc, docs

def hyde_answer(query):
    hypo, docs = hyde_retrieve(query)

    if not docs:
        return "Tidak ditemukan"

    result = "===== HyDE RAG =====\n\n"
    for i, doc in enumerate(docs, 1):
        result += f"[{i}] {doc.metadata['source']}\n"
        result += doc.page_content[:1200] + "\n\n"

    return result


query = "kalah deh"

print(run_rag(query))
print()
print(hyde_answer(query))# Sistem-Pencarian-Judul-dan-Abstrak
# Sistem-Pencarian-Judul-dan-Abstrak
# Sistem-Pencarian-Judul-dan-Abstrak
