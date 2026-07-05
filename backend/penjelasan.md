# Penjelasan Keselarasan `run_evaluation.py` dengan Sistem Utama

Berdasarkan analisis menyeluruh terhadap file `backend/scripts/run_evaluation.py` dan perbandingannya dengan sistem utama (terutama `backend/app/services/rag_service.py` dan `backend/app/core/config.py`), saya dapat memastikan bahwa **script evaluasi sudah SEPENUHNYA selaras dengan sistem utama RAG Anda**.

Berikut adalah detail poin-poin keselarasan yang telah terintegrasi dengan baik:

### 1. Sinkronisasi Model LLM & Konfigurasi (Dynamic Settings)
Pada versi yang sebelumnya, nama model LLM di-hardcode sebagai `"llama3-8b-8192"` di bagian metadata evaluasi. Namun, pada blok kode evaluasi terbaru yang aktif (baris 926), skrip evaluasi sudah menggunakan `settings.GROQ_MODEL`. Artinya, jika Anda mengganti model di `.env` atau `config.py`, script evaluasi akan langsung mendeteksinya. 
Selain itu, berhubung Anda baru saja menaikkan nilai `LLM_MAX_TOKENS = 512` di `config.py`, evaluasi HyDE selanjutnya tidak akan lagi mengalami pemotongan teks abstrak di tengah jalan.

### 2. Integrasi *Evaluation Mode* (`is_eval = True`)
Di dalam `run_evaluation.py`, fungsi `run_standard_rag` dan `run_hyde` memanggil *service* RAG dengan argumen `is_eval=True`.
```python
rag_response = service.standard_rag(query_text, k=top_k, is_eval=True)
hyde_response = service.hyde_rag(query_text, k=top_k, is_eval=True, prompt_type=prompt_type)
```
Ini sangat selaras dengan logika `RAGService` di `rag_service.py` (REVISI FINAL) yang mana argumen `is_eval` akan secara otomatis:
- Mematikan fitur diversifikasi MMR (Maximal Marginal Relevance) agar output murni diurutkan berdasarkan relevansi (distance absolut).
- Mengatur minimum `similarity_score` threshold ke `0.0`, sehingga dokumen yang sedikit kurang relevan tidak akan langsung di-drop sebelum dievaluasi posisinya.

### 3. Dukungan Dua Varian Prompt HyDE
Sistem utama di `rag_service.py` kini menerima parameter opsional `prompt_type`. Skrip evaluasi telah beradaptasi untuk menjalankan kedua *prompt* sekaligus demi keperluan A/B Testing:
- `HyDE (Prompt 1)` akan dieksekusi dengan `prompt_type="prompt1"`
- `HyDE (Prompt 2)` akan dieksekusi dengan `prompt_type="prompt2"`
Keduanya lalu dibandingkan dalam hasil `Hit Rate@K` dan `MRR` (Mean Reciprocal Rank) di JSON dan konsole terminal.

### 4. Format Output *Score* yang Konsisten
Di dalam `RAGService`, fungsi `_distance_to_score` melakukan konversi dari metrik jarak Chroma (seperti Cosine Distance 0.0 - 2.0) menjadi persentase skor relevansi 0 - 100. Skrip evaluasi tidak mencoba menghitung ulang jarak ini. Ia secara langsung mengambil metrik final `meta.get("similarity_score")` yang diberikan oleh sistem utama. Hal ini menjamin bahwa angka yang tampil saat evaluasi sama persis dengan angka yang akan dilihat oleh pengguna di antarmuka frontend (atau API endpoint).

### 5. Kompatibilitas Model E5
*Embedding model* yang Anda gunakan (`intfloat/multilingual-e5-small`) mewajibkan adanya awalan `"query: "` untuk teks yang akan dicari. Karena skrip evaluasi menggunakan *instance* `get_rag_service()`, kewajiban menyisipkan prefix `"query: "` ini sepenuhnya ditangani oleh `rag_service.py`, sehingga pengujian bebas dari bug bias model *embedding*.

### Kesimpulan
Script `run_evaluation.py` siap digunakan. Anda tidak perlu memodifikasinya lebih lanjut sebelum menjalankannya, karena skrip tersebut sudah terikat dengan kuat (tightly coupled secara fungsional) dan patuh pada aturan-aturan yang ada di struktur utama (core) dari FastAPI RAG yang telah direvisi.
