import { defineConfig } from 'vite';
import { resolve } from 'path';
import { readFileSync } from 'fs';

export default defineConfig({
  build: {
    outDir: 'out/media',
    emptyOutDir: false, // Não limpar out/ pois extension.js estará lá
    rollupOptions: {
      input: resolve(__dirname, 'src/webview/chat-entry.js'),
      output: {
        entryFileNames: 'chat.bundle.js',
        format: 'iife',
        name: 'ChatBundle'
      }
    },
    target: 'chrome91', // Target browsers modernos para webview
    minify: false, // Manter legível para debug
    sourcemap: true
  },
  define: {
    global: 'globalThis',
  },
  publicDir: false,
  plugins: [
    // Plugin para copiar CSS
    {
      name: 'copy-css',
      generateBundle() {
        this.emitFile({
          type: 'asset',
          fileName: 'chat.css',
          source: readFileSync(resolve(__dirname, 'media/chat.css'), 'utf-8')
        });
      }
    }
  ]
});
