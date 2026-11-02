# 📚 Frontend V2 — Sistem Pencarian Judul & Abstrak Skripsi

Interface web modern berbasis **React 19 + Vite 8** untuk sistem pencarian akademik judul dan abstrak skripsi dengan teknologi RAG (Retrieval-Augmented Generation) dan HyDE.

## ✨ Fitur

- 🔍 **Pencarian Cerdas**: Dukungan mode RAG dan HyDE
- 💬 **Chat Interface**: Antarmuka conversational untuk pencarian
- 📄 **Document Preview**: Modal detail untuk setiap hasil pencarian
- 🎨 **Modern UI**: Tailwind CSS 4 dengan animasi smooth (Framer Motion)
- ⚡ **Fast & Responsive**: Vite 8 untuk development & build yang cepat
- 📱 **Mobile-Friendly**: Responsive design untuk semua device
- 🎯 **Empty State**: Saran topik pencarian saat pertama kali

## 🛠 Tech Stack

| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| **React** | 19.2.7 | UI framework |
| **Vite** | 8.1.0 | Build tool & dev server |
| **Tailwind CSS** | 4.3.2 | Styling framework |
| **@tailwindcss/vite** | 4.3.2 | Tailwind v4 integration |
| **Framer Motion** | 12.42.0 | Animasi & transitions |
| **Lucide React** | 1.22.0 | Icon set |
| **React Markdown** | 10.1.0 | Render markdown responses |
| **React Router DOM** | 7.18.1 | Client-side routing |
| **pnpm** | - | Package manager |

## 📁 Struktur Proyek

```
frontend-v2/
├── src/
│   ├── assets/               # Static assets (images, fonts, dll)
│   ├── components/           # React components
│   │   ├── Layout.jsx        # Layout wrapper dengan header/footer
│   │   ├── ChatContainer.jsx # Main container: logika chat + state management
│   │   ├── MessageList.jsx   # Render bubble chat (user & bot)
│   │   ├── MessageComposer.jsx # Input field + submit button
│   │   ├── EmptyState.jsx    # Tampilan awal dengan saran topik
│   │   └── DocumentModal.jsx # Modal popup detail dokumen hasil
│   ├── hooks/
│   │   └── useSearch.js      # Custom hook untuk API call ke backend
│   ├── App.jsx               # Root component
│   ├── App.css               # Component-specific styles
│   ├── index.css             # Global styles & design tokens
│   └── main.jsx              # Entry point aplikasi
├── public/                   # Public assets (favicon, logo, dll)
├── dist/                     # Production build output
├── node_modules/             # Dependencies (auto-generated)
├── .gitignore                # Git ignore rules
├── eslint.config.js          # ESLint configuration
├── index.html                # HTML template
├── package.json              # Dependencies & scripts
├── pnpm-lock.yaml            # Lock file pnpm
├── vite.config.js            # Vite configuration
├── DESIGN.md                 # Design specification (draft)
└── README.md                 # This file
```

## 🚀 Setup & Installation

### Prerequisites

- **Node.js**: 20.x atau lebih tinggi
- **pnpm**: Package manager (install dengan `npm install -g pnpm`)
- **Backend API**: FastAPI backend harus sudah running di `http://127.0.0.1:8000`

### Installation Steps

```bash
# 1. Navigasi ke folder frontend-v2
cd frontend-v2

# 2. Install dependencies
pnpm install

# 3. Jalankan development server
pnpm dev
```

Development server akan berjalan di: `http://localhost:5173`

## 📜 Available Scripts

| Command | Deskripsi |
|---------|-----------|
| `pnpm dev` | Jalankan development server dengan hot reload |
| `pnpm build` | Build untuk production → output ke folder `dist/` |
| `pnpm lint` | Jalankan ESLint untuk code quality check |
| `pnpm preview` | Preview production build secara lokal |

### Script Details

```bash
# Development (dengan hot reload)
pnpm dev

# Production build
pnpm build

# Preview production build
pnpm preview

# Lint code
pnpm lint
```

## 🔌 Koneksi Backend API

### Endpoint Configuration

Frontend berkomunikasi dengan backend melalui REST API:

**Main Endpoint:**
```
POST http://127.0.0.1:8000/api/chat
```

**Request Body:**
```json
{
  "message": "kata kunci pencarian",
  "mode": "rag",
  "chat_history": []
}
```

**Response Body:**
```json
{
  "response": "Berikut adalah hasil pencarian...",
  "sources": [
    {
      "title": "Judul Skripsi",
      "abstract": "Abstrak lengkap...",
      "metadata": {...}
    }
  ],
  "mode": "rag"
}
```

### Mode Pencarian

- **`rag`**: Standard RAG (default) - pencarian langsung, lebih cepat
- **`HyDE`**: HyDE RAG - generate hypothetical document, lebih baik untuk query luas

### Mengubah Backend URL

Jika backend berjalan di URL berbeda, ubah konfigurasi di:

1. **`src/hooks/useSearch.js`**:
```javascript
const baseURL = 'http://127.0.0.1:8000'; // Ubah sesuai URL backend Anda
```

2. **`src/components/ChatContainer.jsx`**:
```javascript
const response = await fetch('http://127.0.0.1:8000/api/chat', {
  // ...
});
```

## 🎨 Komponen Utama

### 1. `ChatContainer.jsx`
**Fungsi**: Main orchestrator untuk fitur chat
- Mengelola state messages dan search results
- Handle submit query ke backend
- Koordinasi antara input, message list, dan document modal
- Error handling dan loading states

