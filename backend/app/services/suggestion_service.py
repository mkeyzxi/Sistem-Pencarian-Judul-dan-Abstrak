"""
Suggestion Service
Menangani saran akademik berdasarkan judul dan abstrak yang ditemukan.
"""

from langchain_groq import ChatGroq
from app.core.config import settings


class SuggestionService:
    """Service untuk memberikan saran akademik."""
    
    def __init__(self):
        """Initialize LLM untuk saran akademik."""
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=0.3,  # Sedikit lebih tinggi untuk kreatifitas
            groq_api_key=settings.GROQ_API_KEY,
        )
    
    def generate_suggestion(self, user_title: str, found_documents: list) -> str:
        """
        Generate saran akademik berdasarkan judul yang diajukan dan dokumen yang ditemukan.

        Args:
            user_title: Judul yang diajukan user
            found_documents: List dokumen yang ditemukan dari RAG

        Returns:
            String berisi saran akademik
        """
        # Format dokumen untuk prompt (sederhanakan untuk LLM)
        docs_text = ""
        for i, doc in enumerate(found_documents, 1):
            meta = doc.get('metadata', {})
            judul = meta.get('judul', meta.get('title', 'Unknown'))
            abstrak = doc.get('page_content', doc.get('content', ''))[:500]
            docs_text += f"\n{i}. Judul: {judul}\n"
            docs_text += f"   Abstrak: {abstrak}...\n"

        # Instruksi: Kembalikan OUTPUT JSON murni (no markdown tables).
        prompt = f"""Anda adalah dosen pembimbing akademik berpengalaman di bidang Teknik Informatika.

Seorang mahasiswa mengajukan judul skripsi: "{user_title}"

Dokumen relevan yang ditemukan:
{docs_text}

Tugas Anda:
- Berikan saran akademik singkat (3-5 poin) meliputi:
  1) Relevansi judul terhadap penelitian sebelumnya
  2) Potensi pengembangan metode/algoritma
  3) Saran dataset atau tools
  4) Kelebihan & kekurangan
  5) Rekomendasi modifikasi judul (jika perlu)

Hasil harus memenuhi:
- Kembali sebagai JSON murni (Content-Type: application/json). Contoh struktur yang diharapkan:
  {{
    "title": "{user_title}",
    "recommendations": [
      {{"point": 1, "summary": "...", "details": "..."}},
      ...
    ],
    "modifications": ["saran judul 1", "saran judul 2"],
    "notes": "ringkasan pendek"
  }}
- Jangan gunakan tabel Markdown. Jangan sertakan teks penjelasan di luar JSON.
- Gunakan bahasa Indonesia yang baik dan ringkas.

Berikan hanya JSON sebagai output tanpa tambahan teks.
"""

        try:
            suggestion = self.llm.invoke(prompt).content.strip()
            return suggestion
        except Exception as e:
            return f"Maaf, tidak bisa generate saran saat ini: {str(e)}"
    
    def generate_chat_response(self, query: str, retrieved_docs: list, mode: str = "rag", chat_history: list = None) -> str:
        """
        Generate natural chat response sebagai chatbot.
        
        Args:
            query: Query dari user
            retrieved_docs: Dokumen yang diambil dari RAG/HyDE
            mode: Mode retrieval yang digunakan (rag atau hyde)
            chat_history: Riwayat percakapan sebelumnya
            
        Returns:
            String berisi respon chatbot yang natural
        """
        
        # Format dokumen untuk display (sederhanakan)
        docs_text = ""
        for i, doc in enumerate(retrieved_docs, 1):
            meta = doc.get('metadata', {})
            judul = meta.get('judul', meta.get('title', 'Unknown'))
            source = meta.get('source', 'Unknown')
            abstrak = doc.get('page_content', doc.get('content', ''))[:500]
            docs_text += f"\n{i}. Judul: {judul}\n"
            docs_text += f"   Sumber: {source}\n"
            docs_text += f"   Abstrak: {abstrak}...\n"

        # Format riwayat percakapan
        history_text = ""
        if chat_history:
            history_text = "\nRiwayat:\n"
            for msg in chat_history[-10:]:
                role = "User" if msg.get("role") == "user" else "Asisten"
                history_text += f"{role}: {msg.get('content', '')[:300]}\n"

        prompt = f"""Anda adalah asisten akademik. User mencari topik: '{query}'. Sistem telah menemukan dokumen relevan di bawah ini:
{docs_text}
{history_text}
TUGAS ANDA: Berikan narasi pengantar 1 hingga 2 paragraf menggunakan format Markdown biasa. DILARANG KERAS merespons menggunakan JSON, format array, atau membuat tabel. Jangan me-listing ulang judul-judul dokumen tersebut karena sistem UI frontend sudah menampilkannya secara otomatis dalam bentuk kartu. Cukup berikan narasi pengantar yang ramah dan tarik kesimpulan umum dari dokumen-dokumen yang ditemukan.

Gunakan bahasa Indonesia yang baik.
"""

        try:
            response = self.llm.invoke(prompt).content.strip()
            return response
        except Exception as e:
            return f"Maaf, terjadi error dalam memproses pertanyaan Anda: {str(e)}"


# Singleton instance
suggestion_service = SuggestionService()
