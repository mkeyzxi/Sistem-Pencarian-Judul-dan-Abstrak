# Laporan Analisis Evaluasi Performa Sistem Pencarian Skripsi: Standard RAG vs. HyDE

Dokumen ini menyajikan analisis mendalam dan komprehensif terhadap hasil evaluasi sistem pencarian judul dan abstrak skripsi berdasarkan file dataset evaluasi `hasil_dengan_skor_relevansi (5).json`. 

Evaluasi dilakukan pada **50 query uji** (total 500 observasi dokumen retrieved Top-5) untuk membandingkan efektivitas metode **Standard RAG** dengan **HyDE (Hypothetical Document Embeddings)**, yang dinilai berdasarkan metrik standar *Information Retrieval*: **Mean Reciprocal Rank (MRR)**, **Precision@5**, **Recall@5**, **F1-Score@5**, dan **Hit Rate@5**.

---

## 1. Ringkasan Eksekutif & Metrik Keseluruhan

Secara umum, penerapan metode **HyDE terbukti unggul secara signifikan** dibandingkan Standard RAG dalam keseluruhan observasi. HyDE berhasil mereduksi *vocabulary mismatch* dan membatasi dampak salah ketik (*typo*), sehingga mampu meningkatkan akurasi temuan dokumen relevan pada Top-5 sebesar **+17.81% pada Precision@5** dan meningkatkan **MRR dari 0.7263 menjadi 0.7703**.

### Tabel Perbandingan Metrik Keseluruhan (N=50 Query, Top-K=5)

| Metrik Evaluasi | Standard RAG | HyDE | Selisih / Peningkatan | Interpretasi Kinerja |
| :--- | :---: | :---: | :---: | :--- |
| **Mean Reciprocal Rank (MRR)** | 0.7263 | **0.7703** | **+6.06%** ($\uparrow$) | HyDE menempatkan dokumen relevan pertama di urutan yang lebih tinggi (rata-rata di peringkat 1 atau 2). |
| **Precision@5** | 0.2920 | **0.3440** | **+17.81%** ($\uparrow$) | HyDE mengembalikan lebih banyak dokumen relevan dalam 5 teratas (rata-rata 1.72 vs 1.46 dokumen relevan/query). |
| **Recall@5 (Pooling)** | 0.8121 | **0.8526** | **+4.99%** ($\uparrow$) | HyDE mencakup lebih banyak proporsi dokumen relevan yang tersedia dari kumpulan kandidat (*pool*). |
| **F1-Score@5** | 0.4295 | **0.4902** | **+14.13%** ($\uparrow$) | Keseimbangan presisi dan recall HyDE jauh lebih optimal. |
| **Hit Rate@5** | 88.00% (44/50) | **94.00% (47/50)** | **+6.82%** ($\uparrow$) | HyDE berhasil menemukan setidaknya 1 dokumen relevan pada 47 query, sedangkan RAG gagal pada 6 query. |

---

## 2. Analisis Keandalan Data (Inter-Rater Agreement)

Penilaian relevansi dokumen dilakukan oleh tiga rater/evaluator: dua mahasiswa (`mhs1`, `mhs2`) dan satu dosen (`dsn3`). Analisis reliabilitas kesepakatan menunjukkan hasil yang sangat istimewa:
* **Tingkat Kesepakatan Bulat (Unanimous Agreement / 3 dari 3 Sepakat):** **100.00%** (499 dari 499 observasi valid).
* **Pairwise Agreement (mhs1-mhs2, mhs1-dsn3, mhs2-dsn3):** **100.00%**.
* **Fleiss' Kappa Score:** **1.00** (*Perfect Agreement*).
* **Distribusi Label:** Dari 500 hasil ekstraksi Top-5 (250 observasi RAG + 250 observasi HyDE), terdapat **159 label Relevan (1)** dan **340 label Tidak Relevan (0)** (serta 1 observasi berstatus `null` yang merupakan entri kosong non-relevan).

> [!NOTE]
> Kesepakatan mutlak (100%) antar ketiga evaluator membuktikan bahwa definisi relevansi yang digunakan sangat konsisten dan tidak ambigu. Hal ini menjamin bahwa perbedaan performa antara RAG dan HyDE yang dihitung adalah murni karena perbedaan kapabilitas teknis arsitektur pencarian, bukan karena bias pandangan subyektif annotator.

---

## 3. Evaluasi Kinerja Berdasarkan Tipe Studi Kasus (Kategori Query)

