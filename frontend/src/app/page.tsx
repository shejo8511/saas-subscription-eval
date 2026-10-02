import { SessionRoot } from "@/features/auth/session";
import { SessionPanel } from "@/features/auth/session-panel";
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
          <h1>Accede a tu espacio de empresa.</h1>
          <p>Consulta tu identidad, empresa y rol con una sesión segura.</p>
        </div>
        <SessionRoot>
          <SessionPanel />
        </SessionRoot>
        <SystemStatus />
        <section className="scope-section" aria-labelledby="scope-heading">
          <h2 id="scope-heading">Alcance de esta entrega</h2>
          <div className="scope-content">
            <p>Autenticación · Fase 2</p>
            <p>
              La gestión de licencias y las métricas de consumo se incorporarán
              en las siguientes fases.
            </p>
          </div>
        </section>
      </main>
      <footer className="site-footer">
        Entorno de evaluación · Dos empresas de demostración
      </footer>
    </>
  );
}
