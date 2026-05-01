import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('shows CDR notice', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=CDR Public Data Mode')).toBeVisible({ timeout: 10000 });
  });

  test('shows disclaimer in footer', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=Disclaimer')).toBeVisible();
  });

  test('has start discovery button', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });
    await expect(page.locator('text=Start Discovery')).toBeVisible();
  });

  test('clicking start discovery goes to wizard', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });
    await page.locator('[data-testid="dashboard"]').locator('text=Start Discovery').click();
    await expect(page).toHaveURL(/\/discover/);
  });
});
