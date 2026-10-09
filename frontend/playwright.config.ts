import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 300_000,
  fullyParallel: false,
  reporter: [["list"], ["json", { outputFile: "../ui-audit/results.json" }]],
  use: { baseURL: "http://127.0.0.1:4175", colorScheme: "dark", reducedMotion: "reduce", trace: "retain-on-failure", launchOptions: { channel: "msedge", args: ["--disable-gpu", "--disable-dev-shm-usage"] } },
  webServer: { command: "node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4175", cwd: "C:/Users/win11/NVIDIA_HACKATHON/frontend", url: "http://127.0.0.1:4175", reuseExistingServer: false, timeout: 30_000 },
});
