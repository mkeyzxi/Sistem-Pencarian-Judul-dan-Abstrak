# """
# run_evaluation.py — Evaluasi otomatis Standard RAG vs HyDE
# Jalankan dari folder backend/:
#     python scripts/run_evaluation.py
# """

# import json
# import os
# import sys
# import time
# from datetime import datetime
# from pathlib import Path

# # Tambahkan root backend ke sys.path agar import app.* bisa bekerja
# sys.path.append(str(Path(__file__).resolve().parent.parent))

# from app.services.rag_service import get_rag_service, RAGService

# # ─── Konfigurasi ──────────────────────────────────────────────────────────────

# TOP_K = 5                    # Jumlah dokumen yang di-retrieve per query
# QUERIES_FILE = Path(__file__).parent.parent / "evaluation" / "queries.json"
# OUTPUT_DIR = Path(__file__).parent.parent / "evaluation" / "results"
# DELAY_BETWEEN_QUERIES = 1.5  # detik; hindari rate-limit Groq API untuk HyDE

# # ─── Helper ───────────────────────────────────────────────────────────────────

# def extract_year_from_filename(filename: str) -> int | None:
#     """Ekstrak tahun dari nama file format: 2024_NAMA_PENULIS.pdf"""
#     try:
#         return int(filename.split("_")[0])
#     except (ValueError, IndexError):
#         return None

# def run_standard_rag(service: RAGService, query_text: str, top_k: int) -> list[dict]:
#     rag_response = service.standard_rag(query_text, k=top_k)
#     results = []
    
#     for rank_idx, doc in enumerate(rag_response.get("documents", []), start=1):
#         meta = doc.get("metadata", {})
#         file_source = meta.get("source", "unknown.pdf")
#         skor_similarity = meta.get("similarity_score", 0) / 100.0
        
#         results.append({
#             "Metode": "Standard RAG",
#             "Rank": rank_idx,
#             "Skor_Similarity": round(skor_similarity, 4),
#             "File_Source": file_source,
#             "Tahun": meta.get("tahun") or extract_year_from_filename(file_source),
#             "Judul_Skripsi": meta.get("judul", ""),
#             "Abstrak": doc.get("page_content", ""),
#             "Dokumen_Hipotetikal_LLM": None,
#         })
#     return results


# def run_hyde(service: RAGService, query_text: str, top_k: int) -> list[dict]:
#     hyde_response = service.hyde_rag(query_text, k=top_k)
#     results = []
    
#     hypothetical_doc = hyde_response.get("hypothetical_document", "")
    
#     for rank_idx, doc in enumerate(hyde_response.get("documents", []), start=1):
#         meta = doc.get("metadata", {})
#         file_source = meta.get("source", "unknown.pdf")
#         skor_similarity = meta.get("similarity_score", 0) / 100.0
        
#         results.append({
#             "Metode": "HyDE",
#             "Rank": rank_idx,
#             "Skor_Similarity": round(skor_similarity, 4),
#             "File_Source": file_source,
#             "Tahun": meta.get("tahun") or extract_year_from_filename(file_source),
#             "Judul_Skripsi": meta.get("judul", ""),
#             "Abstrak": doc.get("page_content", ""),
#             "Dokumen_Hipotetikal_LLM": hypothetical_doc,
#         })
#     return results


# def compute_ground_truth_fields(results: list[dict], ground_truth_file: str | None) -> list[dict]:
#     """
#     Tambahkan kolom Hit_Ground_Truth dan Rank_Ground_Truth ke setiap result
#     dalam satu grup (query × metode).
#     """
#     if ground_truth_file is None:
#         for r in results:
#             r["Hit_Ground_Truth"] = None
#             r["Rank_Ground_Truth"] = None
#         return results

#     # Cari di rank berapa ground truth muncul
#     gt_rank = None
#     for r in results:
#         if r["File_Source"] == ground_truth_file:
#             gt_rank = r["Rank"]
#             break

#     for r in results:
#         r["Hit_Ground_Truth"] = (r["File_Source"] == ground_truth_file)
#         r["Rank_Ground_Truth"] = gt_rank  # sama untuk semua baris dalam grup ini

#     return results


# # ─── Main ─────────────────────────────────────────────────────────────────────

