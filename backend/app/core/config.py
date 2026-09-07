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
    
    # API Configuration
    API_TITLE = "Sistem Pencarian Judul & Abstrak Skripsi"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "FastAPI backend untuk chatbot pencarian judul dan abstrak skripsi menggunakan RAG"
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data" / "pdf"
    CHROMA_DB_DIR = BASE_DIR / "chroma_db"
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR = str(CHROMA_DB_DIR)
    
    # Embedding Model
    EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
    EMBEDDING_DEVICE = "cpu"  # Change to "cuda" jika menggunakan GPU
    
    # RAG Configuration
    K_RETRIEVAL = 5  # Jumlah dokumen yang diambil
    FETCH_K = 20    # Jumlah dokumen untuk filtering awal
    
    # LLM Configuration (Groq)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = "openai/gpt-oss-120b"  # Model yang digunakan
    LLM_TEMPERATURE_STANDARD = 0.0
    LLM_TEMPERATURE_HYDE = 0.2
    LLM_TOP_P = 1.0
    LLM_MAX_TOKENS = 500
    LLM_FREQUENCY_PENALTY = 0.0
    LLM_PRESENCE_PENALTY = 0.0
    
    # Chatbot Mode Configuration (Mode ke-4: Asisten Interaktif dengan Gemini API)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")  # Model default dengan context window 1M tokens
    LLM_TEMPERATURE_CHATBOT = 0.4   # Keseimbangan objektivitas & kreativitas
    CHATBOT_MAX_TOKENS = 4096       # Ruang cukup untuk narasi research gap setelah tool calling
    CHATBOT_HISTORY_LIMIT = 8       # Sliding window riwayat percakapan
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True


# Instantiate settings
settings = Settings()
