import { test, expect } from "@playwright/test";

test.describe("AG-Visio smoke", () => {
  test("home page loads and shows join form", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /join conference/i })).toBeVisible();
    await expect(page.getByPlaceholder(/enter your name/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /join room/i })).toBeVisible();
  });

  test("test page link is present", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: /test camera & audio/i })).toBeVisible();
  });

  test("navigating to test page shows video test UI", async ({ page }) => {
    await page.goto("/test");
    await expect(page.getByRole("heading", { name: /video & audio test/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /back to dashboard/i })).toBeVisible();
  });

  test("settings page loads", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.getByRole("heading", { name: /settings/i })).toBeVisible();
  });
});
