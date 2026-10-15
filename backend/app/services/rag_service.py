
"""
RAG Service — REVISI FINAL
Terintegrasi Mode Evaluasi (Bypass Threshold & MMR) & E5 Prefix Absolut.
Prompt HyDE dipertahankan murni dari spesifikasi user.
"""

import threading
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from app.core.config import settings
from app.services.embedding_service import embedding_service


class RAGService:
    """Service untuk menangani RAG dan HyDE retrieval."""

    def __init__(self):
        self.embedding = embedding_service.get_embedding_function()

        print("-> Initializing ChromaDB vectorstore...")
        self.vectorstore = Chroma(
            embedding_function=self.embedding,
            persist_directory=settings.CHROMA_PERSIST_DIR,
            collection_metadata={"hnsw:space": "cosine"}
        )
        print("[OK] ChromaDB loaded")

        # Deteksi distance metric collection (cosine vs l2 vs ip)
        # Agar _distance_to_score tidak salah hitung
        try:
            meta = self.vectorstore._collection.metadata or {}
            self._distance_metric = meta.get("hnsw:space", "cosine")
        except Exception:
            self._distance_metric = "cosine"
        print(f"Distance metric: {self._distance_metric}")

        print("🔄 Initializing Groq LLM...")
        self.llm_standard = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=settings.LLM_TEMPERATURE_STANDARD,
            max_tokens=settings.LLM_MAX_TOKENS,
            groq_api_key=settings.GROQ_API_KEY,
        )
        
        self.llm_hyde = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=settings.LLM_TEMPERATURE_HYDE,
            max_tokens=settings.LLM_MAX_TOKENS,
            groq_api_key=settings.GROQ_API_KEY,
        )
        print("✅ Groq LLM initialized")

        # Prompt 1: Strict Abstract Components (masalah, metode, hasil)
        self.prompt_1 = (
            "Tugas: Tulis satu paragraf abstrak skripsi Teknik Informatika dalam Bahasa Indonesia "
            "berdasarkan topik berikut.\n"
            "Struktur abstrak harus mengikuti komponen berikut secara ketat:\n"
            "1. Masalah: Masalah penelitian yang diselesaikan.\n"
            "2. Metode: Metode, algoritma, atau teknologi yang digunakan.\n"
            "3. Hasil: Hasil atau tujuan akhir yang ingin dicapai.\n\n"
            "Topik: {query}"
        )

        # Prompt 2: Strict Constraints to reduce ambiguity and hallucination (focused and deterministic context)
        # self.prompt_2 = (
        #     "Tugas: Tulis satu paragraf abstrak skripsi Teknik Informatika dalam "
        #     "Bahasa Indonesia berdasarkan topik berikut.\n\n"
        #     "Aturan ketat:\n"
        #     "- Panjang: 1–3 kalimat saja.\n"
        #     "- Hanya sebutkan metode, algoritma, atau teknologi yang TERSEBUT "
        #     "SECARA EKSPLISIT atau TERSIRAT LANGSUNG dari topik. "
        #     "Jangan tambahkan metode lain untuk mengurangi ambiguitas dan halusinasi.\n"
        #     "- Jika topik menggunakan bahasa sehari-hari (misal: 'aplikasi "
        #     "absensi pakai muka'), terjemahkan ke istilah akademis yang tepat "
        #     "(misal: 'Penelitian ini membangun sistem absensi berbasis "
        #     "pengenalan wajah...').\n"
        #     "- Jika ada typo, koreksi otomatis ke istilah baku yang paling "
        #     "mendekati dalam bidang Teknik Informatika.\n"
        #     "- Output hanya teks abstrak. Tanpa salam, tanpa label, tanpa "
        #     "tanda kutip pembuka/penutup.\n\n"
        #     "Topik: {query}"
        # )
        # self.prompt_2 = (
        #     "Tugas: Tulis pernyataan fokus penelitian (research intent) skripsi Teknik Informatika "
        #     "dalam Bahasa Indonesia berdasarkan kueri berikut.\n\n"
        #     "Aturan ketat:\n"
        #     "- Panjang: Maksimal 1–2 kalimat deklaratif yang padat.\n"
        #     "- DILARANG KERAS menuliskan hasil pengujian, kesimpulan, atau angka persentase fiktif.\n"
        #     "- Hanya sebutkan metode, algoritma, atau teknologi yang TERSEBUT "
        #     "SECARA EKSPLISIT atau TERSIRAT LANGSUNG dari kueri. "
        #     "Jangan menebak atau menambahkan metode eksternal.\n"
        #     "- Jika kueri menggunakan bahasa awam (misal: 'aplikasi "
        #     "absensi pakai muka'), terjemahkan ke terminologi akademis murni "
        #     "(misal: 'Penelitian ini mengembangkan sistem absensi berbasis pengenalan wajah').\n"
        #     "- Jika terdapat typo, koreksi otomatis ke istilah baku Teknik Informatika.\n"
        #     "- Output murni teks kalimat. Tanpa salam, tanpa label judul, tanpa "
        #     "tanda kutip pembuka/penutup.\n\n"
        #     "Kueri: {query}"
        # )
        # self.prompt_2 = (
        #     "Tugas: Tulis pernyataan fokus penelitian (research intent) skripsi Teknik Informatika "
        #     "dalam Bahasa Indonesia berdasarkan kueri berikut.\n\n"
        #     "Aturan ketat:\n"
        #     "- Panjang: Maksimal 1–2 kalimat deklaratif yang padat.\n"
        #     "- DILARANG KERAS menuliskan hasil pengujian, kesimpulan, atau angka persentase fiktif.\n"
        #     "- Hanya sebutkan metode, algoritma, atau teknologi yang TERSEBUT "
        #     "SECARA EKSPLISIT atau TERSIRAT LANGSUNG dari kueri. Jangan menebak metode eksternal.\n"
        #     "- SESUAIKAN KATA KERJA AKADEMIS: Jangan selalu menggunakan kata 'mengembangkan' atau 'membangun'. "
        #     "Gunakan kata kerja yang paling akurat sesuai niat kueri (contoh: Menganalisis, Mengevaluasi, "
        #     "Mengimplementasikan, Menerapkan, Mengklasifikasi, atau Menguji).\n"
        #     "- Jika kueri menggunakan bahasa awam (misal: 'cek daun sakit cnn'), terjemahkan ke "
        #     "terminologi akademis murni (misal: 'Penelitian ini mengimplementasikan algoritma Convolutional "
        #     "Neural Network untuk klasifikasi penyakit daun').\n"
        #     "- Jika terdapat typo, koreksi otomatis ke istilah baku Teknik Informatika.\n"
        #     "- Output murni teks kalimat. Tanpa salam, tanpa label judul, tanpa tanda kutip pembuka/penutup.\n\n"
        #     "Kueri: {query}"
        # )

        # self.prompt_2 = (
        #     "Tugas: Tulis pernyataan fokus penelitian (research intent) skripsi Teknik Informatika "
        #     "dalam Bahasa Indonesia berdasarkan kueri berikut.\n\n"
        #     "Aturan ketat (ZERO HALLUCINATION):\n"
        #     "- Panjang: Maksimal 1–2 kalimat deklaratif yang padat.\n"
        #     "- DILARANG KERAS menuliskan hasil pengujian, kesimpulan, atau angka persentase fiktif.\n"
        #     "- ATURAN FOKUS KONTEN (SANGAT PENTING):\n"
        #     "  1. JIKA kueri HANYA berisi masalah/objek (misal: 'hama daun tomat' atau 'sapi dicuri'), DILARANG KERAS menebak/menambahkan nama metode, algoritma, atau teknologi penyelesaian. Fokuslah murni pada eksplorasi/analisis masalah tersebut.\n"
        #     "  2. JIKA kueri HANYA berisi metode/algoritma (misal: 'algoritma CNN' atau 'metode Agile'), DILARANG KERAS mengarang objek studi kasus spesifik. Fokuslah pada implementasi atau evaluasi metode tersebut secara umum.\n"
        #     "  3. JIKA kueri secara eksplisit memuat KEDUANYA (masalah dan metode), gabungkan ke dalam satu kalimat logis tanpa menambah entitas pihak ketiga.\n"
        #     "- SESUAIKAN KATA KERJA AKADEMIS: Jangan selalu menggunakan kata 'mengembangkan' atau 'membangun'. "
        #     "Gunakan kata kerja yang paling akurat sesuai niat kueri (contoh: Menganalisis, Mengevaluasi, "
        #     "Mengimplementasikan, Menerapkan, Mengklasifikasi, atau Memantau).\n"
        #     "- Terjemahkan bahasa awam ke terminologi akademis murni (misal: 'cek daun sakit cnn' -> "
        #     "'Penelitian ini mengimplementasikan algoritma Convolutional Neural Network untuk klasifikasi penyakit daun').\n"
        #     "- Jika terdapat typo, koreksi otomatis ke istilah baku Teknik Informatika.\n"
        #     "- Output murni teks kalimat. Tanpa salam, tanpa label judul, tanpa tanda kutip pembuka/penutup.\n\n"
        #     "Kueri: {query}"
        # )

        # self.prompt_2 = (
        #     "Tugas: Tulis pernyataan fokus penelitian (research intent) skripsi Teknik Informatika "
        #     "dalam Bahasa Indonesia berdasarkan kueri berikut.\n\n"
        #     "Aturan ketat (ZERO HALLUCINATION):\n"
        #     "- Panjang: Maksimal 1–2 kalimat deklaratif yang padat.\n"
        #     "- DILARANG KERAS menuliskan hasil pengujian, kesimpulan, atau angka persentase fiktif.\n"
        #     "- ATURAN FOKUS KONTEN (SANGAT PENTING):\n"
        #     "  1. JIKA kueri HANYA berisi masalah/objek (misal: 'hama daun tomat' atau 'sapi dicuri'), DILARANG KERAS menebak/menambahkan nama metode, algoritma, atau teknologi penyelesaian. Fokuslah murni pada eksplorasi, penanganan, atau analisis masalah tersebut.\n"
        #     "  2. JIKA kueri HANYA berisi metode/algoritma (misal: 'algoritma CNN' atau 'metode Agile'), DILARANG KERAS mengarang objek studi kasus spesifik. Fokuslah pada implementasi atau evaluasi metode tersebut secara umum.\n"
        #     "  3. JIKA kueri secara eksplisit memuat KEDUANYA (masalah dan metode), gabungkan ke dalam satu kalimat logis tanpa menambah entitas pihak ketiga.\n"
        #     "- SESUAIKAN KATA KERJA AKADEMIS: Jangan selalu memaksakan kata 'mengembangkan' atau 'membangun'. "
        #     "Gunakan kata kerja yang paling akurat sesuai niat kueri (contoh: Menganalisis, Mengevaluasi, "
        #     "Mengimplementasikan, Menerapkan, Mengklasifikasi, atau Memantau).\n"
        #     "- TRANSLASI KOSAKATA BAKU (WAJIB): Terjemahkan seluruh bahasa awam, kata benda kasual, atau istilah pasaran ke dalam terminologi akademis murni yang paling lazim digunakan dalam skripsi Teknik Informatika. (Contoh: 'hape' -> 'perangkat mobile/smartphone', 'tong sampah' -> 'tempat sampah', 'bikin web' -> 'sistem informasi berbasis web').\n"
        #     "- Jika terdapat typo, koreksi otomatis ke istilah baku Teknik Informatika.\n"
        #     "- Output murni teks kalimat. Tanpa kata pengantar, tanpa label, tanpa tanda kutip pembuka/penutup.\n\n"
        #     "Kueri: {query}"
        # )
        
        self.prompt_2 = (
                    "Tugas: Tulis pernyataan fokus penelitian (research intent) skripsi Teknik Informatika "
                    "dalam Bahasa Indonesia berdasarkan kueri berikut.\n\n"
                    "Aturan ketat (ZERO HALLUCINATION):\n"
                    "- Panjang: Maksimal 1–2 kalimat deklaratif yang padat.\n"
                    "- DILARANG KERAS menuliskan hasil pengujian, kesimpulan, atau angka persentase fiktif.\n"
                    "- ATURAN FOKUS KONTEN (SANGAT PENTING):\n"
                    "  1. JIKA kueri HANYA berisi masalah/objek (misal: 'hama daun tomat' atau 'sapi dicuri'), DILARANG KERAS menebak/menambahkan nama metode, algoritma, atau teknologi penyelesaian. Fokuslah murni pada eksplorasi, penanganan, atau analisis masalah tersebut.\n"
                    "  2. JIKA kueri HANYA berisi metode/algoritma (misal: 'algoritma CNN' atau 'metode Agile'), DILARANG KERAS mengarang objek studi kasus spesifik. Fokuslah pada implementasi atau evaluasi metode tersebut secara umum.\n"
                    "  3. JIKA kueri secara eksplisit memuat KEDUANYA (masalah dan metode), gabungkan ke dalam satu kalimat logis tanpa menambah entitas pihak ketiga.\n"
                    "- SESUAIKAN KATA KERJA AKADEMIS: Jangan selalu memaksakan kata 'mengembangkan' atau 'membangun'. "
                    "Gunakan kata kerja yang paling akurat sesuai niat kueri (contoh: Menganalisis, Mengevaluasi, "
                    "Mengimplementasikan, Menerapkan, Mengklasifikasi, atau Memantau).\n"
                    "- TRANSLASI KOSAKATA BAKU (WAJIB): Terjemahkan seluruh bahasa awam, kata benda kasual, atau istilah pasaran ke dalam terminologi akademis murni yang paling lazim digunakan dalam skripsi Teknik Informatika. (Contoh: 'hape' -> 'perangkat mobile/smartphone', 'tong sampah' -> 'tempat sampah', 'bikin web' -> 'sistem informasi berbasis web').\n"
                    "- Jika terdapat typo, koreksi otomatis ke istilah baku Teknik Informatika.\n"
                    "- Output murni teks kalimat. Tanpa kata pengantar, tanpa label, tanpa tanda kutip pembuka/penutup.\n\n"
                    "Kueri: {query}"
                )

        # self.prompt_3 = (
        #     "Tugas: Hasilkan representasi dokumen akademis (judul dan kata kunci) "
        #     "untuk memperluas kueri pencarian berikut ke dalam ruang vektor pencarian.\n\n"
        #     "Aturan ketat (HARD RULES):\n"
        #     "- BILINGUAL WAJIB: Pertahankan istilah teknis, nama algoritma, dan konsep IT murni "
        #     "dalam Bahasa Inggris (contoh: 'Computer Vision', 'Deep Learning', 'Internet of Things'). "
        #     "DILARANG KERAS menerjemahkannya ke Bahasa Indonesia.\n"
        #     "- JANGAN gunakan kalimat pembuka/penutup (seperti 'Penelitian ini...', 'Abstrak:').\n"
        #     "- HANYA tuliskan Judul Hipotetikal (1 kalimat) dan 5-7 Kata Kunci teknis spesifik (campuran ID & EN sesuai kelaziman IT).\n"
        #     "- Jika kueri adalah bahasa kasual/typo, langsung terjemahkan ke bentuk akademis dwibahasa yang paling tepat.\n"
        #     "- Output HANYA berupa teks langsung. Tanpa format tambahan.\n\n"
        #     "Topik: {query}"
        # )
        # self.prompt_3 = (
        #    "Tugas: Ekstrak dan perluas kueri berikut menjadi 7-10 kata kunci teknis, "
        #     "objek, dan metode spesifik dalam domain Teknik Informatika.\n\n"
        #     "Aturan ketat (HARD RULES):\n"
        #     "- HANYA hasilkan daftar kata kunci yang dipisahkan dengan koma.\n"
        #     "- DILARANG KERAS membuat kalimat, frasa panjang, atau judul.\n"
        #     "- DILARANG KERAS menggunakan kata-kata generik akademis (seperti: 'Sistem', "
        #     "'Aplikasi', 'Pengembangan', 'Analisis', 'Perancangan', 'Pemantauan', 'Penerapan').\n"
        #     "- BILINGUAL WAJIB: Istilah algoritma dan konsep IT harus murni dalam Bahasa Inggris "
        #     "(misal: 'Deep Learning', 'Computer Vision', 'Internet of Things').\n"
        #     "- Jika kueri berupa masalah (misal: daun membusuk), ubah menjadi kata kunci teknis "
        #     "(misal: Plant Disease Detection, Penyakit Daun).\n"
        #     "- Output HANYA teks daftar kata kunci. Tanpa label, awalan, atau kutipan.\n\n"
        #     "Kueri: {query}"
        # )
        # self.prompt_3 = (
        #     "Tugas: Ekstrak dan perluas kueri berikut menjadi 7-10 kata kunci spesifik "
        #     "untuk pencarian dokumen skripsi Teknik Informatika.\n\n"
        #     "Aturan ketat (HARD RULES):\n"
        #     "- HANYA hasilkan daftar kata kunci yang dipisahkan dengan koma. Tanpa awalan, kalimat, atau judul.\n"
        #     "- PEMISAHAN BAHASA WAJIB:\n"
        #     "  1. Objek masalah, subjek penelitian, dan tempat (misal: daun tomat, sampah laut, penyakit kulit) WAJIB menggunakan Bahasa Indonesia.\n"
        #     "  2. Metode, algoritma, dan teknologi IT (misal: Computer Vision, Deep Learning, Random Forest) WAJIB menggunakan Bahasa Inggris.\n"
        #     "- JIKA kueri berupa masalah awam (misal: 'petani rugi daun membusuk'), ubah menjadi kata kunci teknis campuran (misal: Penyakit Daun, Plant Disease Detection, Computer Vision).\n"
        #     "- JANGAN gunakan kata generik seperti: 'Sistem', 'Aplikasi', 'Pengembangan', 'Analisis'.\n\n"
        #     "Kueri: {query}"
        # )
        
        self.prompt_3 = (
                    "Tugas: Ekstrak dan perluas kueri berikut menjadi 7-10 kata kunci spesifik "
                    "untuk pencarian dokumen skripsi Teknik Informatika.\n\n"
                    "Aturan ketat (HARD RULES):\n"
                    "- ATURAN DOMAIN (MUTLAK): Analisis kueri secara menyeluruh. Jika kueri masuk dalam ranah non-Teknik Informatika, DILARANG KERAS memprosesnya.\n"
                    "  Contoh topik yang HARUS DITOLAK:\n"
                    "  * 'cara jadi dokter' -> DITOLAK (kedokteran)\n"
                    "  * 'model pembelajaran matematika siswa' -> DITOLAK (pendidikan)\n"
                    "  * 'inflasi profitabilitas bank syariah' -> DITOLAK (ekonomi)\n"
                    "  * 'tinjauan yuridis undang-undang' -> DITOLAK (hukum)\n"
                    "  * 'pola asuh gizi stunting' -> DITOLAK (kesehatan)\n"
                    "  * 'dosis pupuk kandang tanaman' -> DITOLAK (pertanian)\n"
                    "  Jika kueri seperti contoh di atas atau sejenisnya, Anda HANYA BOLEH mengeluarkan output string ini persis: 'Kueri ditolak: Topik tidak relevan dengan keilmuan Teknik Informatika.'\n"
                    "- HANYA hasilkan daftar kata kunci yang dipisahkan dengan koma. Tanpa awalan, kalimat, atau judul.\n"
                    "- PEMISAHAN BAHASA WAJIB:\n"
                    "  1. Objek masalah, subjek penelitian, dan tempat (misal: daun tomat, sampah laut, penyakit kulit) WAJIB menggunakan Bahasa Indonesia.\n"
                    "  2. Metode, algoritma, dan teknologi IT (misal: Computer Vision, Deep Learning, Random Forest) WAJIB menggunakan Bahasa Inggris.\n"
                    "- JIKA kueri berupa masalah awam (misal: 'petani rugi daun membusuk'), ubah menjadi kata kunci teknis campuran (misal: Penyakit Daun, Plant Disease Detection, Computer Vision).\n"
                    "- JANGAN gunakan kata generik seperti: 'Sistem', 'Aplikasi', 'Pengembangan', 'Analisis'.\n\n"
                    "Kueri: {query}"
                )
        # Kelebihan komentar prompt lama tidak lagi ditabur ulang:
        # Prompt lama 2 & 3 telah diganti/dihilangkan duplikasinya di atas.

    def get_vector_count(self) -> int:
        try:
            return self.vectorstore._collection.count()
        except Exception:
            return 0

    def _is_non_it_query(self, query: str) -> bool:
        """
        Pre-filter cerdas untuk mendeteksi kueri yang jelas-jelas di luar
        lingkup Teknik Informatika. Return True jika kueri harus ditolak.

        Logika:
        1. Jika ada kata kunci IT (sistem, aplikasi, software, dll) → ITAMAN (return False)
        2. Jika ada profesi non-IT (cara jadi dokter, dll) → DITOLAK (return True)
        3. Jika ada kata kunci non-IT tanpa konteks IT → DITOLAK (return True)

        Menggunakan word boundary matching agar "si" tidak cocok dengan "syariah".
        """
        import re

        query_lower = query.lower()

        # Kata kunci IT yang menandakan query masih dalam lingkup Teknik Informatika
        it_keywords = [
            "sistem", "aplikasi", "software", "program", "komputer", "computer",
            "algoritma", "database", "data", "jaringan", "network", "web",
            "mobile", "android", "ios", "machine learning", "deep learning",
            "artificial intelligence", "ai", "cloud", "server", "client",
            "interface", "ui", "ux", "framework", "library", "api",
            "pemrograman", "coding", "programming", "developer",
            "teknologi informasi", "informatika", "ilkom",
            "sistem informasi", "sistem berkaitan", "berbasis", "berbasis web",
            "berbasis mobile", "berbasis android", "berbasis cloud",
        ]

        # Profesi non-IT (selalu ditolak)
        non_it_professions = [
            "cara jadi", "cara menjadi", "menjadi dokter", "menjadi guru",
            "menjadi pengacara", "menjadi arsitek", "menjadi perawat",
            "menjadi polisi", "menjadi tentara", "menjadi koki",
            "menjadi atlet", "menjadi artis", "menjadi penyanyi",
        ]

        # Kata kunci non-IT (ditolak HANYA jika tidak ada kata IT)
        non_it_keywords = [
            # Kesehatan / Kedokteran
            "dokter", "kedokteran", "kesehatan", "penyakit", "obat", "rumah sakit",
            "klinik", "pasien", "diagnosa", "terapi", "stunting", "gizi",
            "keperawatan", "bidan", "apotek", "farmasi",
            # Pendidikan / Tarbiyah
            "guru", "mengajar", "pembelajaran", "tarbiyah", "pendidikan",
            "siswa", "murid", "sekolah", "kurikulum", "mata pelajaran",
            # Ekonomi / Bisnis
            "inflasi", "profitabilitas", "bank syariah", "ekonomi",
            "akuntansi", "keuangan", "investasi", "saham", "pasar",
            # Hukum
            "hukum", "yuridis", "undang-undang", "peraturan", "pidana",
            "perdata", "pengadilan", "jaksa", "advokat", "notaris",
            # Pertanian
            "pertanian", "petani", "pupuk", "tanaman", "ternak", "perkebunan",
            "padi", "jagung", "kopi", "sawit", "iklim", "hujan",
            # Sosial / Psikologi
            "psikologi", "sosiologi", "antropologi", "politik", "pemerintahan",
            "masyarakat", "budaya", "agama", "keagamaan",
            # Sastra / Seni / Humaniora
            "novel", "sastra", "wacana", "puisi", "cerpen", "literatur",
            "seni", "tari", "musik", "film", "teater", "lukisan", "fotografi",
            "keindahan", "estetika", "filosofi", "etika", "moral",
        ]

        def contains_word(text: str, word: str) -> bool:
            """Cek apakah kata ada sebagai whole word (bukan substring)."""
            return bool(re.search(r'\b' + re.escape(word) + r'\b', text))

        # 1. Cek profesi non-IT (selalu ditolak)
        for profesi in non_it_professions:
            if contains_word(query_lower, profesi):
                return True

        # 2. Cek kata kunci IT → jika ada, query valid (return False)
        for keyword in it_keywords:
            if contains_word(query_lower, keyword):
                return False

        # 3. Cek kata kunci non-IT → jika ada tanpa konteks IT, ditolak
        for keyword in non_it_keywords:
            if contains_word(query_lower, keyword):
                return True

        return False

    def _distance_to_score(self, distance: float) -> float:
        """
        Konversi ChromaDB distance ke similarity score (0–100%).

        - cosine distance  → range [0, 2]  → score = (1 - d/2) * 100
        - l2 distance      → range [0, ∞]  → score = 1/(1+d) * 100  (approx)
        - inner product    → range [0, 1]  → score = (1 - d) * 100
        """
        try:
            d = float(distance)
            metric = self._distance_metric

            if metric == "cosine":
                score = (1.0 - d / 2.0) * 100.0
            elif metric == "l2":
                score = (1.0 / (1.0 + d)) * 100.0
            else:  # "ip" atau inner product
                score = (1.0 - d) * 100.0

            return round(max(0.0, min(100.0, score)), 2)
        except (TypeError, ValueError):
            return 0.0

    def _build_document_response(self, doc, distance: float) -> dict:
        """Bangun response dokumen sesuai format JSON."""
        score = self._distance_to_score(distance)
        return {
            "page_content": doc.page_content,
            "metadata": {
                "source": doc.metadata.get("source", "Unknown"),
                "judul": doc.metadata.get("judul", ""),
                "nama": doc.metadata.get("nama", ""),
                "nim": doc.metadata.get("nim", ""),
                "pembimbing": doc.metadata.get("pembimbing", ""),
                "tahun": doc.metadata.get("tahun", ""),
                "similarity_score": score,
            },
        }

    def _deduplicate(self, docs_with_scores: list) -> list:
        """
        Hilangkan duplikat chunk dari skripsi yang sama.
        Kriteria: NIM + judul yang sama → ambil yang score-nya tertinggi
        (distance terkecil) saja.
        """
        seen: dict[str, tuple] = {}  

        for doc, distance in docs_with_scores:
            nim = doc.metadata.get("nim", "").strip()
            judul = doc.metadata.get("judul", "").strip()
            source = doc.metadata.get("source", "").strip()

            if nim and judul:
                key = f"{nim}|{judul}"
            elif source:
                key = source
            else:
                key = f"__nokey_{id(doc)}"

            if key not in seen or distance < seen[key][1]:
                seen[key] = (doc, distance)

        return list(seen.values())

    def _apply_threshold(
        self,
        docs_with_scores: list,
        min_score: float,
    ) -> list:
        """
        Filter dokumen dengan similarity_score < min_score.
        Bekerja pada raw distance — konversi dulu sebelum filter.
        """
        filtered = []
        for doc, distance in docs_with_scores:
            score = self._distance_to_score(distance)
            if score >= min_score:
                filtered.append((doc, distance))
        return filtered

    def standard_rag(
        self,
        query: str,
        k: int = None,
        min_score: float = None,
        use_mmr: bool = False,
        is_eval: bool = False,
    ) -> dict:
        """
        Standard RAG retrieval.
        Terintegrasi dengan saklar evaluasi (is_eval).
        """
        # Pre-filter: tolak kueri non-Teknik Informatika
        if self._is_non_it_query(query):
            print(f"🚫 Query rejected by pre-filter: {query}")
            return {
                "mode": "rag",
                "query": query,
                "docs_count": 0,
                "documents": [],
                "rejected": True,
            }

        if k is None:
            k = settings.K_RETRIEVAL
            
        if is_eval:
            use_mmr = False  # Mutlak dimatikan saat evaluasi
            min_score = 0.0  # Bypass threshold saat evaluasi
        elif min_score is None:
            min_score = getattr(settings, "MIN_SIMILARITY_SCORE", 30.0)

        # PREFIX E5 WAJIB
        query_repr = f"query: {query.strip()}"

        if use_mmr:
            fetch_k = min(k * 4, self.get_vector_count() or k * 4)
            mmr_docs = self.vectorstore.max_marginal_relevance_search(
                query_repr,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=0.7,
            )
            docs_with_scores = []
            for doc in mmr_docs:
                scored = self.vectorstore.similarity_search_with_score(
                    doc.page_content, k=1
                )
                if scored:
                    docs_with_scores.append((doc, scored[0][1]))
                else:
                    docs_with_scores.append((doc, 1.0))
        else:
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query_repr, k=k * 2
            )

        # Pemfilteran & Dedup HANYA dijalankan jika bukan mode evaluasi
        if not is_eval:
            docs_with_scores = self._apply_threshold(docs_with_scores, min_score)
            docs_with_scores = self._deduplicate(docs_with_scores)

        docs_with_scores = sorted(docs_with_scores, key=lambda x: x[1])[:k]

        documents = [
            self._build_document_response(doc, dist)
            for doc, dist in docs_with_scores
        ]

        return {
            "mode": "rag",
            "query": query,
            "used_mmr": use_mmr,
            "docs_count": len(documents),
            "documents": documents,
        }

    def hyde_rag(
        self,
        query: str,
        k: int = None,
        min_score: float = None,
        is_eval: bool = False,
        prompt_type: str = "prompt3",
    ) -> dict:
        """
        HyDE (Hypothetical Document Embeddings) RAG.
        Terintegrasi dengan saklar evaluasi (is_eval) dan pilihan prompt_type.
        """
        if k is None:
            k = settings.K_RETRIEVAL
            
        if is_eval:
            min_score = 0.0  # Bypass threshold saat evaluasi
        elif min_score is None:
            min_score = getattr(settings, "MIN_SIMILARITY_SCORE", 30.0)

        # Pre-filter: tolak kueri non-Teknik Informatika sebelum memanggil LLM
        if self._is_non_it_query(query):
            print(f"🚫 Query rejected by pre-filter: {query}")
            return {
                "mode": "hyde",
                "query": query,
                "hypothetical_document": "Kueri ditolak: Topik tidak relevan dengan keilmuan Teknik Informatika.",
                "docs_count": 0,
                "documents": [],
                "rejected": True,
            }

        # Pilih template prompt berdasarkan parameter (Default utama: Prompt 3)
        if prompt_type == "prompt1":
            prompt = self.prompt_1.format(query=query.strip())
        elif prompt_type == "prompt2":
            prompt = self.prompt_2.format(query=query.strip())
        else:
            prompt = self.prompt_3.format(query=query.strip())

        try:
            hypothetical_doc = self.llm_hyde.invoke(prompt).content.strip()
            hypothetical_doc = " ".join(hypothetical_doc.split())
            
            # Validasi: jika LLM mengembalikan string kosong, fallback ke query
            if not hypothetical_doc:
                print(f"⚠️  LLM returned empty hypothesis for query: {query}")
                hypothetical_doc = query
            else:
                print(f"✅ HyDE hypothesis generated: {hypothetical_doc[:100]}...")
        except Exception as e:
            print(f"⚠️  Error generating hypothetical doc: {e}")
            hypothetical_doc = query  

        # Validasi: jika LLM menolak kueri (domain filter), return early
        if "Kueri ditolak" in hypothetical_doc:
            print(f"🚫 Query rejected by domain filter: {query}")
            return {
                "mode": "hyde",
                "query": query,
                "hypothetical_document": hypothetical_doc,
                "docs_count": 0,
                "documents": [],
                "rejected": True,
            }

        # PREFIX E5 WAJIB UNTUK HYPOTHETICAL DOC
        query_repr = f"query: {hypothetical_doc}"

        docs_with_scores = self.vectorstore.similarity_search_with_score(
            query_repr, k=k * 2
        )

        # Pemfilteran & Dedup HANYA dijalankan jika bukan mode evaluasi
        if not is_eval:
            docs_with_scores = self._apply_threshold(docs_with_scores, min_score)
            docs_with_scores = self._deduplicate(docs_with_scores)
            
        docs_with_scores = sorted(docs_with_scores, key=lambda x: x[1])[:k]

        documents = [
            self._build_document_response(doc, dist)
            for doc, dist in docs_with_scores
        ]

        return {
            "mode": "hyde",
            "query": query,
            "hypothetical_document": hypothetical_doc,
            "docs_count": len(documents),
            "documents": documents,
        }

    def hybrid_rag(
        self,
        query: str,
        k: int = None,
        min_score: float = None,
        is_eval: bool = False,
    ) -> dict:
        """
        Hybrid RAG retrieval dengan filter metadata tahun dan BM25 fusion.
        """
        from app.services.hybrid_utils import parse_query_metadata, SimpleBM25, hybrid_search_fusion

        # Pre-filter: tolak kueri non-Teknik Informatika
        if self._is_non_it_query(query):
            print(f"🚫 Query rejected by pre-filter: {query}")
            return {
                "mode": "hybrid",
                "query": query,
                "docs_count": 0,
                "documents": [],
                "rejected": True,
            }
        
        if k is None:
            k = settings.K_RETRIEVAL
            
        if is_eval:
            min_score = 0.0
        elif min_score is None:
            min_score = getattr(settings, "MIN_SIMILARITY_SCORE", 30.0)

        # 1. Parse Query & Metadata
        parsed = parse_query_metadata(query)
        clean_query = parsed["clean_query"]
        if not clean_query:
            clean_query = query
        
        # 2. Setup Where Filter untuk ChromaDB
        where_filter = None
        if parsed["tahun_spesifik"]:
            where_filter = {"tahun": str(parsed["tahun_spesifik"])}
        elif parsed["tahun_awal"] and parsed["tahun_akhir"]:
            where_filter = {
                "$and": [
                    {"tahun": {"$gte": str(parsed["tahun_awal"])}},
                    {"tahun": {"$lte": str(parsed["tahun_akhir"])}}
                ]
            }
            
        # PREFIX E5 WAJIB
        query_repr = f"query: {clean_query}"
        
        # 3. Dense Search (ChromaDB)
        # Ambil SEMUA dokumen agar pencarian nama penulis oleh BM25 (leksikal) dapat mencakup seluruh koleksi.
        # Jika hanya mengambil k*4, dokumen dengan nama penulis yang dicari mungkin terlempar duluan karena skor semantiknya rendah.
        pool_size = self.get_vector_count()
        if pool_size == 0:
             return {
                "mode": "hybrid",
                "query": query,
                "clean_query": clean_query,
                "docs_count": 0,
                "documents": [],
            }
            
        dense_results = self.vectorstore.similarity_search_with_score(
            query_repr, k=pool_size, filter=where_filter
        )
        
        if not is_eval:
            dense_results = self._apply_threshold(dense_results, min_score)
            dense_results = self._deduplicate(dense_results)
            
        dense_results = dense_results[:pool_size]
        
        if not dense_results:
             return {
                "mode": "hybrid",
                "query": query,
                "clean_query": clean_query,
                "docs_count": 0,
                "documents": [],
            }
        
        # 4. Sparse Search (BM25)
        documents_for_bm25 = [doc for doc, _ in dense_results]
        bm25 = SimpleBM25(documents_for_bm25)
        bm25_scores = bm25.get_scores(clean_query)
        
        # 5. Fusion
        fused_documents = hybrid_search_fusion(dense_results, bm25_scores, alpha=0.5)
        final_documents = fused_documents[:k]
        
        return {
            "mode": "hybrid",
            "query": query,
            "clean_query": clean_query,
            "filter_applied": where_filter,
            "docs_count": len(final_documents),
            "documents": final_documents,
        }


# ─── Thread-safe singleton ───────────────────────────────────────────────────
_rag_service: RAGService | None = None
_rag_service_lock = threading.Lock()


def get_rag_service() -> RAGService:
    """
    Get atau create RAGService instance (thread-safe).
    """
    global _rag_service
    if _rag_service is None:
        with _rag_service_lock:
            if _rag_service is None:
                _rag_service = RAGService()
    return _rag_service