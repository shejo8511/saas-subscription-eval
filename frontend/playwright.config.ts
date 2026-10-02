import { defineConfig, devices } from "@playwright/test";

const reports = process.env.PLAYWRIGHT_REPORT_DIR ?? "playwright-report";

export default defineConfig({
  outputDir: `${reports}/results`,
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: true,
  retries: 0,
  timeout: 30_000,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: `${reports}/html` }],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? "http://127.0.0.1:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "desktop",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1440, height: 1000 },
      },
    },
    {
      name: "tablet",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 768, height: 1024 },
      },
    },
    {
      name: "mobile",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 375, height: 812 },
      },
    },
  ],
});
