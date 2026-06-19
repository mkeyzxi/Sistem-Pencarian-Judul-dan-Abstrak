# =========================================================
# INSTALL LIBRARY
# =========================================================
# Jalankan cell ini sekali di Google Colab
!pip uninstall -y chromadb hnswlib
!pip install -q \
  "chromadb>=0.5.23" \
  sentence-transformers \
  langchain \
  langchain-community \
  langchain-core \
  langchain-groq \
  langchain-huggingface \
  pypdf

# =========================================================
# IMPORTS & SETUP
# =========================================================
import os
import re
import json
import shutil
import hashlib
import warnings
import time
import numpy as np
import chromadb

from google.colab import drive

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

# Mount Google Drive
drive.mount('/content/drive')

# Suppress Warnings
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings("ignore")

print("Numpy  :", np.__version__)
print("Chroma :", chromadb.__version__)

# =========================================================
# KONFIGURASI
# =========================================================
SIMILARITY_THRESHOLD = 0.82   # Hanya untuk mode produksi
MAX_K_RETRIEVAL      = 5       # Top-K dokumen yang diambil

os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,   # Nol mutlak → output deterministik
)

# =========================================================
# FUNGSI HELPER: EKSTRAKSI PDF & METADATA
# =========================================================

def extract_title(lines: list[str]) -> str:
    title_lines = []
    stop_words = [
        "skripsi", "diajukan", "oleh", "nama", "nim",
        "program studi", "fakultas", "universitas",
    ]
    for line in lines:
        low = line.lower()
        if any(sw in low for sw in stop_words):
            break
        if len(line.strip()) > 3:
            title_lines.append(line.strip())
        if len(" ".join(title_lines)) > 200:
            break
    return " ".join(title_lines)

