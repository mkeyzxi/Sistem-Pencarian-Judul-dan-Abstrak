"""
Chat Endpoint
API endpoint untuk chatbot pencarian skripsi.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.rag_service import get_rag_service
from app.services.suggestion_service import suggestion_service
from app.core.config import settings

# Create router
router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Model untuk request chat."""
    message: str
    mode: Optional[str] = "rag"  # "rag" atau "hyde"
    chat_history: list = []  # Riwayat percakapan untuk konteks follow-up


class ChatResponse(BaseModel):
    """Model untuk response chat."""
    success: bool
    message: str
    query: str
    mode: str
    documents: list = []
    suggestion: Optional[str] = None
    hypothetical_document: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint untuk chatbot.
    
    Query dapat berupa:
    - Topik singkat (contoh: "sistem rekomendasi")
    - Judul skripsi lengkap
    
    Mode:
    - "rag": Standard RAG
    - "hyde": HyDE RAG
    """
    
    try:
        # Validasi input
        if not request.message or len(request.message.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Pesan terlalu pendek. Minimal 3 karakter."
            )
        
        # Get RAG service
        rag = get_rag_service()
        
        # Retrieve dokumen berdasarkan mode
        if request.mode == "hyde":
            result = rag.hyde_rag(request.message)
        else:
            result = rag.standard_rag(request.message)
        
        # Validasi hasil retrieval
        if result["docs_count"] == 0:
            return ChatResponse(
                success=False,
                message="❌ Maaf, tidak ditemukan skripsi yang relevan dengan query Anda. Coba gunakan kata kunci yang berbeda.",
                query=request.message,
                mode=request.mode,
                documents=[]
            )
        
        # Generate chat response (natural)
        chat_message = suggestion_service.generate_chat_response(
            request.message,
            result["documents"],
            request.mode,
            request.chat_history
        )
        
        # Check if this is a full title (generate suggestion if yes)
        suggestion = None
        if len(request.message) > 50 and any(
            keyword in request.message.lower()
            for keyword in ["sistem", "aplikasi", "pengembangan", "implementasi", "analisis"]
        ):
            suggestion = suggestion_service.generate_suggestion(
                request.message,
                result["documents"]
            )
        
        return ChatResponse(
            success=True,
            message=chat_message,
            query=request.message,
            mode=request.mode,
            documents=result["documents"],
            suggestion=suggestion,
            hypothetical_document=result.get("hypothetical_document")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saat memproses query: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        rag = get_rag_service()
        vector_count = rag.get_vector_count()
        
        return {
            "status": "healthy",
            "message": "Server berjalan normal",
            "vector_database": {
                "status": "connected",
                "vectors_count": vector_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Error: {str(e)}",
            "vector_database": {
                "status": "disconnected"
            }
        }


@router.get("/info")
async def get_info():
    """Get system info."""
    try:
        rag = get_rag_service()
        return {
            "app_name": "Chatbot Pencarian Skripsi",
            "version": "1.0.0",
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_model": settings.GROQ_MODEL,
            "retrieval_modes": ["rag", "hyde"],
            "vector_database": {
                "type": "ChromaDB",
                "vectors_count": rag.get_vector_count()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
