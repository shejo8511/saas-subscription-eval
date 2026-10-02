"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getSystemStatus } from "@/lib/system-status";

type State = "loading" | "ready" | "unavailable" | "error";
const labels: Record<State, string> = {
  loading: "Comprobando conexión…",
  ready: "Entorno disponible",
  unavailable: "Base de datos no disponible",
  error: "No se pudo conectar con la API",
};

export function SystemStatus() {
  const [state, setState] = useState<State>("loading");
  const controller = useRef<AbortController | null>(null);
  const refresh = useCallback(() => {
    controller.current?.abort();
    const request = new AbortController();
    controller.current = request;
    return getSystemStatus(request.signal).then(
      (result) => {
        if (!request.signal.aborted) setState(result.database);
      },
      () => {
        if (!request.signal.aborted) setState("error");
      },
    );
  }, []);

  useEffect(() => {
    void refresh();
    return () => controller.current?.abort();
  }, [refresh]);

  return (
    <section
      id="estado"
      aria-labelledby="status-heading"
      className="status-section"
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 id="status-heading">Estado del entorno</h2>
        <button
          type="button"
          onClick={() => {
            setState("loading");
            void refresh();
          }}
          disabled={state === "loading"}
        >
          {state === "loading" ? "Comprobando…" : "Volver a comprobar"}
        </button>
      </div>
      <p
        role="status"
        aria-live="polite"
        className="status-message"
        data-state={state}
      >
        <span aria-hidden="true" className="status-dot" />
        {labels[state]}
      </p>
      <p className="text-sm text-muted">
        {state === "unavailable" || state === "error"
          ? "Comprueba que los servicios estén iniciados y vuelve a intentarlo."
          : "Esta comprobación consulta la API y la disponibilidad real de PostgreSQL."}
      </p>
    </section>
  );
}
