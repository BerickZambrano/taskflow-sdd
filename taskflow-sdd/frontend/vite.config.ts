import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/projects': 'http://localhost:8000',
      '/tasks': 'http://localhost:8000',
      '/tags': 'http://localhost:8000',
      '/time-entries': 'http://localhost:8000',
      '/stats': 'http://localhost:8000',
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
  },
})