def extract_identity(text: str) -> tuple[str, str]:
    nama = re.search(r"nama\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
    nim  = re.search(r"nim\s*[:\-]?\s*(\d+)",  text, re.IGNORECASE)
    res_nama = nama.group(1).strip() if nama else "Unknown"
    res_nim  = nim.group(1).strip()  if nim  else "Unknown"
    return res_nama, res_nim

def extract_abstract(text: str, title: str = "", fallback_text: str = "") -> str:
    # Menggunakan variasi kata kunci penanda abstrak yang umum ditemukan
    match = re.search(r"(?i)(?:ABSTRAK|ABSTRACT|INTISARI)[^\w]*([\s\S]+)", text)

    if match:
        raw_abstract = match.group(1).strip()
    else:
        # Pemicu mekanisme Fallback jika halaman dua atau dokumen kehilangan kata kunci 'ABSTRAK'
        if fallback_text.strip():
            raw_abstract = fallback_text.strip()
        else:
            return ""

    flat_text = re.sub(r"\s+", " ", raw_abstract).strip()

    # Deteksi apakah teks masih mengandung baris formulir cover / penyertaan identitas ulang
    if re.search(r"(?i)(nama|nim|jurusan|program studi|judul)\s*[:\-]", flat_text[:250]):
        pola_gelar = r"(?i)(?:S\.Kom|M\.Kom|M\.T|S\.T|M\.Sc|Ph\.D|M\.Si|M\.M|M\.Pd|M\.Eng|S\.Si)[^\w]*\s+(?=[A-Z0-9])"
        matches_gelar = list(re.finditer(pola_gelar, flat_text[:800]))
        if matches_gelar:
            return flat_text[matches_gelar[-1].end():].strip()

        pola_pembimbing = r"(?i)Pembimbing[\s\S]*?(?=\s[A-Z][a-z]{4,})"
        matches_pem = list(re.finditer(pola_pembimbing, flat_text[:800]))
        if matches_pem:
            return flat_text[matches_pem[-1].end():].strip()

        if title:
            words      = title.split()
            last_words = words[-4:] if len(words) >= 4 else words
            pola_akhir_judul = r"\s+".join([re.escape(w) for w in last_words])
            match_judul = re.search(pola_akhir_judul, flat_text[:1000], re.IGNORECASE)
            if match_judul:
                return flat_text[match_judul.end():].strip()

        # Pembersihan agresif berbasis struktur awal kalimat esai akademik
        match_kalimat = re.search(r"(?i)(?:penelitian|sistem|aplikasi|otonomi|kawasan|latar belakang|tujuan)[\s\S]+", flat_text)
        if match_kalimat:
            return match_kalimat.group(0).strip()

    return flat_text

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def extract_year_from_filename(filename: str) -> int:
    match = re.match(r"(\d{4})_", filename)
    return int(match.group(1)) if match else 2000

# =========================================================
# FASE 1: EKSTRAKSI & SANITASI DATA
# =========================================================
data_dir = "/content/drive/MyDrive/Data_Judul_Abstrak_Skripsi_Teknik_Informatika"
documents: list[Document] = []
seen_hashes: set[str]     = set()

print("=" * 55)
print("FASE 1: MEMULAI EKSTRAKSI PDF...")
print("=" * 55)

if not os.path.exists(data_dir):
    raise FileNotFoundError(
        f"Direktori data tidak ditemukan: {data_dir}\n"
        "Pastikan folder sudah ada di Google Drive Anda."
    )

gagal_diproses = []

for file in sorted(os.listdir(data_dir)):
    if not file.endswith(".pdf"):
        continue

    filepath = os.path.join(data_dir, file)
    try:
        loader = PyPDFLoader(filepath)
        pages  = loader.load()

        if len(pages) < 2:
            print(f"  [SKIP] {file} — kurang dari 2 halaman")
            continue

        cover_text = pages[0].page_content
        full_text  = "\n".join(p.page_content for p in pages)

        # Sediakan konten halaman ke-2 (indeks 1) secara utuh sebagai jaring pengaman fallback
        fallback_page_text = pages[1].page_content if len(pages) >= 2 else ""

        lines     = [l.strip() for l in cover_text.split("\n") if len(l.strip()) > 2]
        title     = clean_text(extract_title(lines))
        nama, nim = extract_identity(cover_text)

        # Kirimkan fallback_page_text ke dalam fungsi pengekstraksi abstrak
        abstract  = clean_text(extract_abstract(full_text, title, fallback_text=fallback_page_text))

        if len(abstract) < 150:
            print(f"  [SKIP] {file} — abstrak terlalu pendek ({len(abstract)} karakter)")
            print(f"         Teks tertangkap: {abstract}")
            continue

        text_hash = hashlib.md5(abstract.lower().encode("utf-8")).hexdigest()
        if text_hash in seen_hashes:
            print(f"  [SKIP DUPLIKAT] {file}")
            print(f"         Teks yang memicu duplikat: {abstract[:150]}...")
            continue

        seen_hashes.add(text_hash)

        year = extract_year_from_filename(file)

        metadata = {
            "source": file,
            "judul" : title,
            "nama"  : nama,
            "nim"   : nim,
            "tahun" : year,
        }
        formatted_content = f"passage: {abstract}"
        documents.append(Document(page_content=formatted_content, metadata=metadata))

    except Exception as e:
        print(f"  [ERROR] {file} gagal diproses: {e}")
        gagal_diproses.append(file)

print(f"\n✅  Ekstraksi Selesai.")
print(f"    Dokumen valid   : {len(documents)}")
print(f"    Duplikat dibuang: {len(seen_hashes) - len(documents) + len(gagal_diproses)}")
print(f"    Gagal diproses  : {len(gagal_diproses)}")
if gagal_diproses:
    print(f"    File bermasalah : {gagal_diproses}")

# =========================================================
# FASE 2: SETUP CHROMA DB & VEKTORISASI
# =========================================================
persist_directory = "/content/chroma_db"
collection_name   = "skripsi_informatika"

try:
    chromadb.api.client.SharedSystemClient.clear_system_cache()
except Exception:
    pass

print("\n" + "=" * 55)
print("FASE 2: MEMBANGUN VECTOR DATABASE...")
print("=" * 55)

if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory, ignore_errors=True)
    print("  Direktori Chroma lama dihapus.")
