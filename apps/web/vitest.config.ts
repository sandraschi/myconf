import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    include: ["**/__tests__/**/*.{test,spec}.{ts,tsx}"],
    exclude: ["**/node_modules/**", "**/e2e/**"],
    globals: false,
    coverage: {
      provider: "v8",
      reporter: ["text", "json-summary", "html"],
      exclude: [
        "node_modules/",
        "__tests__/",
        "**/*.config.*",
        "**/types/**",
      ],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
});
