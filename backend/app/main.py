"""
FastAPI Main Application
Entry point untuk server backend.

Optimasi:
- Uvicorn dengan multi-worker
- Async I/O → menangani banyak concurrent request tanpa blocking
- CORS permissive untuk development, perketat di production
"""

import os
import sys
import threading
from contextlib import asynccontextmanager

# ── Encoding safety (Windows: output di-pipe/redirect pakai cp1252) ──
# Tanpa ini, print emoji (⚡/✅/❌) bisa memicu UnicodeEncodeError dan
# merusak request saat log diarahkan ke file/cron. errors="replace" aman.
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat
from app.services.rag_service import get_rag_service
from app.services.generation_service import get_generation_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hook.

    Production (DEBUG=false): pre-warm model RAG + LLM di background thread
    agar /healthz tetap instan — Render menganggap deploy sukses meski model
    masih loading. Development: lazy-load seperti biasa.
    """
    if not settings.DEBUG:
        def _warmup():
            try:
                get_rag_service()
                get_generation_service()
                print("🔥 Warmup selesai: model RAG & LLM siap")
            except Exception as exc:
                print(f"⚠️ Warmup gagal (service tetap hidup): {exc}")

        threading.Thread(target=_warmup, daemon=True).start()
    yield


# ── Create FastAPI app ──
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PRODUCTION: ubah ke domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

# ── Routers ──
app.include_router(chat.router)


# ── Endpoints utama ──

@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Selamat datang di Sistem Pencarian Skripsi",
        "docs": "/docs",
        "status": "/api/status",
        "health": "/api/health",
    }


@app.get("/healthz", tags=["root"])
async def healthz():
    """Health check super ringan untuk Render (Health Check Path).
    Tidak memicu inisialisasi ChromaDB / model embedding / LLM."""
    return {"status": "ok"}


# ── Entry point untuk development ──
if __name__ == "__main__":
    import uvicorn

    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║      🚀 Sistem Pencarian Judul & Abstrak Skripsi         ║
    ║      Full RAG: Retrieval + Generation (LLM)             ║
    ║                 FastAPI Version {settings.API_VERSION}                      ║
    ╚════════════════════════════════════════════════════════════╝

    📍 Server: http://{settings.HOST}:{settings.PORT}
    📚 Docs:   http://{settings.HOST}:{settings.PORT}/docs
    🩺 Health: http://{settings.HOST}:{settings.PORT}/api/health
    """)

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
