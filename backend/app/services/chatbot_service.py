"""
Chatbot Service — Mode ke-4: Asisten Interaktif Skripsi
Menggunakan Agentic RAG dengan Native Tool Calling (bind_tools).

Arsitektur:
  - Strategi A: In-Memory Cache statistik dataset (Singleton)
  - Strategi B: On-Demand Retrieval via Tool Calling pada ChatGroq
  - LLM melakukan reasoning mandiri kapan perlu melakukan retrieval
"""

import threading
from collections import Counter

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.tools import tool

from app.core.config import settings


# ─── Tool Definition ─────────────────────────────────────────────────────────
# Didefinisikan sebagai top-level function agar LangChain @tool decorator
# dapat membaca docstring sebagai deskripsi tool untuk LLM.

def _extract_text_content(content) -> str:
    """Menguraikan respons content dari Gemini/LLM (bisa berupa list of blocks, dicts, atau string murni)."""
    text = ""
    if isinstance(content, str):
        text = content.strip()
    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if "text" in item and item.get("text"):
                    parts.append(str(item["text"]))
                elif "content" in item and item.get("content"):
                    parts.append(str(item["content"]))
            elif hasattr(item, "text") and getattr(item, "text", None):
                parts.append(str(item.text))
            elif hasattr(item, "content") and getattr(item, "content", None):
                parts.append(str(item.content))
            else:
                parts.append(str(item))
        text = "\n".join(parts).strip()
    elif content is None:
        text = ""
    else:
        text = str(content).strip()

    # Pembersihan gaya bahasa formal: hilangkan penggunaan tanda hubung panjang (em-dash/en-dash)
    if text:
        text = text.replace(" — ", ", ").replace("—", "-").replace("–", "-")
    return text


def _do_thesis_search(query: str, k: int = 5) -> str:
    """Eksekusi pencarian aktual ke ChromaDB via RAGService (Tahan banting terhadap format struktur data)."""
    from app.services.rag_service import get_rag_service

    if isinstance(query, dict):
        query = query.get("query", str(query))
    query = str(query).strip()
    if not query:
        return "Query pencarian tidak boleh kosong."

    try:
        rag = get_rag_service()
        result = rag.standard_rag(query, k=k)

        docs = result.get("documents", [])
        if not docs or len(docs) == 0:
            return "Tidak ditemukan skripsi yang relevan dengan topik tersebut dalam database."

        output_lines = []
        for i, doc in enumerate(docs, 1):
            if isinstance(doc, dict):
                meta = doc.get("metadata", {})
                judul = str(meta.get("judul", "Tidak diketahui"))
                nama = str(meta.get("nama", "-"))
                nim = str(meta.get("nim", "-"))
                tahun = str(meta.get("tahun", "-"))
                pembimbing = str(meta.get("pembimbing", "-"))
                score = str(meta.get("similarity_score", 0))
                abstrak = str(doc.get("page_content", ""))[:600]
            else:
                meta = getattr(doc, "metadata", {})
                judul = str(meta.get("judul", "Tidak diketahui"))
                nama = str(meta.get("nama", "-"))
                nim = str(meta.get("nim", "-"))
                tahun = str(meta.get("tahun", "-"))
                pembimbing = str(meta.get("pembimbing", "-"))
                score = str(getattr(doc, "score", meta.get("similarity_score", 0)))
                abstrak = str(getattr(doc, "page_content", getattr(doc, "content", "")))[:600]

            output_lines.append(
                f"{i}. Judul: {judul}\n"
                f"   Penulis: {nama} | NIM: {nim} | Tahun: {tahun}\n"
                f"   Pembimbing: {pembimbing}\n"
                f"   Skor Relevansi: {score}%\n"
                f"   Abstrak: {abstrak}"
            )

        return "\n\n".join(output_lines)
    except Exception as e:
        print(f"⚠️ Error in _do_thesis_search: {e}")
        return f"Terjadi kendala teknis saat membaca database ChromaDB: {str(e)}"


