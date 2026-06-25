"""
Document Service
Menangani loading, preprocessing, dan ekstraksi konten dari PDF.

REVISI 3 — Metadata Rescue & Explicit Abstract Slicing:
- BARU: Dynamic Metadata Rescue (selamatkan judul/nim/nama dari raw_abstract)
- BARU: Explicit Abstract Slicing (potong tegas di kata "Abstrak:")
- Strategi 1: Academic Title Guillotine (potong berdasarkan gelar terakhir)
- Strategi 2: Pembimbing Anchor (potong berdasarkan kata Pembimbing)
- Strategi 3: Narrative Anchor (potong berdasarkan awal paragraf esai)
- Sanitasi karakter terakhir
"""

import os
import re
from typing import Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from app.core.config import settings


class DocumentService:
    """Service untuk menangani dokumen PDF dan menyiapkan dokumen untuk embedding."""

    # ================================================================== #
    #  UTILITAS
    # ================================================================== #

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitasi karakter pada teks setelah pemotongan Guillotine.

        1. \\n tunggal → spasi
        2. \\n\\n ganda → pertahankan sebagai paragraf baru
        3. Spasi ganda → satu spasi
        """
        if not text:
            return ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Simpan paragraph break (\\n\\n) sementara
        text = text.replace("\n\n", "<<PARA>>")
        # Single newline → spasi
        text = text.replace("\n", " ")
        # Kembalikan paragraph break
        text = text.replace("<<PARA>>", "\n\n")
        # Hapus spasi ganda
        text = re.sub(r"[ \t]{2,}", " ", text)
        # Hapus spasi di awal/akhir setiap baris
        lines = [l.strip() for l in text.split("\n")]
        text = "\n".join(lines)
        # Kurangi newline >2 menjadi 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    # ================================================================== #
    #  EKSTRAKSI JUDUL
    # ================================================================== #

    @staticmethod
    def extract_title(lines: list) -> str:
        """Ekstrak judul dari baris-baris cover page."""
        title_lines = []
        stop_words = [
            "skripsi", "diajukan", "oleh", "nama", "nim",
            "program studi", "fakultas", "universitas"
        ]

        for line in lines:
            low = line.lower().strip()
            if any(sw in low for sw in stop_words):
                break
            if len(line.strip()) > 3:
                title_lines.append(line.strip())
            if len(" ".join(title_lines)) > 200:
                break

        return " ".join(title_lines).strip()

    # ================================================================== #
    #  EKSTRAKSI METADATA (FAULT-TOLERANT)
    # ================================================================== #

    @staticmethod
    def extract_metadata(text: str) -> dict:
        """Ekstrak metadata dari cover/halaman awal.

        Fault-tolerant: jika tidak ditemukan → None / string kosong.
        Mengembalikan dict: judul, nama, nim, pembimbing, tahun
        """
        meta = {
            "judul": None,
            "nama": None,
            "nim": None,
            "pembimbing": None,
            "tahun": None,
        }

        # --- NAMA ---
        m = re.search(
            r"(?:nama\s*(?:penulis|mahasiswa)?\s*[:\-]\s*|oleh\s*[:\-]?\s*)(.+)",
            text,
            re.IGNORECASE,
        )
        if m:
            nama = m.group(1).strip()
            # Stop di NIM, Jurusan, atau digit panjang
            nama = re.split(r"(?i)\s*(?:NIM|Jurusan|Program|Fakultas)\s*[:\-]", nama)[0]
            nama = re.sub(r"[\.\,\;\:]+$", "", nama).strip()
            if len(nama) > 2:
                meta["nama"] = nama

        # --- NIM ---
        m = re.search(r"nim\s*[:\-]?\s*(\d{6,20})", text, re.IGNORECASE)
        if m:
            meta["nim"] = m.group(1).strip()

        # --- PEMBIMBING ---
        pemb_parts = []
        # Cari semua pembimbing (I dan II)
        for pattern in [
            r"pembimbing\s*(?:I|1|pertama)\s*[:\-]\s*(.+?)(?=\s*(?:pembimbing|$))",
            r"pembimbing\s*(?:II|2|kedua)\s*[:\-]\s*(.+?)(?=\s*(?:pembimbing|$|\n))",
        ]:
            m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if m:
                p = m.group(1).strip()
                p = re.sub(r"[\n\r]+", " ", p)
                p = re.sub(r"\s{2,}", " ", p)
                p = re.sub(r"[\.\,\;\:]+$", "", p).strip()
                if len(p) > 2:
                    pemb_parts.append(p)

        # Fallback: cari "Pembimbing :" tanpa nomor
        if not pemb_parts:
            m = re.search(
                r"pembimbing\s*[:\-]\s*(.+)",
                text,
                re.IGNORECASE,
            )
            if m:
                p = re.sub(r"[\.\,\;\:]+$", "", m.group(1).strip()).strip()
                if len(p) > 2:
                    pemb_parts.append(p)

        if pemb_parts:
            meta["pembimbing"] = " dan ".join(pemb_parts)

        # --- TAHUN ---
        m = re.search(r"\b(19|20)\d{2}\b", text)
        if m:
            meta["tahun"] = m.group(0)

        return meta

    # ================================================================== #
    #  ALGORITMA GUILLOTINE — PEMBERSIHAN ABSTRAK
    # ================================================================== #

    # Gelar akademik khas Indonesia — dengan Word Boundary agar tidak
    # memotong kata di tengah (contoh: "Android" tidak lagi match "Dr")
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

    # Pola Pembimbing Anchor
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

    # Kata-kata pembuka esai abstrak yang umum
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
        """Membersihkan raw text abstrak menggunakan strategi bertingkat.

        PRE-STEP: Explicit Abstract Slicing — potong tegas di "Abstrak:" / "Abstract:"
        Strategi 1: Academic Title Guillotine — cari gelar terakhir, potong setelahnya.
        Strategi 2: Pembimbing Anchor — cari kata Pembimbing, potong setelahnya.
        Strategi 3: Narrative Anchor — cari kata pembuka esai, potong dari situ.

        Returns:
            String abstrak bersih, atau raw_text yang sudah di-sanitasi jika semua gagal.
        """
        if not raw_text or len(raw_text.strip()) < 50:
            return cls.sanitize_text(raw_text or "")

        cleaned = raw_text

        # ══════════════════════════════════════════════════════════════ #
        # PRE-STEP: EXPLICIT ABSTRACT SLICING
        # Jika teks mengandung "Abstrak:" atau "Abstract:", potong TEGAS.
        # Buang semua teks sebelumnya (termasuk kata "Abstrak" itu sendiri).
        # Ini mengeliminasi "Judul: ... NIM: ..." yang menempel di awal.
        # ══════════════════════════════════════════════════════════════ #
        abstract_marker = re.search(
            r"(?i)(?:abstrak|abstract)\s*[:\-]?\s*",
            cleaned,
        )
        if abstract_marker:
            after_marker = cleaned[abstract_marker.end():].strip()
            # Hanya gunakan jika masih ada teks substansial setelahnya
            if len(after_marker) >= 80:
                cleaned = after_marker

        # ══════════════════════════════════════════════════════════════ #
        # AREA PENCARIAN: Seluruh panjang string `cleaned`.
        # Regex mencari di seluruh teks, tetapi pemotongan hanya
        # dieksekusi jika cut_pos <= 3000 karakter dari awal
        # (safety guard agar tidak memotong di tengah esai).
        # ══════════════════════════════════════════════════════════════ #
        MAX_CUT_POS = 3000

        # ── STRATEGI 1: Academic Title Guillotine ──
        # Cari SEMUA kemunculan gelar di seluruh cleaned, ambil yang paling belakang
        # yang masih dalam batas MAX_CUT_POS
        try:
            all_matches = list(cls._GELAR_RE.finditer(cleaned))
            # Filter hanya match yang berada dalam batas aman
            safe_matches = [m for m in all_matches if m.end() <= MAX_CUT_POS]
            if safe_matches:
                last_match = safe_matches[-1]
                cut_pos = last_match.end()

                remainder = cleaned[cut_pos:].strip()
                if len(remainder) >= 80:
                    cleaned = remainder
                    return cls._postclean(cls.sanitize_text(cleaned))
        except Exception:
            pass

        # ── STRATEGI 2: Pembimbing Anchor ──
        try:
            pembimbing_matches = list(cls._PEMBIMBING_RE.finditer(cleaned))
            safe_pemb = [m for m in pembimbing_matches if m.end() <= MAX_CUT_POS]
            if safe_pemb:
                last_pemb = safe_pemb[-1]
                cut_pos = last_pemb.end()
                remainder = cleaned[cut_pos:].strip()
                if len(remainder) >= 80:
                    cleaned = remainder
                    return cls._postclean(cls.sanitize_text(cleaned))
        except Exception:
            pass

        # ── STRATEGI 3: Narrative Anchor ──
        try:
            m = cls._NARRATIVE_STARTERS.search(cleaned)
            if m and m.start() <= MAX_CUT_POS:
                remainder = cleaned[m.start():].strip()
                if len(remainder) >= 80:
                    cleaned = remainder
                    return cls._postclean(cls.sanitize_text(cleaned))
        except Exception:
            pass

        # ── FALLBACK: sanitasi saja tanpa pemotongan ──
        return cls._postclean(cls.sanitize_text(cleaned))

    # ================================================================== #
    #  POST-CLEAN: Hardcoded Cleanup
    # ================================================================== #

    @classmethod
    def _postclean(cls, cleaned: str) -> str:
        """Pembersihan hardcode untuk sisa-sisa metadata yang lolos.

        1. Hapus garis underscore panjang (________)
        2. Hapus pengulangan pola "Nama : ... Nim : ... Judul : ..."
        """
        # Hapus garis underscore panjang (10+ karakter)
        cleaned = re.sub(r"_{10,}", "", cleaned)

        # Hapus pola metadata sisa: "Nama : ... Nim : ... Judul : ..."
        cleaned = re.sub(
            r"(?i)(?:Nama|Nim|Judul)\s*[:\-]\s*[^\n]{2,80}(?:\n|$)",
            "",
            cleaned,
        )

        # Bersihkan spasi/newline berlebih setelah penghapusan
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    # ================================================================== #
    #  EKSTRAKSI ABSTRAK (WRAPPER)
    # ================================================================== #

    @staticmethod
    def extract_abstract_block(text: str) -> str:
        """Ekstrak blok kasar setelah header 'ABSTRAK' sampai header berikutnya."""
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
        else:
            # Fallback: ambil awal dokumen (maks 5000 char)
            return text.strip()[:5000]

    # ================================================================== #
    #  LOAD DOKUMEN DARI FOLDER
    # ================================================================== #

    @staticmethod
    def load_documents_from_folder(folder_path: str) -> list:
        """Load dan process semua PDF dari folder.

        Mengembalikan list Document siap embedding.
        - page_content: MURNI teks esai abstrak (tanpa Nama/NIM/Pembimbing)
        - metadata: {source, judul, nama, nim, pembimbing, tahun}
        """
        documents = []

        if not os.path.exists(folder_path):
            print(f"❌ Folder tidak ditemukan: {folder_path}")
            return documents

        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
        print(f"📁 Ditemukan {len(pdf_files)} file PDF")

        for idx, file in enumerate(pdf_files, 1):
            try:
                file_path = os.path.join(folder_path, file)
                print(f"\n⏳ Memproses [{idx}/{len(pdf_files)}]: {file}")

                loader = PyPDFLoader(file_path)
                pages = loader.load()

                if len(pages) < 1:
                    print(f"   ⚠️  PDF kosong / tidak bisa dibaca, di-skip")
                    continue

                cover_text = pages[0].page_content or ""
                body_text = "\n".join(p.page_content for p in pages[1:]) if len(pages) > 1 else ""

                # ── Extract metadata dari cover (prioritas) dan fallback ke body ──
                metadata = DocumentService.extract_metadata(cover_text)
                if not any(metadata.values()) and body_text:
                    metadata = DocumentService.extract_metadata(body_text[:3000])

                # Extract title heuristically dari cover
                lines = [l.strip() for l in cover_text.split("\n") if len(l.strip()) > 2]
                judul = DocumentService.extract_title(lines) or metadata.get("judul") or ""
                metadata["judul"] = judul

                # ── Extract abstract block ──
                raw_abstract = DocumentService.extract_abstract_block(body_text)

                # Jika abstrak terlalu pendek, coba dari combined
                if len(raw_abstract) < 100:
                    combined = cover_text + "\n\n" + body_text
                    raw_abstract = DocumentService.extract_abstract_block(combined)

                # ════════════════════════════════════════════════════ #
                # DYNAMIC METADATA RESCUE
                # Jika metadata dari cover kosong, coba selamatkan
                # dari raw_abstract sebelum teks di-guillotine.
                # ════════════════════════════════════════════════════ #
                if not metadata.get("judul"):
                    m = re.search(
                        r"(?i)Judul\s*[:\-]?\s*(.+?)(?=\n|NIM|Nama|Abstrak|Pembimbing)",
                        raw_abstract,
                    )
                    if m:
                        metadata["judul"] = m.group(1).strip()
                        print(f"   🔧 Metadata Rescue — judul: '{metadata['judul'][:50]}'")

                if not metadata.get("nim"):
                    m = re.search(
                        r"(?i)NIM\s*[:\-]?\s*(\d{6,15})",
                        raw_abstract,
                    )
                    if m:
                        metadata["nim"] = m.group(1).strip()
                        print(f"   🔧 Metadata Rescue — nim: {metadata['nim']}")

                if not metadata.get("nama"):
                    m = re.search(
                        r"(?i)Nama\s*[:\-]?\s*([A-Za-z\s\.\,]+?)(?=\n|NIM|Judul|Abstrak|Pembimbing)",
                        raw_abstract,
                    )
                    if m:
                        rescued_name = m.group(1).strip()
                        rescued_name = re.sub(r"[\.,;:]+$", "", rescued_name).strip()
                        if len(rescued_name) > 2:
                            metadata["nama"] = rescued_name
                            print(f"   🔧 Metadata Rescue — nama: '{metadata['nama']}'")

                # ── GUILLOTINE + ABSTRACT SLICING: Bersihkan metadata ──
                clean_abstract = DocumentService.clean_abstract_text(raw_abstract)

                if len(clean_abstract) < 80:
                    print(f"   ⚠️  Abstrak terlalu pendek ({len(clean_abstract)}), di-skip")
                    continue

                # ── Susun metadata final ──
                # PRIORITAS: Ekstrak tahun & nama dari NAMA FILE PDF
                # Format standar: TAHUN_NAMA_PENULIS.pdf (contoh: 2023_RINI_AMALIAH.pdf)
                file_stem = re.sub(r"(?i)\.pdf$", "", file)  # Buang ekstensi
                file_parts = file_stem.split("_")

                if len(file_parts) >= 2 and re.match(r"^(19|20)\d{2}$", file_parts[0]):
                    # Format standar terdeteksi → ambil dari nama file
                    tahun_from_file = file_parts[0]
                    nama_from_file = " ".join(file_parts[1:]).title()
                    print(f"   📂 Filename Parse — tahun: {tahun_from_file}, nama: '{nama_from_file}'")
                else:
                    # Fallback: nama file tidak standar → gunakan regex lama
                    tahun_from_file = None
                    nama_from_file = None

                tahun = tahun_from_file or metadata.get("tahun") or ""
                if not tahun:
                    m = re.search(r"(19|20)\d{2}", file)
                    if m:
                        tahun = m.group(0)

                nama = nama_from_file or metadata.get("nama") or ""

                doc_meta = {
                    "source": file,
                    "judul": metadata.get("judul") or "",
                    "nama": nama,
                    "nim": metadata.get("nim") or "",
                    "pembimbing": metadata.get("pembimbing") or "",
                    "tahun": tahun,
                }

                doc = Document(
                    page_content=clean_abstract,
                    metadata=doc_meta,
                )
                documents.append(doc)
                print(f"   ✅ Berhasil: judul='{doc_meta['judul'][:60]}'")
                print(f"       abstrak={len(clean_abstract)} char, nama={doc_meta['nama'][:30]}")

            except Exception as e:
                print(f"   ❌ Error memproses {file}: {str(e)}")
                continue

        print(f"\n✨ Total dokumen siap embedding: {len(documents)}")
        return documents
