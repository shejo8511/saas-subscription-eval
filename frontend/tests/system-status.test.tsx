import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { SystemStatus } from "@/components/system-status";
import { getSystemStatus } from "@/lib/system-status";
import { origin, server } from "./server";

describe("environment status", () => {
  it("shows loading before displaying real API status", async () => {
    render(<SystemStatus />);
    expect(screen.getByRole("button", { name: "Comprobando…" })).toBeDisabled();
    expect(await screen.findByText("Entorno disponible")).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Volver a comprobar" }),
    ).toBeEnabled();
  });

  it("reports unavailable PostgreSQL and can retry successfully", async () => {
    server.use(
      http.get(`${origin}/api/v1/ready`, () =>
        HttpResponse.json(
          { status: "unavailable", database: "unavailable" },
          { status: 503 },
        ),
      ),
    );
    render(<SystemStatus />);
    expect(
      await screen.findByText("Base de datos no disponible"),
    ).toBeVisible();
    expect(screen.getByText(/Comprueba que los servicios/)).toBeVisible();
    server.resetHandlers();
    fireEvent.click(screen.getByRole("button", { name: "Volver a comprobar" }));
    expect(await screen.findByText("Entorno disponible")).toBeVisible();
  });

  it("shows a connection error without presenting invented status", async () => {
    server.use(http.get(`${origin}/api/v1/health`, () => HttpResponse.error()));
    render(<SystemStatus />);
    expect(
      await screen.findByText("No se pudo conectar con la API"),
    ).toBeVisible();
  });

  it("aborts pending requests when unmounted", async () => {
    let release!: () => void;
    let started = false;
    const barrier = new Promise<void>((resolve) => {
      release = resolve;
    });
    server.use(
      http.get(`${origin}/api/v1/ready`, async () => {
        started = true;
        await barrier;
        return HttpResponse.json({ status: "ready", database: "ready" });
      }),
    );
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    const view = render(<SystemStatus />);
    await waitFor(() => expect(started).toBe(true));
    const signal = fetchSpy.mock.calls[0][1]!.signal!;
    view.unmount();
    expect(signal.aborted).toBe(true);
    release();
    fetchSpy.mockRestore();
  });
});

describe("health contract", () => {
  it.each([500, 404])(
    "rejects unexpected readiness HTTP %s",
    async (status) => {
      server.use(
        http.get(
          `${origin}/api/v1/ready`,
          () => new HttpResponse(null, { status }),
        ),
      );
      await expect(
        getSystemStatus(new AbortController().signal),
      ).rejects.toThrow("No se pudo consultar");
    },
  );

  it("rejects failed process health", async () => {
    server.use(
      http.get(
        `${origin}/api/v1/health`,
        () => new HttpResponse(null, { status: 503 }),
      ),
    );
    await expect(getSystemStatus(new AbortController().signal)).rejects.toThrow(
      "No se pudo consultar",
    );
  });

  it.each([null, "ok", {}, { status: "wrong" }])(
    "rejects malformed process response %j",
    async (value) => {
      server.use(
        http.get(`${origin}/api/v1/health`, () => HttpResponse.json(value)),
      );
      await expect(
        getSystemStatus(new AbortController().signal),
      ).rejects.toThrow("respuesta inesperada");
    },
  );

  it.each([
    null,
    "ready",
    {},
    { status: "ready" },
    { status: "ready", database: "other" },
    { status: "wrong", database: "ready" },
  ])("rejects malformed readiness response %j", async (value) => {
    server.use(
      http.get(`${origin}/api/v1/ready`, () => HttpResponse.json(value)),
    );
    await expect(getSystemStatus(new AbortController().signal)).rejects.toThrow(
      "respuesta inesperada",
    );
  });

  it("rejects inconsistent HTTP/body status", async () => {
    server.use(
      http.get(`${origin}/api/v1/ready`, () =>
        HttpResponse.json(
          { status: "ready", database: "ready" },
          { status: 503 },
        ),
      ),
    );
    await expect(getSystemStatus(new AbortController().signal)).rejects.toThrow(
      "respuesta inesperada",
    );
  });
});