### 2. `MessageList.jsx`
**Fungsi**: Render daftar pesan chat
- Bubble chat untuk user dan bot
- Display source documents dalam grid
- Auto-scroll ke message terbaru
- Animasi entrance dengan Framer Motion

### 3. `MessageComposer.jsx`
**Fungsi**: Input field untuk user query
- Auto-focus dan keyboard shortcuts
- Disable saat loading
- Placeholder dinamis
- Submit on Enter key

### 4. `EmptyState.jsx`
**Fungsi**: Tampilan awal sebelum ada chat
- Suggested topics (quick search chips)
- Welcome message dan instruksi
- Hero section dengan ilustrasi

### 5. `DocumentModal.jsx`
**Fungsi**: Popup detail dokumen
- Full abstract display
- Metadata (penulis, tahun, dll)
- Close on backdrop click atau ESC key
- Smooth animation enter/exit

### 6. `Layout.jsx`
**Fungsi**: Wrapper layout aplikasi
- Header dengan logo dan title
- Footer dengan copyright
- Consistent spacing dan max-width

## 🎨 Styling & Design

### Design System

**Design Tokens** (defined in `index.css`):
- Primary color: Blue-600
- Text hierarchy: text-gray-900, text-gray-600, text-gray-500
- Spacing: Tailwind default scale
- Border radius: rounded-lg, rounded-xl, rounded-2xl
- Shadows: shadow-sm, shadow-md, shadow-lg

### Animasi

Menggunakan **Framer Motion** untuk:
- Fade in/out components
- Slide up/down messages
- Scale animations untuk buttons
- Modal overlay transitions

### Responsive Breakpoints

```css
sm: 640px   /* Small devices */
md: 768px   /* Medium devices */
lg: 1024px  /* Large devices */
xl: 1280px  /* Extra large devices */
2xl: 1536px /* 2X Extra large */
```

## 🧪 Development Tips

### Hot Reload
Vite menyediakan HMR (Hot Module Replacement) otomatis. Setiap perubahan di file `.jsx`, `.css`, atau assets akan langsung ter-refresh tanpa full reload.

### Component Development
```bash
# Struktur komponen yang direkomendasikan:
src/components/
  ComponentName/
    ComponentName.jsx
    ComponentName.css (optional)
    index.js (re-export)
```

### Custom Hooks
Hook `useSearch.js` bisa diperluas untuk:
- Caching results
- Rate limiting
- Retry logic
- Request cancellation

## 📦 Build & Deployment

### Production Build

```bash
pnpm build
```

Output akan berada di folder `dist/` dengan:
- Optimized & minified JavaScript
- CSS yang di-purge (unused classes dihapus)
- Asset hashing untuk cache busting
- Source maps (optional)

### Deployment Options

#### 1. Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

#### 2. Netlify
```bash
# Build command
pnpm build

# Publish directory
dist
```

#### 3. Static Hosting (Nginx/Apache)
```bash
pnpm build
# Copy folder dist/ ke web server
```

#### 4. Docker
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build
CMD ["pnpm", "preview", "--host", "0.0.0.0"]
```

### Environment Variables

Untuk production dengan backend URL berbeda:

1. Buat file `.env.production`:
```env
VITE_API_URL=https://api.yourdomain.com
```

2. Update kode untuk menggunakan env var:
```javascript
const baseURL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
```

## 🐛 Troubleshooting

### Port 5173 sudah digunakan
```bash
# Gunakan port lain
pnpm dev --port 3000
```

### Backend connection failed
1. Pastikan backend running di `http://127.0.0.1:8000`
2. Cek CORS settings di backend (FastAPI harus allow origin frontend)
3. Buka Network tab di DevTools untuk cek request details

### Build error: out of memory
```bash
# Increase Node memory limit
NODE_OPTIONS=--max-old-space-size=4096 pnpm build
```

### Styling tidak muncul (Tailwind v4)
Pastikan `@tailwindcss/vite` sudah di-import di `vite.config.js`:
```javascript
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

## 📝 Roadmap & Future Enhancements

### Design Evolution
- [ ] Implementasi penuh "Digital Card Catalog" dari `DESIGN.md`
- [ ] Side-by-side comparison RAG vs HyDE
- [ ] Advanced filters (tahun, kategori, pembimbing)
- [ ] Bookmark dan history pencarian

### Features
- [ ] Export results (PDF, CSV)
- [ ] Share search URL
- [ ] Dark mode
- [ ] Voice search input
- [ ] Multi-language support

### Performance
- [ ] Lazy load components
- [ ] Virtual scrolling untuk results
- [ ] Service worker untuk offline support
- [ ] Progressive Web App (PWA)

## 📄 Catatan Desain

Proyek ini memiliki dua draft desain:
1. **`DESIGN.md`**: Metafora "Digital Card Catalog / Laci Katalog" dengan dua drawer berdampingan
2. **`DESIGN_RAG_UI_BLUE.md`**: Alternatif tema dengan color scheme blue

> **Status**: Implementasi saat ini belum mengadopsi penuh spesifikasi "laci berdampingan" - masih berupa chat interface sederhana dengan daftar sumber.

## 🤝 Contributing

Untuk kontribusi:
1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📞 Support & License

Bagian dari proyek akademik **Sistem Pencarian Judul & Abstrak Skripsi** - Teknik Informatika.

Lihat `readme.md` di root repository untuk dokumentasi lengkap tentang sistem secara keseluruhan.

---
**Last Updated**: November 2026 | React 19.2.7 | Vite 8.1.0 | Tailwind CSS 4.3.2
