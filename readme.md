# 📚 Chatbot Eksperimen Pencarian Judul & Abstrak Skripsi Teknik Informatika UIN Alauddin Makassar

Chatbot ini merupakan **chatbot eksperimen berbasis FastAPI + RAG (Retrieval-Augmented Generation)** yang digunakan untuk:

* Mencari **judul dan abstrak skripsi Teknik Informatika UIN Alauddin Makassar**
* Memberikan **respon seperti chatbot** (natural & interaktif)
* Memberikan **saran akademik tambahan** jika user memasukkan **judul skripsi lengkap**

Chatbot ini **bukan sistem produksi**, melainkan digunakan untuk **eksperimen riset, evaluasi RAG, dan kebutuhan akademik (skripsi)**.

---

## 🎯 Tujuan Sistem

1. Mengimplementasikan **RAG (Standard RAG & HyDE RAG)**
2. Menguji kemampuan chatbot dalam:

   * Menemukan skripsi relevan
   * Menampilkan judul & abstrak
   * Memberikan saran pengembangan judul
3. Menjadi dasar **evaluasi performa pencarian judul & abstrak skripsi**

---

## 🏗️ Arsitektur Sistem

```
User (Vue.js)
   ↓
FastAPI (Chat Endpoint)
   ↓
RAG / HyDE Retrieval
   ↓
ChromaDB (Vector Store)
   ↓
PDF Judul & Abstrak Skripsi
```

---

## 📁 Struktur Folder Project

```
backend/
│
├── app/
│   ├── main.py                 # Entry FastAPI
│   │
│   ├── api/
│   │   └── chat.py              # Endpoint chatbot
│   │
│   ├── services/
│   │   ├── document_service.py  # Load & preprocessing PDF
│   │   ├── embedding_service.py # HuggingFace Embedding
│   │   ├── rag_service.py       # RAG & HyDE logic
│   │   └── suggestion_service.py# Saran judul skripsi
│   │
│   └── core/
│       └── config.py            # Konfigurasi & env
│
├── data/
│   └── pdf/                     # Dataset PDF skripsi
│
├── chroma_db/                   # Vector database (persist)
│
├── scripts/
│   └── build_index.py           # Script embedding (sekali jalan)
│
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ Instalasi & Setup

### 1️⃣ Buat Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2️⃣ Install Dependency

```bash
pip install -r requirements.txt
```

`requirements.txt`

```
fastapi
uvicorn
python-dotenv
langchain
langchain-community
langchain-core
langchain-groq
langchain-huggingface
chromadb
sentence-transformers
pypdf
```

---

## 📄 Dataset

* Dataset berupa **file PDF skripsi Teknik Informatika UIN Alauddin Makassar**
* Setiap PDF minimal memiliki:

  * Sampul
  * Abstrak

Letakkan semua PDF di:

```
backend/data/pdf/
```

---

## 🔧 Preprocessing & Embedding (WAJIB)

Embedding **hanya dilakukan sekali**, bukan saat chatbot berjalan.

Jalankan:

```bash
python scripts/build_index.py
```

Proses ini akan:

* Mengekstrak judul, identitas, dan abstrak
* Membersihkan teks
* Membuat embedding dengan `intfloat/multilingual-e5-small`
* Menyimpan vektor ke `chroma_db/`

---

## 🚀 Menjalankan Server FastAPI

```bash
uvicorn app.main:app --reload
```

Akses:

* API: [http://localhost:8000](http://localhost:8000)
* Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💬 Endpoint Chatbot

### `POST /chat`

#### Request Body

```json
{
  "message": "Judul skripsi atau topik",
  "mode": "rag"
}
```

Mode:

* `rag` → Standard RAG
* `hyde` → HyDE RAG

---

## 🤖 Logika Respon Chatbot

Chatbot **tidak hanya mengembalikan dokumen**, tetapi juga memberikan respon natural.

### 🔹 Jika input berupa topik singkat

Contoh:

```
"sistem rekomendasi"
```

Respon:

* Menampilkan beberapa judul & abstrak relevan
* Memberikan ringkasan singkat

### 🔹 Jika input berupa judul skripsi lengkap

Contoh:

```
"Sistem Rekomendasi Pemilihan Dosen Pembimbing Menggunakan Collaborative Filtering"
```

Respon chatbot:

1. Menyapa user
2. Menampilkan skripsi relevan
3. Memberikan **saran akademik**, seperti:

   * Potensi pengembangan metode
   * Perbandingan dengan penelitian sebelumnya
   * Variasi dataset atau algoritma

---

## 🧠 Contoh Respon Chatbot

```
Halo 👋
Berdasarkan judul yang kamu ajukan, berikut beberapa skripsi yang relevan:

