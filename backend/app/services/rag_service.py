"""
RAG Service — Fokus RAG (Standard)
Fungsi: Standard RAG retrieval untuk frontend-v2.
E5 Prefix absolut untuk query pencarian.
"""

import re
import threading
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from app.core.config import settings
from app.services.embedding_service import embedding_service


class RAGService:
    """Service untuk Standard RAG retrieval."""

    def __init__(self):
        self.embedding = embedding_service.get_embedding_function()

        print("-> Initializing ChromaDB vectorstore...")
        self.vectorstore = Chroma(
            embedding_function=self.embedding,
            persist_directory=settings.CHROMA_PERSIST_DIR,
            collection_metadata={"hnsw:space": "cosine"},
        )
        print("[OK] ChromaDB loaded")

        # Deteksi distance metric collection
        try:
            meta = self.vectorstore._collection.metadata or {}
            self._distance_metric = meta.get("hnsw:space", "cosine")
        except Exception:
            self._distance_metric = "cosine"
        print(f"Distance metric: {self._distance_metric}")

        # LLM untuk RAG
        print("🔄 Initializing Groq LLM...")
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=settings.LLM_TEMPERATURE_STANDARD,
            max_tokens=settings.LLM_MAX_TOKENS,
            groq_api_key=settings.GROQ_API_KEY,
        )

    def get_vector_count(self) -> int:
        try:
            return self.vectorstore._collection.count()
        except Exception:
            return 0

    def _is_non_it_query(self, query: str) -> bool:
        """
        Pre-filter cerdas untuk mendeteksi kueri yang jelas-jelas di luar
        lingkup Teknik Informatika. Return True jika kueri harus ditolak.
        """
        query_lower = query.lower()

        it_keywords = [
            "sistem", "aplikasi", "software", "program", "komputer", "computer",
            "algoritma", "database", "data", "jaringan", "network", "web",
            "mobile", "android", "ios", "machine learning", "deep learning",
            "artificial intelligence", "ai", "cloud", "server", "client",
            "interface", "ui", "ux", "framework", "library", "api",
            "pemrograman", "coding", "programming", "developer",
            "teknologi informasi", "informatika", "ilkom",
            "sistem informasi", "sistem berkaitan", "berbasis", "berbasis web",
            "berbasis mobile", "berbasis android", "berbasis cloud",
        ]

        non_it_professions = [
            "cara jadi", "cara menjadi", "menjadi dokter", "menjadi guru",
            "menjadi pengacara", "menjadi arsitek", "menjadi perawat",
            "menjadi polisi", "menjadi tentara", "menjadi koki",
            "menjadi atlet", "menjadi artis", "menjadi penyanyi",
        ]

        non_it_keywords = [
            "dokter", "kedokteran", "kesehatan", "penyakit", "obat", "rumah sakit",
            "klinik", "pasien", "diagnosa", "terapi", "stunting", "gizi",
            "keperawatan", "bidan", "apotek", "farmasi",
            "guru", "mengajar", "pembelajaran", "tarbiyah", "pendidikan",
            "siswa", "murid", "sekolah", "kurikulum", "mata pelajaran",
            "inflasi", "profitabilitas", "bank syariah", "ekonomi",
            "akuntansi", "keuangan", "investasi", "saham", "pasar",
            "hukum", "yuridis", "undang-undang", "peraturan", "pidana",
            "perdata", "pengadilan", "jaksa", "advokat", "notaris",
            "pertanian", "petani", "pupuk", "tanaman", "ternak",
            "padi", "jagung", "kopi", "sawit", "iklim", "hujan",
            "psikologi", "sosiologi", "antropologi", "politik", "pemerintahan",
            "masyarakat", "budaya", "agama", "keagamaan",
            "novel", "sastra", "wacana", "puisi", "cerpen", "literatur",
            "seni", "tari", "musik", "film", "teater", "lukisan", "fotografi",
            "keindahan", "estetika", "filosofi", "etika", "moral",
        ]

        def contains_word(text: str, word: str) -> bool:
            return bool(re.search(r'\b' + re.escape(word) + r'\b', text))

        # 1. Cek profesi non-IT (selalu ditolak)
        for profesi in non_it_professions:
            if contains_word(query_lower, profesi):
                return True

        # 2. Cek kata kunci IT → jika ada, query valid (return False)
        for keyword in it_keywords:
            if contains_word(query_lower, keyword):
                return False

        # 3. Cek kata kunci non-IT → jika ada tanpa konteks IT, ditolak
        for keyword in non_it_keywords:
            if contains_word(query_lower, keyword):
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
            else:  # "ip" atau inner product
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

    def _apply_threshold(
        self,
        docs_with_scores: list,
        min_score: float,
    ) -> list:
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
        Standard RAG retrieval.
        """
        # Pre-filter: tolak kueri non-Teknik Informatika
        if self._is_non_it_query(query):
            print(f"🚫 Query rejected by pre-filter: {query}")
            return {
                "mode": "rag",
                "query": query,
                "docs_count": 0,
                "documents": [],
                "rejected": True,
            }

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

        return {
            "mode": "rag",
            "query": query,
            "used_mmr": use_mmr,
            "docs_count": len(documents),
            "documents": documents,
        }


# ─── Thread-safe singleton ───────────────────────────────────────────────────
_rag_service: RAGService | None = None
_rag_service_lock = threading.Lock()


def get_rag_service() -> RAGService:
    """Get atau create RAGService instance (thread-safe)."""
    global _rag_service
    if _rag_service is None:
        with _rag_service_lock:
            if _rag_service is None:
                _rag_service = RAGService()
    return _rag_service
