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
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  expect((await loginResponse).status()).toBe(200);
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

test("all four roles/companies sign in, reload and sign out through the public proxy", async ({
  page,
}, info) => {
  const errors = checkConsole(page);
  await page.goto("/");
  for (const account of accounts) {
    await enter(page, account);
    await page.reload();
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
    await page.getByRole("button", { name: "Cerrar sesión" }).click();
    expect((await logoutResponse).status()).toBe(200);
    await expect(page.getByLabel("Email", { exact: true })).toBeVisible();
    expect(
      (await page.context().cookies()).some(
        (cookie) => cookie.name === "b2b_session",
      ),
    ).toBe(false);
  }
  expect(errors).toEqual([]);
  await page.getByLabel("Email", { exact: true }).fill("");
  await page.screenshot({
    path: info.outputPath(`login-${info.project.name}.png`),
    fullPage: true,
  });
});

test("independent tenants coexist; sequential switch never reveals previous identity", async ({
  browser,
}) => {
  const first = await browser.newContext({ baseURL: process.env.BASE_URL });
  const second = await browser.newContext({ baseURL: process.env.BASE_URL });
  try {
    const a = await first.newPage();
    const b = await second.newPage();
    await Promise.all([a.goto("/"), b.goto("/")]);
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
    await a.getByRole("button", { name: "Cerrar sesión" }).click();
    expect((await logoutResponse).status()).toBe(200);
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
  await page.goto("/");
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
  await page.reload();
  await expect(page.getByLabel("Email", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Tu sesión" })).toHaveCount(0);
});
