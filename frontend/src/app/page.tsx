import { SystemStatus } from "@/components/system-status";

export default function Home() {
  return (
    <>
      <header className="site-header">
        <a href="#main" className="brand">
          Suscripciones B2B
        </a>
        <a href="/api/docs" className="text-sm">
          Consultar API <span aria-hidden="true">↗</span>
        </a>
      </header>
      <main id="main" className="page-content">
        <div className="intro">
          <h1>Una base para gestionar tus suscripciones.</h1>
          <p>
            El entorno inicial conecta la interfaz, la API y la base de datos.
            Comprueba su disponibilidad antes de continuar.
          </p>
        </div>
        <SystemStatus />
        <section className="scope-section" aria-labelledby="scope-heading">
          <h2 id="scope-heading">Alcance de esta entrega</h2>
          <div className="scope-content">
            <p>Base ejecutable · Fase 1</p>
            <p>
              La autenticación, la gestión de licencias y las métricas de
              consumo se incorporarán en las siguientes fases.
            </p>
          </div>
        </section>
      </main>
      <footer className="site-footer">
        Entorno de evaluación · Sin cuentas de acceso todavía
      </footer>
    </>
  );
}