# def main():
#     # 1. Load queries
#     if not QUERIES_FILE.exists():
#         print(f"[ERROR] File query tidak ditemukan: {QUERIES_FILE}")
#         sys.exit(1)

#     with open(QUERIES_FILE, "r", encoding="utf-8") as f:
#         queries = json.load(f)
#     print(f"[INFO] Loaded {len(queries)} queries dari {QUERIES_FILE}")

#     # 2. Init service
#     service = get_rag_service()
#     print("[INFO] RAGService initialized.")

#     # 3. Siapkan output dir
#     OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
#     timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
#     output_path = OUTPUT_DIR / f"eval_{timestamp_str}.json"

#     all_results = []
#     total = len(queries)

#     for i, query in enumerate(queries, start=1):
#         qid = query["ID"]
#         tipe = query["Tipe"]
#         query_text = query["Query_Text"]
#         ground_truth_file = query.get("Ground_Truth_File")

#         print(f"\n[{i}/{total}] {qid} | {tipe} | \"{query_text}\"")

#         # — Standard RAG —
#         print(f"  → Standard RAG ...", end=" ", flush=True)
#         try:
#             rag_results = run_standard_rag(service, query_text, TOP_K)
#             rag_results = compute_ground_truth_fields(rag_results, ground_truth_file)
#         except Exception as e:
#             print(f"ERROR: {e}")
#             rag_results = []

#         for r in rag_results:
#             all_results.append({
#                 "ID": qid,
#                 "Tipe": tipe,
#                 "Query_Text": query_text,
#                 "Ground_Truth_File": ground_truth_file,
#                 **r
#             })
#         print(f"OK ({len(rag_results)} results)")

#         # — HyDE —
#         print(f"  → HyDE ...", end=" ", flush=True)
#         try:
#             hyde_results = run_hyde(service, query_text, TOP_K)
#             hyde_results = compute_ground_truth_fields(hyde_results, ground_truth_file)
#         except Exception as e:
#             print(f"ERROR: {e}")
#             hyde_results = []

#         for r in hyde_results:
#             all_results.append({
#                 "ID": qid,
#                 "Tipe": tipe,
#                 "Query_Text": query_text,
#                 "Ground_Truth_File": ground_truth_file,
#                 **r
#             })
#         print(f"OK ({len(hyde_results)} results)")

#         # Rate-limit delay (Groq API)
#         if i < total:
#             time.sleep(DELAY_BETWEEN_QUERIES)

#     # 4. Susun output final
#     output = {
#         "metadata": {
#             "timestamp": datetime.now().isoformat(),
#             "top_k": TOP_K,
#             "embedding_model": "intfloat/multilingual-e5-small",
#             "llm_model": "llama3-8b-8192",
#             "chroma_collection": "skripsi_docs",
#             "total_queries": len(queries),
#             "methods": ["Standard RAG", "HyDE"]
#         },
#         "results": all_results
#     }

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(output, f, ensure_ascii=False, indent=2)

#     print(f"\n[DONE] {len(all_results)} records → {output_path}")


# if __name__ == "__main__":
#     main()



















# """
# run_evaluation.py — Evaluasi otomatis Standard RAG vs HyDE
# Jalankan dari folder backend/:
#     python scripts/run_evaluation.py

# Metrik yang dihitung per query:
#   - Hit@K      : apakah ground truth ada di top-K hasil
#   - Rank_GT    : di posisi berapa ground truth ditemukan (None = tidak ada)
#   - RR         : Reciprocal Rank = 1/Rank_GT (0 jika tidak ditemukan)
#   - P@K        : Precision@K (hanya bermakna jika ada multi-GT, di sini proxy)
#   - Latency_ms : waktu eksekusi retrieval dalam milidetik

# Metrik agregat (per metode × per tipe query):
#   - Hit_Rate@K : mean(Hit@K)
#   - MRR        : mean(RR)
#   - Avg_Score  : rata-rata similarity score dokumen yang dikembalikan
#   - Avg_Latency_ms
# """

# import json
# import os
# import sys
# import time
# from datetime import datetime
# from pathlib import Path

# sys.path.append(str(Path(__file__).resolve().parent.parent))

# from app.services.rag_service import get_rag_service, RAGService

