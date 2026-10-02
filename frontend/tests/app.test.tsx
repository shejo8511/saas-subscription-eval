import { renderToStaticMarkup } from "react-dom/server";
import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import Home from "@/app/page";
import RootLayout, { metadata } from "@/app/layout";

it("renders the phase 1 shell with working API navigation", async () => {
  render(<Home />);
  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
    "Accede a tu espacio de empresa.",
  );
  expect(screen.getByRole("link", { name: /Consultar API/ })).toHaveAttribute(
    "href",
    "/api/docs",
  );
  expect(await screen.findByText("Entorno disponible")).toBeVisible();
  expect(screen.getByText(/Dos empresas de demostración/)).toBeVisible();
});

it("sets Spanish document language and accessible skip navigation", () => {
  const layout = RootLayout({ children: <main id="main">Prueba</main> });
  expect(layout.props.lang).toBe("es");
  const html = renderToStaticMarkup(layout);
  expect(html).toContain('lang="es"');
  expect(html).toContain('href="#main"');
  expect(html).toContain("Ir al contenido");
  expect(metadata.title).toBe("Suscripciones B2B · Base del proyecto");
});
