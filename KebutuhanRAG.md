# Konsep Lengkap RAG (Retrieval-Augmented Generation) 
*Studi Kasus: Proyek Sistem Pencarian Judul dan Abstrak Skripsi*

RAG (Retrieval-Augmented Generation) adalah arsitektur kecerdasan buatan yang menggabungkan kemampuan pencarian informasi (retrieval) dari sebuah database spesifik dengan kemampuan bahasa natural dari LLM (Large Language Model) untuk menghasilkan jawaban yang akurat, relevan, dan tidak berhalusinasi. 

Berdasarkan arsitektur **Sistem Pencarian Judul dan Abstrak Skripsi** yang sedang Anda kembangkan, proyek ini telah mengimplementasikan konsep RAG tingkat lanjut (*Advanced RAG*). Berikut adalah analisis komprehensif mengenai apa saja kebutuhan sistem RAG secara lengkap dan bagaimana hal tersebut diimplementasikan dalam proyek Anda.

---

## 1. Knowledge Base (Sumber Data & Pemrosesan)
RAG membutuhkan sumber informasi yang akan menjadi "otak" acuannya. LLM tidak akan menggunakan pengetahuan umumnya sendiri, melainkan akan merujuk pada *knowledge base* ini.

**Kebutuhan:**
*   **Data Ingestion:** Kemampuan membaca berbagai format data (PDF, TXT, CSV, dll).
*   **Data Cleaning:** Menghilangkan *noise* (teks tidak relevan, footer, header).
*   **Chunking:** Memotong dokumen panjang menjadi bagian-bagian kecil agar konteks yang masuk ke LLM tidak melebihi *token limit*.

**Implementasi di Proyek Anda:**
*   Proyek ini menggunakan **PyPDFLoader** (dari ekosistem LangChain) untuk membaca file dokumen skripsi mahasiswa.
*   Terdapat tahapan ekstraksi cerdas di `document_service.py` untuk mengambil secara spesifik *Judul (dari Cover)*, *Identitas (NIM & Nama)*, dan *Abstrak (dari isi)*.
*   Fungsi `clean_text()` bekerja krusial di sini untuk membuang teks *noise* seperti atribut kop universitas agar data yang diindeks bersih dan padat informasi.

## 2. Embedding Model (Penerjemah Semantik)
Komputer tidak memahami teks, ia hanya mengerti angka. Embedding adalah proses mengubah potongan teks (kata, kalimat, atau paragraf) menjadi deretan angka matematis (vektor) yang mewakili makna semantik dari teks tersebut.

**Kebutuhan:**
*   Model *embedding* yang sesuai dengan bahasa data yang digunakan (contoh: model bahasa Indonesia atau *multilingual*).
*   Dimensi vektor yang optimal (keseimbangan antara akurasi makna dan kecepatan pencarian).

**Implementasi di Proyek Anda:**
*   Menggunakan model **`intfloat/multilingual-e5-small`** via `HuggingFaceEmbeddings`. Pilihan ini sangat brilian karena mendukung multibahasa (bahasa Indonesia) dan sangat ringan (versi *small*), sehingga pemrosesan RAG berjalan efisien meskipun menggunakan CPU biasa (tanpa GPU/CUDA).

## 3. Vector Database (Penyimpanan dan Pencarian Vektor)
Database relasional biasa (SQL) tidak bisa melakukan pencarian "kemiripan makna". Kita membutuhkan *Vector Database* untuk menyimpan vektor-vektor *embedding* dan melakukan *Similarity Search* (pencarian kedekatan jarak antar vektor).

**Kebutuhan:**
*   Vector DB yang andal dan mendukung metadata filtering (pencarian bersyarat).

**Implementasi di Proyek Anda:**
*   Menggunakan **ChromaDB** yang berjalan secara lokal (`backend/chroma_db`).
*   Metrik jarak (*distance metric*) yang mendukung seperti *cosine similarity*, *L2*, atau *Inner Product* telah disesuaikan dengan perhitungan skor kesamaan (`_distance_to_score`).

## 4. Retrieval Strategies (Strategi Pencarian Konteks)
Ini adalah jantung dari *Advanced RAG*. Strategi *retrieval* menentukan sebagus apa dokumen yang ditemukan untuk dijadikan konteks oleh LLM. Proyek Anda secara luar biasa telah menggabungkan beberapa paradigma *retrieval*.

**Kebutuhan & Implementasi di Proyek Anda:**
*   **Standard Dense Retrieval (MMR):**
    Proyek menggunakan `max_marginal_relevance_search` (MMR). Berbeda dengan pencarian semantik biasa (yang berpotensi menghasilkan dokumen kembar/mirip satu sama lain), MMR menyeimbangkan antara **relevansi** dengan **keberagaman (diversity)**. Hasilnya, skripsi yang direkomendasikan lebih variatif.
