import { test, expect } from '@playwright/test';

test.describe('Dashboard Functionality', () => {
  // Authenticate before each test
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByText(/try demo/i).click();
    await expect(page).toHaveURL(/dashboard/);
  });

  test('dashboard loads with analytics data', async ({ page }) => {
    // Check welcome message
    await expect(page.getByText(/welcome/i)).toBeVisible();
    
    // Check for analytics cards
    await expect(page.getByText(/contacts/i)).toBeVisible();
    await expect(page.getByText(/goals/i)).toBeVisible();
    await expect(page.getByText(/interactions/i)).toBeVisible();
    await expect(page.getByText(/suggestions/i)).toBeVisible();
  });

  test('quick action buttons work', async ({ page }) => {
    // Test "Add Contact" button
    await page.getByRole('button', { name: /add contact/i }).click();
    await expect(page).toHaveURL(/contacts/);
    
    // Go back to dashboard
    await page.getByText('Dashboard').click();
    
    // Test "Create Goal" button
    await page.getByRole('button', { name: /create goal/i }).click();
    await expect(page).toHaveURL(/goals/);
    
    // Go back to dashboard
    await page.getByText('Dashboard').click();
    
    // Test "AI Insights" button
    await page.getByRole('button', { name: /ai insights/i }).click();
    await expect(page).toHaveURL(/intelligence/);
  });

  test('recent activity section displays', async ({ page }) => {
    // Should have recent activity section
    await expect(page.getByText(/recent activity/i)).toBeVisible();
    
    // Should show either activity items or empty state
    const hasActivity = await page.getByText(/added.*contact/i).isVisible();
    const hasEmptyState = await page.getByText(/no recent activity/i).isVisible();
    
    expect(hasActivity || hasEmptyState).toBeTruthy();
  });

  test('navigation accessibility', async ({ page }) => {
    // Check for proper ARIA labels
    await expect(page.getByRole('navigation')).toBeVisible();
    await expect(page.getByRole('main')).toBeVisible();
    
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    const focusedElement = await page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  test('mobile responsive layout', async ({ page, isMobile }) => {
    if (isMobile) {
      // Check mobile menu toggle
      await expect(page.getByLabelText(/toggle.*menu/i)).toBeVisible();
      
      // Analytics cards should stack vertically
      const analyticsSection = page.getByLabelText(/dashboard statistics/i);
      await expect(analyticsSection).toBeVisible();
    }
  });

  test('data refresh functionality', async ({ page }) => {
    // Wait for initial data load
    await page.waitForLoadState('networkidle');
    
    // Check if refresh functionality exists
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      
      // Should not cause any errors
      await expect(page.getByText(/welcome/i)).toBeVisible();
    }
  });
});