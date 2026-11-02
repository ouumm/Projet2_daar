import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// En dev, /api est proxifie vers le backend Django local
export default defineConfig({
  plugins: [vue()],
  server: { proxy: { '/api': 'http://localhost:8000' } },
})
