"""
FastAPI Main Application
Entry point untuk server backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware untuk allow frontend menghubungi backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PRODUCTION: ubah ke domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Selamat datang di Chatbot Pencarian Skripsi",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/health",
        "info": "/api/info"
    }


@app.get("/api/status", tags=["status"])
async def status():
    """System status."""
    return {
        "status": "running",
        "api_version": settings.API_VERSION,
        "app_name": settings.API_TITLE
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║      🚀 Chatbot Pencarian Judul & Abstrak Skripsi        ║
    ║                 FastAPI Version {settings.API_VERSION}                      ║
    ╚════════════════════════════════════════════════════════════╝
    
    📍 Server: http://{settings.HOST}:{settings.PORT}
    📚 Docs:   http://{settings.HOST}:{settings.PORT}/docs
    🔍 ReDoc:  http://{settings.HOST}:{settings.PORT}/redoc
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
