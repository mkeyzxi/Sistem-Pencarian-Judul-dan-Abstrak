"""
Build Index Script
Script untuk membuat index ChromaDB dari PDF dengan mekanisme Hashing dan Checkpointing.
Jalankan script ini sebelum menjalankan FastAPI server.

Usage:
    python scripts/build_index.py
"""

import os
import sys
import json
import hashlib
import shutil
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.document_service import DocumentService
from app.services.embedding_service import embedding_service
from langchain_community.vectorstores import Chroma

# Paths
DATA_DIR = Path(settings.BASE_DIR) / "data"
HASH_REGISTRY_FILE = DATA_DIR / "processed_hashes.json"

def get_file_hash(filepath: str) -> str:
    """Menghitung SHA-256 dari sebuah file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_processed_hashes() -> set:
    """Load registry hash yang sudah diproses."""
    if os.path.exists(HASH_REGISTRY_FILE):
        try:
            with open(HASH_REGISTRY_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_processed_hash(new_hash: str):
    """Menambahkan hash baru secara inkremental ke registry."""
    hashes = load_processed_hashes()
    hashes.add(new_hash)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HASH_REGISTRY_FILE, "w") as f:
        json.dump(list(hashes), f, indent=4)

def build_index():
    """Build ChromaDB index dari dokumen PDF dengan Anti-Duplikasi dan Checkpointing."""
    parser = argparse.ArgumentParser(description="Build ChromaDB index dari PDF skripsi.")
    parser.add_argument("--reset", action="store_true", help="Hapus ChromaDB dan registry hash sebelum mulai (Clean Build).")
    args = parser.parse_args()
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║      🔨 Building ChromaDB Index (Pragmatic Checkpoint)     ║
    ║    Sistem Pencarian Judul & Abstrak Skripsi               ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    if args.reset:
        print("\n⚠️  PERINGATAN: Mode --reset diaktifkan. Melakukan Hard Reset...")
        chroma_dir = str(settings.CHROMA_PERSIST_DIR)
        if os.path.exists(chroma_dir):
            try:
                shutil.rmtree(chroma_dir)
                print("   🗑️ Folder ChromaDB berhasil dihapus.")
            except Exception as e:
                print(f"   ❌ Gagal menghapus folder ChromaDB: {e}")
        
        if os.path.exists(HASH_REGISTRY_FILE):
            try:
                os.remove(HASH_REGISTRY_FILE)
                print("   🗑️ Registry Hash berhasil dihapus.")
            except Exception as e:
                print(f"   ❌ Gagal menghapus registry hash: {e}")
        
        print("✅ Hard Reset selesai. Memulai build index baru...\n")
    
    pdf_folder = str(settings.DATA_DIR)
    
    if not os.path.exists(pdf_folder):
        print(f"❌ Folder PDF tidak ditemukan: {pdf_folder}")
        return False

    pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print("❌ Tidak ada file PDF di folder data/pdf/")
        return False

    processed_hashes = load_processed_hashes()
    files_to_process = []
    file_hashes = {}

    print("\n🔍 Memeriksa duplikasi file (Hashing)...")
    for filepath in pdf_files:
        file_hash = get_file_hash(filepath)
        file_hashes[filepath] = file_hash
        if file_hash not in processed_hashes:
            files_to_process.append(filepath)

    print(f"   Total PDF ditemukan: {len(pdf_files)}")
    print(f"   PDF sudah ada di database: {len(pdf_files) - len(files_to_process)}")
    print(f"   PDF baru untuk diproses: {len(files_to_process)}")

    if not files_to_process:
        print("\n✅ Tidak ada PDF baru. Vector database sudah up-to-date.")
        return True

    # Get embedding service
    print("\n🔄 Initializing embedding model...")
    try:
        embedding = embedding_service.get_embedding_function()
        print("✅ Embedding model siap")
    except Exception as e:
        print(f"❌ Error loading embedding model: {e}")
        return False
    
    chroma_dir = str(settings.CHROMA_PERSIST_DIR)
    
    # Create or load vectorstore
    print(f"\n📊 Connecting to Chroma vectorstore...")
    try:
        vectorstore = Chroma(
            embedding_function=embedding,
            persist_directory=chroma_dir
        )
        print("✅ Vectorstore connected")
    except Exception as e:
        print(f"❌ Error connecting vectorstore: {e}")
        return False
    
    print(f"\n⏳ Memulai proses ekstraksi dan embedding (Incremental)...")
    
    success_count = 0
    fail_count = 0
    
    for idx, filepath in enumerate(files_to_process, 1):
        filename = os.path.basename(filepath)
        file_hash = file_hashes[filepath]
        print(f"\n[{idx}/{len(files_to_process)}] Memproses file: {filename}")
        
        # Ekstrak 1 dokumen
        try:
            docs = DocumentService.load_documents_from_files([filepath])
        except Exception as e:
            print(f"   ❌ Gagal memproses dokumen akibat error internal: {e}")
            docs = []
        
        if not docs:
            print(f"   ⏩ Dokumen ditolak oleh Quality Gate. Menyimpan hash agar tidak diulang.")
            fail_count += 1
            # Tetap simpan hash karena ini adalah murni kegagalan kualitas dokumen
            save_processed_hash(file_hash)
            continue
            
        # Jika lolos, embed dan persist
        try:
            vectorstore.add_documents(docs, ids=[file_hash])
            vectorstore.persist()
            save_processed_hash(file_hash)
            success_count += 1
            print(f"   💾 Checkpoint tersimpan. Dokumen berhasil di-embed.")
        except Exception as e:
            print(f"   ❌ Gagal memasukkan ke ChromaDB: {e}")
            fail_count += 1

    try:
        vector_count = vectorstore._collection.count()
        print(f"\n✨ Index building complete!")
        print(f"   Berhasil: {success_count} dokumen")
        print(f"   Ditolak / Gagal: {fail_count} dokumen")
        print(f"   Total vektor di DB: {vector_count}")
        print(f"\n📍 ChromaDB location: {chroma_dir}")
        print("\n✅ Ready to start FastAPI server!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying index: {e}")
        return False


if __name__ == "__main__":
    try:
        success = build_index()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user. Checkpoint aman.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
