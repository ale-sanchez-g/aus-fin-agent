import { test, expect } from '@playwright/test';

test.describe('Sync Status', () => {
  test('shows provider table', async ({ page }) => {
    await page.goto('/sync-status');
    await expect(page.locator('[data-testid="sync-status"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Provider Sync Status')).toBeVisible();
  });

  test('shows CDR Public badge', async ({ page }) => {
    await page.goto('/sync-status');
    await page.waitForSelector('[data-testid="sync-status"]', { timeout: 10000 });
    await expect(page.locator('text=CDR Public').first()).toBeVisible();
  });
});
