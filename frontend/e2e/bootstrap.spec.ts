import { test, expect } from "@playwright/test";

test("shell connects through Next.js to FastAPI and PostgreSQL", async ({
  page,
  request,
}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Una base para gestionar tus suscripciones.",
  );
  await expect(page.getByRole("status")).toHaveText("Entorno disponible");
  await page.getByRole("button", { name: "Volver a comprobar" }).click();
  await expect(page.getByRole("status")).toHaveText("Entorno disponible");
  for (const endpoint of ["health", "ready"]) {
    const response = await request.get(`/api/v1/${endpoint}`);
    expect(response.status()).toBe(200);
    expect((await response.json()).status).toBe(
      endpoint === "health" ? "ok" : "ready",
    );
  }
  const spec = await request.get("/api/openapi.json");
  expect(spec.status()).toBe(200);
  expect((await spec.json()).paths).toHaveProperty("/api/v1/ready");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
  await page.screenshot({
    path: testInfo.outputPath(`shell-${testInfo.project.name}.png`),
    fullPage: true,
  });
});

test("keyboard navigation exposes focus and skip link", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("status")).toHaveText("Entorno disponible");
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Ir al contenido" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeInViewport();
  await page.getByRole("button", { name: "Volver a comprobar" }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("status")).toHaveText("Entorno disponible");
});
