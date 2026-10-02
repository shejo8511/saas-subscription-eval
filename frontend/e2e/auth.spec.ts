import { readFileSync } from "node:fs";
import { test, expect, type Page } from "@playwright/test";

type Account = {
  email: string;
  password: string;
  role: string;
  company: string;
};
const accounts = JSON.parse(
  readFileSync(process.env.E2E_CREDENTIALS_FILE!, "utf8"),
) as Account[];
// Auth requests contain ephemeral credentials/cookies: never record them in traces or error screenshots.
test.setTimeout(90_000);
test.use({ trace: "off", screenshot: "off", actionTimeout: 20_000 });

async function visit(page: Page, expectedStatus: number, reload = false) {
  const identityResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/auth/me") &&
      response.request().method() === "GET",
  );
  const [response] = await Promise.all([
    identityResponse,
    reload
      ? page.reload({ waitUntil: "domcontentloaded" })
      : page.goto("/", { waitUntil: "domcontentloaded" }),
  ]);
  expect(response.status()).toBe(expectedStatus);
  expect(await response.finished()).toBeNull();
}

async function enter(page: Page, account: Account) {
  await expect(page.getByLabel("Email", { exact: true })).toBeVisible();
  // A single evaluate keeps credential values out of Playwright locator call logs.
  await page.evaluate(
    ({ email, password }) => {
      const setter = Object.getOwnPropertyDescriptor(
        HTMLInputElement.prototype,
        "value",
      )!.set!;
      for (const [id, value] of [
        ["email", email],
        ["password", password],
      ]) {
        const input = document.getElementById(id)!;
        setter.call(input, value);
        input.dispatchEvent(new Event("input", { bubbles: true }));
      }
    },
    { email: account.email, password: account.password },
  );
  const loginResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/auth/login") &&
      response.request().method() === "POST",
  );
  const [response] = await Promise.all([
    loginResponse,
    page.getByRole("button", { name: "Entrar", exact: true }).click(),
  ]);
  expect(response.status()).toBe(200);
  expect(await response.finished()).toBeNull();
  await expect(page.getByRole("heading", { name: "Tu sesión" })).toBeVisible();
  await expect(page.getByText(account.company, { exact: true })).toBeVisible();
  await expect(page.getByText(account.role, { exact: true })).toBeVisible();
}

function checkConsole(page: Page) {
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
  return errors;
}

for (const account of accounts) {
  test(`${account.role} ${account.company} signs in, reloads and signs out through the public proxy`, async ({
    page,
  }, info) => {
    const errors = checkConsole(page);
    await visit(page, 401);
    await enter(page, account);
    await visit(page, 200, true);
    await expect(
      page.getByText(account.company, { exact: true }),
    ).toBeVisible();
    const response = await page.request.get("/api/v1/auth/me");
    expect(response.status()).toBe(200);
    expect(response.headers()["cache-control"]).toBe("no-store");
    expect(
      await page.evaluate(
        () =>
          Object.keys(localStorage).length + Object.keys(sessionStorage).length,
      ),
    ).toBe(0);
    expect(
      await page.evaluate(() => document.cookie.includes("b2b_session=")),
    ).toBe(false);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    if (account === accounts[0])
      await page.screenshot({
        path: info.outputPath(`session-${info.project.name}.png`),
        fullPage: true,
      });
    const logoutResponse = page.waitForResponse(
      (response) =>
        response.url().endsWith("/auth/logout") &&
        response.request().method() === "POST",
    );
    const [logoutResult] = await Promise.all([
      logoutResponse,
      page.getByRole("button", { name: "Cerrar sesión" }).click(),
    ]);
    expect(logoutResult.status()).toBe(200);
    expect(await logoutResult.finished()).toBeNull();
    await expect(page.getByLabel("Email", { exact: true })).toBeVisible();
    expect(
      (await page.context().cookies()).some(
        (cookie) => cookie.name === "b2b_session",
      ),
    ).toBe(false);
    expect(errors).toEqual([]);
    await page.getByLabel("Email", { exact: true }).fill("");
    if (account === accounts[0])
      await page.screenshot({
        path: info.outputPath(`login-${info.project.name}.png`),
        fullPage: true,
      });
  });
}

test("independent tenants coexist; sequential switch never reveals previous identity", async ({
  browser,
  viewport,
}) => {
  const first = await browser.newContext({
    baseURL: process.env.BASE_URL,
    viewport,
  });
  const second = await browser.newContext({
    baseURL: process.env.BASE_URL,
    viewport,
  });
  try {
    const a = await first.newPage();
    const b = await second.newPage();
    await Promise.all([visit(a, 401), visit(b, 401)]);
    await Promise.all([enter(a, accounts[0]), enter(b, accounts[2])]);
    await expect(a.getByText(accounts[2].company, { exact: true })).toHaveCount(
      0,
    );
    await expect(b.getByText(accounts[0].company, { exact: true })).toHaveCount(
      0,
    );
    const logoutResponse = a.waitForResponse(
      (response) =>
        response.url().endsWith("/auth/logout") &&
        response.request().method() === "POST",
    );
    const [logoutResult] = await Promise.all([
      logoutResponse,
      a.getByRole("button", { name: "Cerrar sesión" }).click(),
    ]);
    expect(logoutResult.status()).toBe(200);
    expect(await logoutResult.finished()).toBeNull();
    await expect(a.getByLabel("Email", { exact: true })).toBeVisible();
    await a.evaluate((previous) => {
      const observer = new MutationObserver(() => {
        if (
          document
            .querySelector(".identity-details")
            ?.textContent?.includes(previous)
        )
          document.documentElement.dataset.staleIdentity = "true";
      });
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true,
      });
    }, accounts[0].company);
    await enter(a, accounts[2]);
    expect(
      await a.locator("html").getAttribute("data-stale-identity"),
    ).toBeNull();
    await expect(
      b.getByText(accounts[2].company, { exact: true }),
    ).toBeVisible();
  } finally {
    await first.close();
    await second.close();
  }
});

test("signed CSRF, cookie attributes, replay rejection and anonymous guards via Next", async ({
  page,
}) => {
  await visit(page, 401);
  await enter(page, accounts[1]);
  const cookies = await page.context().cookies();
  const session = cookies.find((cookie) => cookie.name === "b2b_session")!;
  const csrf = cookies.find((cookie) => cookie.name === "b2b_csrf")!;
  expect(session.httpOnly).toBe(true);
  expect(session.sameSite).toBe("Strict");
  expect(session.path).toBe("/");
  expect(session.secure).toBe(false);
  expect(csrf.httpOnly).toBe(false);
  const invalid = await page.request.post("/api/v1/auth/logout", {
    headers: { Origin: "http://attacker.invalid", "X-CSRF-Token": csrf.value },
  });
  expect(invalid.status()).toBe(403);
  const missing = await page.request.post("/api/v1/auth/logout", {
    headers: { Origin: process.env.BASE_URL! },
  });
  expect(missing.status()).toBe(403);
  const result = await page.request.post("/api/v1/auth/logout", {
    headers: { Origin: process.env.BASE_URL!, "X-CSRF-Token": csrf.value },
  });
  expect(result.status()).toBe(200);
  expect(
    result
      .headersArray()
      .filter((header) => header.name.toLowerCase() === "set-cookie").length,
  ).toBe(2);
  await page.context().addCookies([session]);
  expect((await page.request.get("/api/v1/auth/me")).status()).toBe(401);
  await visit(page, 401, true);
  await expect(page.getByLabel("Email", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Tu sesión" })).toHaveCount(0);
});
