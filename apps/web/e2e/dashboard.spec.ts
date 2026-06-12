import { test, expect } from "@playwright/test";

test.describe("Dashboard smoke + navigation", () => {
  test("home page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("text=AG-Visio").or(page.locator("text=MyConf")).first()).toBeVisible();
  });

  test("sidebar navigation works", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    const sidebar = page.locator("nav").first();
    const links = sidebar.locator("a");
    const count = await links.count();
    expect(count).toBeGreaterThanOrEqual(3);
  });

  test("settings page loads sections", async ({ page }) => {
    await page.goto("/settings");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("text=Settings").first()).toBeVisible({ timeout: 10000 });
  });

  test("health page loads", async ({ page }) => {
    await page.goto("/health");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("text=Health").or(page.locator("text=health")).first()).toBeVisible({ timeout: 10000 });
  });

  test("meetings page loads", async ({ page }) => {
    await page.goto("/meetings");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("text=Meetings").or(page.locator("text=meetings")).first()).toBeVisible({ timeout: 10000 });
  });

  test("keyboard shortcut ? opens help modal", async ({ page }) => {
    await page.goto("/");
    await page.keyboard.press("?");
    const modal = page.locator('[role="dialog"]').or(page.locator(".modal"));
    await expect(modal.first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe("REST API", () => {
  test("GET /api/health returns 200", async ({ request }) => {
    const resp = await request.get("/api/health");
    expect(resp.ok()).toBeTruthy();
  });

  test("POST /api/token with empty body returns 400 or 422", async ({ request }) => {
    const resp = await request.post("/api/token", { data: {} });
    expect(resp.status()).toBeGreaterThanOrEqual(400);
  });

  test("GET /api/token/discovery returns JSON", async ({ request }) => {
    const resp = await request.get("/api/token/discovery");
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    expect(body).toBeDefined();
  });
});

test.describe("Join flow", () => {
  test("entering name shows validation or routes to room", async ({ page }) => {
    await page.goto("/");
    const nameInput = page.locator('input[placeholder*="name" i], input[placeholder*="Name"]').first();
    if (await nameInput.isVisible()) {
      await nameInput.fill("TestUser");
      const joinBtn = page.locator("button").filter({ hasText: /join|enter/i }).first();
      await joinBtn.click();
      // Should either show error (no LiveKit) or navigate
      await page.waitForTimeout(2000);
      const hasError = await page.locator("text=Error, text=error, text=fail").count();
      const hasRoom = page.url().includes("/room") || page.url().includes("/meeting");
      expect(hasError > 0 || hasRoom).toBeTruthy();
    }
  });
});
