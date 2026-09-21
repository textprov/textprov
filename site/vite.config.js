import { defineConfig, searchForWorkspaceRoot } from "vite";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  base: "./",
  server: {
    fs: {
      allow: [searchForWorkspaceRoot(process.cwd())],
    },
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(here, "index.html"),
        encoder: resolve(here, "encoder.html"),
        spec: resolve(here, "spec.html"),
      },
    },
  },
});
