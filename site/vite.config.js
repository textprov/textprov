import { documents } from "./build-proposal.js";
import { defineConfig, searchForWorkspaceRoot } from "vite";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  base: "./",
  resolve: {
    alias: {
      textprov: resolve(here, "../js/textprov.js"),
    },
  },
  optimizeDeps: {
    include: ["textprov"],
  },
  server: {
    fs: {
      allow: [searchForWorkspaceRoot(process.cwd())],
    },
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(here, "index.html"),
        proposal: resolve(here, "proposal.html"),
        ...Object.fromEntries(documents.map(([id]) => [id, resolve(here, `${id}.html`)])),
      },
    },
  },
});