# # ─── Konfigurasi ──────────────────────────────────────────────────────────────

# TOP_K = 5
# QUERIES_FILE = Path(__file__).parent.parent / "evaluation" / "queries.json"
# OUTPUT_DIR = Path(__file__).parent.parent / "evaluation" / "results"
# DELAY_BETWEEN_QUERIES = 1.5  # detik; hindari rate-limit Groq untuk HyDE

# # ─── Helper ───────────────────────────────────────────────────────────────────

# def normalize_source(source: str) -> str:
#     """
#     Normalisasi path source agar perbandingan GT tidak gagal karena
#     perbedaan path penuh vs basename.

#     Contoh:
#       "/data/skripsi/2024_BUDI.pdf"  →  "2024_BUDI.pdf"
#       "2024_BUDI.pdf"                →  "2024_BUDI.pdf"
#     """
#     return Path(source).name if source else ""


# def extract_year_from_filename(filename: str) -> int | None:
#     """Ekstrak tahun dari nama file format: 2024_NAMA_PENULIS.pdf"""
#     try:
#         return int(Path(filename).name.split("_")[0])
#     except (ValueError, IndexError):
#         return None


# def run_standard_rag(
#     service: RAGService, query_text: str, top_k: int
# ) -> tuple[list[dict], float]:
#     """
#     Jalankan Standard RAG dan kembalikan (results, latency_ms).
#     Score TIDAK dibagi 100 — dipertahankan dalam format 0–100
#     sesuai output rag_service.py.
#     """
#     t0 = time.perf_counter()
#     rag_response = service.standard_rag(query_text, k=top_k)
#     latency_ms = (time.perf_counter() - t0) * 1000

#     results = []
#     for rank_idx, doc in enumerate(rag_response.get("documents", []), start=1):
#         meta = doc.get("metadata", {})
#         file_source = meta.get("source", "unknown.pdf")
#         results.append({
#             "Metode": "Standard RAG",
#             "Rank": rank_idx,
#             "Skor_Similarity": round(meta.get("similarity_score", 0), 4),
#             "File_Source": file_source,
#             "File_Source_Basename": normalize_source(file_source),
#             "Tahun": meta.get("tahun") or extract_year_from_filename(file_source),
#             "Judul_Skripsi": meta.get("judul", ""),
#             "Abstrak": doc.get("page_content", ""),
#             "Dokumen_Hipotetikal_LLM": None,
#             "Latency_ms": round(latency_ms, 1),
#         })
#     return results, latency_ms


# def run_hyde(
#     service: RAGService, query_text: str, top_k: int
# ) -> tuple[list[dict], float]:
#     """
#     Jalankan HyDE RAG dan kembalikan (results, latency_ms).
#     Latency mencakup waktu generate hypothetical doc + retrieval.
#     """
#     t0 = time.perf_counter()
#     hyde_response = service.hyde_rag(query_text, k=top_k)
#     latency_ms = (time.perf_counter() - t0) * 1000

#     hypothetical_doc = hyde_response.get("hypothetical_document", "")
#     results = []
#     for rank_idx, doc in enumerate(hyde_response.get("documents", []), start=1):
#         meta = doc.get("metadata", {})
#         file_source = meta.get("source", "unknown.pdf")
#         results.append({
#             "Metode": "HyDE",
#             "Rank": rank_idx,
#             "Skor_Similarity": round(meta.get("similarity_score", 0), 4),
#             "File_Source": file_source,
#             "File_Source_Basename": normalize_source(file_source),
#             "Tahun": meta.get("tahun") or extract_year_from_filename(file_source),
#             "Judul_Skripsi": meta.get("judul", ""),
#             "Abstrak": doc.get("page_content", ""),
#             "Dokumen_Hipotetikal_LLM": hypothetical_doc,
#             "Latency_ms": round(latency_ms, 1),
#         })
#     return results, latency_ms


# def compute_ir_metrics(
#     results: list[dict],
#     ground_truth_file: str | None,
# ) -> list[dict]:
#     """
#     Hitung metrik IR per query × metode dan tambahkan ke setiap row:

#       Hit_GT        : bool — apakah GT ada di hasil sama sekali
#       Rank_GT       : int | None — posisi GT di ranking (1-based)
#       RR            : float — Reciprocal Rank (1/Rank_GT, atau 0.0)

