import { defineConfig, searchForWorkspaceRoot } from "vite";

export default defineConfig({
  base: "./",
  server: {
    fs: {
      allow: [searchForWorkspaceRoot(process.cwd())]
    }
  }
});
