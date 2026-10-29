"""
Chat Endpoints
API endpoint untuk pencarian skripsi (RAG) yang difokuskan pada kebutuhan frontend-v2.
Mode: "rag" (Standard RAG).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.rag_service import get_rag_service

# Create router
router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Model untuk request chat."""
    message: str
    mode: Optional[str] = "rag"  # "rag"
    chat_history: list = []  # Riwayat percakapan untuk konteks follow-up


class ChatResponse(BaseModel):
    """Model untuk response chat."""
    success: bool
    message: str
    query: str
    mode: str
    documents: list = []
    suggestion: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint untuk pencarian RAG.
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
        
        # Retrieve dokumen menggunakan Standard RAG
        result = rag.standard_rag(request.message)
        
        # Validasi: jika kueri ditolak oleh domain filter
        if result.get("rejected"):
            return ChatResponse(
                success=False,
                message="Kueri ditolak: Topik tidak relevan dengan keilmuan Teknik Informatika.",
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
        
        return ChatResponse(
            success=True,
            message="Pencarian berhasil",
            query=request.message,
            mode=request.mode,
            documents=result["documents"],
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saat memproses query: {str(e)}"
        )