os.makedirs(persist_directory, exist_ok=True)

embedding = HuggingFaceEmbedembeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

client     = chromadb.PersistentClient(path=persist_directory)
collection = client.get_or_create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"},
)

vectorstore = Chroma(
    embedding_function=embedding,
    client=client,
    collection_name=collection_name,
)

BATCH_SIZE = 50
for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i : i + BATCH_SIZE]
    if batch:
        vectorstore.add_documents(batch)
        print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} dokumen ditambahkan...")

total_vectors = vectorstore._collection.count()
print(f"\n✅  Vektorisasi Selesai. Total vektor tersimpan: {total_vectors}")

# =========================================================
# FASE 3: RETRIEVAL — MODE EVALUASI
# =========================================================

def retrieve_standard_rag_eval(query: str, k: int = MAX_K_RETRIEVAL) -> list[Document]:
    query_repr = f"query: {query}"
    results    = vectorstore.similarity_search_with_score(query_repr, k=k)

    formatted = []
    for doc, distance in results:
        similarity = round(1.0 - distance, 4)
        doc.metadata["similarity_score"] = similarity
        formatted.append(doc)

    return formatted

def retrieve_hyde_eval(query: str, k: int = MAX_K_RETRIEVAL) -> tuple[str, list[Document]]:
    prompt = f"""Anda adalah mesin ekstraksi entitas teknis murni untuk sistem temu kembali informasi. Terjemahkan niat kueri awam menjadi representasi abstrak teknis spesifik (algoritma, sensor, arsitektur) dalam satu kalimat padat. DILARANG memberi salam, penjelasan, atau kalimat pengantar. Langsung berikan output teknisnya.

Contoh 1:
Input: "alat biar motor gak gampang dicuri"
Output: Sistem keamanan kendaraan bermotor menggunakan mikrokontroler Arduino, modul GPS tracking, sensor Passive Infra Red (PIR), dan integrasi notifikasi SMS atau Internet of Things (IoT).

Contoh 2:
Input: "cara otomatis pisahin telur bagus"
Output: Klasifikasi fertilitas dan kualitas telur ayam menggunakan algoritma Computer Vision seperti YOLOv8 atau Convolutional Convolutional Network (CNN) terintegrasi sensor cahaya LDR dan Load Cell.

Contoh 3:
Input: "yolo"
Output: Algoritma deteksi objek real-time You Only Look Once (YOLO) pada disiplin Computer Vision dan Deep Learning untuk identifikasi dan klasifikasi citra digital.

Input: "{query}"
Output:"""

    try:
        raw_response = llm.invoke(prompt).content.strip()
        print(f"  [DEBUG LLM RAW] {raw_response[:150]}")
        hypothetical_doc = re.sub(r"^Output:\s*", "", raw_response, flags=re.IGNORECASE).strip()

        if not hypothetical_doc:
            raise ValueError("LLM mengembalikan respons kosong setelah pembersihan regex.")

    except Exception as e:
        print(f"  [HyDE ERROR] DETAIL KEGAGALAN pada kueri '{query}': {str(e)}")
        return "GAGAL_LLM", []

    query_repr = f"passage: {hypothetical_doc}"
    results    = vectorstore.similarity_search_with_score(query_repr, k=k)

    formatted = []
    for doc, distance in results:
        similarity = round(1.0 - distance, 4)
        doc.metadata["similarity_score"] = similarity
        formatted.append(doc)

    return hypothetical_doc, formatted

# =========================================================
# FUNGSI PRODUKSI
# =========================================================

def _parse_query_and_year(query: str) -> tuple[str, int | None]:
    match = re.search(r"\b(20\d{2}|19\d{2})\b", query)
    if match:
        year        = int(match.group(1))
        clean_query = re.sub(r"\b(20\d{2}|19\d{2})\b", "", query).strip()
        clean_query = re.sub(r"\s+", " ", clean_query).strip()
        return clean_query, year
    return query, None