#     Menggunakan basename untuk perbandingan agar robust terhadap perbedaan path.
#     """
#     if not ground_truth_file:
#         for r in results:
#             r.update({"Hit_GT": None, "Rank_GT": None, "RR": None})
#         return results

#     gt_basename = normalize_source(ground_truth_file)

#     # Cari rank GT
#     rank_gt = None
#     for r in results:
#         if normalize_source(r.get("File_Source_Basename", "")) == gt_basename:
#             rank_gt = r["Rank"]
#             break

#     rr = (1.0 / rank_gt) if rank_gt is not None else 0.0
#     hit = rank_gt is not None

#     for r in results:
#         r["Hit_GT"] = hit
#         r["Rank_GT"] = rank_gt
#         r["RR"] = round(rr, 4)

#     return results


# def compute_summary(all_results: list[dict]) -> dict:
#     """
#     Hitung metrik agregat dari seluruh results.

#     Struktur output:
#     {
#       "by_method": {
#         "Standard RAG": { "Hit_Rate@K": ..., "MRR": ..., "Avg_Score": ..., "Avg_Latency_ms": ... },
#         "HyDE":         { ... }
#       },
#       "by_method_and_type": {
#         "Standard RAG": {
#           "Leksikal": { ... },
#           "Semantik":  { ... },
#         },
#         ...
#       },
#       "winner": "HyDE" | "Standard RAG" | "Tie"
#     }
#     """
#     from collections import defaultdict

#     # Kumpulkan data per (method, tipe)
#     # Gunakan satu row per query × method (ambil Rank=1 sebagai proxy per-query)
#     # Tapi kita ingin metrik per query, bukan per row — ambil row mana saja
#     # karena Hit_GT, RR, Rank_GT sama untuk semua row dalam satu query × method
#     seen: dict[tuple, dict] = {}  # (qid, method) → representative row
#     for r in all_results:
#         key = (r["ID"], r["Metode"])
#         if key not in seen:
#             seen[key] = r

#     def agg(rows: list[dict]) -> dict:
#         """Agregasi untuk sekumpulan representative rows."""
#         valid = [r for r in rows if r.get("Hit_GT") is not None]
#         if not valid:
#             return {
#                 "n_queries": len(rows),
#                 "Hit_Rate@K": None,
#                 "MRR": None,
#                 "Avg_Score_Top1": None,
#                 "Avg_Latency_ms": None,
#             }
#         # Avg score: ambil score rank-1 untuk setiap query
#         scores_top1 = []
#         for r in valid:
#             # cari row rank=1 untuk query ini
#             qid, method = r["ID"], r["Metode"]
#             rank1_rows = [
#                 x for x in all_results
#                 if x["ID"] == qid and x["Metode"] == method and x["Rank"] == 1
#             ]
#             if rank1_rows:
#                 scores_top1.append(rank1_rows[0]["Skor_Similarity"])

#         return {
#             "n_queries": len(valid),
#             "Hit_Rate@K": round(sum(r["Hit_GT"] for r in valid) / len(valid), 4),
#             "MRR": round(sum(r["RR"] for r in valid) / len(valid), 4),
#             "Avg_Score_Top1": round(sum(scores_top1) / len(scores_top1), 2) if scores_top1 else None,
#             "Avg_Latency_ms": round(
#                 sum(r["Latency_ms"] for r in valid) / len(valid), 1
#             ),
#         }

#     by_method: dict[str, list] = defaultdict(list)
#     by_method_type: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

#     for row in seen.values():
#         method = row["Metode"]
#         tipe = row.get("Tipe", "Unknown")
#         by_method[method].append(row)
#         by_method_type[method][tipe].append(row)

#     summary_by_method = {m: agg(rows) for m, rows in by_method.items()}
#     summary_by_method_type = {
#         m: {t: agg(rows) for t, rows in types.items()}
#         for m, types in by_method_type.items()
#     }

#     # Tentukan pemenang berdasarkan MRR (lebih informatif dari Hit Rate)
#     mrr_rag = (summary_by_method.get("Standard RAG") or {}).get("MRR") or 0
#     mrr_hyde = (summary_by_method.get("HyDE") or {}).get("MRR") or 0
#     if mrr_rag > mrr_hyde:
#         winner = "Standard RAG"
#     elif mrr_hyde > mrr_rag:
#         winner = "HyDE"
#     else:
#         winner = "Tie"

