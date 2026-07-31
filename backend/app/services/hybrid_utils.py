import re
import math

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


class SimpleBM25:
    """Implementasi murni Python untuk BM25 Okapi Retrieval."""
    def __init__(self, documents: list, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.raw_docs = documents
        # Asumsikan 'documents' adalah list of Langchain Document
        self.corpus = [
            self._tokenize(f"{doc.metadata.get('nama', '')} {doc.page_content}") 
            for doc in documents
        ]
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
        # Asumsikan distance metric adalah cosine. Jika lain, bisa disesuaikan.
        chroma_sim = max(0.0, 1.0 - (distance / 2.0))
        bm25_sim = normalized_bm25[idx]
        
        # Hitung Skor Akhir
        fused_score = (alpha * chroma_sim) + ((1.0 - alpha) * bm25_sim)
        percentage_score = round(fused_score * 100, 2)
        
        # Tambahkan skor gabungan ke metadata dokumen
        doc_data = {
            "page_content": doc.page_content,
            "metadata": {
                "source": doc.metadata.get("source", "Unknown"),
                "judul": doc.metadata.get("judul", ""),
                "nama": doc.metadata.get("nama", ""),
                "nim": doc.metadata.get("nim", ""),
                "pembimbing": doc.metadata.get("pembimbing", ""),
                "tahun": doc.metadata.get("tahun", ""),
                "similarity_score": percentage_score,
                "hybrid_chroma_score": round(chroma_sim * 100, 2),
                "hybrid_bm25_score": round(bm25_sim * 100, 2)
            }
        }
        fused_results.append((doc_data, percentage_score))

    # Urutkan berdasarkan skor tertinggi (descending)
    fused_results.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in fused_results]
