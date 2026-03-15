import { test, expect } from "@playwright/test";

test.describe("Multi-client conferencing", () => {
    test("two users can join the same room and see each other", async ({ browser }) => {
        // Client 1
        const context1 = await browser.newContext();
        const page1 = await context1.newPage();
        await page1.goto("/");
        await page1.getByPlaceholder(/enter your name/i).fill("Alice");
        await page1.getByRole("button", { name: /join room/i }).click();
        await expect(page1.getByText(/Alice/i)).toBeVisible({ timeout: 15000 });

        // Client 2
        const context2 = await browser.newContext();
        const page2 = await context2.newPage();
        await page2.goto("/");
        await page2.getByPlaceholder(/enter your name/i).fill("Bob");
        await page2.getByRole("button", { name: /join room/i }).click();
        await expect(page2.getByText(/Bob/i)).toBeVisible({ timeout: 15000 });

        // Verify Alice sees Bob
        await expect(page1.getByText(/Bob/i)).toBeVisible({ timeout: 15000 });

        // Verify Bob sees Alice
        await expect(page2.getByText(/Alice/i)).toBeVisible({ timeout: 15000 });

        await context1.close();
        await context2.close();
    });
});