def _filter_by_threshold(
    results_with_distance: list[tuple[Document, float]],
    threshold: float = SIMILARITY_THRESHOLD,
) -> list[Document]:
    filtered = []
    for doc, distance in results_with_distance:
        similarity = round(1.0 - distance, 4)
        if similarity >= threshold:
            doc.metadata["similarity_score"] = similarity
            filtered.append(doc)
    return filtered

def retrieve_standard_rag(query: str, k: int = MAX_K_RETRIEVAL) -> list[Document]:
    clean_query, year = _parse_query_and_year(query)
    query_repr        = f"query: {clean_query}"
    where_filter      = {"tahun": {"$eq": year}} if year else None

    if where_filter:
        results = vectorstore.similarity_search_with_score(query_repr, k=k, filter=where_filter)
    else:
        results = vectorstore.similarity_search_with_score(query_repr, k=k)

    return _filter_by_threshold(results)

def retrieve_hyde(query: str, k: int = MAX_K_RETRIEVAL) -> tuple[str, list[Document]]:
    clean_query, year = _parse_query_and_year(query)
    where_filter      = {"tahun": {"$eq": year}} if year else None

    prompt = f"""Anda adalah mesin ekstraksi entitas teknis murni untuk sistem temu kembali informasi. Terjemahkan niat kueri awam menjadi representasi abstrak teknis spesifik (algoritma, sensor, arsitektur) dalam satu kalimat padat. DILARANG memberi salam, penjelasan, atau kalimat pengantar. Langsung berikan output teknisnya.

Contoh 1:
Input: "alat biar motor gak gampang dicuri"
Output: Sistem keamanan kendaraan bermotor menggunakan mikrokontroler Arduino, modul GPS tracking, sensor Passive Infra Red (PIR), dan integrasi notifikasi SMS atau Internet of Things (IoT).

Contoh 2:
Input: "cara otomatis pisahin telur bagus"
Output: Klasifikasi fertilitas dan kualitas telur ayam menggunakan algoritma Computer Vision seperti YOLOv8 atau Convolutional Network (CNN) terintegrasi sensor cahaya LDR dan Load Cell.

Contoh 3:
Input: "yolo"
Output: Algoritma deteksi objek real-time You Only Look Once (YOLO) pada disiplin Computer Vision dan Deep Learning untuk identifikasi dan klasifikasi citra digital.

Input: "{clean_query}"
Output:"""

    try:
        raw_response = llm.invoke(prompt).content.strip()
        hypothetical_doc = re.sub(r"^Output:\s*", "", raw_response, flags=re.IGNORECASE).strip()

        if not hypothetical_doc:
            raise ValueError("LLM mengembalikan respons kosong setelah pembersihan regex.")

    except Exception as e:
        print(f"  [HyDE PRODUKSI ERROR] {e} — fallback ke kueri asli")
        hypothetical_doc = clean_query

    query_repr = f"passage: {hypothetical_doc}"

    if where_filter:
        results = vectorstore.similarity_search_with_score(query_repr, k=k, filter=where_filter)
    else:
        results = vectorstore.similarity_search_with_score(query_repr, k=k)

    return hypothetical_doc, _filter_by_threshold(results)

# =========================================================
# FASE 4: EKSEKUSI EVALUASI
# =========================================================

