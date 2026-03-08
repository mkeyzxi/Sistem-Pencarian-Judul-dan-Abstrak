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
        
        # Format dokumen untuk prompt
        docs_text = ""
        for i, doc in enumerate(found_documents, 1):
            docs_text += f"\n{i}. Judul: {doc.get('title', 'Unknown')}\n"
            docs_text += f"   Abstrak: {doc.get('content', '')[:500]}...\n"
        
        prompt = f"""Anda adalah dosen pembimbing akademik yang berpengalaman di bidang Teknik Informatika UIN Alauddin Makassar.

Seorang mahasiswa mengajukan judul skripsi: "{user_title}"

Berdasarkan penelitian-penelitian relevan yang sudah ada:
{docs_text}

Berikan saran akademik singkat (3-5 poin) tentang:
1. Relevansi judul dengan penelitian sebelumnya
2. Potensi pengembangan metode atau algoritma
3. Saran dataset atau tools yang bisa digunakan
4. Kelebihan dan kekurangan judul yang diajukan
5. Rekomendasi modifikasi judul (jika perlu)

Saran harus:
- Konstruktif dan mendukung
- Berbasis pada penelitian yang ada
- Praktis dan dapat diimplementasikan
- Gunakan bahasa Indonesia yang baik

Format respon: Berikan saran point-by-point dengan penjelasan singkat."""
        
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
        
        # Format dokumen untuk display
        docs_text = "Berikut beberapa judul dan abstrak skripsi yang relevan:\n\n"
        for i, doc in enumerate(retrieved_docs, 1):
            docs_text += f"**[{i}] {doc.get('title', 'Unknown')}**\n"
            docs_text += f"Sumber: {doc.get('source', 'Unknown')}\n"
            docs_text += f"Abstrak: {doc.get('content', '')[:800]}...\n\n"
        
        # Format riwayat percakapan
        history_text = ""
        if chat_history:
            history_text = "\n--- RIWAYAT PERCAKAPAN SEBELUMNYA ---\n"
            for msg in chat_history[-10:]:  # Max 10 pesan terakhir
                role = "User" if msg.get("role") == "user" else "Asisten"
                history_text += f"{role}: {msg.get('content', '')[:500]}\n"
            history_text += "--- AKHIR RIWAYAT ---\n\n"
        
        prompt = f"""Anda adalah chatbot asisten akademik yang ramah dan membantu mahasiswa mencari skripsi relevan.

{history_text}User menanyakan: "{query}"

Dokumen relevan yang ditemukan:
{docs_text}

Buatlah respon chatbot yang:
1. Menyapa user dengan ramah
2. Menginformasikan hasil pencarian
3. Jika ada riwayat percakapan, PAHAMI KONTEKS-nya. Jika user bertanya lanjutan tentang hasil sebelumnya (misalnya "jelaskan lebih detail nomor 2", "apa kelebihan skripsi pertama"), jawab berdasarkan konteks percakapan sebelumnya.
4. Menawarkan bantuan lebih lanjut

Format respon:
- Mulai dengan sapaan ramah
- Tampilkan hasil pencarian dalam TABEL MARKDOWN dengan kolom:
  | No | Judul | Sumber | Ringkasan |
  Kolom "Ringkasan" WAJIB berisi penjelasan singkat (1-2 kalimat) tentang:
  • Apa masalah/topik yang diangkat
  • Siapa subjek/objek penelitian (jika ada)
  • Metode atau temuan penting
- Setelah tabel, berikan penjelasan ringkas tentang relevansi
- Akhiri dengan penawaran bantuan
- Gunakan bahasa Indonesia yang baik dan natural

Mode: {mode}"""
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            return response
        except Exception as e:
            return f"Maaf, terjadi error dalam memproses pertanyaan Anda: {str(e)}"


# Singleton instance
suggestion_service = SuggestionService()
