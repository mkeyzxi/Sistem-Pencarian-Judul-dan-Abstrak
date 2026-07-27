# Instruksi Pembuatan Fitur Hybrid Search dengan Smart Query Parser (Untuk AI Coding Assistant)

**Konteks Proyek:**
Ini adalah prototipe Information Retrieval skripsi Teknik Informatika. Terdapat _search bar_ utama dan radio button "RAG", "HyDE", dan opsi baru "Hybrid (Eksperimental)". Pengguna tidak ingin ada input UI tambahan untuk filter. Semua filter (seperti tahun) diketik langsung di _search bar_ utama (misal: "machine learning 2024" atau "chatbot 2024 hingga 2026").

**Tujuan:**
Buat fitur "Hybrid" di mana _backend_ mampu mengekstrak _metadata_ (tahun/rentang tahun) dari teks mentah secara otomatis, menggunakan informasi tersebut untuk _filter_ SQL, lalu melakukan _Hybrid Search_ (ChromaDB + BM25) pada sisa teksnya.

---

## TUGAS 1: Modifikasi Frontend (UI)

1. **Radio Button Saja:** Tambahkan radio button "Hybrid (Eksperimental)" di sebelah RAG dan HyDE.
2. **Tanpa Form Tambahan:** Jangan tambahkan input apa pun selain _search bar_ utama yang sudah ada. Biarkan antarmuka tetap minimalis.
3. **Payload:** Kirim JSON berisi `{ query: "teks mentah dari user", method: "hybrid" }` ke _backend_.

## TUGAS 2: Modifikasi Backend (API Endpoint)

1. **Tahap 1: Query Parsing (Ekstraksi Entitas):**
   - Buat fungsi pra-pemrosesan (menggunakan RegEx yang kokoh atau prompt LLM kecil) untuk menganalisis string `query`.
   - Deteksi pola tahun.
     - Jika ada satu tahun (misal: "2024"): ekstrak `tahun_spesifik = 2024`.
     - Jika ada pola rentang (misal: "2024-2026", "2024 sampai 2026", "2024 hingga 2026"): ekstrak `tahun_awal = 2024`, `tahun_akhir = 2026`.
   - **PENTING:** Hapus string tahun dan kata penghubungnya dari _query_ asli agar tidak menjadi _noise_ di pencarian vektor. Simpan ke dalam variabel `clean_query` (misal: "machine learning").

2. **Tahap 2: Pre-Filtering (SQL Database):**
   - Lakukan kueri SQL ke basis data utama dengan kondisi:
     - Jika ada `tahun_spesifik`: `WHERE tahun = ?`
     - Jika ada rentang tahun: `WHERE tahun BETWEEN ? AND ?`
   - Kembalikan id dokumen ke dalam variabel `filtered_docs`.

3. **Tahap 3: Parallel Retrieval (Hanya pada filtered_docs):**
   - **Dense (ChromaDB):** Lakukan _similarity search_ menggunakan `clean_query` pada `filtered_docs`. Dapatkan skor.
   - **Sparse (BM25):** Lakukan pencarian BM25 menggunakan `clean_query` pada `filtered_docs`. Dapatkan skor.

4. **Tahap 4: Normalisasi & Fusion:**
   - Normalisasi skor BM25 ke 0-1 (Min-Max Scaling).
   - Terapkan Alpha Weighting: `Skor_Akhir = (0.5 * Skor_Chroma) + (0.5 * Skor_BM25_Normalized)`.
   - Urutkan dan kembalikan JSON Top-5 dokumen.

**Catatan untuk AI:**
Berikan kode fungsi `Query Parsing` (RegEx) yang benar-benar siap pakai untuk bahasa Indonesia (menangani kata "hingga", "sampai", "-"). Jangan merusak arsitektur RAG dan HyDE yang lama.

---

## ℹ️ INFORMASI PENDUKUNG & BLUEPRINT IMPLEMENTASI

Dokumen referensi ini menyediakan rancangan kode teknis, formula matematika, dan integrasi UI/API untuk mempermudah pengerjaan fitur Hybrid Search.

### 1. Tahap 1: Blueprint Query Parser (Regex Python)
Berikut adalah implementasi Python yang kokoh untuk mengekstrak metadata tahun/rentang tahun dari teks pencarian dalam Bahasa Indonesia:

```python
import re

def parse_query_metadata(query: str) -> dict:
    """
    Mengekstrak informasi tahun spesifik atau rentang tahun dari string kueri
    dan mengembalikan kueri bersih tanpa informasi tahun tersebut.
    """
    # Pola mendeteksi rentang tahun (misal: "2020-2023", "2020 sampai 2023", "2020 hingga 2023")
    range_pattern = r"\b((?:19|20)\d{2})\s*(?:-|sampai|hingga|s/d|s\.d)\s*((?:19|20)\d{2})\b"
    # Pola mendeteksi tahun tunggal (misal: "2024")
    single_pattern = r"\b((?:19|20)\d{2})\b"
    
    tahun_spesifik = None
    tahun_awal = None
    tahun_akhir = None
    clean_query = query
    
    # 1. Cari rentang tahun terlebih dahulu
    range_match = re.search(range_pattern, query, re.IGNORECASE)
    if range_match:
        tahun_awal = int(range_match.group(1))
        tahun_akhir = int(range_match.group(2))
        # Hapus bagian range tahun dari query
        clean_query = re.sub(range_pattern, "", clean_query, flags=re.IGNORECASE)
    else:
        # 2. Cari tahun tunggal
        single_match = re.search(single_pattern, query)
        if single_match:
            tahun_spesifik = int(single_match.group(1))
            # Hapus tahun spesifik dari query
            clean_query = re.sub(single_pattern, "", clean_query)
            
    # Bersihkan kata penghubung/preposisi sisa yang berkaitan dengan waktu (misal: "tahun", "pada", "antara")
    clean_query = re.sub(r"\b(tahun|antara|pada|di|range|rentang)\b", "", clean_query, flags=re.IGNORECASE)
    # Runtuhkan spasi berlebih
    clean_query = re.sub(r"\s+", " ", clean_query).strip()
    
    return {
        "clean_query": clean_query,
        "tahun_spesifik": tahun_spesifik,
        "tahun_awal": tahun_awal,
        "tahun_akhir": tahun_akhir
    }
```

---

### 2. Tahap 2: Representasi Filter Metadata (ChromaDB / SQL)
Metadata `tahun` disimpan dalam format string (misal: `"2024"`) di database ChromaDB. Berikut cara memetakan hasil query parser ke filter metadata ChromaDB:

*   **Kasus 1: Tahun Spesifik (`tahun_spesifik = 2024`)**
    ```python
    where_filter = {"tahun": str(tahun_spesifik)}
    ```
*   **Kasus 2: Rentang Tahun (`2021 hingga 2024`)**
    ```python
    where_filter = {
        "$and": [
            {"tahun": {"$gte": str(tahun_awal)}},
            {"tahun": {"$lte": str(tahun_akhir)}}
        ]
    }
    ```
*   **Kasus 3: Tanpa Filter**
    ```python
    where_filter = None
    ```

Jika Anda menggunakan database SQL relasional eksternal (misal: SQLite/MySQL), gunakan kueri SQL berikut untuk memfilter ID dokumen sebelum melakukan retrieval:
```sql
-- Jika tahun spesifik terdeteksi
SELECT id, page_content, judul, tahun FROM skripsi WHERE tahun = :tahun_spesifik;

-- Jika rentang tahun terdeteksi
SELECT id, page_content, judul, tahun FROM skripsi WHERE tahun BETWEEN :tahun_awal AND :tahun_akhir;
```

---

### 3. Tahap 3 & 4: Retrieval & Fusion (Tanpa Dependency Eksternal)
Karena pustaka `rank_bm25` mungkin tidak terpasang secara default, berikut adalah implementasi kelas `SimpleBM25` murni dalam Python, berserta kalkulasi normalisasi dan Alpha Weighting:

```python
import math

class SimpleBM25:
    """Implementasi murni Python untuk BM25 Okapi Retrieval."""
    def __init__(self, documents: list, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.raw_docs = documents
        self.corpus = [self._tokenize(doc["page_content"]) for doc in documents]
        self.corpus_size = len(self.corpus)
        self.avg_doc_len = sum(len(d) for d in self.corpus) / self.corpus_size if self.corpus_size > 0 else 0
        
        self.doc_freqs = []
        self.doc_lens = []
        self.idf = {}
        self._initialize()

    def _tokenize(self, text: str) -> list:
        # Tokenisasi sederhana berbasis kata dasar dan pembersihan simbol
        return re.findall(r"\b\w+\b", text.lower())

    def _initialize(self):
        term_doc_counts = {}
        for doc in self.corpus:
            self.doc_lens.append(len(doc))
            freqs = {}
            for word in doc:
                freqs[word] = freqs.get(word, 0) + 1
            self.doc_freqs.append(freqs)
            
            for word in set(doc):
                term_doc_counts[word] = term_doc_counts.get(word, 0) + 1
                
        for word, count in term_doc_counts.items():
            self.idf[word] = math.log((self.corpus_size - count + 0.5) / (count + 0.5) + 1.0)

    def get_scores(self, query: str) -> list:
        query_tokens = self._tokenize(query)
        scores = []
        for idx in range(self.corpus_size):
            score = 0.0
            doc_len = self.doc_lens[idx]
            freqs = self.doc_freqs[idx]
            for token in query_tokens:
                if token in freqs:
                    tf = freqs[token]
                    idf_val = self.idf.get(token, 0.0)
                    denom = tf + self.k1 * (1.0 - self.b + self.b * doc_len / self.avg_doc_len)
                    score += idf_val * tf * (self.k1 + 1.0) / denom
            scores.append(score)
        return scores


def hybrid_search_fusion(dense_results: list, bm25_scores: list, alpha: float = 0.5) -> list:
    """
    Menggabungkan hasil Dense Search (ChromaDB) dan Sparse Search (BM25).
    
    - Skor ChromaDB didapat dari formula: 1.0 - (distance / 2.0)
    - Skor BM25 dinormalisasi ke rentang [0, 1] menggunakan Min-Max Scaling.
    - Nilai output akhir dikalikan 100 agar sesuai format persentase UI (0-100%).
    """
    if not dense_results:
        return []

    # 1. Normalisasi Skor BM25 (Min-Max Scaling)
    min_bm25 = min(bm25_scores) if bm25_scores else 0.0
    max_bm25 = max(bm25_scores) if bm25_scores else 0.0
    bm25_range = max_bm25 - min_bm25

    normalized_bm25 = []
    for score in bm25_scores:
        if bm25_range > 0:
            norm_score = (score - min_bm25) / bm25_range
        else:
            norm_score = 0.0
        normalized_bm25.append(norm_score)

    # 2. Linear Fusion
    fused_results = []
    for idx, (doc, distance) in enumerate(dense_results):
        # Konversi Cosine Distance ke Similarity Score (0.0 - 1.0)
        chroma_sim = 1.0 - (distance / 2.0)
        bm25_sim = normalized_bm25[idx]
        
        # Hitung Skor Akhir
        fused_score = (alpha * chroma_sim) + ((1.0 - alpha) * bm25_sim)
        percentage_score = round(fused_score * 100, 2)
        
        # Tambahkan skor gabungan ke metadata dokumen
        doc_data = {
            "page_content": doc.page_content,
            "metadata": {
                **doc.metadata,
                "similarity_score": percentage_score
            }
        }
        fused_results.append((doc_data, percentage_score))

    # Urutkan berdasarkan skor tertinggi (descending)
    fused_results.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in fused_results[:5]]
```

---

### 4. Blueprint Modifikasi Frontend (Vue.js 3)

#### **File:** `frontend/src/composables/useSearchMode.js`
Tambahkan state untuk mode `hybrid`:
```javascript
import { ref } from 'vue'

const searchMode = ref('rag'); // Default mode
export function useSearchMode() {
  const setMode = (mode) => {
    searchMode.value = mode; // Mode baru bisa berupa 'rag', 'hyde', atau 'hybrid'
  }
  return { searchMode, setMode }
}
```

#### **File:** `frontend/src/components/Sidebar.vue`
Tambahkan elemen radio button baru untuk mode Hybrid di bagian panel kontrol:
```html
<!-- Radio Button Hybrid (Eksperimental) -->
<label class="flex items-center gap-3 px-3.5 py-3 rounded-lg cursor-pointer transition-all duration-200"
  :class="searchMode === 'hybrid'
    ? 'bg-bg-highlight border border-primary/30'
    : 'bg-bg-elevated hover:bg-bg-highlight border border-transparent'
    ">
  <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors" 
       :class="searchMode === 'hybrid' ? 'border-primary' : 'border-border-bright'">
    <div v-if="searchMode === 'hybrid'" class="w-2 h-2 rounded-full bg-primary"></div>
  </div>
  <input v-model="searchMode" @click="setMode('hybrid')" type="radio" value="hybrid" class="sr-only" />
  <div class="flex-1 min-w-0">
    <span class="text-sm font-bold text-text-base">Hybrid Mode</span>
    <p class="text-[10px] text-text-subdued mt-0.5">Filter metadata & BM25</p>
  </div>
  <span v-if="searchMode === 'hybrid'" class="material-symbols-outlined text-primary text-base">check_circle</span>
</label>
```