1. Judul: ...
   Abstrak: ...

📌 Saran Pengembangan:
Judul yang kamu ajukan sudah relevan. Namun, berdasarkan penelitian sebelumnya,
kamu dapat mempertimbangkan:
- Mengganti metode X dengan Y
- Menggunakan dataset terbaru
- Menambahkan evaluasi performa
```

---

## 🔐 Environment Variable

`.env`

```
GROQ_API_KEY=your_api_key_here
```

---

## 📊 Catatan Akademik

* Chatbot ini **tidak menggantikan pembimbing skripsi**
* Digunakan sebagai **alat bantu eksplorasi judul & literatur awal**
* Cocok untuk:

  * Evaluasi RAG vs HyDE
  * Pengujian retrieval
  * Penelitian NLP & IR

---

## 📌 Status Project

✅ Eksperimen RAG & HyDE
✅ Dataset skripsi lokal
✅ Chatbot FastAPI
❌ Bukan sistem produksi

---

## 👨‍🎓 Konteks Penelitian

Project ini dikembangkan sebagai bagian dari:

> **Eksperimen chatbot pencarian judul dan abstrak skripsi Teknik Informatika
> UIN Alauddin Makassar menggunakan pendekatan Retrieval-Augmented Generation (RAG)**

---

✨ Siap dikembangkan ke:

* Evaluasi Top-K
* Precision / Recall
* UI Vue.js
* Logging percakapan

---

📌 **Catatan:** Seluruh logika chatbot mengacu pada kode eksperimen LangChain + ChromaDB yang telah disiapkan sebelumnya.


Kode program dibawah ini menggunakan google colab mau dirubah ke FastAPi namun dengan respon yang lebih baik
!pip uninstall chromadb -y

!pip install -U \
langchain langchain-community langchain-core \
langchain-groq langchain-huggingface \
chromadb sentence-transformers pypdf


import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


import torch
print("GPU aktif:", torch.cuda.is_available())

import os
import re
import shutil

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

def extract_title(lines):
    title_lines = []
    stop_words = [
        "skripsi", "diajukan", "oleh", "nama", "nim",
        "program studi", "fakultas", "universitas"
    ]

    for line in lines:
        low = line.lower()

        if any(sw in low for sw in stop_words):
            break

        if len(line.strip()) > 3:
            title_lines.append(line.strip())

        if len(" ".join(title_lines)) > 150:
            break

    return " ".join(title_lines)

def extract_identity(text):
    nama = re.search(r"nama\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
    nim  = re.search(r"nim\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)

    result = []
    if nama:
        result.append(f"Nama: {nama.group(1).strip()}")
    if nim:
        result.append(f"NIM: {nim.group(1).strip()}")

    return " | ".join(result)

def extract_abstract(text):
    match = re.search(r"abstrak(.*)", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def clean_text(text):
    noise = [
        "sampul skripsi",
        "diajukan untuk memenuhi",
        "program studi",
        "fakultas",
        "universitas"
    ]

    for n in noise:
        text = re.sub(n, "", text, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", text).strip()


data_dir = "/content/drive/MyDrive/Data_Judul_Abstrak_Skripsi_Teknik_Informatika"
documents = []


for file in os.listdir(data_dir):
    if not file.endswith(".pdf"):
        continue

    loader = PyPDFLoader(os.path.join(data_dir, file))
    pages = loader.load()

    if len(pages) < 2:
        continue

    cover_text = pages[0].page_content
    body_text = "\n".join(p.page_content for p in pages[1:])

    lines = [l.strip() for l in cover_text.split("\n") if len(l.strip()) > 2]

    title = extract_title(lines)
    identity = extract_identity(cover_text)
    abstract = extract_abstract(body_text)

    if len(abstract) < 200:
        continue

    title = clean_text(title)
    abstract = clean_text(abstract)

    content = f"""
Judul: {title}
{identity}

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