#     return {
#         "by_method": summary_by_method,
#         "by_method_and_type": summary_by_method_type,
#         "winner_by_MRR": winner,
#     }


# # ─── Main ─────────────────────────────────────────────────────────────────────

# def main():
#     if not QUERIES_FILE.exists():
#         print(f"[ERROR] File query tidak ditemukan: {QUERIES_FILE}")
#         sys.exit(1)

#     with open(QUERIES_FILE, "r", encoding="utf-8") as f:
#         queries = json.load(f)
#     print(f"[INFO] Loaded {len(queries)} queries dari {QUERIES_FILE}")

#     service = get_rag_service()
#     print("[INFO] RAGService initialized.")

#     OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
#     timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
#     output_path = OUTPUT_DIR / f"eval_{timestamp_str}.json"

#     all_results: list[dict] = []
#     total = len(queries)

#     for i, query in enumerate(queries, start=1):
#         qid = query["ID"]
#         tipe = query["Tipe"]
#         query_text = query["Query_Text"]
#         ground_truth_file = query.get("Ground_Truth_File")

#         print(f"\n[{i}/{total}] {qid} | {tipe} | \"{query_text}\"")

#         # — Standard RAG —
#         print(f"  → Standard RAG ...", end=" ", flush=True)
#         try:
#             rag_results, rag_latency = run_standard_rag(service, query_text, TOP_K)
#             rag_results = compute_ir_metrics(rag_results, ground_truth_file)
#             print(f"OK | {rag_latency:.0f}ms | {len(rag_results)} docs | "
#                   f"Hit={rag_results[0]['Hit_GT'] if rag_results else 'N/A'} "
#                   f"RR={rag_results[0]['RR'] if rag_results else 'N/A'}")
#         except Exception as e:
#             print(f"ERROR: {e}")
#             rag_results = []

#         for r in rag_results:
#             all_results.append({"ID": qid, "Tipe": tipe,
#                                  "Query_Text": query_text,
#                                  "Ground_Truth_File": ground_truth_file, **r})

#         # — HyDE —
#         print(f"  → HyDE ...", end=" ", flush=True)
#         try:
#             hyde_results, hyde_latency = run_hyde(service, query_text, TOP_K)
#             hyde_results = compute_ir_metrics(hyde_results, ground_truth_file)
#             print(f"OK | {hyde_latency:.0f}ms | {len(hyde_results)} docs | "
#                   f"Hit={hyde_results[0]['Hit_GT'] if hyde_results else 'N/A'} "
#                   f"RR={hyde_results[0]['RR'] if hyde_results else 'N/A'}")
#         except Exception as e:
#             print(f"ERROR: {e}")
#             hyde_results = []

#         for r in hyde_results:
#             all_results.append({"ID": qid, "Tipe": tipe,
#                                  "Query_Text": query_text,
#                                  "Ground_Truth_File": ground_truth_file, **r})

#         if i < total:
#             time.sleep(DELAY_BETWEEN_QUERIES)

#     # Hitung summary agregat
#     print("\n[INFO] Computing summary metrics...")
#     summary = compute_summary(all_results)

#     # Print ringkasan ke terminal
#     print("\n" + "="*60)
#     print("HASIL EVALUASI — RINGKASAN")
#     print("="*60)
#     for method, stats in summary["by_method"].items():
#         print(f"\n  {method}:")
#         print(f"    Hit Rate@{TOP_K} : {stats.get('Hit_Rate@K')}")
#         print(f"    MRR           : {stats.get('MRR')}")
#         print(f"    Avg Score@1   : {stats.get('Avg_Score_Top1')}")
#         print(f"    Avg Latency   : {stats.get('Avg_Latency_ms')} ms")
#     print(f"\n  Pemenang (MRR) : {summary['winner_by_MRR']}")
#     print("="*60)

