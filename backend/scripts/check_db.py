import os
import sys
from pathlib import Path

# Tambahkan parent directory ke path agar bisa import dari app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.embedding_service import embedding_service
from langchain_community.vectorstores import Chroma

def check_db():
    print("🔄 Loading embedding model...")
    embedding = embedding_service.get_embedding_function()
    
    chroma_dir = str(settings.CHROMA_PERSIST_DIR)
    print(f"📊 Connecting to Chroma vectorstore at {chroma_dir}...\n")
    
    vectorstore = Chroma(
        embedding_function=embedding,
        persist_directory=chroma_dir,
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    # Akses langsung ke koleksi ChromaDB bawaan
    collection = vectorstore._collection
    count = collection.count()
    
    print(f"✅ Total vektor/dokumen di database: {count}")
    
    if count == 0:
        print("Database masih kosong.")
        return
        
    print("\n🔍 Menampilkan 3 dokumen pertama yang berhasil di-embed:")
    # Gunakan fungsi peek() untuk mengambil sejumlah dokumen tanpa harus melakukan search
    results = collection.peek(limit=3)
    
    for i in range(len(results['ids'])):
        print(f"\n{'='*50}")
        print(f"📄 Dokumen {i+1}")
        print(f"ID Hash  : {results['ids'][i]}")
        
        metadata = results['metadatas'][i]
        print(f"File     : {metadata.get('source', 'Unknown')}")
        print(f"Judul    : {metadata.get('judul', 'Unknown')}")
        
        content = results['documents'][i]
        # Memotong isi konten maksimal 300 karakter agar terminal tidak penuh
        print(f"\nIsi Abstrak (Preview):\n{content[:300]}...")
        print(f"{'='*50}")

if __name__ == "__main__":
    check_db()
