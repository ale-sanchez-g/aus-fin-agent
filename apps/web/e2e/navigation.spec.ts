import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('loads dashboard page', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('h2').filter({ hasText: 'Dashboard' })).toBeVisible();
  });

  test('navigates to discover page', async ({ page }) => {
    await page.goto('/');
    await page.locator('nav[aria-label="Main navigation"]').locator('text=Discover').click();
    await expect(page).toHaveURL(/\/discover/);
  });

  test('navigates to sync status page', async ({ page }) => {
    await page.goto('/');
    await page.locator('nav[aria-label="Main navigation"]').locator('text=Sync Status').click();
    await expect(page).toHaveURL(/\/sync-status/);
    await expect(page.locator('[data-testid="sync-status"]')).toBeVisible({ timeout: 10000 });
  });

  test('shows 404 for unknown routes', async ({ page }) => {
    await page.goto('/this-page-does-not-exist');
    await expect(page.locator('text=404')).toBeVisible();
  });

  test('navigation has correct links', async ({ page }) => {
    await page.goto('/');
    const nav = page.locator('nav[aria-label="Main navigation"]');
    await expect(nav).toBeVisible();
    await expect(nav.locator('text=Dashboard')).toBeVisible();
    await expect(nav.locator('text=Discover')).toBeVisible();
    await expect(nav.locator('text=Products')).toBeVisible();
    await expect(nav.locator('text=Sync Status')).toBeVisible();
  });
});
