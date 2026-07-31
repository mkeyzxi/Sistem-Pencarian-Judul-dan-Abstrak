import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import time
from pathlib import Path

# Setup path agar dapat mengimpor dari app/
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag_service import get_rag_service
from dotenv import load_dotenv

def main():
    # Pastikan environment variable termuat (api key groq, dll)
    load_dotenv()
    
    print("🔄 Menginisialisasi RAG Service...")
    rag = get_rag_service()
    
    # 5 Tema, masing-masing 1 query
    test_cases = [
        {"tema": "Kueri Konseptual/Sinonim (Semantic Gap)", "query": "petani rugi wabah daun"},

    ]
    
    TOP_K = 5  # Jumlah dokumen retrieved yang ingin ditampilkan dan dibandingkan
    results = []
    
    print("\n🚀 Memulai Perbandingan Prompt HyDE (Prompt 1 vs Prompt 2)...")
    
    for case in test_cases:
        tema = case["tema"]
        query = case["query"]
        print(f"\n{'='*60}")
        print(f"Tema  : {tema}")
        print(f"Query : '{query}'")
        print(f"{'='*60}")
        
        # Eksekusi Prompt 1
        print("⏳ Menjalankan Prompt 1 (Strict Abstract Components - Masalah, Metode, Hasil)...")
        start = time.time()
        # Menggunakan is_eval=True agar memotong batas minimum skor dan mmr, murni untuk membandingkan hipotesis
        res_prompt_1 = rag.hyde_rag(query=query, k=TOP_K, is_eval=True, prompt_type="prompt1")
        time_1 = time.time() - start
        
        # Eksekusi Prompt 2
        print("⏳ Menjalankan Prompt 2 (Research Intent / Zero Hallucination)...")
        start = time.time()
        res_prompt_2 = rag.hyde_rag(query=query, k=TOP_K, is_eval=True, prompt_type="prompt2")
        time_2 = time.time() - start
        
        hyp_1 = res_prompt_1.get("hypothetical_document", "")
        hyp_2 = res_prompt_2.get("hypothetical_document", "")
        docs_1 = res_prompt_1.get("documents", [])
        docs_2 = res_prompt_2.get("documents", [])
        
        print("\n🔹 Hasil Prompt 1:")
        print(f"📄 Hipotesis: {hyp_1}")
        print(f"⏱️ Waktu    : {time_1:.2f}s")
        print(f"📚 Top-{TOP_K} Dokumen Retrieved (Prompt 1):")
        for idx, d in enumerate(docs_1, 1):
            meta = d.get("metadata", {})
            print(f"   [{idx}] Skor: {meta.get('similarity_score', 0)}% | File: {meta.get('source', '')}")
            print(f"       Judul: {meta.get('judul', 'Tanpa Judul')}")
        
        print("\n🔹 Hasil Prompt 2:")
        print(f"📄 Hipotesis: {hyp_2}")
        print(f"⏱️ Waktu    : {time_2:.2f}s")
        print(f"📚 Top-{TOP_K} Dokumen Retrieved (Prompt 2):")
        for idx, d in enumerate(docs_2, 1):
            meta = d.get("metadata", {})
            print(f"   [{idx}] Skor: {meta.get('similarity_score', 0)}% | File: {meta.get('source', '')}")
            print(f"       Judul: {meta.get('judul', 'Tanpa Judul')}")
        
        # Simpan dalam dict
        results.append({
            "tema": tema,
            "query": query,
            "prompt_1": {
                "hypothetical_document": hyp_1,
                "latency_sec": round(time_1, 2),
                "documents": docs_1
            },
            "prompt_2": {
                "hypothetical_document": hyp_2,
                "latency_sec": round(time_2, 2),
                "documents": docs_2
            }
        })
        
    print(f"\n{'='*60}")
    print("✅ Perbandingan Selesai!")
    
    # Simpan hasil output ke dalam folder evaluation
    output_dir = Path(__file__).parent.parent / "evaluation" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "hyde_prompt_comparison.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print(f"📂 Hasil perbandingan (JSON) telah disimpan di: {output_file.relative_to(Path(__file__).parent.parent.parent)}")

if __name__ == "__main__":
    main()
