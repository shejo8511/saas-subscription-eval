import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Suscripciones B2B · Base del proyecto",
  description: "Estado del entorno inicial de gestión de suscripciones B2B.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body>
        <a href="#main" className="skip-link">
          Ir al contenido
        </a>
        {children}
      </body>
    </html>
  );
}
