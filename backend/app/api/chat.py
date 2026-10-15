"""
Chat & Chatbot Endpoints
API endpoint untuk pencarian skripsi (RAG/HyDE/Hybrid) dan chatbot interaktif.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.rag_service import get_rag_service
from app.services.suggestion_service import suggestion_service

# Create router
router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Model untuk request chat."""
    message: str
    mode: Optional[str] = "rag"  # "rag", "hyde", atau "hybrid"
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
    - "hybrid": Hybrid Search (BM25 + ChromaDB + Metadata Filter)
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
        elif request.mode == "hybrid":
            result = rag.hybrid_rag(request.message)
        else:
            result = rag.standard_rag(request.message)
        
        # Validasi: jika kueri ditolak oleh domain filter
        if result.get("rejected"):
            return ChatResponse(
                success=False,
                message=result.get("hypothetical_document") or "Kueri ditolak: Topik tidak relevan dengan keilmuan Teknik Informatika.",
                query=request.message,
                mode=request.mode,
                documents=[]
            )
        
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


# ─── Chatbot Mode (Mode ke-4: Asisten Interaktif) ────────────────────────────

class ChatbotRequest(BaseModel):
    """Model untuk request chatbot interaktif."""
    message: str
    chat_history: list = []  # Riwayat percakapan (sliding window, max 8)


class ChatbotResponse(BaseModel):
    """Model untuk response chatbot interaktif (tanpa documents[])."""
    success: bool
    message: str
    mode: str = "chatbot"


@router.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_endpoint(request: ChatbotRequest):
    """
    Endpoint untuk mode Chatbot Interaktif (Mode ke-4).
    
    Berbeda dari /api/chat yang mengembalikan dokumen hasil pencarian,
    endpoint ini berfungsi sebagai asisten interaktif yang:
    - Menjawab pertanyaan umum seputar skripsi
    - Merekomendasikan judul baru (via Agentic RAG + Tool Calling)
    - Menganalisis research gap
    - Mendiskusikan ide penelitian
    
    Response TIDAK mengandung field 'documents' — hanya teks narasi markdown.
    """
    try:
        # Validasi input
        if not request.message or len(request.message.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Pesan terlalu pendek. Minimal 3 karakter."
            )
        
        # Lazy import untuk menghindari overhead saat startup
        from app.services.chatbot_service import get_chatbot_service
        chatbot_svc = get_chatbot_service()
        
        # Generate response (Agentic RAG with Tool Calling)
        response_text = chatbot_svc.generate_response(
            request.message,
            request.chat_history
        )
        
        return ChatbotResponse(
            success=True,
            message=response_text,
            mode="chatbot"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saat memproses pertanyaan chatbot: {str(e)}"
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
        from app.core.config import settings
        rag = get_rag_service()
        return {
            "app_name": "Chatbot Pencarian Skripsi",
            "version": "1.0.0",
            "embedding_model": "intfloat/multilingual-e5-small",
            "llm_model": "meta-llama/llama-3-70b-versatile (Groq untuk RAG/HyDE/Hybrid)",
            "chatbot_llm_model": f"{settings.GEMINI_MODEL} (Gemini API untuk Chatbot Mode)",
            "retrieval_modes": ["rag", "hyde", "hybrid", "chatbot"],
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
