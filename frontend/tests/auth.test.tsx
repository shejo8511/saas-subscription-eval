import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { http, HttpResponse } from "msw";
import { afterEach, expect, it, vi } from "vitest";
import {
  AuthError,
  getIdentity,
  login,
  logout,
  type Identity,
} from "@/features/auth/api";
import {
  SessionProvider,
  SessionRoot,
  useSession,
} from "@/features/auth/session";
import { SessionPanel } from "@/features/auth/session-panel";
import { origin, server } from "./server";

const identity = (name = "Empresa A"): Identity => ({
  id: "user-id",
  name: "Ana",
  email: "ana@test.invalid",
  role: "Admin",
  company: { id: name, name },
  expires_at: new Date(Date.now() + 1_800_000).toISOString(),
});
const endpoint = (path: string) => `${origin}/api/v1/auth/${path}`;
afterEach(() => vi.useRealTimers());

function endpoints(initial: Identity | null = null) {
  let current = initial;
  server.use(
    http.get(endpoint("me"), () =>
      current
        ? HttpResponse.json(current)
        : HttpResponse.json({}, { status: 401 }),
    ),
    http.get(endpoint("csrf"), () =>
      HttpResponse.json({ csrf_token: "test-csrf" }),
    ),
    http.post(endpoint("login"), async ({ request }) => {
      const body = (await request.json()) as {
        email: string;
        password: string;
      };
      expect(request.headers.get("X-CSRF-Token")).toBe("test-csrf");
      expect(body.password).toBe(" preserved ");
      current = identity(
        body.email === "b@test.invalid" ? "Empresa B" : "Empresa A",
      );
      return HttpResponse.json(current);
    }),
    http.post(endpoint("logout"), () => {
      current = null;
      return HttpResponse.json({ status: "logged_out" });
    }),
  );
}
function mount() {
  return render(
    <SessionRoot>
      <SessionPanel />
    </SessionRoot>,
  );
}
async function fill(email = "a@test.invalid") {
  fireEvent.change(await screen.findByLabelText("Email"), {
    target: { value: email },
  });
  fireEvent.change(screen.getByLabelText("Contraseña"), {
    target: { value: " preserved " },
  });
  fireEvent.click(screen.getByRole("button", { name: "Entrar" }));
}

it("restores a session and focuses the identity heading", async () => {
  endpoints(identity());
  mount();
  expect(screen.getByText("Comprobando sesión…")).toBeVisible();
  expect(screen.queryByText("Empresa A")).not.toBeInTheDocument();
  expect(await screen.findByText("Empresa A")).toBeVisible();
  expect(screen.getByRole("heading", { name: "Tu sesión" })).toHaveFocus();
});

it("validates fields, authenticates, logs out and switches company without stale cache", async () => {
  endpoints();
  const cache = new QueryClient();
  render(
    <QueryClientProvider client={cache}>
      <SessionProvider>
        <SessionPanel />
      </SessionProvider>
    </QueryClientProvider>,
  );
  await screen.findByLabelText("Email");
  fireEvent.click(screen.getByRole("button", { name: "Entrar" }));
  expect(screen.getByRole("alert")).toHaveTextContent(
    "Introduce un email válido",
  );
  await fill();
  await screen.findByText("Empresa A");
  cache.setQueryData(["private", "A"], { company: "Empresa A" });
  fireEvent.click(screen.getByRole("button", { name: "Cerrar sesión" }));
  expect(screen.queryByText("Empresa A")).not.toBeInTheDocument();
  await screen.findByLabelText("Email");
  expect(cache.getQueryData(["private", "A"])).toBeUndefined();
  await fill("b@test.invalid");
  expect(await screen.findByText("Empresa B")).toBeVisible();
  expect(screen.queryByText("Empresa A")).not.toBeInTheDocument();
});

it.each([0, 503])(
  "distinguishes network/server failure %s and recovers",
  async (status) => {
    server.use(
      http.get(endpoint("me"), () =>
        status ? new HttpResponse(null, { status }) : HttpResponse.error(),
      ),
    );
    mount();
    expect(await screen.findByRole("alert")).toHaveTextContent(
      status ? "El servicio" : "No hay conexión",
    );
    endpoints();
    fireEvent.click(screen.getByRole("button", { name: "Volver a intentar" }));
    expect(await screen.findByLabelText("Email")).toBeVisible();
  },
);

