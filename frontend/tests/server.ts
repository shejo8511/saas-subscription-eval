import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const origin = "http://localhost:3000";
export const server = setupServer(
  http.get(`${origin}/api/v1/health`, () =>
    HttpResponse.json({ status: "ok" }),
  ),
  http.get(`${origin}/api/v1/ready`, () =>
    HttpResponse.json({ status: "ready", database: "ready" }),
  ),
);
