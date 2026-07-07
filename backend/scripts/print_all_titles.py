import sys
import os
from pathlib import Path

# Fix encoding issue untuk Windows console agar tidak error saat print emoji/karakter khusus
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Tambahkan direktori backend ke path agar bisa import app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.rag_service import get_rag_service

def main():
    service = get_rag_service()
    
    # Mengambil semua data dari Chroma DB (hanya metadatanya saja agar lebih ringan)
    all_data = service.vectorstore.get(include=["metadatas"])
    metadatas = all_data.get("metadatas", [])
    
    count = 1
    seen_titles = set()
    
    # Karena satu skripsi dipecah menjadi beberapa chunk, kita hilangkan duplikat judulnya
    for meta in metadatas:
        judul = meta.get("judul")
        if judul and judul not in seen_titles:
            print(f"judul {count} : {judul}")
            seen_titles.add(judul)
            count += 1

if __name__ == "__main__":
    main()
