import { afterEach, expect, it, vi } from "vitest";
import config from "../next.config";

afterEach(() => vi.unstubAllEnvs());

it("uses an internal API destination without exposing Docker hostnames to browsers", async () => {
  vi.stubEnv("API_INTERNAL_URL", "http://backend:8000");
  expect(await config.rewrites!()).toEqual([
    { source: "/api/:path*", destination: "http://backend:8000/api/:path*" },
  ]);
});

it("supports local API development", async () => {
  vi.stubEnv("API_INTERNAL_URL", undefined);
  expect(await config.rewrites!()).toEqual([
    { source: "/api/:path*", destination: "http://127.0.0.1:8000/api/:path*" },
  ]);
});