Kelima puluh query uji dibagi ke dalam **5 kategori skenario studi kasus** (masing-masing 10 query). Perbedaan karakteristik kueri menghasilkan dinamika performa yang kontras antara kedua metode.

```
+------------------------------------+--------------------------------+---------------------------------+
| Tipe Studi Kasus (N=10/tipe)       | Standard RAG (MRR / P@5 / Hit) | HyDE (MRR / P@5 / Hit)          |
+------------------------------------+--------------------------------+---------------------------------+
| 1. Bahasa Kasual (Vocab Mismatch)  | 0.5067 / 0.2600 / 80.0%       | 0.6783 / 0.5400 / 100%   (WIN)  |
| 2. Konseptual / Sinonim            | 0.6083 / 0.2600 / 80.0%       | 0.6333 / 0.3200 / 80.0%  (WIN)  |
| 3. Berbasis Masalah (Implicit)     | 0.7500 / 0.3800 / 90.0% (WIN)  | 0.7400 / 0.3200 / 100%   (TIE)  |
| 4. Leksikal Spesifik (Exact Match) | 1.0000 / 0.3000 / 100%  (WIN)  | 0.8500 / 0.2400 / 90.0%         |
| 5. Tipografi (Typo / Noisy)        | 0.7667 / 0.2600 / 90.0%       | 0.9500 / 0.3000 / 100%   (WIN)  |
+------------------------------------+--------------------------------+---------------------------------+
```

### Tabel Detail Metrik per Tipe Studi Kasus

| Tipe Studi Kasus | Metode | MRR | Precision@5 | Recall@5 | F1-Score@5 | Hit Rate@5 | Analisa Perbandingan |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Kueri Bahasa Kasual** *(Vocabulary Mismatch)* | Standard RAG<br>**HyDE** | 0.5067<br>**0.6783** | 0.2600<br>**0.5400** | 0.5821<br>**0.9464** | 0.3595<br>**0.6877** | 80.0%<br>**100%** | **HyDE Menang Telak (+107.7% Precision & Hit Rate 100%):** Bahasa awam ("program hape", "bikin web", "foto daun", "apk tebak sakit di hape") tidak cocok dengan kosa kata formal abstrak skripsi ("sistem mobile", "berbasis web", "citra daun", "diagnosis penyakit / mobile health"). HyDE berhasil menerjemahkan intensi kasual ke bahasa ilmiah. |
| **2. Kueri Konseptual / Sinonim** *(Semantic Gap)* | Standard RAG<br>**HyDE** | 0.6083<br>**0.6333** | 0.2600<br>**0.3200** | 0.7833<br>**0.7833** | 0.3904<br>**0.4544** | 80.0%<br>**80.0%** | **HyDE Unggul:** Istilah akademis konseptual tanpa kata kunci harfiah (mis. *"pengawasan derajat keasaman akuakultur"*) mampu diperluas oleh HyDE menjadi representasi vektor yang tepat (monitoring pH kolam/akuarium). |
| **3. Kueri Berbasis Masalah** *(Implicit Intent)* | **Standard RAG**<br>HyDE | **0.7500**<br>0.7400 | **0.3800**<br>0.3200 | **0.8200**<br>0.6833 | **0.5193**<br>0.4359 | 90.0%<br>**100%** | **Standard RAG Unggul pada Presisi, HyDE pada Coverage:** Kata kunci masalah (mis. *"amonia tinggi"*, *"telur busuk"*) umumnya sudah tertulis secara harfiah di latar belakang abstrak. Saat HyDE mencoba menebak solusi/metodenya, terkadang terjadi halusinasi yang menggeser fokus semantik dari masalah aslinya. |
| **4. Kueri Leksikal Spesifik** *(Exact Match)* | **Standard RAG**<br>HyDE | **1.0000**<br>0.8500 | **0.3000**<br>0.2400 | **0.9750**<br>0.8500 | **0.4588**<br>0.3743 | **100%**<br>90.0% | **Standard RAG Menang Sempurna (MRR 1.00):** Ketika query sudah sangat akademis dan presisi (mis. *"Fuzzy Mamdani berbasis IoT"* atau *"Arduino dan Firebase Android"*), penambahan teks naratif oleh LLM (HyDE) justru menambah *noise* dan melunakkan bobot kata kunci teknis tersebut. |
| **5. Kueri Tipografi** *(Typo / Noisy Query)* | Standard RAG<br>**HyDE** | 0.7667<br>**0.9500** | 0.2600<br>**0.3000** | 0.9000<br>**1.0000** | 0.4034<br>**0.4615** | 90.0%<br>**100%** | **HyDE Unggul Meredam Typo:** HyDE bertindak sebagai *auto-corrector* cerdas. Query dengan cacat ejaan parah (mis. *"detedsi pnyakit daaun tomtat"*, *"klasofikasi kubbis ccn"*) diperbaiki sempurna oleh LLM sebelum di-embed ke ruang vektor. |