#     output = {
#         "metadata": {
#             "timestamp": datetime.now().isoformat(),
#             "top_k": TOP_K,
#             "embedding_model": "intfloat/multilingual-e5-small",
#             "llm_model": "llama3-8b-8192",
#             "chroma_collection": "skripsi_docs",
#             "total_queries": len(queries),
#             "methods": ["Standard RAG", "HyDE"],
#         },
#         "summary": summary,      # ← BARU: metrik agregat
#         "results": all_results,  # raw results tetap ada
#     }

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(output, f, ensure_ascii=False, indent=2)

#     print(f"\n[DONE] {len(all_results)} records → {output_path}")


# if __name__ == "__main__":
#     main()




"""
run_evaluation.py — Evaluasi otomatis Standard RAG vs HyDE
Jalankan dari folder backend/:
    python scripts/run_evaluation.py

Metrik yang dihitung per query:
  - Hit@K      : apakah ground truth ada di top-K hasil
  - Rank_GT    : di posisi berapa ground truth ditemukan (None = tidak ada)
  - RR         : Reciprocal Rank = 1/Rank_GT (0 jika tidak ditemukan)
  - P@K        : Precision@K (hanya bermakna jika ada multi-GT, di sini proxy)
  - Latency_ms : waktu eksekusi retrieval dalam milidetik

Metrik agregat (per metode × per tipe query):
  - Hit_Rate@K : mean(Hit@K)
  - MRR        : mean(RR)
  - Avg_Score  : rata-rata similarity score dokumen yang dikembalikan
  - Avg_Latency_ms
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

TOP_K = 5
QUERIES_FILE = Path(__file__).parent.parent / "evaluation" / "queries.json"
OUTPUT_DIR = Path(__file__).parent.parent / "evaluation" / "results"
DELAY_BETWEEN_QUERIES = 1.5  # detik; hindari rate-limit Groq untuk HyDE

# ─── Helper ───────────────────────────────────────────────────────────────────

def normalize_source(source: str) -> str:
    """
    Normalisasi path source agar perbandingan GT tidak gagal karena
    perbedaan path penuh vs basename.

    Contoh:
      "/data/skripsi/2024_BUDI.pdf"  →  "2024_BUDI.pdf"
      "2024_BUDI.pdf"                →  "2024_BUDI.pdf"
    """
    return Path(source).name if source else ""


def run_standard_rag(
    service: RAGService, query_text: str, top_k: int
) -> tuple[list[dict], float]:
    """
    Jalankan Standard RAG dan kembalikan (results, latency_ms).
    Score dipertahankan dalam format 0–100 sesuai output rag_service.py.
    """
    t0 = time.perf_counter()
    rag_response = service.standard_rag(query_text, k=top_k, is_eval=True)
    latency_ms = (time.perf_counter() - t0) * 1000

    results = []
    for rank_idx, doc in enumerate(rag_response.get("documents", []), start=1):
        meta = doc.get("metadata", {})
        file_source = meta.get("source", "unknown.pdf")
        results.append({
            "Metode": "Standard RAG",
            "Rank": rank_idx,
            "Skor_Similarity": round(meta.get("similarity_score", 0), 4),
            "File_Source": file_source,
            "File_Source_Basename": normalize_source(file_source),
            "Tahun": meta.get("tahun") or extract_year_from_filename(file_source),
            "Judul_Skripsi": meta.get("judul", ""),
            "Abstrak": doc.get("page_content", ""),
            "Dokumen_Hipotetikal_LLM": None,
            "Latency_ms": round(latency_ms, 1),
        })
    return results, latency_ms


def run_hyde(
    service: RAGService, query_text: str, top_k: int
) -> tuple[list[dict], float]:
    """
    Jalankan HyDE RAG dan kembalikan (results, latency_ms).
    Latency mencakup waktu generate hypothetical doc + retrieval.
    """
    t0 = time.perf_counter()
    hyde_response = service.hyde_rag(query_text, k=top_k, is_eval=True, prompt_type="prompt2")
    latency_ms = (time.perf_counter() - t0) * 1000

    hypothetical_doc = hyde_response.get("hypothetical_document", "")
    method_name = "HyDE"
    results = []
    for rank_idx, doc in enumerate(hyde_response.get("documents", []), start=1):
        meta = doc.get("metadata", {})
        file_source = meta.get("source", "unknown.pdf")
        results.append({
            "Metode": method_name,
            "Rank": rank_idx,
            "Skor_Similarity": round(meta.get("similarity_score", 0), 4),
            "File_Source": file_source,
            "File_Source_Basename": normalize_source(file_source),
            "Tahun": meta.get("tahun") or extract_year_from_filename(file_source),
            "Judul_Skripsi": meta.get("judul", ""),
            "Abstrak": doc.get("page_content", ""),
            "Dokumen_Hipotetikal_LLM": hypothetical_doc,
            "Latency_ms": round(latency_ms, 1),
        })
    return results, latency_ms


def compute_ir_metrics(
    results: list[dict],
    ground_truth_file: str | None,
) -> list[dict]:
    """
    Hitung metrik IR per query × metode dan tambahkan ke setiap row:

      Hit_GT        : bool — apakah GT ada di hasil sama sekali
      Rank_GT       : int | None — posisi GT di ranking (1-based)
      RR            : float — Reciprocal Rank (1/Rank_GT, atau 0.0)

    Menggunakan basename untuk perbandingan agar robust terhadap perbedaan path.
    """
    if not ground_truth_file:
        for r in results:
            r.update({"Hit_GT": None, "Rank_GT": None, "RR": None})
        return results

    gt_basename = normalize_source(ground_truth_file)

    # Cari rank GT
    rank_gt = None
    for r in results:
        if normalize_source(r.get("File_Source_Basename", "")) == gt_basename:
            rank_gt = r["Rank"]
            break

    rr = (1.0 / rank_gt) if rank_gt is not None else 0.0
    hit = rank_gt is not None

    for r in results:
        r["Hit_GT"] = hit
        r["Rank_GT"] = rank_gt
        r["RR"] = round(rr, 4)

    return results


def compute_summary(all_results: list[dict]) -> dict:
    """
    Hitung metrik agregat dari seluruh results.
    """
    from collections import defaultdict

    # Kumpulkan data per (method, tipe)
    # Gunakan satu row per query × method (ambil Rank=1 sebagai proxy per-query)
    seen: dict[tuple, dict] = {}  # (qid, method) → representative row
    for r in all_results:
        key = (r["ID"], r["Metode"])
        if key not in seen:
            seen[key] = r

    def agg(rows: list[dict]) -> dict:
        """Agregasi untuk sekumpulan representative rows."""
        valid = [r for r in rows if r.get("Hit_GT") is not None]
        if not valid:
            return {
                "n_queries": len(rows),
                "Hit_Rate@K": None,
                "MRR": None,
                "Avg_Score_Top1": None,
                "Avg_Latency_ms": None,
            }
        # Avg score: ambil score rank-1 untuk setiap query
        scores_top1 = []
        for r in valid:
            # cari row rank=1 untuk query ini
            qid, method = r["ID"], r["Metode"]
            rank1_rows = [
                x for x in all_results
                if x["ID"] == qid and x["Metode"] == method and x["Rank"] == 1
            ]
            if rank1_rows:
                scores_top1.append(rank1_rows[0]["Skor_Similarity"])

        return {
            "n_queries": len(valid),
            "Hit_Rate@K": round(sum(r["Hit_GT"] for r in valid) / len(valid), 4),
            "MRR": round(sum(r["RR"] for r in valid) / len(valid), 4),
            "Avg_Score_Top1": round(sum(scores_top1) / len(scores_top1), 2) if scores_top1 else None,
            "Avg_Latency_ms": round(
                sum(r["Latency_ms"] for r in valid) / len(valid), 1
            ),
        }

    by_method: dict[str, list] = defaultdict(list)
    by_method_type: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

    for row in seen.values():
        method = row["Metode"]
        tipe = row.get("Tipe", "Unknown")
        by_method[method].append(row)
        by_method_type[method][tipe].append(row)

    summary_by_method = {m: agg(rows) for m, rows in by_method.items()}
    summary_by_method_type = {
        m: {t: agg(rows) for t, rows in types.items()}
        for m, types in by_method_type.items()
    }

    # Tentukan pemenang berdasarkan MRR (lebih informatif dari Hit Rate)
    mrr_rag = (summary_by_method.get("Standard RAG") or {}).get("MRR") or 0
    mrr_hyde = (summary_by_method.get("HyDE") or {}).get("MRR") or 0

    mrr_dict = {
        "Standard RAG": mrr_rag,
        "HyDE": mrr_hyde
    }

    winner = max(mrr_dict, key=mrr_dict.get)
    if list(mrr_dict.values()).count(mrr_dict[winner]) > 1:
        winner = "Tie / Multiple methods share the top MRR"

    return {
        "by_method": summary_by_method,
        "by_method_and_type": summary_by_method_type,
        "winner_by_MRR": winner,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not QUERIES_FILE.exists():
        print(f"[ERROR] File query tidak ditemukan: {QUERIES_FILE}")
        sys.exit(1)

    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        queries = json.load(f)
    print(f"[INFO] Loaded {len(queries)} queries dari {QUERIES_FILE}")

    service = get_rag_service()
    print("[INFO] RAGService initialized.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"eval_{timestamp_str}.json"

    all_results: list[dict] = []
    total = len(queries)

    for i, query in enumerate(queries, start=1):
        qid = query["ID"]
        tipe = query["Tipe"]
        query_text = query["Query_Text"]
        ground_truth_file = query.get("Ground_Truth_File")

        print(f"\n[{i}/{total}] {qid} | {tipe} | \"{query_text}\"")

        # — Standard RAG —
        print(f"  → Standard RAG ...", end=" ", flush=True)
        try:
            rag_results, rag_latency = run_standard_rag(service, query_text, TOP_K)
            rag_results = compute_ir_metrics(rag_results, ground_truth_file)
            print(f"OK | {rag_latency:.0f}ms | {len(rag_results)} docs | "
                  f"Hit={rag_results[0]['Hit_GT'] if rag_results else 'N/A'} "
                  f"RR={rag_results[0]['RR'] if rag_results else 'N/A'}")
        except Exception as e:
            print(f"ERROR: {e}")
            rag_results = []

        for r in rag_results:
            all_results.append({"ID": qid, "Tipe": tipe,
                                 "Query_Text": query_text,
                                 "Ground_Truth_File": ground_truth_file, **r})

        # — HyDE —
        print(f"  → HyDE ...", end=" ", flush=True)
        try:
            hyde_results, hyde_latency = run_hyde(service, query_text, TOP_K)
            hyde_results = compute_ir_metrics(hyde_results, ground_truth_file)
            print(f"OK | {hyde_latency:.0f}ms | {len(hyde_results)} docs | "
                  f"Hit={hyde_results[0]['Hit_GT'] if hyde_results else 'N/A'} "
                  f"RR={hyde_results[0]['RR'] if hyde_results else 'N/A'}")
        except Exception as e:
            print(f"ERROR: {e}")
            hyde_results = []

        for r in hyde_results:
            all_results.append({"ID": qid, "Tipe": tipe,
                                 "Query_Text": query_text,
                                 "Ground_Truth_File": ground_truth_file, **r})

        if i < total:
            time.sleep(DELAY_BETWEEN_QUERIES)

    # Hitung summary agregat
    print("\n[INFO] Computing summary metrics...")
    summary = compute_summary(all_results)

    # Print ringkasan ke terminal
    print("\n" + "="*60)
    print("HASIL EVALUASI — RINGKASAN")
    print("="*60)
    for method, stats in summary["by_method"].items():
        print(f"\n  {method}:")
        print(f"    Hit Rate@{TOP_K} : {stats.get('Hit_Rate@K')}")
        print(f"    MRR           : {stats.get('MRR')}")
        print(f"    Avg Score@1   : {stats.get('Avg_Score_Top1')}")
        print(f"    Avg Latency   : {stats.get('Avg_Latency_ms')} ms")
    print(f"\n  Pemenang (MRR) : {summary['winner_by_MRR']}")
    print("="*60)

    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "top_k": TOP_K,
            "embedding_model": "intfloat/multilingual-e5-small",
            "llm_model": settings.GROQ_MODEL,
            "chroma_collection": "skripsi_docs",
            "total_queries": len(queries),
            "methods": ["Standard RAG", "HyDE"],
        },
        "summary": summary,      # ← Metrik agregat
        "results": all_results,  # raw results tetap ada
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] {len(all_results)} records → {output_path}")


if __name__ == "__main__":
    main()