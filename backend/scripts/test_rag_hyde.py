import sys
import json
import time
from pathlib import Path

# Fix encoding issue for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Tambahkan direktori backend ke path agar bisa import app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.rag_service import get_rag_service

def extract_year_from_filename(filename: str) -> str:
    parts = filename.split('_')
    if parts and parts[0].isdigit() and len(parts[0]) == 4:
        return parts[0]
    return ""

def compute_ir_metrics(results: list[dict], ground_truth_file: str | None) -> list[dict]:
    """Menghitung metrik evaluasi Hit_GT, Rank_GT, dan RR."""
    if not ground_truth_file:
        for r in results:
            r.update({"Hit_GT": None, "Rank_GT": None, "RR": None})
        return results

    gt_basename = Path(ground_truth_file).name

    rank_gt = None
    for r in results:
        if r.get("File_Source_Basename", "") == gt_basename:
            rank_gt = r["Rank"]
            break

    rr = (1.0 / rank_gt) if rank_gt is not None else 0.0
    hit = rank_gt is not None

    for r in results:
        r["Hit_GT"] = hit
        r["Rank_GT"] = rank_gt
        r["RR"] = round(rr, 4)

    return results

def main():
    service = get_rag_service()
    
    # Path ke file queries_new.json
    queries_path = Path(__file__).parent.parent / "evaluation" / "queries_new.json"
    
    if not queries_path.exists():
        print(f"[ERROR] File query tidak ditemukan: {queries_path}")
        return

    with open(queries_path, "r", encoding="utf-8") as f:
        all_queries = json.load(f)
        
    # Daftar ID query yang akan diuji (Standard RAG & HyDE)
    target_ids = ["Q07"]
    
    # Filter query bersumber dari queries_new.json (case-insensitive)
    queries = [q for q in all_queries if q.get("ID", "").upper() in [tid.upper() for tid in target_ids]]
    
    if not queries:
        print(f"Tidak ada query yang cocok dengan ID {target_ids} di {queries_path.name}")
        return
        
    all_results = []
    
    for i, query in enumerate(queries):
        print(f"\n[{i+1}/{len(queries)}] Testing {query['ID']} | {query.get('Tipe', '')} | \"{query['Query_Text']}\" (Standard RAG vs HyDE)...")
        
        # --------------------------------------------------------------------------
        # 1. Standard RAG
        # --------------------------------------------------------------------------
        print("  → Menjalankan Standard RAG...", end=" ", flush=True)
        try:
            t0 = time.perf_counter()
            response = service.standard_rag(query["Query_Text"], k=5, is_eval=True)
            latency_ms = (time.perf_counter() - t0) * 1000
            
            rag_results = []
            for idx, doc in enumerate(response.get("documents", []), start=1):
                meta = doc.get("metadata", {})
                file_source = meta.get("source", "unknown.pdf")
                basename = Path(file_source).name if file_source else ""
                tahun = meta.get("tahun") or extract_year_from_filename(file_source)
                
                rag_results.append({
                    "ID": query["ID"],
                    "Tipe": query["Tipe"],
                    "Query_Text": query["Query_Text"],
                    "Ground_Truth_File": query["Ground_Truth_File"],
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
                })
            
            # Hitung metrics IR (Hit, Rank, RR)
            rag_results = compute_ir_metrics(rag_results, query["Ground_Truth_File"])
            all_results.extend(rag_results)
            print("Selesai.")
                
        except Exception as e:
            print(f"Error: {e}")

        # --------------------------------------------------------------------------
        # 2. HyDE (Menggunakan prompt 3 seperti di run_evaluation)
        # --------------------------------------------------------------------------
        print("  → Menjalankan HyDE...", end=" ", flush=True)
        try:
            t0 = time.perf_counter()
            hyde_response = service.hyde_rag(query["Query_Text"], k=5, is_eval=True, prompt_type="prompt3")
            latency_ms = (time.perf_counter() - t0) * 1000
            
            hypothetical_doc = hyde_response.get("hypothetical_document", "")
            
            hyde_results = []
            for idx, doc in enumerate(hyde_response.get("documents", []), start=1):
                meta = doc.get("metadata", {})
                file_source = meta.get("source", "unknown.pdf")
                basename = Path(file_source).name if file_source else ""
                tahun = meta.get("tahun") or extract_year_from_filename(file_source)
                
                hyde_results.append({
                    "ID": query["ID"],
                    "Tipe": query["Tipe"],
                    "Query_Text": query["Query_Text"],
                    "Ground_Truth_File": query["Ground_Truth_File"],
                    "Metode": "HyDE",
                    "Rank": idx,
                    "Skor_Similarity": round(meta.get("similarity_score", 0), 4),
                    "File_Source": file_source,
                    "File_Source_Basename": basename,
                    "Tahun": tahun,
                    "Judul_Skripsi": meta.get("judul", ""),
                    "Abstrak": doc.get("page_content", ""),
                    "Dokumen_Hipotetikal_LLM": hypothetical_doc,
                    "Latency_ms": round(latency_ms, 1),
                })
                
            # Hitung metrics IR
            hyde_results = compute_ir_metrics(hyde_results, query["Ground_Truth_File"])
            all_results.extend(hyde_results)
            print("Selesai.")

        except Exception as e:
            print(f"Error: {e}")

        if i < len(queries) - 1:
            print("Menunggu 5 detik sebelum lanjut agar tidak rate-limit...")
            time.sleep(5)

    # --------------------------------------------------------------------------
    # Menyimpan dan Menampilkan Output
    # --------------------------------------------------------------------------
    output_path = Path(__file__).parent.parent / "evaluation" / "results" / "eval_rag_hyde_selected_queries.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 60)
    print("HASIL PENGUJIAN QUERY TERPILIH (STANDARD RAG & HYDE)")
    print("=" * 60)
    print(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\n[DONE] Hasil json evaluasi lengkap telah disimpan di:\n{output_path}")

if __name__ == "__main__":
    main()
