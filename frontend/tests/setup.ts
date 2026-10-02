import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll } from "vitest";
import { cleanup } from "@testing-library/react";
import { server } from "./server";

beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" });
  const fetch = globalThis.fetch.bind(globalThis);
  // Node's fetch needs absolute URLs; browsers resolve against document origin.
  globalThis.fetch = (input, options) =>
    fetch(
      typeof input === "string"
        ? new URL(input, "http://localhost:3000")
        : input,
      options,
    );
});
afterEach(() => {
  cleanup();
  server.resetHandlers();
});
afterAll(() => server.close());
