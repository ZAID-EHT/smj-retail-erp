import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue()],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    outDir: "../my_store_ui/public/frontend",
    emptyOutDir: true,
    cssCodeSplit: false,
    sourcemap: true,
    lib: {
      entry: fileURLToPath(new URL("./src/main.js", import.meta.url)),
      name: "RetailERPFrontend",
      formats: ["iife"],
      fileName: () => "retail-erp.js",
    },
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) =>
          assetInfo.name?.endsWith(".css") ? "retail-erp.css" : "assets/[name]-[hash][extname]",
      },
    },
  },
});
