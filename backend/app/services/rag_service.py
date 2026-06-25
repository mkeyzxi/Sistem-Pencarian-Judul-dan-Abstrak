# """
# RAG Service
# Menangani Standard RAG dan HyDE RAG retrieval logic.

# REVISI 2: Output format sesuai REVISIDUA.md
# - Setiap dokumen dikembalikan sebagai {page_content, metadata}
# - similarity_score masuk ke dalam metadata
# """

# from langchain_community.vectorstores import Chroma
# from langchain_groq import ChatGroq
# from app.core.config import settings
# from app.services.embedding_service import embedding_service


# class RAGService:
#     """Service untuk menangani RAG dan HyDE retrieval."""
    
#     def __init__(self):
#         """Initialize RAG Service dengan embedding dan LLM."""
#         self.embedding = embedding_service.get_embedding_function()
        
#         # Initialize ChromaDB vectorstore
#         print("🔄 Initializing ChromaDB vectorstore...")
#         self.vectorstore = Chroma(
#             embedding_function=self.embedding,
#             persist_directory=settings.CHROMA_PERSIST_DIR
#         )
#         print("✅ ChromaDB loaded")
        
#         # Initialize Groq LLM
#         print("🔄 Initializing Groq LLM...")
#         self.llm = ChatGroq(
#             model=settings.GROQ_MODEL,
#             temperature=settings.LLM_TEMPERATURE,
#             groq_api_key=settings.GROQ_API_KEY,
#         )
#         print("✅ Groq LLM initialized")
    
#     def get_vector_count(self) -> int:
#         """Dapatkan jumlah vektor yang tersimpan."""
#         try:
#             return self.vectorstore._collection.count()
#         except:
#             return 0
    
#     @staticmethod
#     def _distance_to_score(distance: float) -> float:
#         """Konversi ChromaDB distance ke similarity score (0-100%).
        
#         ChromaDB dengan cosine distance mengembalikan nilai 0-2:
#         - 0 = identik (similarity 100%)
#         - 1 = orthogonal (similarity 0%)
#         - 2 = berlawanan (similarity -100%, kita clamp ke 0%)
        
#         Rumus: similarity = (1.0 - distance) * 100, di-clamp ke [0, 100].
#         """
#         try:
#             score = (1.0 - float(distance)) * 100.0
#             score = max(0.0, min(100.0, score))
#             return round(score, 2)
#         except (TypeError, ValueError):
#             return 0.0

#     def _build_document_response(self, doc, distance: float) -> dict:
#         """Bangun response dokumen sesuai format REVISIDUA.md.
        
#         Output: {
#             "page_content": "...",
#             "metadata": {
#                 "source": "...",
#                 "judul": "...",
#                 "nama": "...",
#                 "nim": "...",
#                 "pembimbing": "...",
#                 "tahun": "...",
#                 "similarity_score": 75.0
#             }
#         }
#         """
#         score = self._distance_to_score(distance)

#         return {
#             "page_content": doc.page_content,
#             "metadata": {
#                 "source": doc.metadata.get("source", "Unknown"),
#                 "judul": doc.metadata.get("judul", ""),
#                 "nama": doc.metadata.get("nama", ""),
#                 "nim": doc.metadata.get("nim", ""),
#                 "pembimbing": doc.metadata.get("pembimbing", ""),
#                 "tahun": doc.metadata.get("tahun", ""),
#                 "similarity_score": score,
#             },
#         }

#     def standard_rag(self, query: str, k: int = None) -> dict:
#         """
#         Standard RAG retrieval - langsung retrieve dokumen relevan.
        
#         Menggunakan similarity_search_with_score() yang mengembalikan
#         list[(Document, distance)] sehingga skor relevansi bisa dihitung.
        
#         Args:
#             query: Query dari user
#             k: Jumlah dokumen yang diambil (default dari settings)
            
#         Returns:
#             Dictionary berisi hasil retrieval dan metadata
#         """
#         if k is None:
#             k = settings.K_RETRIEVAL
        
#         docs_with_scores = self.vectorstore.similarity_search_with_score(
#             query,
#             k=k,
#         )

#         documents = []
#         for doc, distance in docs_with_scores:
#             documents.append(self._build_document_response(doc, distance))

#         return {
#             "mode": "rag",
#             "query": query,
#             "docs_count": len(documents),
#             "documents": documents
#         }
    
#     def hyde_rag(self, query: str, k: int = None) -> dict:
#         """
#         HyDE (Hypothetical Document Embeddings) RAG.
#         Generate hypothetical document untuk memperbaiki retrieval.
        