---

## 4. Analisis Tajam (Deep-Dive Insights & Temuan Anomali)

Berdasarkan pembedahan observasi pada level individual query, terdapat fenomena arsitektural yang sangat penting untuk dipahami dalamembangan sistem *Information Retrieval* akademis ini:

### A. Di Mana HyDE Berperan Sebagai Penyelamat (From Zero to Hero)
Pada beberapa query, Standard RAG mengalami kegagalan total (**MRR = 0.00**, tidak ada dokumen relevan di Top-5), sementara HyDE mampu meraih **MRR 1.00** (dokumen pertama langsung relevan):
1. **Q03: *"foto daun buat cek hama"* (Kueri Bahasa Kasual)**
   * **Standard RAG:** MRR = 0.00 | Precision@5 = 0.00. RAG terpecah fokusnya pada kata "foto" dan "hama" secara literal, menghasilkan skripsi *alat pengusir babi hutan dengan sensor kamera* atau *monitoring jamaah haji*.
   * **HyDE:** MRR = 1.00 | Precision@5 = 0.80. HyDE menerjemahkan frasa tersebut menjadi konsep *"klasifikasi penyakit daun dengan computer vision / deep learning"*, sehingga langsung menarik skripsi *Implementasi MobileNet Klasifikasi Penyakit Daun Jeruk* di peringkat ke-1.
2. **Q14: *"pengawasan derajat keasaman akuakultur"* (Kueri Konseptual)**
   * **Standard RAG:** MRR = 0.00 | Precision@5 = 0.00.
   * **HyDE:** MRR = 1.00 | Precision@5 = 0.80. Kata *"derajat keasaman"* dan *"akuakultur"* disintesakan dengan tepat oleh HyDE menjadi parameter *"pH"* dan *"kolam/tambakan"*.
3. **Q41: *"detedsi pnyakit daaun tomtat"* (Kueri Tipografi)**
   * **Standard RAG:** MRR = 0.00 | Precision@5 = 0.00. Model embedding RAG gagal memetakan token berantakan *"detedsi"*, *"daaun"*, dan *"tomtat"*.
   * **HyDE:** MRR = 1.00 | Precision@5 = 0.40. LLM menyerap konteks dan mengenerate abstrak yang benar dengan kata "deteksi penyakit daun tomat", berhasil mendongkrak pencarian.
4. **Q07: *"apk tebak sakit di hape"* (Kueri Bahasa Kasual)**
   * **Standard RAG:** MRR = 0.3333 (Rank 3) | Precision@5 = 0.20. RAG terisolasi pada kata literal "sakit" dan "hape", menyemburkan hasil yang relevansinya rendah atau di peringkat bawah (seperti klasifikasi daun teh di Rank 1).
   * **HyDE:** MRR = 1.00 | Precision@5 = 0.60. HyDE mengekspansi frasa kasual "apk tebak sakit di hape" menjadi terminologi akademis *"Diagnosis Penyakit, Mobile Health, Disease Detection, Klasifikasi Penyakit"*, sehingga langsung berhasil menempatkan dokumen relevan pada peringkat ke-1, ke-4, dan ke-5.

### B. Di Mana HyDE Justru Mengalami Stagnasi / Menurunkan Performa (Semantic Noise)
Meskipun HyDE unggul di query rumit/kasual, terdapat kelemahan nyata ketika dihadapi dengan **query eksplisit / harfiah**:
1. **Q40: *"Arduino dan Firebase Android"* (Kueri Leksikal Spesifik)**
   * **Standard RAG:** MRR = 1.00 | Precision@5 = 0.40. Langsung menemukan skripsi yang secara spesifik menggabungkan ketiga teknologi tersebut.
   * **HyDE:** MRR = 0.00 | Precision@5 = 0.00. **(Gagal Total)**.
   * **Penyebab:** Saat diberi query yang berisi murni susunan nama alat/teknologi tanpa konteks masalah, LLM mencoba "mengarang" cerita latar belakang abstrak (misalnya membayangkan proyek smart home atau monitoring cuaca tertentu). Narasi halusinasi ini melunakkan fokus ruang vektor dari teknologi *Arduino+Firebase+Android* ke arah topik halusinasi buatan LLM tersebut.
