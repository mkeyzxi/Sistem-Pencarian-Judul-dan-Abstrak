"""
RAG Service — Fokus RAG (Standard)
Dengan caching hasil retrieval, thread-safe, dan optimasi performa
untuk melayani banyak user bersamaan.

Fungsi:
- Standard RAG retrieval
- In-memory LRU cache untuk query identik (menghindari komputasi ulang)
- Thread-safe via double-checked locking
- E5 Prefix absolut untuk query pencarian
"""

import re
import time
import threading
import hashlib
from collections import OrderedDict
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from app.core.config import settings
from app.services.embedding_service import embedding_service


# ─── Query Cache (LRU, thread-safe) ───────────────────────────────────────────

class QueryCache:
    """
    LRU Cache untuk hasil RAG retrieval.
    - Kunci: hash query + k (agar hasil tetap relevan per jumlah dokumen)
    - TTL: 120 detik (menghindari cache stale)
    - Ukuran: maksimal 200 entri
    - Thread-safe dengan RLock
    """

    MAX_SIZE = 200
    TTL_SECONDS = 120

    def __init__(self):
        self._store: OrderedDict[str, tuple[float, dict]] = OrderedDict()
        self._lock = threading.RLock()

    @staticmethod
    def _make_key(query: str, k: int) -> str:
        """Buat kunci cache dari query dan parameter k."""
        normalized = re.sub(r'\s+', ' ', query.strip().lower())
        raw = f"{normalized}|k={k}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, query: str, k: int) -> dict | None:
        """Ambil dari cache jika ada dan belum expired."""
        key = self._make_key(query, k)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            ts, value = entry
            if time.time() - ts > self.TTL_SECONDS:
                # Expired — hapus
                del self._store[key]
                return None
            # Move to end (MRU)
            self._store.move_to_end(key)
            return value

    def set(self, query: str, k: int, value: dict) -> None:
        """Simpan hasil ke cache."""
        key = self._make_key(query, k)
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (time.time(), value)
            # Evict oldest jika melebihi batas
            while len(self._store) > self.MAX_SIZE:
                self._store.popitem(last=False)

    def stats(self) -> dict:
        with self._lock:
            return {"entries": len(self._store), "max_size": self.MAX_SIZE}


