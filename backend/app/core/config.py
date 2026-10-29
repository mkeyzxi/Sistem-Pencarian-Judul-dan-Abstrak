"""
Configuration file for FastAPI backend.
Loads environment variables from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings and configuration."""

    # ── API Configuration ──
    API_TITLE = "Sistem Pencarian Judul & Abstrak Skripsi"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "FastAPI backend untuk pencarian judul & abstrak skripsi menggunakan RAG"

    # ── Paths ──
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data" / "pdf"
    CHROMA_DB_DIR = BASE_DIR / "chroma_db"

    # ── ChromaDB Configuration ──
    CHROMA_PERSIST_DIR = str(CHROMA_DB_DIR)

    # ── Embedding Model ──
    EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
    EMBEDDING_DEVICE = "cpu"  # Ganti ke "cuda" jika menggunakan GPU

    # ── RAG Configuration ──
    K_RETRIEVAL = 5       # Jumlah dokumen yang diambil
    FETCH_K = 20         # Jumlah dokumen untuk filtering awal

    # ── LLM Configuration (Groq) ──
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = "openai/gpt-oss-120b"
    LLM_TEMPERATURE_STANDARD = 0.0
    LLM_TEMPERATURE_GENERATION = 0.2  # Sedikit kreatif untuk narasi
    LLM_TOP_P = 1.0
    LLM_MAX_TOKENS = 500              # Untuk retrieval / filter
    LLM_MAX_TOKENS_GENERATION = 1024  # Untuk narasi sintesis (lebih panjang)
    LLM_FREQUENCY_PENALTY = 0.0
    LLM_PRESENCE_PENALTY = 0.0

    # ── RAG Generation ──
    # Jumlah dokumen maksimum yang dikirim ke LLM untuk sintesis narasi
    MAX_DOCS_FOR_LLM = 5
    # Panjang maksimal potongan abstrak per dokumen yang dikirim ke LLM
    EXCERPT_LENGTH = 500

    # ── Server Configuration ──
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # ── Worker Configuration (untuk uvicorn multi-worker) ──
    # Jumlah worker = 4 (saran: CPU_COUNT jika resource tersedia)
    WORKERS = int(os.getenv("WORKERS", "4"))


# Instantiate settings
settings = Settings()