it("shows mutation errors, clears passwords and never retries sensitive requests", async () => {
  endpoints();
  let calls = 0;
  server.use(
    http.post(endpoint("login"), () => {
      calls++;
      return new HttpResponse(null, { status: 401 });
    }),
  );
  mount();
  await fill();
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Email o contraseña",
  );
  expect(screen.getByLabelText("Contraseña")).toHaveValue("");
  expect(calls).toBe(1);
});

it("keeps the session when logout fails and exposes a recovery message", async () => {
  endpoints(identity());
  server.use(
    http.post(
      endpoint("logout"),
      () => new HttpResponse(null, { status: 503 }),
    ),
  );
  mount();
  await screen.findByText("Empresa A");
  fireEvent.click(screen.getByRole("button", { name: "Cerrar sesión" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("El servicio");
  expect(screen.getByText("Empresa A")).toBeVisible();
});

it("cancels delayed responses and does not flash the old identity after logout", async () => {
  endpoints(identity());
  const cache = new QueryClient();
  render(
    <QueryClientProvider client={cache}>
      <SessionProvider>
        <SessionPanel />
      </SessionProvider>
    </QueryClientProvider>,
  );
  await screen.findByText("Empresa A");
  let release!: () => void;
  let arrived!: () => void;
  const started = new Promise<void>((resolve) => {
    arrived = resolve;
  });
  const barrier = new Promise<void>((resolve) => {
    release = resolve;
  });
  server.use(
    http.get(endpoint("me"), async () => {
      arrived();
      await barrier;
      return HttpResponse.json(identity());
    }),
  );
  void cache.invalidateQueries({ queryKey: ["session"] });
  await started;
  fireEvent.click(screen.getByRole("button", { name: "Cerrar sesión" }));
  await screen.findByLabelText("Email");
  release();
  await waitFor(() => expect(cache.getQueryData(["session"])).toBeNull());
  expect(screen.queryByText("Empresa A")).not.toBeInTheDocument();
});

it("refreshes an expired session with a controlled clock", async () => {
  vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "Date"] });
  const cache = new QueryClient({
    defaultOptions: { queries: { staleTime: Infinity } },
  });
  cache.setQueryData(["session"], {
    ...identity(),
    expires_at: new Date(Date.now() + 1000).toISOString(),
  });
  server.use(
    http.get(endpoint("me"), () => HttpResponse.json({}, { status: 401 })),
  );
  render(
    <QueryClientProvider client={cache}>
      <SessionProvider>
        <SessionPanel />
      </SessionProvider>
    </QueryClientProvider>,
  );
  expect(screen.getByText("Empresa A")).toBeVisible();
  await act(async () => {
    await vi.advanceTimersByTimeAsync(1001);
  });
  vi.useRealTimers();
  expect(await screen.findByLabelText("Email")).toBeVisible();
});

it("prevents duplicate submissions while a mutation is pending", async () => {
  endpoints();
  let calls = 0;
  let release!: () => void;
  const barrier = new Promise<void>((resolve) => {
    release = resolve;
  });
  server.use(
    http.post(endpoint("login"), async () => {
      calls++;
      await barrier;
      return HttpResponse.json(identity());
    }),
  );
  mount();
  await screen.findByLabelText("Email");
  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: "a@test.invalid" },
  });
  fireEvent.change(screen.getByLabelText("Contraseña"), {
    target: { value: " preserved " },
  });
  const form = screen.getByRole("button", { name: "Entrar" }).closest("form")!;
  fireEvent.submit(form);
  fireEvent.submit(form);
  await waitFor(() => expect(calls).toBe(1));
  release();
  await screen.findByText("Empresa A");
});

it.each([403, 422, 429, 500])(
  "maps API error %s without leaking the server payload",
  async (status) => {
    server.use(
      http.get(endpoint("csrf"), () => HttpResponse.json({ csrf_token: "x" })),
      http.post(endpoint("login"), () =>
        HttpResponse.json({ private: "sensitive" }, { status }),
      ),
    );
    await expect(login("a@test.invalid", "x")).rejects.toMatchObject({
      status,
    });
  },
);

it("propagates cancellation and network errors, and calls logout without a body", async () => {
  endpoints();
  await logout();
  server.use(http.get(endpoint("me"), () => HttpResponse.error()));
  await expect(
    getIdentity(new AbortController().signal),
  ).rejects.toBeInstanceOf(AuthError);
  const controller = new AbortController();
  controller.abort();
  await expect(getIdentity(controller.signal)).rejects.toMatchObject({
    name: "AbortError",
  });
});

it("requires the session provider", () => {
  function Missing() {
    useSession();
    return null;
  }
  expect(() => render(<Missing />)).toThrow("SessionProvider is required");
});