def generate_evaluation_json(
    queries: list[dict],
    output_file: str = "evaluasi_rag_vs_hyde.json",
) -> None:
    print("\n" + "=" * 55)
    print("FASE 4: MEMULAI PENGUJIAN KUERI...")
    print(f"        Total kueri: {len(queries)}")
    print("=" * 55)

    eval_data: list[dict] = []

    for q_idx, q_dict in enumerate(queries, 1):
        query = q_dict["query"]
        tipe  = q_dict["tipe"]
        print(f"\n[{q_idx:02d}/{len(queries)}] Tipe: {tipe}")
        print(f"          Kueri: '{query}'")

        # 1. EVALUASI STANDARD RAG
        std_docs = retrieve_standard_rag_eval(query)

        if not std_docs:
            eval_data.append({
                "ID"         : f"Q{q_idx:02d}",
                "Tipe"       : tipe,
                "Query_Text" : query,
                "Metode"     : "Standard RAG",
                "Status"     : "GAGAL - Tidak ada dokumen ditemukan di database",
            })
            print("  [Standard RAG] Tidak ada dokumen ditemukan.")
        else:
            for rank, doc in enumerate(std_docs, 1):
                eval_data.append({
                    "ID"              : f"Q{q_idx:02d}",
                    "Tipe"            : tipe,
                    "Query_Text"      : query,
                    "Metode"          : "Standard RAG",
                    "Rank"            : rank,
                    "Skor_Similarity" : doc.metadata.get("similarity_score", 0),
                    "File_Source"     : doc.metadata.get("source", "Unknown"),
                    "Tahun"           : doc.metadata.get("tahun", "Unknown"),
                    "Judul_Skripsi"   : doc.metadata.get("judul", "Unknown"),
                    "Abstrak"         : doc.page_content.replace("passage: ", ""),
                })
            print(f"  [Standard RAG] {len(std_docs)} dokumen ditemukan. "
                  f"Skor: {[d.metadata['similarity_score'] for d in std_docs]}")

        # 2. EVALUASI HyDE
        hypo_text, hyde_docs = retrieve_hyde_eval(query)
        time.sleep(2)

        if hypo_text == "GAGAL_LLM":
            eval_data.append({
                "ID"                    : f"Q{q_idx:02d}",
                "Tipe"                  : tipe,
                "Query_Text"            : query,
                "Metode"                : "HyDE",
                "Dokumen_Hipotetikal_LLM" : "GAGAL_LLM",
                "Status"                : "GAGAL_LLM - Data cacat, eksklusi dari metrik MRR & Recall",
            })
            print("  [HyDE] ⚠️  LLM gagal → data ditandai GAGAL_LLM, BUKAN fallback ke kueri asli.")
        elif not hyde_docs:
            eval_data.append({
                "ID"                    : f"Q{q_idx:02d}",
                "Tipe"                  : tipe,
                "Query_Text"            : query,
                "Metode"                : "HyDE",
                "Dokumen_Hipotetikal_LLM" : hypo_text,
                "Status"                : "GAGAL - Tidak ada dokumen ditemukan di database",
            })
            print("  [HyDE] Tidak ada dokumen ditemukan di database.")
        else:
            print(f"  [HyDE] Dokumen hipotetis: {hypo_text[:120]}{'...' if len(hypo_text) > 120 else ''}")
            for rank, doc in enumerate(hyde_docs, 1):
                eval_data.append({
                    "ID"                    : f"Q{q_idx:02d}",
                    "Tipe"                  : tipe,
                    "Query_Text"            : query,
                    "Metode"                : "HyDE",
                    "Rank"                  : rank,
                    "Dokumen_Hipotetikal_LLM" : hypo_text if rank == 1 else "-",
                    "Skor_Similarity"         : doc.metadata.get("similarity_score", 0),
                    "File_Source"             : doc.metadata.get("source", "Unknown"),
                    "Tahun"                   : doc.metadata.get("tahun", "Unknown"),
                    "Judul_Skripsi"           : doc.metadata.get("judul", "Unknown"),
                    "Abstrak"                 : doc.page_content.replace("passage: ", ""),
                })
            print(f"  [HyDE] {len(hyde_docs)} dokumen ditemukan. "
                  f"Skor: {[d.metadata['similarity_score'] for d in hyde_docs]}")

    save_path = f"/content/drive/MyDrive/{output_file}"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=4)

    print("\n" + "=" * 55)
    print(f"✅  Evaluasi Selesai!")
    print(f"    Total entri JSON : {len(eval_data)}")
    print(f"    File disimpan di : {save_path}")
    print("=" * 55)

# =========================================================
# DAFTAR KUERI PENGUJIAN
# =========================================================
queries_pengujian = [
    {"tipe": "Metadata Query", "query": "sistem informasi berbasis web 2020"},
]

# =========================================================
# JALANKAN EVALUASI
# =========================================================
generate_evaluation_json(queries_pengujian)