2. **Q16: *"logika samar pengendalian suhu"* (Kueri Konseptual)**
   * **Standard RAG:** MRR = 1.00 | Precision@5 = 0.20. (Menemukan skripsi *Fuzzy Tsukamoto pada Sistem Kontrol Nutrisi Aquaponic* di peringkat 1).
   * **HyDE:** MRR = 0.00 | Precision@5 = 0.00. Terkadang padanan kata seperti "logika samar" justru dibawa secara literal oleh LLM tanpa mengonversinya dengan kuat ke keyword standar akademis Indonesia yaitu *"Fuzzy Logic"*, atau menggeser fokusnya ke sistem pendingin ruangan umum yang tidak terdapat di database.

### C. Analisis Blind Spot (Kegagalan Kedua Metode)
Terdapat 1 query di mana **baik Standard RAG maupun HyDE mencatatkan skor nol absolut (MRR = 0.00, Precision = 0.00)**:
1. **Q18: *"penganalisisan kondisi psikologis jaringan"* (Kueri Konseptual / Psikologi-Jaringan)**

**Analisis Penyebab:** Kegagalan ini **bukan** karena kecacatan model embedding atau LLM, melainkan karena **keterbatasan koleksi dokumen (Out-of-Domain / Corpus Absence)**. Dalam database repositori skripsi yang dievaluasi, memang tidak terdapat penelitian yang fokus pada analisa psikologis berbasis jaringan. Hal ini wajar dalam evaluasi IR dan menunjukkan batasan pengetahuan dokumen (*knowledge boundary*). *(Catatan: Kueri Q07 sebelumnya yang merupakan out-of-domain mengenai GIS kriminalitas telah diperbarui menjadi kueri kasual "apk tebak sakit di hape", yang kini berhasil ditangani dengan sangat baik oleh HyDE).*

---

## 5. Kesimpulan & Rekomendasi Arsitektural (Next Steps)

Berdasarkan analisis kritis di atas, pendekatan "satu metode untuk semua" (*one-size-fits-all*) tidak memberikan hasil terbaik. Standard RAG luar biasa cepat dan akurat untuk kata kunci teknis eksplisit, sementara HyDE adalah juru selamat untuk bahasa awam, typo, dan sinonim rumit.

### Rekomendasi Strategis Pengembangan Sistem:
1. **Implementasi Hybrid Adaptive Retrieval (RAG + HyDE Routing):**
   * **Query Classifier:** Gunakan pengklasifikasi ringan (atau prompt klasifikasi cepat sebelum retrieval) untuk mendeteksi tipe query.
   * **Jalur Standard RAG:** Jika query terdeteksi sebagai **Kueri Leksikal Spesifik / Exact Match** (kombinasi nama algoritma, bahasa pemrogram, atau hardware spesifik seperti *CNN, YOLOv8, Arduino, Flutter, Firebase*), langsung gunakan **Standard RAG** untuk menjaga presisi dan meminimalkan latensi.
   * **Jalur HyDE:** Jika query berkarakteristik **Kasual, Panjang, Mengalami Typo, atau Konseptual Awam**, aktifkan pipeline **HyDE** untuk menjembatani kesenjangan semantik.
2. **Tuning Prompt HyDE untuk Kueri Hardware/Teknologi:**
   * Untuk mengatasi kegagalan seperti pada kes Kasus Q40, rancang *system prompt* HyDE agar menerapkan aturan ketat: *"Jika query berisi spesifikasi kombinasi teknologi/platform tertentu (mis. Arduino + Firebase), pastikan seluruh nama teknologi tersebut menjadi fokus dominan dan wajib dicantumkan berulang pada abstrak buatan tanpa mengubah domain masalah secara sembarangan."*
3. **Pemanfaatan Re-Ranking:**
   * Terapkan *cross-encoder reranker* (misal: BGE-Reranker atau Cohere Rerank) setelah tahap retrieval Top-10 (gabungan dari RAG dan HyDE) sebelum ditampilkan Top-5 kepada user, guna menggabungkan kekuatan presisi RAG dengan jangkauan recall HyDE.
