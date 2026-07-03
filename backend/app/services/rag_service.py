
"""
RAG Service — REVISI FINAL
Terintegrasi Mode Evaluasi (Bypass Threshold & MMR) & E5 Prefix Absolut.
Prompt HyDE dipertahankan murni dari spesifikasi user.
"""

import threading
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from app.core.config import settings
from app.services.embedding_service import embedding_service


class RAGService:
    """Service untuk menangani RAG dan HyDE retrieval."""

    def __init__(self):
        self.embedding = embedding_service.get_embedding_function()

        print("🔄 Initializing ChromaDB vectorstore...")
        self.vectorstore = Chroma(
            embedding_function=self.embedding,
            persist_directory=settings.CHROMA_PERSIST_DIR,
            collection_metadata={"hnsw:space": "cosine"}
        )
        print("✅ ChromaDB loaded")

        # Deteksi distance metric collection (cosine vs l2 vs ip)
        # Agar _distance_to_score tidak salah hitung
        try:
            meta = self.vectorstore._collection.metadata or {}
            self._distance_metric = meta.get("hnsw:space", "cosine")
        except Exception:
            self._distance_metric = "cosine"
        print(f"📐 Distance metric: {self._distance_metric}")

        print("🔄 Initializing Groq LLM...")
        self.llm_standard = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=getattr(settings, "LLM_TEMPERATURE_STANDARD", 0.0),
            max_tokens=settings.LLM_MAX_TOKENS,
            model_kwargs={
                "top_p": settings.LLM_TOP_P,
                "frequency_penalty": settings.LLM_FREQUENCY_PENALTY,
                "presence_penalty": settings.LLM_PRESENCE_PENALTY,
            },
            groq_api_key=settings.GROQ_API_KEY,
        )
        
        self.llm_hyde = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=getattr(settings, "LLM_TEMPERATURE_HYDE", 0.4),
            max_tokens=settings.LLM_MAX_TOKENS,
            model_kwargs={
                "top_p": settings.LLM_TOP_P,
                "frequency_penalty": settings.LLM_FREQUENCY_PENALTY,
                "presence_penalty": settings.LLM_PRESENCE_PENALTY,
            },
            groq_api_key=settings.GROQ_API_KEY,
        )
        print("✅ Groq LLM initialized")

        # Prompt 1: Strict Abstract Components (masalah, metode, hasil)
        self.prompt_1 = (
            "Tugas: Tulis satu paragraf abstrak skripsi Teknik Informatika dalam Bahasa Indonesia "
            "berdasarkan topik berikut.\n"
            "Struktur abstrak harus mengikuti komponen berikut secara ketat:\n"
            "1. Masalah: Masalah penelitian yang diselesaikan.\n"
            "2. Metode: Metode, algoritma, atau teknologi yang digunakan.\n"
            "3. Hasil: Hasil atau tujuan akhir yang ingin dicapai.\n\n"
            "Topik: {query}"
        )

        # Prompt 2: Strict Constraints to reduce ambiguity and hallucination (focused and deterministic context)
        self.prompt_2 = (
            "Tugas: Tulis satu paragraf abstrak skripsi Teknik Informatika dalam "
            "Bahasa Indonesia berdasarkan topik berikut.\n\n"
            "Aturan ketat:\n"
            "- Panjang: 2–3 kalimat saja.\n"
            "- Hanya sebutkan metode, algoritma, atau teknologi yang TERSEBUT "
            "SECARA EKSPLISIT atau TERSIRAT LANGSUNG dari topik. "
            "Jangan tambahkan metode lain untuk mengurangi ambiguitas dan halusinasi.\n"
            "- Jika topik menggunakan bahasa sehari-hari (misal: 'aplikasi "
            "absensi pakai muka'), terjemahkan ke istilah akademis yang tepat "
            "(misal: 'Penelitian ini membangun sistem absensi berbasis "
            "pengenalan wajah...').\n"
            "- Jika ada typo, koreksi otomatis ke istilah baku yang paling "
            "mendekati dalam bidang Teknik Informatika.\n"
            "- Output hanya teks abstrak. Tanpa salam, tanpa label, tanpa "
            "tanda kutip pembuka/penutup.\n\n"
            "Topik: {query}"
        )

    def get_vector_count(self) -> int:
        try:
            return self.vectorstore._collection.count()
        except Exception:
            return 0

    def _distance_to_score(self, distance: float) -> float:
        """
        Konversi ChromaDB distance ke similarity score (0–100%).

        - cosine distance  → range [0, 2]  → score = (1 - d/2) * 100
        - l2 distance      → range [0, ∞]  → score = 1/(1+d) * 100  (approx)
        - inner product    → range [0, 1]  → score = (1 - d) * 100
        """
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
        """
        Hilangkan duplikat chunk dari skripsi yang sama.
        Kriteria: NIM + judul yang sama → ambil yang score-nya tertinggi
        (distance terkecil) saja.
        """
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
        """
        Filter dokumen dengan similarity_score < min_score.
        Bekerja pada raw distance — konversi dulu sebelum filter.
        """
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
        is_eval: bool = False,
    ) -> dict:
        """
        Standard RAG retrieval.
        Terintegrasi dengan saklar evaluasi (is_eval).
        """
        if k is None:
            k = settings.K_RETRIEVAL
            
        if is_eval:
            use_mmr = False  # Mutlak dimatikan saat evaluasi
            min_score = 0.0  # Bypass threshold saat evaluasi
        elif min_score is None:
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

        # Pemfilteran & Dedup HANYA dijalankan jika bukan mode evaluasi
        if not is_eval:
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

    def hyde_rag(
        self,
        query: str,
        k: int = None,
        min_score: float = None,
        is_eval: bool = False,
        prompt_type: str = "prompt2",
    ) -> dict:
        """
        HyDE (Hypothetical Document Embeddings) RAG.
        Terintegrasi dengan saklar evaluasi (is_eval) dan pilihan prompt_type.
        """
        if k is None:
            k = settings.K_RETRIEVAL
            
        if is_eval:
            min_score = 0.0  # Bypass threshold saat evaluasi
        elif min_score is None:
            min_score = getattr(settings, "MIN_SIMILARITY_SCORE", 30.0)

        # Pilih template prompt berdasarkan parameter
        if prompt_type == "prompt1":
            prompt = self.prompt_1.format(query=query.strip())
        else:
            prompt = self.prompt_2.format(query=query.strip())

        try:
            hypothetical_doc = self.llm_hyde.invoke(prompt).content.strip()
            hypothetical_doc = " ".join(hypothetical_doc.split())
        except Exception as e:
            print(f"⚠️  Error generating hypothetical doc: {e}")
            hypothetical_doc = query  

        # PREFIX E5 WAJIB UNTUK HYPOTHETICAL DOC
        query_repr = f"query: {hypothetical_doc}"

        docs_with_scores = self.vectorstore.similarity_search_with_score(
            query_repr, k=k * 2
        )

        # Pemfilteran & Dedup HANYA dijalankan jika bukan mode evaluasi
        if not is_eval:
            docs_with_scores = self._apply_threshold(docs_with_scores, min_score)
            docs_with_scores = self._deduplicate(docs_with_scores)
            
        docs_with_scores = sorted(docs_with_scores, key=lambda x: x[1])[:k]

        documents = [
            self._build_document_response(doc, dist)
            for doc, dist in docs_with_scores
        ]

        return {
            "mode": "hyde",
            "query": query,
            "hypothetical_document": hypothetical_doc,
            "docs_count": len(documents),
            "documents": documents,
        }


# ─── Thread-safe singleton ───────────────────────────────────────────────────
_rag_service: RAGService | None = None
_rag_service_lock = threading.Lock()


def get_rag_service() -> RAGService:
    """
    Get atau create RAGService instance (thread-safe).
    """
    global _rag_service
    if _rag_service is None:
        with _rag_service_lock:
            if _rag_service is None:
                _rag_service = RAGService()
    return _rag_service