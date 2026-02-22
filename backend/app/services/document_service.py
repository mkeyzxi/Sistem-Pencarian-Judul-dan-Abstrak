"""
Document Service
Menangani loading, preprocessing, dan ekstraksi konten dari PDF.
"""

import os
import re
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from app.core.config import settings


class DocumentService:
    """Service untuk menangani dokumen PDF."""
    
    @staticmethod
    def extract_title(lines: list) -> str:
        """
        Ekstrak judul dari halaman sampul.
        
        Args:
            lines: List baris dari teks sampul
            
        Returns:
            String judul yang sudah dibersihkan
        """
        title_lines = []
        stop_words = [
            "skripsi", "diajukan", "oleh", "nama", "nim",
            "program studi", "fakultas", "universitas", "makassar"
        ]
        
        for line in lines:
            low = line.lower()
            
            # Stop jika menemukan stop words
            if any(sw in low for sw in stop_words):
                break
            
            # Tambah line jika memiliki isi
            if len(line.strip()) > 3:
                title_lines.append(line.strip())
            
            # Batasi panjang judul
            if len(" ".join(title_lines)) > 150:
                break
        
        return " ".join(title_lines)
    
    @staticmethod
    def extract_identity(text: str) -> str:
        """
        Ekstrak nama dan NIM dari teks.
        
        Args:
            text: Teks yang mengandung data identitas
            
        Returns:
            String identitas (Nama: X | NIM: Y)
        """
        nama = re.search(r"nama\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
        nim = re.search(r"nim\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
        
        result = []
        if nama:
            result.append(f"Nama: {nama.group(1).strip()}")
        if nim:
            result.append(f"NIM: {nim.group(1).strip()}")
        
        return " | ".join(result)
    
    @staticmethod
    def extract_abstract(text: str) -> str:
        """
        Ekstrak abstrak dari teks.
        
        Args:
            text: Teks yang mengandung abstrak
            
        Returns:
            String abstrak
        """
        # Cari bagian abstrak
        match = re.search(
            r"abstrak(.*?)(?:pendahuluan|kata kunci|daftar|bab|$)",
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if match:
            return match.group(1).strip()
        return ""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Bersihkan teks dari noise dan karakter tidak perlu.
        
        Args:
            text: Teks yang akan dibersihkan
            
        Returns:
            Teks yang sudah dibersihkan
        """
        noise = [
            "sampul skripsi",
            "diajukan untuk memenuhi",
            "program studi",
            "fakultas",
            "universitas",
            "teknik informatika",
            "uin alauddin makassar",
        ]
        
        for n in noise:
            text = re.sub(n, "", text, flags=re.IGNORECASE)
        
        # Hapus multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    @staticmethod
    def load_documents_from_folder(folder_path: str) -> list:
        """
        Load dan process semua PDF dari folder.
        
        Args:
            folder_path: Path ke folder yang berisi PDF
            
        Returns:
            List of Document objects yang sudah diproses
        """
        documents = []
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder tidak ditemukan: {folder_path}")
            return documents
        
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
        print(f"📁 Ditemukan {len(pdf_files)} file PDF")
        
        for idx, file in enumerate(pdf_files, 1):
            try:
                file_path = os.path.join(folder_path, file)
                print(f"\n⏳ Memproses [{idx}/{len(pdf_files)}]: {file}")
                
                # Load PDF
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                
                if len(pages) < 2:
                    print(f"   ⚠️  PDF terlalu pendek, di-skip")
                    continue
                
                # Extract konten dari halaman
                cover_text = pages[0].page_content
                body_text = "\n".join(p.page_content for p in pages[1:])
                
                # Parse informasi
                lines = [l.strip() for l in cover_text.split("\n") if len(l.strip()) > 2]
                
                title = DocumentService.extract_title(lines)
                identity = DocumentService.extract_identity(cover_text)
                abstract = DocumentService.extract_abstract(body_text)
                
                # Validasi
                if len(abstract) < 100:
                    print(f"   ⚠️  Abstrak terlalu pendek, di-skip")
                    continue
                
                # Clean text
                title = DocumentService.clean_text(title)
                abstract = DocumentService.clean_text(abstract)
                
                # Buat content
                content = f"""Judul: {title}
{identity}

Abstrak:
{abstract}""".strip()
                
                # Tambah dokumen
                doc = Document(
                    page_content=content,
                    metadata={"source": file, "title": title}
                )
                documents.append(doc)
                print(f"   ✅ Berhasil di-proses")
                
            except Exception as e:
                print(f"   ❌ Error memproses {file}: {str(e)}")
                continue
        
        print(f"\n✨ Total dokumen siap embedding: {len(documents)}")
        return documents
