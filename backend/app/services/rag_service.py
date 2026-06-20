"""
RAG Service
Menangani Standard RAG dan HyDE RAG retrieval logic.

REVISI 2: Output format sesuai REVISIDUA.md
- Setiap dokumen dikembalikan sebagai {page_content, metadata}
- similarity_score masuk ke dalam metadata
"""

from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from app.core.config import settings
from app.services.embedding_service import embedding_service


class RAGService:
    """Service untuk menangani RAG dan HyDE retrieval."""
    
    def __init__(self):
        """Initialize RAG Service dengan embedding dan LLM."""
        self.embedding = embedding_service.get_embedding_function()
        
        # Initialize ChromaDB vectorstore
        print("🔄 Initializing ChromaDB vectorstore...")
        self.vectorstore = Chroma(
            embedding_function=self.embedding,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )
        print("✅ ChromaDB loaded")
        
        # Initialize Groq LLM
        print("🔄 Initializing Groq LLM...")
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            groq_api_key=settings.GROQ_API_KEY,
        )
        print("✅ Groq LLM initialized")
    
    def get_vector_count(self) -> int:
        """Dapatkan jumlah vektor yang tersimpan."""
        try:
            return self.vectorstore._collection.count()
        except:
            return 0
    
    @staticmethod
    def _distance_to_score(distance: float) -> float:
        """Konversi ChromaDB distance ke similarity score (0-100%).
        
        ChromaDB dengan cosine distance mengembalikan nilai 0-2:
        - 0 = identik (similarity 100%)
        - 1 = orthogonal (similarity 0%)
        - 2 = berlawanan (similarity -100%, kita clamp ke 0%)
        
        Rumus: similarity = (1.0 - distance) * 100, di-clamp ke [0, 100].
        """
        try:
            score = (1.0 - float(distance)) * 100.0
            score = max(0.0, min(100.0, score))
            return round(score, 2)
        except (TypeError, ValueError):
            return 0.0

    def _build_document_response(self, doc, distance: float) -> dict:
        """Bangun response dokumen sesuai format REVISIDUA.md.
        
        Output: {
            "page_content": "...",
            "metadata": {
                "source": "...",
                "judul": "...",
                "nama": "...",
                "nim": "...",
                "pembimbing": "...",
                "tahun": "...",
                "similarity_score": 75.0
            }
        }
        """
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

    def standard_rag(self, query: str, k: int = None) -> dict:
        """
        Standard RAG retrieval - langsung retrieve dokumen relevan.
        
        Menggunakan similarity_search_with_score() yang mengembalikan
        list[(Document, distance)] sehingga skor relevansi bisa dihitung.
        
        Args:
            query: Query dari user
            k: Jumlah dokumen yang diambil (default dari settings)
            
        Returns:
            Dictionary berisi hasil retrieval dan metadata
        """
        if k is None:
            k = settings.K_RETRIEVAL
        
        docs_with_scores = self.vectorstore.similarity_search_with_score(
            query,
            k=k,
        )

        documents = []
        for doc, distance in docs_with_scores:
            documents.append(self._build_document_response(doc, distance))

        return {
            "mode": "rag",
            "query": query,
            "docs_count": len(documents),
            "documents": documents
        }
    
    def hyde_rag(self, query: str, k: int = None) -> dict:
        """
        HyDE (Hypothetical Document Embeddings) RAG.
        Generate hypothetical document untuk memperbaiki retrieval.
        
        Args:
            query: Query dari user
            k: Jumlah dokumen yang diambil
            
        Returns:
            Dictionary berisi hypothetical doc dan dokumen relevan
        """
        if k is None:
            k = settings.K_RETRIEVAL
        
        # Generate hypothetical abstract
        prompt = f"""Tuliskan abstrak skripsi singkat (3-4 kalimat) yang relevan dengan topik berikut:

Topik: "{query}"

Abstrak:"""
        
        try:
            hypothetical_doc = self.llm.invoke(prompt).content.strip()
        except Exception as e:
            print(f"Error generating hypothetical doc: {e}")
            hypothetical_doc = query
        
        # Retrieve menggunakan hypothetical doc sebagai query
        docs_with_scores = self.vectorstore.similarity_search_with_score(
            hypothetical_doc,
            k=k,
        )

        documents = []
        for doc, distance in docs_with_scores:
            documents.append(self._build_document_response(doc, distance))

        return {
            "mode": "hyde",
            "query": query,
            "hypothetical_document": hypothetical_doc,
            "docs_count": len(documents),
            "documents": documents
        }


# Singleton instance
rag_service = None


def get_rag_service():
    """Get or create RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service