*   **HyDE (Hypothetical Document Embeddings):**
    Ini adalah teknik mutakhir. Jika *query* mahasiswa pendek atau samar, sistem meminta LLM membayangkan/menuliskan "Abstrak Hipotetikal" terlebih dahulu (Prompt 1, 2, atau 3 di `rag_service.py`). Kemudian, teks khayalan inilah yang diubah menjadi vektor untuk mencari ke database. Ini sangat ampuh mereduksi kekosongan pencarian (*zero-hit retrieval*).
*   **Hybrid Search (Dense + Sparse BM25):**
    Pada RAG tingkat lanjut, pengembang sadar bahwa *vector search* buruk dalam pencarian spesifik (seperti nama penulis, atau singkatan). Proyek ini mengatasi hal tersebut dengan `hybrid_rag()`. Sistem menggabungkan pencarian semantik ChromaDB (Dense) dengan pencarian leksikal persis kata menggunakan `SimpleBM25` (Sparse). Penggabungan ini dieksekusi dengan teknik *Fusion* (seperti RRF).
*   **Deduplication & Thresholding:**
    Sistem mengeksekusi fungsi `_apply_threshold` (untuk membuang skripsi dengan skor kemiripan rendah) dan `_deduplicate` (memastikan tidak ada skripsi dengan NIM sama yang muncul dua kali).

## 5. Large Language Model (Generasi Jawaban)
Tahap terakhir dimana LLM membaca konteks (hasil pencarian skripsi) yang diberikan, lalu merangkum atau menjawab sesuai instruksi *prompt*.

**Kebutuhan:**
*   LLM yang memiliki penalaran (reasoning) cepat dan baik.
*   *Prompt Engineering* yang kuat untuk membatasi ruang gerak LLM agar **TIDAK berhalusinasi**.

**Implementasi di Proyek Anda:**
*   Menggunakan infrastruktur **Groq** dengan model `openai/gpt-oss-20b` (sebelumnya Llama-3) via `ChatGroq`. Groq dipilih karena kecepatan *inference* token-nya yang ekstrim, cocok untuk *chatbot realtime*.
*   **Strict Prompting:** Pada `rag_service.py`, terlihat *Prompt Engineering* yang sangat ketat ("ZERO HALLUCINATION"). Terdapat instruksi tegas: *"DILARANG KERAS menuliskan hasil pengujian"*, *"BILINGUAL WAJIB"*, dan aturan penerjemahan kata awam ke terminologi akademis murni (contoh: 'bikin web' menjadi 'sistem informasi berbasis web'). Ini adalah praktik terbaik (*best-practice*) di industri untuk sistem RAG.

## 6. Metadata Filtering (Advanced Feature)
Sistem RAG modern butuh lebih dari sekadar pencarian makna; ia butuh pencarian bersyarat.

**Implementasi di Proyek Anda:**
Pada `hybrid_rag()`, Anda menerapkan eksekusi filter `where_filter` pada ChromaDB (menggunakan `$and`, `$gte`, `$lte`). Hal ini memungkinkan *user* untuk memberikan *query* seperti "Cari skripsi AI antara tahun 2021 hingga 2023", dan sistem secara dinamis menyaring datanya di *database layer*.

---

## Kesimpulan
Sistem yang Anda bangun bukan sekadar RAG biasa (*Naive RAG*), melainkan telah memenuhi arsitektur **Advanced RAG**. 

**Komponen RAG yang telah terpenuhi di proyek Anda:**
1. ✅ **Data Extraction & Clean Up** (via document_service)
2. ✅ **Multilingual Embedding** (via intfloat/multilingual-e5-small)
3. ✅ **Persistent Vector Store** (via ChromaDB)
4. ✅ **Advanced Retrieval Pipeline** (Hybrid Search, HyDE, MMR)
5. ✅ **Metadata Extraction & Filtering** (Filter Tahun dan Identitas)
6. ✅ **Post-Retrieval Processing** (Thresholding & Deduplication)
7. ✅ **Strict Grounded Generation** (LLM Groq dengan prompt anti-halusinasi)

Proyek ini sangat solid secara arsitektur, relevan, dan efisien untuk diimplementasikan dalam skala institusi akademik. Kombinasi *HyDE* dan *Hybrid Search* menjamin skripsi yang ditemukan akan sangat relevan, tak peduli sekasual apa pun mahasiswa mengetik kata pencariannya.
