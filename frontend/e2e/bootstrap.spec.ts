import { test, expect, type Page } from "@playwright/test";

async function withEnvironmentResponses(
  page: Page,
  action: () => Promise<unknown>,
) {
  const responses = ["health", "ready"].map((endpoint) =>
    page.waitForResponse(
      (response) =>
        response.url().endsWith(`/api/v1/${endpoint}`) &&
        response.request().method() === "GET",
    ),
  );
  const [, received] = await Promise.all([action(), Promise.all(responses)]);
  for (const [index, response] of received.entries()) {
    expect(response.status()).toBe(200);
    expect((await response.json()).status).toBe(index === 0 ? "ok" : "ready");
  }
}

test("shell connects through Next.js to FastAPI and PostgreSQL", async ({
  page,
  request,
}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (
      message.type() === "error" &&
      !(
        message.text().includes("401") &&
        message.location().url.includes("/api/v1/auth/me")
      )
    )
      errors.push(message.text());
  });
  await withEnvironmentResponses(page, () =>
    page.goto("/", { waitUntil: "domcontentloaded" }),
  );
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Accede a tu espacio de empresa.",
  );
  await expect(page.getByRole("status")).toHaveText("Entorno disponible");
  await withEnvironmentResponses(page, () =>
    page.getByRole("button", { name: "Volver a comprobar" }).click(),
  );
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
  await withEnvironmentResponses(page, () =>
    page.goto("/", { waitUntil: "domcontentloaded" }),
  );
  await expect(page.getByRole("status")).toHaveText("Entorno disponible");
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Ir al contenido" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeInViewport();
  await page.getByRole("button", { name: "Volver a comprobar" }).focus();
  await withEnvironmentResponses(page, () => page.keyboard.press("Enter"));
  await expect(page.getByRole("status")).toHaveText("Entorno disponible");
});