#         Args:
#             query: Query dari user
#             k: Jumlah dokumen yang diambil
            
#         Returns:
#             Dictionary berisi hypothetical doc dan dokumen relevan
#         """
#         if k is None:
#             k = settings.K_RETRIEVAL
        
#         # Generate hypothetical abstract
#         clean_query = query.strip()
#         prompt = f"""Anda adalah asisten akademik yang ahli dalam penulisan abstrak skripsi Teknik Informatika. Tugas Anda adalah menghasilkan sebuah potongan abstrak hipotetis (maksimal 3 kalimat) yang merangkum fokus utama penelitian berdasarkan kueri berikut.

# Aturan Mutlak:
# 1. Koreksi Leksikal (Typo): Jika kueri mengandung salah ketik atau singkatan tidak baku, perbaiki secara otomatis ke dalam istilah baku Teknik Informatika sebelum menyusun abstrak.
# 2. Kueri Awam (Semantik): Jika kueri menggunakan bahasa non-formal (misal: "alat buat cegah maling motor"), terjemahkan dan susun menjadi narasi akademis spesifik (misal: "Penelitian ini mengembangkan sistem keamanan kendaraan bermotor menggunakan mikrokontroler...").
# 3. Kueri Teknis (Leksikal): Jika kueri sudah berisi algoritma/istilah spesifik (misal: "k-means", "yolov8"), JANGAN berhalusinasi menambahkan sensor, metode, atau arsitektur lain secara acak. Fokuskan narasi murni pada implementasi metode tersebut.
# 4. Format: Dilarang memberikan salam, pendahuluan, atau label 'Output:'. Langsung berikan teks abstraknya.

# Kueri: "{clean_query}"
# Abstrak Hipotetis:"""
        
#         try:
#             hypothetical_doc = self.llm.invoke(prompt).content.strip()
#         except Exception as e:
#             print(f"Error generating hypothetical doc: {e}")
#             hypothetical_doc = query
        
#         # Retrieve menggunakan hypothetical doc sebagai query
#         docs_with_scores = self.vectorstore.similarity_search_with_score(
#             hypothetical_doc,
#             k=k,
#         )

#         documents = []
#         for doc, distance in docs_with_scores:
#             documents.append(self._build_document_response(doc, distance))

#         return {
#             "mode": "hyde",
#             "query": query,
#             "hypothetical_document": hypothetical_doc,
#             "docs_count": len(documents),
#             "documents": documents
#         }


# # Singleton instance
# rag_service = None


# def get_rag_service():
#     """Get or create RAG service instance."""
#     global rag_service
#     if rag_service is None:
#         rag_service = RAGService()
#     return rag_service


