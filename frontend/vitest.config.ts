import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  test: {
    environment: "jsdom",
    maxWorkers: 1,
    testTimeout: 15_000,
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/**/*.test.{ts,tsx}"],
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}", "next.config.ts"],
      reporter: ["text", "json", "json-summary", "lcov", "html"],
      thresholds: { lines: 80, statements: 80, functions: 80, branches: 80 },
    },
  },
});
