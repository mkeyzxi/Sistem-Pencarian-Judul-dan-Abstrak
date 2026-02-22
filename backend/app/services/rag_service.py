"""
RAG Service
Menangani Standard RAG dan HyDE RAG retrieval logic.
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
    
    def standard_rag(self, query: str, k: int = None) -> dict:
        """
        Standard RAG retrieval - langsung retrieve dokumen relevan.
        
        Args:
            query: Query dari user
            k: Jumlah dokumen yang diambil (default dari settings)
            
        Returns:
            Dictionary berisi hasil retrieval dan metadata
        """
        if k is None:
            k = settings.K_RETRIEVAL
        
        # Retrieve dokumen menggunakan Max Marginal Relevance
        docs = self.vectorstore.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=settings.FETCH_K
        )
        
        return {
            "mode": "rag",
            "query": query,
            "docs_count": len(docs),
            "documents": [
                {
                    "title": doc.metadata.get("title", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown"),
                    "content": doc.page_content[:1500],  # Limit content
                    "score": None
                }
                for doc in docs
            ]
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
        
        # Embed hypothetical document
        hypo_vector = self.embedding.embed_query(hypothetical_doc)
        
        # Retrieve dokumen berdasarkan hypothetical vector
        docs = self.vectorstore.similarity_search_by_vector(
            hypo_vector,
            k=k
        )
        
        return {
            "mode": "hyde",
            "query": query,
            "hypothetical_document": hypothetical_doc,
            "docs_count": len(docs),
            "documents": [
                {
                    "title": doc.metadata.get("title", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown"),
                    "content": doc.page_content[:1500],
                    "score": None
                }
                for doc in docs
            ]
        }


# Singleton instance
rag_service = None


def get_rag_service():
    """Get or create RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service
