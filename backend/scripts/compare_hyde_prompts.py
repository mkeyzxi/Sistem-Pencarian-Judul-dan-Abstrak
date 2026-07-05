import sys
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
        {"tema": "Sistem Pendukung Keputusan", "query": "sistem pendukung keputusan metode"},
        {"tema": "Otomatisasi/IoT", "query": "cara otomatis pisahin telur bagus"},
        {"tema": "Computer Vision", "query": "klasifikasi kematangan buah cabai cnn"},
        {"tema": "Umum", "query": "frameowrk"},
        {"tema": "Sistem Pendukung Keputusan", "query": "sistem pendukung keputusan 2020"}
    ]
    
    results = []
    
    print("\n🚀 Memulai Perbandingan Prompt HyDE...")
    
    for case in test_cases:
        tema = case["tema"]
        query = case["query"]
        print(f"\n{'='*50}")
        print(f"Tema  : {tema}")
        print(f"Query : '{query}'")
        print(f"{'='*50}")
        
        # Eksekusi Prompt 1
        print("⏳ Menjalankan Prompt 1 (Strict Abstract Components)...")
        start = time.time()
        # Menggunakan is_eval=True agar memotong batas minimum skor dan mmr, murni untuk membandingkan hipotesis
        res_prompt_1 = rag.hyde_rag(query=query, k=1, is_eval=True, prompt_type="prompt1")
        time_1 = time.time() - start
        
        # Eksekusi Prompt 2
        print("⏳ Menjalankan Prompt 2 (Strict Constraints)...")
        start = time.time()
        res_prompt_2 = rag.hyde_rag(query=query, k=1, is_eval=True, prompt_type="prompt2")
        time_2 = time.time() - start
        
        # Eksekusi Prompt 3
        print("⏳ Menjalankan Prompt 3 (Structured Instructions)...")
        start = time.time()
        res_prompt_3 = rag.hyde_rag(query=query, k=1, is_eval=True, prompt_type="prompt3")
        time_3 = time.time() - start
        
        hyp_1 = res_prompt_1.get("hypothetical_document", "")
        hyp_2 = res_prompt_2.get("hypothetical_document", "")
        hyp_3 = res_prompt_3.get("hypothetical_document", "")
        
        print("\n🔹 Hasil Prompt 1:")
        print(f"{hyp_1}\n(Waktu: {time_1:.2f}s)")
        
        print("\n🔹 Hasil Prompt 2:")
        print(f"{hyp_2}\n(Waktu: {time_2:.2f}s)")
        
        print("\n🔹 Hasil Prompt 3:")
        print(f"{hyp_3}\n(Waktu: {time_3:.2f}s)")
        
        # Simpan dalam dict
        results.append({
            "tema": tema,
            "query": query,
            "prompt_1": {
                "hypothetical_document": hyp_1,
                "latency_sec": round(time_1, 2)
            },
            "prompt_2": {
                "hypothetical_document": hyp_2,
                "latency_sec": round(time_2, 2)
            },
            "prompt_3": {
                "hypothetical_document": hyp_3,
                "latency_sec": round(time_3, 2)
            }
        })
        
    print(f"\n{'='*50}")
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