@tool
def search_thesis_database(query: str) -> str:
    """Cari judul dan abstrak skripsi yang relevan dari database kampus berdasarkan topik atau kata kunci.

    Gunakan tool ini ketika:
    - Pengguna meminta rekomendasi judul skripsi baru (wajib cari dulu yang sudah ada)
    - Pengguna ingin tahu penelitian apa saja yang sudah ada tentang suatu topik
    - Pengguna bertanya tentang research gap atau celah penelitian
    - Pengguna ingin memverifikasi apakah judul skripsinya sudah pernah diteliti
    - Pengguna membutuhkan referensi skripsi terdahulu untuk pembahasan

    JANGAN gunakan tool ini untuk:
    - Pertanyaan umum tentang panduan/format/struktur skripsi
    - Pertanyaan konseptual tentang teori/algoritma secara umum
    - Obrolan santai atau sapaan

    Args:
        query: Topik, kata kunci, atau deskripsi penelitian yang ingin dicari
    """
    return _do_thesis_search(query)


# ─── Chatbot Service ─────────────────────────────────────────────────────────

class ChatbotService:
    """
    Service untuk chatbot interaktif asisten skripsi.
    Singleton pattern — hanya satu instance per application lifetime.
    """

    def __init__(self):
        print("🤖 Initializing ChatbotService with Google Gemini API...")

        # LLM instance khusus chatbot (menggunakan Gemini API untuk menghindari limit TPM Groq)
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=settings.LLM_TEMPERATURE_CHATBOT,
            max_tokens=settings.CHATBOT_MAX_TOKENS,
            google_api_key=settings.GEMINI_API_KEY,
        )

        # Bind tool ke LLM (Native Function Calling)
        self.tools = [search_thesis_database]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_map = {t.name: t for t in self.tools}

        # In-memory cache untuk statistik dataset (Strategy A)
        self._dataset_context_cache: str | None = None
        self._cache_lock = threading.Lock()

        print("✅ ChatbotService initialized (Agentic RAG + Tool Calling)")

    # ─── Dataset Context Cache ────────────────────────────────────────────

    def _build_dataset_context(self) -> str:
        """
        Bangun dan cache statistik dataset dari ChromaDB.
        Hanya dihitung sekali (lazy init), disimpan di memori.
        """
        if self._dataset_context_cache is not None:
            return self._dataset_context_cache

        with self._cache_lock:
            # Double-check setelah acquire lock
            if self._dataset_context_cache is not None:
                return self._dataset_context_cache

            try:
                from app.services.rag_service import get_rag_service

                rag = get_rag_service()
                collection = rag.vectorstore._collection

                # Ambil semua metadata tanpa embeddings (efisien)
                all_data = collection.get(include=["metadatas"])
                metadatas = all_data.get("metadatas", [])
                total = len(metadatas)

                if total == 0:
                    self._dataset_context_cache = (
                        "Database skripsi kosong. Belum ada data yang di-index."
                    )
                    return self._dataset_context_cache

                # ── Hitung distribusi ────────────────────────────────
                years = Counter()
                methods = Counter()
                topics = Counter()

                method_keywords = {
                    "cnn", "svm", "naive bayes", "knn", "k-nearest",
                    "random forest", "decision tree", "deep learning",
                    "machine learning", "neural network", "nlp",
                    "clustering", "klasifikasi", "regresi", "deteksi",
                    "segmentasi", "prediksi", "rekomendasi", "sentimen",
                    "chatbot", "web", "mobile", "android", "ios",
                    "iot", "internet of things", "blockchain",
                    "data mining", "fuzzy", "genetika",
                    "backpropagation", "lstm", "rnn", "gru",
                    "yolo", "ocr", "gis", "erp", "crm",
                    "k-means", "apriori", "c4.5", "id3",
                    "logistic regression", "xgboost", "transfer learning",
                    "computer vision", "image processing",
                    "natural language processing", "text mining",
                    "speech recognition", "face recognition",
                    "object detection", "semantic", "bert", "transformers",
                    "convolutional", "recurrent",
                }

                topic_keywords = {
                    "kesehatan", "pendidikan", "pertanian", "keamanan",
                    "e-commerce", "perpustakaan", "inventori", "inventory",
                    "absensi", "presensi", "keuangan", "akademik",
                    "monitoring", "penjualan", "informasi", "pengenalan",
                    "pengolahan", "citra", "teks", "suara", "wajah",
                    "penyakit", "tanaman", "hewan", "wisata", "pariwisata",
                    "transportasi", "logistik", "rumah sakit", "klinik",
                    "apotek", "restoran", "hotel", "laundry",
                    "parkir", "sampah", "lingkungan", "bencana",
                    "covid", "corona", "pandemi",
                    "media sosial", "twitter", "instagram",
                    "kriminal", "hukum", "quran", "al-quran", "islami",
                }

                for meta in metadatas:
                    # Tahun
                    tahun = str(meta.get("tahun", "")).strip()
                    if tahun and tahun.isdigit():
                        years[tahun] += 1

                    # Ekstrak keywords dari judul
                    judul = (meta.get("judul", "") or "").lower()
                    for kw in method_keywords:
                        if kw in judul:
                            methods[kw.upper()] += 1
                    for kw in topic_keywords:
                        if kw in judul:
                            topics[kw.title()] += 1

                # ── Format context string ────────────────────────────
                lines = [f"Total skripsi dalam database: {total} dokumen"]

                if years:
                    sorted_years = sorted(years.items())
                    year_str = ", ".join(
                        f"{y} ({c} skripsi)" for y, c in sorted_years
                    )
                    lines.append(f"Distribusi tahun: {year_str}")

                if methods:
                    top_methods = methods.most_common(15)
                    method_str = ", ".join(
                        f"{m} ({c}x)" for m, c in top_methods
                    )
                    lines.append(f"Metode/algoritma terpopuler: {method_str}")

                if topics:
                    top_topics = topics.most_common(15)
                    topic_str = ", ".join(
                        f"{t} ({c}x)" for t, c in top_topics
                    )
                    lines.append(f"Topik/domain terpopuler: {topic_str}")

                # Identifikasi gap potensial
                if methods:
                    rare_methods = [
                        m for m, c in methods.items() if c <= 2
                    ]
                    if rare_methods:
                        lines.append(
                            f"Metode yang masih jarang diteliti (≤2 skripsi): "
                            f"{', '.join(rare_methods[:10])}"
                        )

                self._dataset_context_cache = "\n".join(lines)
                print(f"📊 Dataset context cached: {total} documents analyzed")
                return self._dataset_context_cache

            except Exception as e:
                print(f"⚠️ Error building dataset context: {e}")
                self._dataset_context_cache = (
                    "Statistik dataset tidak tersedia saat ini."
                )
                return self._dataset_context_cache

    def refresh_cache(self):
        """Force refresh dataset context cache (misal setelah re-index)."""
        with self._cache_lock:
            self._dataset_context_cache = None
        print("🔄 Dataset context cache cleared")

    # ─── System Prompt ────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        """Bangun system prompt dengan persona + dataset context."""
        dataset_context = self._build_dataset_context()

        return f"""Anda adalah **Asisten Skripsi TI** — asisten akademik interaktif untuk mahasiswa Program Studi Teknik Informatika, Fakultas Sains dan Teknologi, UIN Alauddin Makassar.

═══════════════════════════════════════════
PERAN DAN KAPABILITAS ANDA:
═══════════════════════════════════════════

1. **Panduan Skripsi Umum**
   - Menjelaskan struktur skripsi standar (Bab I–V: Pendahuluan, Tinjauan Pustaka, Metodologi, Hasil & Pembahasan, Penutup).
   - Memberikan tips memilih topik, merumuskan masalah, menyusun proposal, dan menulis abstrak.
   - Menjawab pertanyaan tentang aturan dan administrasi skripsi secara umum.

2. **Rekomendasi Judul Skripsi Baru**
   - WAJIB gunakan tool `search_thesis_database` untuk memeriksa judul/topik yang sudah ada di database.
   - Identifikasi celah penelitian (research gap) dari data skripsi terdahulu.
   - Rekomendasikan judul baru yang orisinal berdasarkan gap yang ditemukan.
   - Sertakan justifikasi: mengapa judul ini relevan, apa gap-nya, metode apa yang bisa digunakan.

3. **Analisis Research Gap**
   - WAJIB gunakan tool `search_thesis_database` untuk mendapatkan data skripsi terdahulu.
   - Analisis tren: topik/metode apa yang sudah jenuh vs yang masih minim.
   - Identifikasi peluang penelitian berdasarkan kombinasi topik×metode yang belum pernah dicoba.

4. **Diskusi Pengembangan Ide Penelitian**
   - Bantu mahasiswa mempersempit atau memperluas topik.
   - Sarankan metodologi, algoritma, dataset, dan tools yang sesuai.
   - Evaluasi kelebihan dan kelemahan ide mahasiswa secara konstruktif.

5. **Verifikasi Judul Mahasiswa**
   - WAJIB gunakan tool `search_thesis_database` untuk mengecek apakah topik serupa sudah pernah diteliti.
   - Berikan analisis kesamaan dan saran diferensiasi.

═══════════════════════════════════════════
KONTEKS DATASET SKRIPSI KAMPUS (LIVE):
═══════════════════════════════════════════
{dataset_context}

═══════════════════════════════════════════
ATURAN PERILAKU:
═══════════════════════════════════════════

- Selalu jawab dalam **Bahasa Indonesia** yang ramah, natural, dan akademis.
- Gunakan **format Markdown** untuk memperjelas jawaban (bold, list, heading, blockquote, dsb.).
- **DILARANG MENGGUNAKAN EMOJI APAPUN** (seperti 🚀, ✨, 💡, dsb.) dalam seluruh jawaban. Jawab dengan gaya formal, ilmiah, dan akademis murni.
- Gunakan format Markdown yang ringkas, to the point, dan hindari pengulangan kalimat yang tidak perlu agar analisis dapat disampaikan secara utuh.
- **DILARANG MENGGUNAKAN TANDA HUBUNG PANJANG (EM-DASH / "—")** dalam kalimat. Gunakan tanda baca koma (,), titik dua (:), atau tanda kurung sesuai Ejaan Bahasa Indonesia yang formal.
- **DILARANG KERAS** mengarang atau menghallusinasi data skripsi yang tidak ada di database. Jika tool mengembalikan hasil kosong, katakan secara jujur bahwa data tidak ditemukan.
- Untuk pertanyaan UMUM (panduan skripsi, teori, konsep), jawab langsung TANPA memanggil tool.
- Untuk pertanyaan yang MEMBUTUHKAN DATA skripsi (rekomendasi judul, research gap, verifikasi), WAJIB panggil tool terlebih dahulu.
- Berikan jawaban yang **substansial dan mendalam**, bukan sekadar daftar poin generik.
- Jika mahasiswa bertanya di luar cakupan skripsi Teknik Informatika, arahkan dengan sopan kembali ke topik yang relevan."""

    # ─── Response Generation (Agentic Loop) ───────────────────────────────

    def generate_response(
        self,
        message: str,
        chat_history: list | None = None,
    ) -> str:
        """
        Generate respons chatbot dengan Agentic Tool Calling.

        Flow:
        1. Susun messages (system + history + user)
        2. Invoke LLM with bound tools
        3. Jika LLM memutuskan memanggil tool → eksekusi → feed back → re-invoke
        4. Return respons final (teks markdown)
        """
        # ── Build message chain ──────────────────────────────────────
        messages = [SystemMessage(content=self._build_system_prompt())]

        # Chat history (sliding window)
        if chat_history:
            limit = settings.CHATBOT_HISTORY_LIMIT
            for msg in chat_history[-limit:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if not content:
                    continue
                if role == "user":
                    messages.append(HumanMessage(content=content))
                else:
                    messages.append(AIMessage(content=content))

        # Current user message
        messages.append(HumanMessage(content=message))

        try:
            # ── [Langkah 1] Panggilan Pertama: Detection & Retrieval ──────────
            response = self.llm_with_tools.invoke(messages)

            # Jika LLM memutuskan untuk memanggil tool
            if response.tool_calls:
                tool_cache = {}
                retrieved_contexts = []

                for tc in response.tool_calls:
                    tool_name = tc["name"]
                    tool_args = tc["args"]
                    cache_key = f"{tool_name}:{tool_args}"

                    print(
                        f"🔧 Chatbot Tool Call: {tool_name}({tool_args})"
                    )

                    # Cek cache duplikat kueri
                    if cache_key in tool_cache:
                        tool_result = tool_cache[cache_key]
                        print("   ↳ Cache hit — skip duplicate query")
                    elif tool_name in self.tool_map:
                        tool_result = self.tool_map[tool_name].invoke(
                            tool_args
                        )
                        tool_cache[cache_key] = tool_result
                    else:
                        tool_result = (
                            f"Tool '{tool_name}' tidak tersedia."
                        )

                    query_label = tool_args.get("query", str(tool_args)) if isinstance(tool_args, dict) else str(tool_args)
                    retrieved_contexts.append(f"### Kueri Pencarian: `{query_label}`\n\n{tool_result}")

                # ── [Langkah 2] Panggilan Kedua: Prompted Synthesis (Tanpa Skema Tool!) ──
                # Mengemas hasil pencarian ChromaDB menjadi HumanMessage murni
                # Mencegah error skema ToolMessage pada Google Gemini & matikan Greedy Looping
                print("🧠 Synthesizing final answer from retrieved thesis abstracts...")
                all_context_text = "\n\n---\n\n".join(retrieved_contexts)

                synthesis_prompt = (
                    f"**Pertanyaan Pengguna:**\n{message}\n\n"
                    f"═══════════════════════════════════════════════════════════\n"
                    f"REFERENSI DATA SKRIPSI KAMPUS (DARI DATABASE CHROMADB):\n"
                    f"═══════════════════════════════════════════════════════════\n"
                    f"{all_context_text}\n"
                    f"═══════════════════════════════════════════════════════════\n\n"
                    f"**Instruksi Khusus Asisten Akademik:**\n"
                    f"1. Jadikan data referensi skripsi di atas sebagai pijakan ilmiah wajib untuk menjawab pertanyaan pengguna.\n"
                    f"2. Jika pengguna meminta rekomendasi judul dan research gap:\n"
                    f"   - Tawarkan 3–5 rekomendasi judul skripsi baru yang **inovatif dan belum ada** di daftar di atas.\n"
                    f"   - Paparkan **Research Gap** secara tajam (mengapa penelitian sebelumnya punya kelemahan/keterbatasan yang diisi oleh judul baru ini).\n"
                    f"   - Sebutkan skripsi terdahulu mana dari database di atas yang menjadi rujukan perbandingannya.\n"
                    f"3. Sajikan dengan format Markdown yang rapi, formal, dan mudah dibaca (bold, bullet list, atau tabel).\n"
                    f"4. **DILARANG KERAS menggunakan emoji apapun** dalam jawaban agar mempertahankan kewibawaan publikasi ilmiah.\n"
                    f"5. **DILARANG menggunakan tanda hubung panjang (em-dash / '—')** dalam kalimat. Gunakan tanda baca standar (koma, titik dua, atau kurung) yang sesuai kaidah bahasa Indonesia akademis."
                )

                # Pesan sintesis bersih: SystemPrompt + History + Synthesis Prompt
                synthesis_messages = messages[:-1] + [HumanMessage(content=synthesis_prompt)]
                synthesis_response = self.llm.invoke(synthesis_messages)
                final_content = _extract_text_content(synthesis_response.content)

                # Debug jika entah mengapa respons masih kosong
                if not final_content:
                    print(f"⚠️ Debug synthesis_response empty: {synthesis_response}")
            else:
                # Pertanyaan teoritis / santai (Tanpa tool calling)
                final_content = _extract_text_content(response.content)

            if not final_content:
                final_content = (
                    "Maaf, saya tidak dapat menghasilkan respons saat ini. "
                    "Silakan coba lagi dengan pertanyaan yang lebih spesifik."
                )

            return final_content

        except Exception as e:
            print(f"❌ Chatbot error: {e}")
            return (
                "Maaf, terjadi kesalahan dalam memproses pertanyaan Anda. "
                f"Silakan coba lagi nanti.\n\n"
                f"*(Detail teknis: {str(e)})*"
            )


# ─── Thread-safe Singleton ────────────────────────────────────────────────────
_chatbot_service: ChatbotService | None = None
_chatbot_lock = threading.Lock()


def get_chatbot_service() -> ChatbotService:
    """Get atau create ChatbotService instance (thread-safe)."""
    global _chatbot_service
    if _chatbot_service is None:
        with _chatbot_lock:
            if _chatbot_service is None:
                _chatbot_service = ChatbotService()
    return _chatbot_service
