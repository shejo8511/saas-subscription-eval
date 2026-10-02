export type Identity = {
  id: string;
  name: string;
  email: string;
  role: "Admin" | "User";
  company: { id: string; name: string };
  expires_at: string;
};

export class AuthError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request(
  path: string,
  options: RequestInit = {},
): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`/api/v1/auth/${path}`, {
      ...options,
      credentials: "same-origin",
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new AuthError(
      0,
      "No hay conexión. Comprueba tu red y vuelve a intentar.",
    );
  }
  if (!response.ok) {
    const messages: Record<number, string> = {
      401: "Email o contraseña no válidos, o sesión expirada.",
      403: "La protección de la sesión cambió. Vuelve a intentar.",
      422: "Revisa el email y la contraseña.",
      429: "Demasiados intentos. Espera antes de volver a intentar.",
    };
    throw new AuthError(
      response.status,
      messages[response.status] ??
        "El servicio no está disponible. Vuelve a intentar.",
    );
  }
  return response;
}

export async function getIdentity(
  signal: AbortSignal,
): Promise<Identity | null> {
  try {
    return await (await request("me", { signal })).json();
  } catch (error) {
    if (error instanceof AuthError && error.status === 401) return null;
    throw error;
  }
}

async function mutate(
  path: "login" | "logout",
  body?: { email: string; password: string },
): Promise<Response> {
  const csrf = (await (await request("csrf")).json()) as { csrf_token: string };
  return request(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrf.csrf_token,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
}

export async function login(
  email: string,
  password: string,
): Promise<Identity> {
  return (await mutate("login", { email, password })).json();
}

export async function logout(): Promise<void> {
  await mutate("logout");
}
