import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import { fileURLToPath } from 'url'

const projectRoot = fileURLToPath(new URL('.', import.meta.url))

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, projectRoot, 'VITE_')

  // Tanpa VITE_API_URL, bundle produksi akan memanggil 127.0.0.1 di komputer
  // pengunjung dan seluruh pencarian gagal. Gagalkan build sejak awal.
  if (mode === 'production' && !env.VITE_API_URL) {
    throw new Error(
      'VITE_API_URL belum diisi. Buat frontend-v2/.env.production berisi ' +
        'VITE_API_URL=https://alamat-backend (lihat .env.example).',
    )
  }

  return {
    plugins: [
      tailwindcss(),
      react()
    ],
    resolve: {
      alias: {
        '@': path.resolve(projectRoot, './src'),
      },
    },
  }
})
