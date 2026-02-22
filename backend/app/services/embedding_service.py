"""
Embedding Service
Menghandle embedding model initialization dan caching.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings


class EmbeddingService:
    """Service untuk menangani embedding dengan HuggingFace."""
    
    _instance = None  # Singleton pattern
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize embedding model (sekali saja)."""
        if self._initialized:
            return
        
        print(f"🔄 Loading embedding model: {settings.EMBEDDING_MODEL}")
        
        self.embedding = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": settings.EMBEDDING_DEVICE},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        self._initialized = True
        print("✅ Embedding model loaded successfully")
    
    def get_embedding_function(self):
        """Return embedding function untuk digunakan di RAG."""
        return self.embedding
    
    def embed_text(self, text: str):
        """Embed satu text menjadi vektor."""
        return self.embedding.embed_query(text)
    
    def embed_texts(self, texts: list):
        """Embed multiple texts menjadi vektor."""
        return self.embedding.embed_documents(texts)


# Singleton instance
embedding_service = EmbeddingService()
