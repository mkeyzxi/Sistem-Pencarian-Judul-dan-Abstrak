import sys
import os

# Tambahkan path backend agar import berjalan lancar
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import get_rag_service

def test_raw_retrieval(query: str):
    rag = get_rag_service()
    
    print(f"=== Kueri Asli ===\n{query}")
    
    # 1. RAG Murni (Embedding Kueri -> Pencarian)
    query_repr = f"query: {query.strip()}"
    rag_results = rag.vectorstore.similarity_search_with_score(query_repr, k=5)
    
    rag_array = []
    for doc, dist in rag_results:
        doc_id = doc.metadata.get("nim", doc.metadata.get("source", "Unknown"))
        rag_array.append((doc_id, round(dist, 4)))
        
    print("\n[HASIL RAG MURNI]")
    print(rag_array)

    # 2. HyDE (Dokumen Hipotetikal -> Embedding -> Pencarian)
    prompt = rag.prompt_2.format(query=query.strip())
    hypo_doc = rag.llm_hyde.invoke(prompt).content.strip()
    hypo_doc_clean = " ".join(hypo_doc.split())
    
    print(f"\n=== Dokumen Hipotetikal ===\n{hypo_doc_clean}")
    
    hypo_repr = f"query: {hypo_doc_clean}"
    hyde_results = rag.vectorstore.similarity_search_with_score(hypo_repr, k=5)
    
    hyde_array = []
    for doc, dist in hyde_results:
        doc_id = doc.metadata.get("nim", doc.metadata.get("source", "Unknown"))
        hyde_array.append((doc_id, round(dist, 4)))
        
    print("\n[HASIL HyDE]")
    print(hyde_array)

if __name__ == "__main__":
    query_test = "penerapan algoritma CNN untuk deteksi penyakit daun padi"
    test_raw_retrieval(query_test)