"""
RAG Service — REVISI 3
Perbaikan: distance formula, HyDE prompt, threshold filtering,
deduplication, MMR untuk Standard RAG, dan thread-safe singleton.
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
            persist_directory=settings.CHROMA_PERSIST_DIR
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
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            groq_api_key=settings.GROQ_API_KEY,
        )
        print("✅ Groq LLM initialized")

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
        """Bangun response dokumen sesuai format REVISIDUA.md."""
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

        Jika NIM kosong (metadata tidak lengkap), fallback ke source path.
        """
        seen: dict[str, tuple] = {}  # key → (doc, distance)

        for doc, distance in docs_with_scores:
            nim = doc.metadata.get("nim", "").strip()
            judul = doc.metadata.get("judul", "").strip()
            source = doc.metadata.get("source", "").strip()

            # Buat dedup key: utamakan NIM+judul, fallback ke source
            if nim and judul:
                key = f"{nim}|{judul}"
            elif source:
                key = source
            else:
                # Tidak bisa dedup, selalu masukkan
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
        use_mmr: bool = True,
    ) -> dict:
        """
        Standard RAG retrieval.

        Perbaikan dari versi sebelumnya:
        1. Opsional MMR (Maximal Marginal Relevance) untuk diversifikasi hasil
        2. Similarity threshold filtering
        3. Deduplication berdasarkan NIM/judul

        Args:
            query     : Query dari user
            k         : Jumlah dokumen dikembalikan (default dari settings)
            min_score : Minimum similarity score 0–100 (default dari settings)
            use_mmr   : Gunakan MMR untuk hasil yang lebih beragam

        Returns:
            Dictionary berisi hasil retrieval dan metadata
        """
        if k is None:
            k = settings.K_RETRIEVAL
        if min_score is None:
            min_score = getattr(settings, "MIN_SIMILARITY_SCORE", 30.0)

        if use_mmr:
            # MMR fetch lebih banyak kandidat dulu (fetch_k), lalu diversifikasi
            fetch_k = min(k * 4, self.get_vector_count() or k * 4)
            mmr_docs = self.vectorstore.max_marginal_relevance_search(
                query,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=0.7,  # 0=max diversity, 1=max relevance
            )
            # MMR tidak mengembalikan score, ambil score via similarity_search
            # untuk dokumen yang sudah dipilih MMR
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
                query, k=k * 2  # ambil lebih banyak sebelum filter
            )

        # Threshold filtering
        docs_with_scores = self._apply_threshold(docs_with_scores, min_score)

        # Deduplication
        docs_with_scores = self._deduplicate(docs_with_scores)

        # Ambil top-k setelah filter+dedup
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
    ) -> dict:
        """
        HyDE (Hypothetical Document Embeddings) RAG.

        Perbaikan prompt:
        - Satu instruksi positif yang jelas, tanpa aturan berlapis
        - Eksplisit: output harus Bahasa Indonesia
        - Eksplisit: 2–3 kalimat saja, murni konten akademis
        - Eksplisit: jika kueri tidak relevan dengan TI, tetap hasilkan
          abstrak terdekat tanpa mengarang bidang/metode yang tidak disebut

        Args:
            query     : Query dari user
            k         : Jumlah dokumen dikembalikan
            min_score : Minimum similarity score 0–100

        Returns:
            Dictionary berisi hypothetical doc dan dokumen relevan
        """
        if k is None:
            k = settings.K_RETRIEVAL
        if min_score is None:
            min_score = getattr(settings, "MIN_SIMILARITY_SCORE", 30.0)

        # ─── Prompt HyDE yang diperbaiki ───────────────────────────────────────
        # Filosofi:
        #   1. SATU tugas jelas: tulis abstrak hipotetis skripsi Teknik Informatika
        #   2. Batasan output diatur POSITIF ("tulis hanya X") bukan LARANGAN
        #   3. Deteksi typo/kueri awam dilakukan IMPLISIT lewat contoh
        #   4. Bahasa Indonesia eksplisit → hindari output campur bahasa
        #   5. Strict: HANYA sebutkan metode/teknologi yang ada di kueri
        # ───────────────────────────────────────────────────────────────────────
        prompt = (
            "Tugas: Tulis satu paragraf abstrak skripsi Teknik Informatika dalam "
            "Bahasa Indonesia berdasarkan topik berikut.\n\n"
            "Aturan ketat:\n"
            "- Panjang: 2–3 kalimat saja.\n"
            "- Hanya sebutkan metode, algoritma, atau teknologi yang TERSEBUT "
            "SECARA EKSPLISIT atau TERSIRAT LANGSUNG dari topik. "
            "Jangan tambahkan metode lain.\n"
            "- Jika topik menggunakan bahasa sehari-hari (misal: 'aplikasi "
            "absensi pakai muka'), terjemahkan ke istilah akademis yang tepat "
            "(misal: 'Penelitian ini membangun sistem absensi berbasis "
            "pengenalan wajah...').\n"
            "- Jika ada typo, koreksi otomatis ke istilah baku yang paling "
            "mendekati dalam bidang Teknik Informatika.\n"
            "- Output hanya teks abstrak. Tanpa salam, tanpa label, tanpa "
            "tanda kutip pembuka/penutup.\n\n"
            f"Topik: {query.strip()}"
        )

        try:
            hypothetical_doc = self.llm.invoke(prompt).content.strip()
            # Sanitasi: buang baris kosong ganda dan leading/trailing whitespace
            hypothetical_doc = " ".join(hypothetical_doc.split())
        except Exception as e:
            print(f"⚠️  Error generating hypothetical doc: {e}")
            hypothetical_doc = query  # graceful fallback

        # Retrieve menggunakan hypothetical doc
        docs_with_scores = self.vectorstore.similarity_search_with_score(
            hypothetical_doc,
            k=k * 2,  # ambil lebih banyak sebelum filter
        )

        # Threshold + deduplication (sama seperti standard_rag)
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

    Menggunakan double-checked locking pattern agar aman
    di environment async / multi-thread seperti FastAPI.
    """
    global _rag_service
    if _rag_service is None:
        with _rag_service_lock:
            if _rag_service is None:  # check ulang di dalam lock
                _rag_service = RAGService()
    return _rag_service