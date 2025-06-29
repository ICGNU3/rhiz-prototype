import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('landing page loads correctly', async ({ page }) => {
    await page.goto('/');
    
    // Check that the landing page loads
    await expect(page).toHaveTitle(/Rhiz/);
    await expect(page.locator('h1')).toContainText('Rhiz');
    
    // Check for main call-to-action elements
    await expect(page.getByText('Get Started')).toBeVisible();
    await expect(page.getByText('Try Demo')).toBeVisible();
  });

  test('login page loads correctly', async ({ page }) => {
    await page.goto('/login');
    
    // Check for login form elements
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /send magic link/i })).toBeVisible();
    
    // Check for demo login option
    await expect(page.getByText(/try demo/i)).toBeVisible();
  });

  test('magic link form validation', async ({ page }) => {
    await page.goto('/login');
    
    // Try to submit empty form
    await page.getByRole('button', { name: /send magic link/i }).click();
    
    // Should show validation error
    await expect(page.getByText(/email.*required/i)).toBeVisible();
    
    // Enter invalid email
    await page.getByLabel(/email/i).fill('invalid-email');
    await page.getByRole('button', { name: /send magic link/i }).click();
    
    // Should show email format error
    await expect(page.getByText(/valid email/i)).toBeVisible();
  });

  test('demo login flow works', async ({ page }) => {
    await page.goto('/login');
    
    // Click demo login
    await page.getByText(/try demo/i).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.getByText(/welcome/i)).toBeVisible();
  });

  test('protected routes redirect to login', async ({ page }) => {
    // Try to access protected route without authentication
    await page.goto('/app/dashboard');
    
    // Should redirect to login
    await expect(page).toHaveURL(/login/);
  });

  test('navigation works when authenticated', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByText(/try demo/i).click();
    
    // Test navigation to different sections
    await page.getByText('Contacts').click();
    await expect(page).toHaveURL(/contacts/);
    
    await page.getByText('Goals').click();
    await expect(page).toHaveURL(/goals/);
    
    await page.getByText('Dashboard').click();
    await expect(page).toHaveURL(/dashboard/);
  });

  test('logout functionality works', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByText(/try demo/i).click();
    
    // Find and click logout
    await page.getByText('Logout').click();
    
    // Should redirect to landing page
    await expect(page).toHaveURL('/');
    
    // Try to access protected route - should redirect to login
    await page.goto('/app/dashboard');
    await expect(page).toHaveURL(/login/);
  });
});