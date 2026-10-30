"""
Chat Endpoints
API endpoint untuk pencarian skripsi (RAG) untuk frontend-v2.

Fitur:
- Async I/O (FastAPI) — banyak request concurrent tanpa blocking
- Query cache di RAGService (reduksi latency ~0ms untuk query duplikat)
- Narrative LLM (Opsi A — Full RAG: Retrieval + Generation)
- Rate limiting per-IP sederhana
- Health check ringan
"""

import time
import asyncio
import threading
from collections import deque
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.services.rag_service import get_rag_service
from app.services.generation_service import get_generation_service

router = APIRouter(prefix="/api", tags=["chat"])


# ─── Rate Limiter Sederhana (per IP) ─────────────────────────────────────────
RATE_LIMIT = 30
TIME_WINDOW = 60
_rate_store: dict = {}
_rate_lock = threading.Lock()


def _check_rate_limit(client_ip: str) -> bool:
    """Return True jika request diizinkan."""
    now = time.time()
    with _rate_lock:
        if client_ip not in _rate_store:
            _rate_store[client_ip] = deque()
        dq = _rate_store[client_ip]
        while dq and dq[0] < now - TIME_WINDOW:
            dq.popleft()
        if len(dq) >= RATE_LIMIT:
            return False
        dq.append(now)
        return True


# ─── Models ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "rag"
    chat_history: list = []
    # Opsi: aktifkan narasi LLM (default True)
    include_narrative: Optional[bool] = True


class ChatResponse(BaseModel):
    success: bool
    message: str
    query: str
    mode: str
    documents: list = []
    # Narasi sintesis dari LLM (Opsi A — Full RAG)
    narrative: Optional[str] = None
    # Statistik
    latency_ms: Optional[float] = None
    from_cache: Optional[bool] = False
    narrative_from_cache: Optional[bool] = False


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """
    Endpoint pencarian RAG dengan narasi LLM (Full RAG: Retrieval + Generation).

    Flow:
    1. Validasi input
    2. Rate limit check
    3. Retrieval dari ChromaDB (dengan cache)
    4. Jika include_narrative=True → sintesis narasi via LLM (dengan cache)
    5. Return response berisi documents + narrative
    """

    # ── Validasi input ──
    if not request.message or len(request.message.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Pesan terlalu pendek. Minimal 3 karakter."
        )

    # ── Rate limit check ──
    client_ip = req.client.host if req.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Terlalu banyak request. Silakan coba lagi dalam beberapa saat."
        )

    t_start = time.perf_counter()

    try:
        rag = get_rag_service()

        # ── Retrieval (blocking → jalankan di thread pool) ──
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            rag.standard_rag,
            request.message,
        )

        # ── Rejected by domain filter ──
        if result.get("rejected"):
            return ChatResponse(
                success=False,
                message="Kueri ditolak: Topik tidak relevan dengan keilmuan Teknik Informatika.",
                query=request.message,
                mode="rag",
                documents=[],
                latency_ms=0,
                from_cache=False,
            )

        # ── No documents ──
        if result["docs_count"] == 0:
            return ChatResponse(
                success=False,
                message="❌ Maaf, tidak ditemukan skripsi yang relevan dengan query Anda. Coba gunakan kata kunci yang berbeda.",
                query=request.message,
                mode="rag",
                documents=[],
                latency_ms=result.get("latency_ms", 0),
                from_cache=result.get("from_cache", False),
            )

        documents = result["documents"]
        narrative = None
        narrative_from_cache = False

        # ── Generation (Opsi A: Full RAG) ──
        if request.include_narrative and documents:
            gen_service = get_generation_service()

            # Jalankan di thread pool agar event loop tidak tersumbat
            gen_result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: {
                    "narrative": gen_service.generate_narrative(request.message, documents),
                },
            )
            narrative = gen_result["narrative"]
            # Deteksi apakah narrative dari cache (bandingkan dengan cache stats)
            narrative_from_cache = (
                gen_service.cache.get(request.message, documents) == narrative
            )

        total_latency = round((time.perf_counter() - t_start) * 1000, 2)

        return ChatResponse(
            success=True,
            message="Pencarian berhasil",
            query=request.message,
            mode="rag",
            documents=documents,
            narrative=narrative,
            latency_ms=total_latency,
            from_cache=result.get("from_cache", False),
            narrative_from_cache=narrative_from_cache,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saat memproses query: {str(e)}"
        )


# ─── Health Check & Status ─────────────────────────────────────────────────────

@router.get("/health", tags=["status"])
async def health():
    """Health check ringan — tidak menyentuh ChromaDB / LLM."""
    rag = get_rag_service()
    gen = get_generation_service()
    return {
        "status": "ok",
        "retrieval_cache": rag.cache.stats(),
        "narrative_cache": gen.cache.stats(),
    }


@router.get("/status", tags=["status"])
async def status():
    """Status system."""
    return {
        "status": "running",
        "service": "Sistem Pencarian Skripsi (Full RAG: Retrieval + Generation)",
    }
