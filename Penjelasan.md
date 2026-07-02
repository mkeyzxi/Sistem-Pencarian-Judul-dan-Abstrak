# Penjelasan Front-End: Sistem Pencarian Judul dan Abstrak Skripsi

Dokumen ini menjelaskan tentang antarmuka pengguna (front-end), fitur-fitur yang tersedia, serta teknologi yang digunakan untuk membangun dan menghubungkannya dengan sisi server (back-end).

## Teknologi Front-End yang Digunakan
Front-end aplikasi ini dibangun menggunakan teknologi modern berbasis web:
1. **Vue.js 3**: Framework JavaScript utama yang digunakan untuk membangun antarmuka pengguna secara reaktif dan berbasis komponen.
2. **Vite**: Build tool yang sangat cepat untuk lingkungan pengembangan lokal (development server) dan pembuatan *bundle* yang optimal untuk *production*.
3. **Tailwind CSS (v4)**: Framework CSS *utility-first* untuk mengatur *styling* antarmuka (UI) dengan cepat, responsif, dan konsisten secara langsung di dalam *template* HTML.
4. **Vue Router**: Digunakan untuk menangani navigasi dan *routing* halaman pada mode *Single Page Application* (SPA), seperti berpindah antara beranda dan halaman tentang.
5. **Pinia**: Sistem *state management* untuk Vue.js, digunakan untuk mengelola state atau data yang bisa diakses secara global oleh komponen.
6. **Marked**: *Library* pembantu yang berfungsi untuk melakukan *parsing* respons teks berformat Markdown dari LLM menjadi HTML yang dapat dirender ke pengguna.
7. **Iconify**: Digunakan untuk menambahkan koleksi ikon dengan mudah di berbagai komponen visual UI.

## Struktur dan Komponen UI Utama
Aplikasi mengusung arsitektur berbasis komponen (`src/components/`), yang membuat kode lebih rapi dan dapat digunakan ulang:
- **`MainChat.vue` & `ChatArea.vue`**: Berfungsi sebagai kanvas utama untuk menampilkan balasan dari chatbot, daftar riwayat *chat*, beserta efek animasi pengetikan.
- **`InputArea.vue` & `InputChat.vue`**: Menangani kolom *input* di mana pengguna mengetikkan instruksi atau *query* pencarian.
- **`Sidebar.vue` & `Drawer.vue`**: Antarmuka navigasi samping untuk pengaturan, perpindahan mode, atau melihat menu aplikasi.
- **`TableResults.vue`**: Menampilkan daftar dokumen abstrak/judul skripsi yang direkomendasikan dengan tampilan *table* yang rapi.

## Fitur Utama
1. **Antarmuka Chatbot (Conversational UI)**: Desain menyerupai ChatGPT, memungkinkan pengguna untuk memberikan pertanyaan atau pencarian dengan bahasa alami.
2. **Pengaturan Mode Pencarian**: Pengguna dapat memilih mode tertentu (misal: RAG, Pencarian Semantik). Fitur ini dikelola oleh *state* spesifik melalui `useSearchMode.js`.
3. **Contextual History**: Aplikasi menyimpan dan mengingat percakapan sebelumnya (*chat history*) yang membuat jawaban bot menjadi lebih relevan.
4. **Penyajian Data Ganda**: Menggabungkan respons natural (teks jawaban konklusif) dan data terstruktur (daftar referensi skripsi/dokumen).

## Bagaimana Front-End Terhubung dengan Back-End?

Front-end difokuskan secara murni untuk tampilan visual dan interaksi pengguna, sementara pemrosesan logika, pencarian (Vector Database/ChromaDB), dan koneksi LLM berada pada Back-End (dibangun dengan Python **FastAPI**). Hubungan keduanya terjadi melalui jembatan **REST API**.

### 1. Logika Komunikasi via Vue Composables (`useChatbot.js`)
Di dalam direktori `composables`, file `useChatbot.js` bertindak sebagai sentral/penghubung untuk berkomunikasi dengan *backend*.
- Menggunakan *reactive state* bawaan Vue (`ref`) seperti `messages` (untuk menyimpan daftar chat), `isLoading` (untuk indikator *loading*), dan `error` (untuk penanganan *error*).
- Fungsi `sendMessage` adalah aktor utama yang mengonversi input pengguna untuk kemudian dikirim ke server.

### 2. Pertukaran Data Menggunakan Fetch API
Aplikasi mengeksekusi request HTTP ke server menggunakan metode *native* JavaScript `fetch`:
```javascript
const response = await fetch('http://127.0.0.1:8000/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        "message": message, // Teks pencarian dari pengguna
        "mode": mode,       // Mode pencarian saat ini
        "chat_history": history // Konteks percakapan terakhir (maksimal 10)
    }),
})
```
- **Endpoint**: Menembak ke *base URL* `http://127.0.0.1:8000` (port bawaan Uvicorn/FastAPI backend) ke rute `/api/chat`.
- **Payload Request**: Mengirim *body* berformat JSON yang terdiri dari pesan, mode pencarian, dan riwayat yang dibatasi agar token tidak membludak.
- **Handling Response**: Setelah respons diterima dari FastAPI, datanya akan dibongkar (berupa `data.message` untuk teks balasan dari LLM dan `data.documents` untuk sumber dokumen yang dirujuk). Data baru kemudian dimasukkan (`push`) ke dalam *state* `messages` sehingga UI bereaksi dan menampilkannya di layar.

### 3. Sistem CORS (Cross-Origin Resource Sharing)
Karena Front-End (Vite) biasanya berjalan pada port `5173` sementara Back-End berjalan pada port `8000`, peramban (browser) memicu pengamanan dasar (*Same-Origin Policy*). 
Agar koneksi *fetch* ini diizinkan dan tidak ditolak/di-blok, sistem FastAPI backend menggunakan modul `CORSMiddleware` (berada di file `backend/app/main.py`) yang mengizinkan *request* dari *origin* atau domain Front-End.
