import sys
import json
import time
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

# Tambahkan direktori backend ke path agar bisa import app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.rag_service import get_rag_service

def extract_year_from_filename(filename: str) -> str:
    parts = filename.split('_')
    if parts and parts[0].isdigit() and len(parts[0]) == 4:
        return parts[0]
    return ""

def main():
    service = get_rag_service()
    
    query_text = "siram bawang otomatis pakai sensor"
    
    try:
        t0 = time.perf_counter()
        response = service.standard_rag(query_text, k=5, is_eval=True)
        latency_ms = (time.perf_counter() - t0) * 1000
        
        results = []
        for idx, doc in enumerate(response.get("documents", []), start=1):
            meta = doc.get("metadata", {})
            file_source = meta.get("source", "unknown.pdf")
            basename = Path(file_source).name if file_source else ""
            tahun = meta.get("tahun") or extract_year_from_filename(file_source)
            
            results.append({
                "ID": "Q20",
                "Tipe": "Semantic Gap",
                "Query_Text": query_text,
                "Ground_Truth_File": None,
                "Metode": "Standard RAG",
                "Rank": idx,
                "Skor_Similarity": round(meta.get("similarity_score", 0), 4),
                "File_Source": file_source,
                "File_Source_Basename": basename,
                "Tahun": tahun,
                "Judul_Skripsi": meta.get("judul", ""),
                "Abstrak": doc.get("page_content", ""),
                "Dokumen_Hipotetikal_LLM": None,
                "Latency_ms": round(latency_ms, 1),
                "Hit_GT": None,
                "Rank_GT": None,
                "RR": None
            })
            
        print(json.dumps(results, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error saat menjalankan Standard RAG: {e}")

if __name__ == "__main__":
    main()
