"""
Build Index Script
Script untuk membuat index ChromaDB dari PDF yang ada di folder data.
Jalankan script ini sebelum menjalankan FastAPI server.

Usage:
    python scripts/build_index.py
"""

import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.document_service import DocumentService
from app.services.embedding_service import embedding_service
from langchain_community.vectorstores import Chroma


def build_index():
    """Build ChromaDB index dari dokumen PDF."""
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         🔨 Building ChromaDB Index                         ║
    ║    Sistem Pencarian Judul & Abstrak Skripsi               ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check if PDF folder exists
    pdf_folder = str(settings.DATA_DIR)
    if not os.path.exists(pdf_folder):
        print(f"❌ Folder PDF tidak ditemukan: {pdf_folder}")
        print(f"📁 Silahkan buat folder dan letakkan PDF di: {pdf_folder}")
        return False
    
    # Load documents
    print("\n📂 Loading dokumen dari folder PDF...")
    documents = DocumentService.load_documents_from_folder(pdf_folder)
    
    if not documents:
        print("\n❌ Tidak ada dokumen yang berhasil di-load")
        print("💡 Pastikan:")
        print("   1. Folder data/pdf/ berisi file PDF")
        print("   2. PDF minimal 2 halaman (cover + isi)")
        print("   3. PDF memiliki abstrak minimal 100 karakter")
        return False
    
    # Get embedding service
    print("\n🔄 Initializing embedding model...")
    try:
        embedding = embedding_service.get_embedding_function()
        print("✅ Embedding model siap")
    except Exception as e:
        print(f"❌ Error loading embedding model: {e}")
        return False
    
    # Clear existing ChromaDB
    chroma_dir = str(settings.CHROMA_PERSIST_DIR)
    print(f"\n🗑️  Clearing existing ChromaDB: {chroma_dir}")
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)
        print("   ✅ ChromaDB cleared")
    
    # Create new vectorstore
    print(f"\n📊 Creating new Chroma vectorstore...")
    try:
        vectorstore = Chroma(
            embedding_function=embedding,
            persist_directory=chroma_dir
        )
        print("✅ Vectorstore created")
    except Exception as e:
        print(f"❌ Error creating vectorstore: {e}")
        return False
    
    # Add documents to vectorstore
    print(f"\n⏳ Embedding {len(documents)} dokumen...")
    batch_size = 5
    
    try:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            vectorstore.add_documents(batch)
            
            progress = min(i + batch_size, len(documents))
            print(f"   [{progress}/{len(documents)}] Embedded {len(batch)} dokumen")
        
        # Persist
        vectorstore.persist()
        print("\n✅ Vectorstore persisted")
        
    except Exception as e:
        print(f"❌ Error embedding dokumen: {e}")
        return False
    
    # Verify
    try:
        vector_count = vectorstore._collection.count()
        print(f"\n✨ Index building complete!")
        print(f"   Total vektor tersimpan: {vector_count}")
        
        if vector_count == 0:
            print("   ⚠️  Warning: No vectors were stored!")
            return False
        
        print(f"\n📍 ChromaDB location: {chroma_dir}")
        print("\n✅ Ready to start FastAPI server!")
        print("   Run: uvicorn app.main:app --reload")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying index: {e}")
        return False


if __name__ == "__main__":
    try:
        success = build_index()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