class RAGService:
    """Service untuk Standard RAG retrieval dengan caching."""

    def __init__(self):
        # ── Inisialisasi Embedding ──
        self.embedding = embedding_service.get_embedding_function()

        # ── Inisialisasi ChromaDB ──
        print("-> Initializing ChromaDB vectorstore...")
        self.vectorstore = Chroma(
            embedding_function=self.embedding,
            persist_directory=settings.CHROMA_PERSIST_DIR,
            collection_metadata={"hnsw:space": "cosine"},
        )
        print("[OK] ChromaDB loaded")

        # ── Deteksi distance metric ──
        try:
            meta = self.vectorstore._collection.metadata or {}
            self._distance_metric = meta.get("hnsw:space", "cosine")
        except Exception:
            self._distance_metric = "cosine"
        print(f"Distance metric: {self._distance_metric}")

        # ── Cache untuk hasil RAG ──
        self.cache = QueryCache()

        # ── Pre-filter: keyword list ──
        # Dipakai _is_non_it_query (dipanggil di thread berbeda secara bersamaan)
        # Keyword di-memo agar tidak re-parse regex setiap kali
        self._it_keywords: set[str] = set()
        self._non_it_keywords: set[str] = set()
        self._non_it_professions: set[str] = set()
        self._init_keywords()

    def _init_keywords(self) -> None:
        """Inisialisasi set keyword untuk pre-filter (sangat cepat lookup)."""
        self._it_keywords = {
            "sistem", "aplikasi", "software", "program", "komputer", "computer",
            "algoritma", "database", "data", "jaringan", "network", "web",
            "mobile", "android", "ios", "machine learning", "deep learning",
            "artificial intelligence", "ai", "cloud", "server", "client",
            "interface", "ui", "ux", "framework", "library", "api",
            "pemrograman", "coding", "programming", "developer",
            "teknologi informasi", "informatika", "ilkom",
            "sistem informasi", "berbasis", "berbasis web",
            "berbasis mobile", "berbasis android", "berbasis cloud",
        }
        self._non_it_keywords = {
            "dokter", "kedokteran", "kesehatan", "penyakit", "obat",
            "rumah sakit", "klinik", "pasien", "diagnosa", "terapi",
            "stunting", "gizi", "keperawatan", "bidan", "apotek", "farmasi",
            "guru", "mengajar", "pembelajaran", "tarbiyah", "pendidikan",
            "siswa", "murid", "sekolah", "kurikulum", "mata pelajaran",
            "inflasi", "profitabilitas", "bank syariah", "ekonomi",
            "akuntansi", "keuangan", "investasi", "saham", "pasar",
            "hukum", "yuridis", "undang-undang", "peraturan", "pidana",
            "perdata", "pengadilan", "jaksa", "advokat", "notaris",
            "pertanian", "petani", "pupuk", "tanaman", "ternak",
            "padi", "jagung", "kopi", "sawit", "iklim", "hujan",
            "psikologi", "sosiologi", "antropologi", "politik",
            "masyarakat", "budaya", "agama", "keagamaan",
            "novel", "sastra", "puisi", "cerpen", "literatur",
            "seni", "tari", "musik", "film", "teater", "fotografi",
            "filosofi", "etika", "moral",
        }
        self._non_it_professions = {
            "cara jadi", "cara menjadi", "menjadi dokter", "menjadi guru",
            "menjadi pengacara", "menjadi arsitek", "menjadi perawat",
            "menjadi polisi", "menjadi tentara", "menjadi koki",
            "menjadi atlet", "menjadi artis", "menjadi penyanyi",
        }

    def get_vector_count(self) -> int:
        try:
            return self.vectorstore._collection.count()
        except Exception:
            return 0

    def _is_non_it_query(self, query: str) -> bool:
        """
        Pre-filter cepat: apakah kueri di luar lingkup TI?
        Menggunakan set lookup (O(1)) + word boundary check (cepat).
        """
        query_lower = query.lower()

        # 1. Profesi non-IT → ditolak langsung
        for profesi in self._non_it_professions:
            if re.search(r'\b' + re.escape(profesi) + r'\b', query_lower):
                return True

        # 2. Ada keyword IT → valid
        for kw in self._it_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', query_lower):
                return False

        # 3. Ada keyword non-IT → ditolak
        for kw in self._non_it_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', query_lower):
                return True

        return False

    def _distance_to_score(self, distance: float) -> float:
        """Konversi ChromaDB distance ke similarity score (0–100%)."""
        try:
            d = float(distance)
            metric = self._distance_metric
            if metric == "cosine":
                score = (1.0 - d / 2.0) * 100.0
            elif metric == "l2":
                score = (1.0 / (1.0 + d)) * 100.0
            else:
                score = (1.0 - d) * 100.0
            return round(max(0.0, min(100.0, score)), 2)
        except (TypeError, ValueError):
            return 0.0

    def _build_document_response(self, doc, distance: float) -> dict:
        """Bangun response dokumen sesuai format JSON."""
        score = self._distance_to_score(distance)
        return {
            "page_content": doc.page_content,
            "metadata": {
                "source": doc.metadata.get("source", "Unknown"),
                "judul": doc.metadata.get("judul", ""),
                "nama": doc.metadata.get("nama", ""),
                "nim": doc.metadata.get("nim", ""),
                "pembimbing": doc.metadata.get("pembimbing", ""),
                "tahun": doc.metadata.get("tahun", ""),
                "similarity_score": score,
            },
        }

    def _deduplicate(self, docs_with_scores: list) -> list:
        """Hilangkan duplikat chunk dari skripsi yang sama."""
        seen: dict[str, tuple] = {}
        for doc, distance in docs_with_scores:
            nim = doc.metadata.get("nim", "").strip()
            judul = doc.metadata.get("judul", "").strip()
            source = doc.metadata.get("source", "").strip()

            if nim and judul:
                key = f"{nim}|{judul}"
            elif source:
                key = source
            else:
                key = f"__nokey_{id(doc)}"

            if key not in seen or distance < seen[key][1]:
                seen[key] = (doc, distance)

        return list(seen.values())

    def _apply_threshold(self, docs_with_scores: list, min_score: float) -> list:
        """Filter dokumen dengan similarity_score < min_score."""
        filtered = []
        for doc, distance in docs_with_scores:
            score = self._distance_to_score(distance)
            if score >= min_score:
                filtered.append((doc, distance))
        return filtered

    def standard_rag(
        self,
        query: str,
        k: int = None,
        min_score: float = None,
        use_mmr: bool = False,
    ) -> dict:
        """
        Standard RAG retrieval dengan in-memory caching.
        Query yang sama (k yang sama) → langsung ambil dari cache (latency ~0ms).
        """
        # ── Cek cache dulu (paling cepat, tanpa akses ChromaDB) ──
        cache_hit = self.cache.get(query, k or settings.K_RETRIEVAL)
        if cache_hit is not None:
            print(f"⚡ CACHE HIT: {query[:60]}...")
            cache_hit = cache_hit.copy()
            cache_hit["from_cache"] = True
            cache_hit["latency_ms"] = 0
            return cache_hit

        # ── Pre-filter: tolak kueri non-Teknik Informatika (tanpa cache) ──
        if self._is_non_it_query(query):
            print(f"🚫 Query rejected by pre-filter: {query}")
            return {
                "mode": "rag",
                "query": query,
                "docs_count": 0,
                "documents": [],
                "rejected": True,
                "from_cache": False,
            }

        # ── Retrieval dari ChromaDB ──
        t0 = time.perf_counter()

        if k is None:
            k = settings.K_RETRIEVAL

        min_score = getattr(settings, "MIN_SIMILARITY_SCORE", 30.0)

        # PREFIX E5 WAJIB
        query_repr = f"query: {query.strip()}"

        if use_mmr:
            fetch_k = min(k * 4, self.get_vector_count() or k * 4)
            mmr_docs = self.vectorstore.max_marginal_relevance_search(
                query_repr,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=0.7,
            )
            docs_with_scores = []
            for doc in mmr_docs:
                scored = self.vectorstore.similarity_search_with_score(
                    doc.page_content, k=1
                )
                if scored:
                    docs_with_scores.append((doc, scored[0][1]))
                else:
                    docs_with_scores.append((doc, 1.0))
        else:
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query_repr, k=k * 2
            )

        # Filter & Dedup
        docs_with_scores = self._apply_threshold(docs_with_scores, min_score)
        docs_with_scores = self._deduplicate(docs_with_scores)
        docs_with_scores = sorted(docs_with_scores, key=lambda x: x[1])[:k]

        documents = [
            self._build_document_response(doc, dist)
            for doc, dist in docs_with_scores
        ]

        result = {
            "mode": "rag",
            "query": query,
            "used_mmr": use_mmr,
            "docs_count": len(documents),
            "documents": documents,
            "from_cache": False,
        }
        result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # ── Simpan ke cache (hanya jika ada hasil, hindari cache kosong) ──
        if documents:
            self.cache.set(query, k, result)

        return result


# ─── Thread-safe singleton ───────────────────────────────────────────────────
_rag_service: RAGService | None = None
_rag_service_lock = threading.Lock()


def get_rag_service() -> RAGService:
    """Get atau create RAGService instance (thread-safe, double-checked locking)."""
    global _rag_service
    if _rag_service is None:
        with _rag_service_lock:
            if _rag_service is None:
                _rag_service = RAGService()
    return _rag_service
