# PROMPT PERBAIKAN BACKEND: REGEX WORD BOUNDARY & LLM RESPONSE FORMAT

Bertindaklah sebagai Senior Python Engineer. Terjadi dua anomali kritis pada sistem RAG Skripsi saya:

1. Response Chat LLM bocor menampilkan JSON mentah ke UI.
2. Fungsi Guillotine abstrak memotong kata di tengah-tengah secara brutal (contoh: "Android" terpotong menjadi "oid"). Ini terjadi karena regex gelar akademik seperti `Dr\.?` menangkap string "dr" di dalam kata "Android" akibat ketiadaan Word Boundary (`\b`).

Lakukan perbaikan pada 2 file berikut HANYA pada bagian yang diinstruksikan:

### 1. Perbaiki `app/services/suggestion_service.py` (Hapus Output JSON)

- Buka metode `generate_chat_response()`.
- HAPUS seluruh instruksi yang meminta LLM membuat output JSON "card-ready".
- Ganti prompt-nya persis menjadi seperti ini:
  "Anda adalah asisten akademik. User mencari topik: '{query}'. Sistem telah menemukan dokumen relevan di bawah ini: {docs_text}.
  TUGAS ANDA: Berikan narasi pengantar 1 hingga 2 paragraf menggunakan format Markdown biasa. DILARANG KERAS merespons menggunakan JSON, format array, atau membuat tabel. Jangan me-listing ulang judul-judul dokumen tersebut karena sistem UI frontend sudah menampilkannya secara otomatis dalam bentuk kartu. Cukup berikan narasi pengantar yang ramah dan tarik kesimpulan umum dari dokumen-dokumen yang ditemukan."

### 2. Perbaiki `app/services/document_service.py` (Regex Boundary & Limitasi Area Potong)

- Di definisi `_GELAR_RE`, Anda WAJIB menambahkan Word Boundary `\b` di awal dan di akhir kelompok gelar, serta mengatur agar case-insensitive-nya lebih aman. Ubah menjadi pola yang tidak merusak kata di tengah. Gunakan pola boundary eksplisit: `r"\b(?:S\.?Kom|M\.?Kom|M\.?T|S\.?T|M\.?Sc|Ph\.?D|M\.?Si|M\.?M|M\.?Pd|M\.?Eng|S\.?Si|S\.?Pd|S\.?H|M\.?H|Dr|Prof|Ir|S\.?Ag|M\.?Ag)\b[\.\,\s]*"`
- Di metode `clean_abstract_text()`, BATASI area pencarian regex untuk Strategi Guillotine dan Narrative Anchor HANYA pada `raw_text[:800]` (800 karakter pertama).
- Logikanya: Lakukan `finditer` atau `search` HANYA pada string 800 karakter awal tersebut. Hal ini mencegah algoritma memotong teks jika kata pemicu (seperti gelar atau kata "Penelitian ini") ternyata disebut oleh mahasiswa di tengah-tengah atau akhir esai aslinya. Jika `cut_pos` ditemukan di dalam 800 karakter awal, lakukan pemotongan pada `raw_text` aslinya.

Berikan saya revisi kode untuk `suggestion_service.py` (metode `generate_chat_response` saja) dan `document_service.py` (regex GELAR_RE dan metode `clean_abstract_text` saja).
