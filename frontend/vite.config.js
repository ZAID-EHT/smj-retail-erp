import { fileURLToPath, URL } from "node:url";
import { copyFileSync, existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

const outputDirectory = fileURLToPath(new URL("../my_store_ui/public/frontend", import.meta.url));

function retainDeskCompatibilityAssets() {
  return {
    name: "retail-erp-desk-compatibility-assets",
    closeBundle() {
      const manifestPath = resolve(outputDirectory, ".vite/manifest.json");
      if (!existsSync(manifestPath)) return;
      const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
      const entry = manifest["src/main.js"] || Object.values(manifest).find((item) => item.isEntry);
      const stylesheet = entry?.css?.[0] || manifest["style.css"]?.file;
      if (!entry?.file || !stylesheet) return;
      copyFileSync(resolve(outputDirectory, entry.file), resolve(outputDirectory, "retail-erp.js"));
      copyFileSync(resolve(outputDirectory, stylesheet), resolve(outputDirectory, "retail-erp.css"));
    },
  };
}

export default defineConfig({
  plugins: [vue(), retainDeskCompatibilityAssets()],
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
    outDir: outputDirectory,
    emptyOutDir: true,
    cssCodeSplit: false,
    sourcemap: true,
    manifest: true,
    lib: {
      entry: fileURLToPath(new URL("./src/main.js", import.meta.url)),
      name: "RetailERPFrontend",
      formats: ["iife"],
      fileName: () => "assets/retail-erp-[hash].js",
    },
    rollupOptions: {
      output: {
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
  },
});
