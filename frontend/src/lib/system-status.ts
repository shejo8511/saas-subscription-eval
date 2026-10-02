export type SystemStatus = { database: "ready" | "unavailable" };

export async function getSystemStatus(
  signal: AbortSignal,
): Promise<SystemStatus> {
  const [health, readiness] = await Promise.all([
    fetch("/api/v1/health", { signal, cache: "no-store" }),
    fetch("/api/v1/ready", { signal, cache: "no-store" }),
  ]);
  if (!health.ok || (readiness.status !== 200 && readiness.status !== 503)) {
    throw new Error("No se pudo consultar el estado del servicio.");
  }
  const process: unknown = await health.json();
  const database: unknown = await readiness.json();
  if (
    typeof process !== "object" ||
    process === null ||
    !("status" in process) ||
    process.status !== "ok" ||
    typeof database !== "object" ||
    database === null ||
    !("status" in database) ||
    !("database" in database) ||
    !(
      (readiness.status === 200 &&
        database.status === "ready" &&
        database.database === "ready") ||
      (readiness.status === 503 &&
        database.status === "unavailable" &&
        database.database === "unavailable")
    )
  ) {
    throw new Error("El servicio devolvió una respuesta inesperada.");
  }
  return { database: database.database as SystemStatus["database"] };
}
