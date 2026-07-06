import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  // Override the default Cloudflare preset and force a static site build
  nitro: { 
    preset: 'static',
    prerender: {
      // This forces Nitro to physically generate an index.html file!
      routes: ['/'] 
    }
  }, 
  
  tanstackStart: {
    ssr: false, 
    server: { 
      entry: "server",
      output: {
        dir: 'dist',
        serverDir: 'dist/server',
        publicDir: 'dist/public'
      }
    },
  },
});
