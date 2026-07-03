import re
from langchain_community.document_loaders import PyMuPDFLoader

file_path = "data/pdf/2016_RIFALDY_RAMADHAN_L.pdf"
loader = PyMuPDFLoader(file_path)
pages = loader.load()
raw_text = pages[0].page_content

print("=== RAW TEXT ===")
print(repr(raw_text))

print("\n=== HASIL EKSTRAKSI LOGIKA BARU ===")
# Simulasi Anchor-Based Slicing
raw_title = re.split(r'\bSKRIPSI\b|\bDIAJUKAN\b', raw_text, flags=re.IGNORECASE)[0]
# Runtuhkan spasi dan newline
clean_title = re.sub(r'\s+', ' ', raw_title).strip()
# Hapus sisa karakter non-alfabet di awal jika ada
clean_title = re.sub(r'^[^a-zA-Z]+', '', clean_title) 

print(f"Judul Terekstrak : '{clean_title}'")
print(f"Jumlah Karakter  : {len(clean_title)}")