"""
Document Service
Menangani loading, preprocessing, dan ekstraksi konten dari PDF dengan Strict Quality Gate.
Implementasi 100% Rule-Based Pipeline (Tanpa LLM/API).
"""

import os
import re
from typing import Optional, List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import wordninja

class DocumentService:
    """Service untuk menangani dokumen PDF dengan Quality Gate mutlak tanpa API LLM."""

    # ================================================================== #
    #  UTILITAS & PRE-PROCESSING
    # ================================================================== #

    @staticmethod
    def split_long_words(text: str) -> str:
        """Pecah kata yang hilang spasinya menggunakan wordninja."""
        if not text:
            return ""
        words = text.split()
        processed_words = []
        for word in words:
            if len(word) > 20 and not any(c in word for c in ".-/,_"):
                split_word = " ".join(wordninja.split(word))
                processed_words.append(split_word)
            else:
                processed_words.append(word)
        return " ".join(processed_words)

    @staticmethod
    def sanitize_text(text: str) -> str:
        if not text:
            return ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\n\n", "<<PARA>>")
        text = text.replace("\n", " ")
        text = text.replace("<<PARA>>", "\n\n")
        text = re.sub(r"[ \t]{2,}", " ", text)
        lines = [l.strip() for l in text.split("\n")]
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def fix_ocr_spaces(text: str) -> str:
        """Heuristik Perbaikan Spasi Ghaib (OCR Artifacts)."""
        if not text:
            return ""
        # 1. Menghapus spasi ganda secara merata
        text = re.sub(r'\s+', ' ', text)
        
        # 2. Menggabungkan spasi pada pola berantakan "S I S T E M"
        def repl_multi(match):
            return match.group(0).replace(" ", "")
        text = re.sub(r'(?:[A-Z]\s){2,}[A-Z]\b', repl_multi, text)
        
        # 3. Memperbaiki huruf tunggal terpisah ("T ANI" -> "TANI")
        text = re.sub(r'\b([A-Z])\s([A-Z]+)\b', r'\1\2', text)
        
        # 4. Dictionary hardcode untuk kata terpotong
        hardcodes = {
            "IMPLEMENT ASI": "IMPLEMENTASI",
            "SIST EM": "SISTEM",
            "INFOR MASI": "INFORMASI",
            "APLIK ASI": "APLIKASI",
            "PENGEMBANG AN": "PENGEMBANGAN",
            "KLASIFIK ASI": "KLASIFIKASI",
            "PENELITI AN": "PENELITIAN"
        }
        
        for k, v in hardcodes.items():
            # Support exact match and title case match
            text = text.replace(k, v)
            text = text.replace(k.title(), v.title())
            
        return text.strip()

    # ================================================================== #
    #  EKSTRAKSI DETERMINISTIK & VALIDASI
    # ================================================================== #

    @staticmethod
    def is_valid_title(title_text: str) -> bool:
        """Validasi ketat apakah teks layak disebut judul skripsi."""
        if not title_text:
            return False
        
        # 1. Panjang karakter
        if not (20 <= len(title_text) <= 250):
            return False
            
        # 2. Minimal 3 kata
        words = title_text.split()
        if len(words) < 3:
            return False
            
        # 3. Rasio karakter alfabet vs simbol/angka
        alpha_count = sum(c.isalpha() for c in title_text)
        if alpha_count / len(title_text) < 0.5:
            # Jika lebih dari 50% karakternya bukan alfabet (angka/simbol), tolak
            return False
            
        return True

    @staticmethod
    def extract_nim_regex(text: str) -> Optional[str]:
        m = re.search(r'\b\d{6,15}\b', text)
        if m:
            return m.group(0)
        return None

    @staticmethod
    def extract_title_deterministic(text: str) -> Optional[str]:
        """Ekstrak judul dari cover PDF menggunakan Anchor-Based Slicing."""
        if not text:
            return None
            
        # 1. Tangkap Teks Sebelum Anchor
        parts = re.split(r'\bSKRIPSI\b|\bDIAJUKAN\b|\bTUGAS\s+AKHIR\b', text, flags=re.IGNORECASE)
        raw_title = parts[0]
        
        # 2. Runtuhkan Spasi dan Newline (Flattening)
        clean_title = re.sub(r'\s+', ' ', raw_title).strip()
        
        # 3. Hapus Sisa Sampah di Awal (Karakter non-alfabetik)
        clean_title = re.sub(r'^[^a-zA-Z]+', '', clean_title).strip()
        
        if DocumentService.is_valid_title(clean_title):
            return clean_title
        return None

    # ================================================================== #
    #  ALGORITMA GUILLOTINE — PEMBERSIHAN ABSTRAK
    # ================================================================== #

    _GELAR_RE = re.compile(
        r"\b(?:"
        r"S\.?Kom|M\.?Kom|M\.?T|S\.?T|"
        r"M\.?Sc|Ph\.?D|M\.?Si|M\.?M|"
        r"M\.?Pd|M\.?Eng|S\.?Si|S\.?Pd|"
        r"S\.?H|M\.?H|Dr|Prof|Ir|"
        r"S\.?Ag|M\.?Ag"
        r")\b"
        r"[\.\,\s]*",
        re.IGNORECASE,
    )

    _PEMBIMBING_RE = re.compile(
        r"(?:pembimbing|dosen\s+pembimbing)\s*(?:I{1,2}|1|2)?\s*[:\-]?\s*"
        r"[A-Za-z\s\.\,\'\-]+?"
        r"(?:"
        r"(?:S\.?\s*Kom|M\.?\s*Kom|S\.?\s*T|M\.?\s*T|M\.?\s*Sc|Ph\.?\s*D|"
        r"M\.?\s*Si|M\.?\s*M|M\.?\s*Pd|M\.?\s*Eng|S\.?\s*Si|Dr|Prof|Ir)"
        r"[\.\,\s]*"
        r")+",
        re.IGNORECASE,
    )

    _NARRATIVE_STARTERS = re.compile(
        r"(?i)(?:"
        r"latar\s+belakang|"
        r"penelitian\s+ini|"
        r"skripsi\s+ini|"
        r"tugas\s+akhir\s+ini|"
        r"studi\s+ini|"
        r"perkembangan\s+teknologi|"
        r"kemajuan\s+teknologi|"
        r"seiring\s+(?:dengan\s+)?(?:perkembangan|berkembangnya)|"
        r"saat\s+ini|"
        r"dewasa\s+ini|"
        r"pada\s+era|"
        r"di\s+era|"
        r"tujuan\s+dari|"
        r"tujuan\s+penelitian|"
        r"masalah\s+yang|"
        r"permasalahan|"
        r"salah\s+satu|"
        r"dalam\s+(?:era|perkembangan|penelitian|dunia)|"
        r"pemanfaatan|penerapan|pengembangan|penggunaan|"
        r"sistem\s+(?:informasi|ini|yang)|"
        r"teknologi\s+(?:informasi|yang|ini)|"
        r"perancangan|implementasi|analisis|"
        r"aplikasi\s+(?:ini|yang|merupakan)|"
        r"lembaga|pemerintah|masyarakat|"
        r"setiap\s+(?:wanita|orang|manusia)|"
        r"cabai\s+merupakan|"
        r"pertumbuhan\s+(?:tanaman|ekonomi)|"
        r"kebakaran\s+hutan"
        r")",
    )

    @classmethod
    def clean_abstract_text(cls, raw_text: str) -> str:
        if not raw_text or len(raw_text.strip()) < 50:
            cleaned = cls._postclean(cls.sanitize_text(raw_text or ""))
            return cls.split_long_words(cleaned)

        cleaned = raw_text

        abstract_marker = re.search(
            r"(?i)(?:abstrak|abstract)\s*[:\-]?\s*",
            cleaned,
        )
        if abstract_marker:
            after_marker = cleaned[abstract_marker.end():].strip()
            if len(after_marker) >= 80:
                cleaned = after_marker

        MAX_CUT_POS = 3000

        try:
            all_matches = list(cls._GELAR_RE.finditer(cleaned))
            safe_matches = [m for m in all_matches if m.end() <= MAX_CUT_POS]
            if safe_matches:
                last_match = safe_matches[-1]
                cut_pos = last_match.end()
                remainder = cleaned[cut_pos:].strip()
                if len(remainder) >= 80:
                    cleaned = remainder
                    cleaned = cls._postclean(cls.sanitize_text(cleaned))
                    return cls.split_long_words(cleaned)
        except Exception:
            pass

        try:
            pembimbing_matches = list(cls._PEMBIMBING_RE.finditer(cleaned))
            safe_pemb = [m for m in pembimbing_matches if m.end() <= MAX_CUT_POS]
            if safe_pemb:
                last_pemb = safe_pemb[-1]
                cut_pos = last_pemb.end()
                remainder = cleaned[cut_pos:].strip()
                if len(remainder) >= 80:
                    cleaned = remainder
                    cleaned = cls._postclean(cls.sanitize_text(cleaned))
                    return cls.split_long_words(cleaned)
        except Exception:
            pass

        try:
            m = cls._NARRATIVE_STARTERS.search(cleaned)
            if m and m.start() <= MAX_CUT_POS:
                remainder = cleaned[m.start():].strip()
                if len(remainder) >= 80:
                    cleaned = remainder
                    cleaned = cls._postclean(cls.sanitize_text(cleaned))
                    return cls.split_long_words(cleaned)
        except Exception:
            pass

        cleaned = cls._postclean(cls.sanitize_text(cleaned))
        return cls.split_long_words(cleaned)

    @classmethod
    def _postclean(cls, cleaned: str) -> str:
        cleaned = re.sub(r"_{10,}", "", cleaned)
        cleaned = re.sub(
            r"(?i)(?:Nama|Nim|Judul)\s*[:\-]\s*[^\n]{2,80}(?:\n|$)",
            "",
            cleaned,
        )
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    @staticmethod
    def extract_abstract_block(text: str) -> str:
        if not text:
            return ""

        match = re.search(
            r"abstrak[:\s]*"
            r"([\s\S]*?)"
            r"(?=\n\s*(?:kata[\s\-]?kunci|keywords?|pendahuluan|daftar\s+isi|bab\s+|abstract\s*\n|\Z))",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()
        return text.strip()[:5000]

    # ================================================================== #
    #  LOAD DOKUMEN (Dengan Strict Rule-Based Extraction)
    # ================================================================== #

    @staticmethod
    def load_documents_from_files(file_paths: List[str]) -> List[Document]:
        """Load dan process PDF menggunakan ekstraksi murni lokal deterministik."""
        documents = []
        print(f"📁 Memproses {len(file_paths)} file PDF (Strict Rule-Based)...")

        for idx, file_path in enumerate(file_paths, 1):
            file = os.path.basename(file_path)
            try:
                print(f"\n⏳ Memproses [{idx}/{len(file_paths)}]: {file}")

                loader = PyPDFLoader(file_path)
                pages = loader.load()

                if len(pages) < 1:
                    print(f"   ⚠️  FAILED_QUALITY_CHECK: PDF kosong / tidak terbaca.")
                    continue

                cover_text = pages[0].page_content or ""
                # Heuristik pembersihan Spasi OCR
                cover_text = DocumentService.fix_ocr_spaces(cover_text)
                
                body_text = "\n".join(p.page_content for p in pages[1:]) if len(pages) > 1 else ""

                # Ekstraksi Nama File
                file_stem = re.sub(r"(?i)\.pdf$", "", file)
                file_parts = file_stem.split("_")
                
                tahun = None
                nama = ""
                if len(file_parts) >= 2 and re.match(r"^(19|20)\d{2}$", file_parts[0]):
                    tahun = file_parts[0]
                    nama = " ".join(file_parts[1:]).title()

                if not tahun:
                    m = re.search(r"(19|20)\d{2}", file)
                    if m:
                        tahun = m.group(0)

                # Ekstraksi Murni Deterministik
                judul = DocumentService.extract_title_deterministic(cover_text)
                nim = DocumentService.extract_nim_regex(cover_text)

                # Quality Gate 1: Judul Lokal Gagal
                if not judul:
                    print(f"   🚨 FAILED_LOCAL_EXTRACTION: Judul gagal diekstrak atau ditolak oleh is_valid_title(). Dokumen di-SKIPPED.")
                    continue

                # Abstrak Ekstraksi & Quality Gate
                raw_abstract = DocumentService.extract_abstract_block(body_text)
                if len(raw_abstract) < 100:
                    combined = cover_text + "\n\n" + body_text
                    raw_abstract = DocumentService.extract_abstract_block(combined)

                clean_abstract = DocumentService.clean_abstract_text(raw_abstract)

                # Quality Gate 2: Abstrak Pendek
                if len(clean_abstract) < 300:
                    print(f"   ⚠️  FAILED_QUALITY_CHECK: Abstrak terlalu pendek ({len(clean_abstract)} char), dokumen ditolak.")
                    continue

                doc_meta = {
                    "source": file,
                    "judul": judul,
                    "nama": nama,
                    "nim": nim or "",
                    "pembimbing": "",
                    "tahun": tahun or "",
                }

                doc = Document(
                    page_content=f"Judul: {judul}\n\nAbstrak:\n{clean_abstract}",
                    metadata=doc_meta,
                )
                documents.append(doc)
                print(f"   ✅ SUCCESS: '{judul[:60]}...'")
                print(f"       abstrak={len(clean_abstract)} char")

            except Exception as e:
                print(f"   ❌ Error internal saat memproses {file}: {str(e)}")
                continue

        return documents
