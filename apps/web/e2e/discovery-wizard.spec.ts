import { test, expect } from '@playwright/test';

test.describe('Discovery Wizard', () => {
  test('loads discovery wizard page', async ({ page }) => {
    await page.goto('/discover');
    await expect(page.locator('text=Product Discovery').first()).toBeVisible({ timeout: 10000 });
  });

  test('shows product category selection step', async ({ page }) => {
    await page.goto('/discover');
    await expect(page.locator('text=Select Product Category')).toBeVisible({ timeout: 10000 });
  });
});
