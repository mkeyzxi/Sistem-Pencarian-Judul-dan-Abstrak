# 📚 Frontend V2 — UI Sistem Pencarian Judul & Abstrak Skripsi

Frontend berbasis **React + Vite** untuk menguji coba antarmuka mesin pencari akademik (retrieval RAG / HyDE) terhadap koleksi judul & abstrak skripsi Teknik Informatika.

**Stack**

- React 19 + Vite 8
- Tailwind CSS 4 (`@tailwindcss/vite`)
- `framer-motion` — animasi mikro
- `lucide-react` — ikon
- `react-markdown` — render hasil
- `react-router-dom` — routing
- pnpm (package manager)

---

## Struktur Proyek

```
frontend-v2/
├── src/
│   ├── App.jsx              # Root: Layout + ChatContainer
│   ├── main.jsx             # Entry point
│   ├── index.css            # Global styles / design tokens
│   ├── components/
│   │   ├── Layout.jsx       # Kerangka halaman
│   │   ├── ChatContainer.jsx# Logika pencarian + daftar pesan & sumber
│   │   ├── MessageList.jsx  # Render bubble pesan
│   │   ├── MessageComposer.jsx # Input pencarian
│   │   ├── EmptyState.jsx   # State awal / saran topik
│   │   └── DocumentModal.jsx# Detail dokumen hasil
│   └── hooks/
│       └── useSearch.js     # Hook pencarian (RAG / HyDE)
├── public/                  # Aset statis (logo, ikon, favicon)
├── DESIGN.md                # Spesifikasi desain "Laci Katalog" (draft)
└── DESIGN_RAG_UI_BLUE.md   # Alternatif tema
```

> Catatan: desain formal UI (metafora "laci katalog" per `DESIGN.md`) masih draft — implementasi saat ini masih berupa antarmuka chat sederhana yang memanggil endpoint `/api/chat` backend.

---

## Setup & Jalankan

Prasyarat: Node.js 20+, pnpm, dan backend FastAPI sudah berjalan di `http://127.0.0.1:8000`.

```bash
cd frontend-v2
pnpm install
pnpm dev
```

Dev server berjalan di `http://localhost:5173`.

### Scripts

| Command      | Deskripsi                       |
| ------------ | ------------------------------- |
| `pnpm dev`   | Jalankan dev server (Vite)      |
| `pnpm build` | Build untuk produksi → `dist/`  |
| `pnpm lint`  | Jalankan ESLint                 |
| `pnpm preview` | Preview build produksi        |

---

## Koneksi ke Backend

- Endpoint utama: `POST http://127.0.0.1:8000/api/chat`
  - body: `{ "message": "kata kunci...", "mode": "rag" | "HyDE", "chat_history": [] }`
  - `ChatContainer.jsx` memakai mode `rag`; `useSearch.js` mendukung perbandingan `rag` vs `HyDE` (mode HyDE dikirim sebagai `HyDE` agar memicu fallback di backend).
- Untuk mengubah URL backend, ubah konstanta `baseURL` di `src/hooks/useSearch.js` dan URL `fetch` di `src/components/ChatContainer.jsx`.

---

## Catatan Desain

- Referensi desain: `DESIGN.md` (metafora *Digital Card Catalog* / "Laci Katalog") dan `DESIGN_RAG_UI_BLUE.md`.
- Implementasi saat ini belum mengadopsi penuh spesifikasi "dua laci berdampingan" RAG vs HyDE — masih tampilan chat dengan daftar sumber.

## License & Contact

Bagian dari proyek akademik Sistem Pencarian Judul & Abstrak Skripsi. Lihat `readme.md` di root repository untuk dokumentasi lengkap.
