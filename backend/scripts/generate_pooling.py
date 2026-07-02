"""
generate_pooling.py — Generate Candidate Pool (Top-10 RAG + Top-10 HyDE)
untuk Pelabelan Manual (Ground Truth)

Jalankan dari folder backend/:
    python scripts/generate_pooling.py
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.rag_service import get_rag_service, RAGService
from app.core.config import settings

# ─── Konfigurasi ──────────────────────────────────────────────────────────────
TOP_K_POOL = 10
QUERIES_FILE = Path(__file__).parent.parent / "evaluation" / "queries.json"
OUTPUT_FILE = Path(__file__).parent.parent / "evaluation" / "pooling_candidates.json"
DELAY_BETWEEN_QUERIES = 1.5  # detik; hindari rate-limit Groq API

def normalize_source(source: str) -> str:
    return Path(source).name if source else ""

def main():
    if not QUERIES_FILE.exists():
        print(f"[ERROR] File query tidak ditemukan: {QUERIES_FILE}")
        sys.exit(1)

    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        queries = json.load(f)
    print(f"[INFO] Loaded {len(queries)} queries dari {QUERIES_FILE}")

    service = get_rag_service()
    print("[INFO] RAGService initialized.")

    pooling_data = []
    total = len(queries)

    for i, query in enumerate(queries, start=1):
        qid = query["ID"]
        tipe = query["Tipe"]
        query_text = query["Query_Text"]
        print(f"\n[{i}/{total}] Memproses QID: {qid} | \"{query_text}\"")

        candidates_map = {}

        # 1. Run Standard RAG (Top-10)
        print("  → Retrieval Standard RAG ...", end=" ", flush=True)
        try:
            rag_resp = service.standard_rag(query_text, k=TOP_K_POOL, is_eval=True)
            for doc in rag_resp.get("documents", []):
                meta = doc.get("metadata", {})
                file_source = meta.get("source", "unknown.pdf")
                basename = normalize_source(file_source)
                score = meta.get("similarity_score", 0)
                
                candidates_map[basename] = {
                    "File_Source": file_source,
                    "Judul_Skripsi": meta.get("judul", ""),
                    "Abstrak": doc.get("page_content", ""),
                    "Retrieved_By": ["Standard RAG"],
                    "Max_Similarity_Score": score,
                    "Label_Manual": None
                }
            print(f"OK ({len(rag_resp.get('documents', []))} docs)")
        except Exception as e:
            print(f"ERROR: {e}")

        # 2. Run HyDE (Prompt 1) (Top-10)
        print("  → Retrieval HyDE (Prompt 1) ...", end=" ", flush=True)
        try:
            hyde1_resp = service.hyde_rag(query_text, k=TOP_K_POOL, is_eval=True, prompt_type="prompt1")
            for doc in hyde1_resp.get("documents", []):
                meta = doc.get("metadata", {})
                file_source = meta.get("source", "unknown.pdf")
                basename = normalize_source(file_source)
                score = meta.get("similarity_score", 0)

                if basename in candidates_map:
                    candidates_map[basename]["Retrieved_By"].append("HyDE (Prompt 1)")
                    candidates_map[basename]["Max_Similarity_Score"] = max(candidates_map[basename]["Max_Similarity_Score"], score)
                else:
                    candidates_map[basename] = {
                        "File_Source": file_source,
                        "Judul_Skripsi": meta.get("judul", ""),
                        "Abstrak": doc.get("page_content", ""),
                        "Retrieved_By": ["HyDE (Prompt 1)"],
                        "Max_Similarity_Score": score,
                        "Label_Manual": None
                    }
            print(f"OK ({len(hyde1_resp.get('documents', []))} docs)")
        except Exception as e:
            print(f"ERROR: {e}")

        # 3. Run HyDE (Prompt 2) (Top-10)
        print("  → Retrieval HyDE (Prompt 2) ...", end=" ", flush=True)
        try:
            hyde2_resp = service.hyde_rag(query_text, k=TOP_K_POOL, is_eval=True, prompt_type="prompt2")
            for doc in hyde2_resp.get("documents", []):
                meta = doc.get("metadata", {})
                file_source = meta.get("source", "unknown.pdf")
                basename = normalize_source(file_source)
                score = meta.get("similarity_score", 0)

                if basename in candidates_map:
                    candidates_map[basename]["Retrieved_By"].append("HyDE (Prompt 2)")
                    candidates_map[basename]["Max_Similarity_Score"] = max(candidates_map[basename]["Max_Similarity_Score"], score)
                else:
                    candidates_map[basename] = {
                        "File_Source": file_source,
                        "Judul_Skripsi": meta.get("judul", ""),
                        "Abstrak": doc.get("page_content", ""),
                        "Retrieved_By": ["HyDE (Prompt 2)"],
                        "Max_Similarity_Score": score,
                        "Label_Manual": None
                    }
            print(f"OK ({len(hyde2_resp.get('documents', []))} docs)")
        except Exception as e:
            print(f"ERROR: {e}")

        pooling_data.append({
            "Query_ID": qid,
            "Tipe": tipe,
            "Query_Text": query_text,
            "Candidates_Count": len(candidates_map),
            "Candidates": list(candidates_map.values())
        })

        if i < total:
            time.sleep(DELAY_BETWEEN_QUERIES)

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pooling_data, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] Berhasil men-generate {len(pooling_data)} query pool.")
    print(f"Output kandidat disimpan ke: {OUTPUT_FILE}")
    print("Silakan buka file tersebut untuk melakukan pelabelan biner manual (Label_Manual: 1 untuk relevan, 0 untuk tidak relevan).")

if __name__ == "__main__":
    main()
