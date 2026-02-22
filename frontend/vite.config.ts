import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      // Forward /api requests to FastAPI — no CORS issues
      "/api": {
        target: "http://api:8000",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});