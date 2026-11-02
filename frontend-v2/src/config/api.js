// Vite menanam nilai VITE_API_URL ke bundle saat build, jadi alamat backend
// produksi ditentukan saat `pnpm build`, bukan saat halaman dibuka.
// Fallback ke backend lokal hanya untuk dev server; build produksi tanpa
// VITE_API_URL ditolak di vite.config.js.
const DEV_API_URL = 'http://127.0.0.1:8000'

export const API_BASE_URL = (import.meta.env.VITE_API_URL || DEV_API_URL).replace(/\/+$/, '')
