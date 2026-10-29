"""
FastAPI Main Application
Entry point untuk server backend.

Optimasi:
- Uvicorn dengan multi-worker
- Async I/O → menangani banyak concurrent request tanpa blocking
- CORS permissive untuk development, perketat di production
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat

# ── Create FastAPI app ──
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
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
