# Testing Guide for Rhiz Platform

## Overview

This guide covers the comprehensive testing infrastructure for the Rhiz platform, including unit tests, integration tests, and end-to-end (E2E) tests.

## Testing Stack

### Frontend Testing
- **Vitest**: Fast unit test runner with hot module reloading
- **React Testing Library**: Component testing utilities
- **@testing-library/jest-dom**: Custom Jest matchers for DOM elements
- **@testing-library/user-event**: User interaction simulation
- **jsdom**: DOM simulation for Node.js environment

### Backend Testing
- **pytest**: Python testing framework
- **pytest-cov**: Coverage reporting
- **pytest-flask**: Flask-specific testing utilities
- **pytest-mock**: Mocking utilities

### End-to-End Testing
- **Playwright**: Cross-browser automation and testing
- **Multiple browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari

### Code Quality & Linting
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **Black**: Python code formatting
- **flake8**: Python linting
- **isort**: Python import sorting
- **mypy**: Python type checking

## Running Tests

### Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode
npm run test:ci

# Run tests with UI
npm run test:ui
```

### Backend Tests

```bash
# Run all Python tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_app.py

# Run with verbose output
pytest -v
```

### End-to-End Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test e2e/auth.spec.ts

# Run with UI mode
npx playwright test --ui

# Run on specific browser
npx playwright test --project=chromium
```

### Linting and Formatting

```bash
# Frontend linting
cd frontend
npm run lint
npm run format:check
npm run type-check

# Backend linting
black --check .
flake8 .
isort --check-only .
mypy . --ignore-missing-imports
```

## Test Structure

### Frontend Test Organization

```
frontend/src/
├── test/
│   └── setup.ts              # Global test setup and mocks
├── components/
│   ├── Navigation.tsx
│   └── Navigation.test.tsx    # Component tests
├── pages/
│   ├── Dashboard.tsx
│   └── Dashboard.test.tsx     # Page tests
└── services/
    ├── api.ts
    └── api.test.ts           # Service tests
```

### Backend Test Organization

```
tests/
├── __init__.py
├── conftest.py               # Test configuration and fixtures
├── test_app.py              # Application tests
├── test_models.py           # Model tests
├── test_routes.py           # Route tests
└── test_services.py         # Service tests
```

### E2E Test Organization

```
e2e/
├── auth.spec.ts             # Authentication flow tests
├── dashboard.spec.ts        # Dashboard functionality tests
├── contacts.spec.ts         # Contact management tests
└── goals.spec.ts           # Goal management tests
```

## CI/CD Integration

The testing infrastructure is fully integrated into our GitHub Actions CI/CD pipeline:

### Pipeline Stages

1. **Frontend Linting**: ESLint, Prettier, TypeScript type checking
2. **Backend Linting**: Black, flake8, isort, mypy
3. **Frontend Tests**: Vitest unit tests with coverage
4. **Backend Tests**: pytest with coverage
5. **E2E Tests**: Playwright across multiple browsers
6. **Build Verification**: Production build check
7. **Security Scanning**: Trivy vulnerability scanning
8. **Deployment Readiness**: Final verification

### Coverage Requirements

- **Frontend**: 80% coverage minimum (branches, functions, lines, statements)
- **Backend**: 80% coverage minimum
- **E2E**: Critical user flows covered

## Writing Tests

### Frontend Component Tests

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Component from './Component'

describe('Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders correctly', () => {
    render(
      <MemoryRouter>
        <Component />
      </MemoryRouter>
    )
    
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
```

### Backend API Tests

```python
def test_api_endpoint(client, authenticated_user):
    """Test API endpoint functionality."""
    response = client.get('/api/endpoint')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
```

### E2E Tests

```typescript
import { test, expect } from '@playwright/test'

test.describe('Feature', () => {
  test('user can complete workflow', async ({ page }) => {
    await page.goto('/')
    
    await page.getByText('Button').click()
    await expect(page).toHaveURL('/expected-url')
  })
})
```

## Accessibility Testing

### ARIA and Screen Reader Support
- All interactive elements have proper ARIA labels
- Screen reader text for complex interactions
- Focus management and keyboard navigation
- High contrast mode compatibility

### Testing Tools
- Built-in accessibility assertions in Playwright
- Manual screen reader testing guidelines
- Color contrast validation

## Mobile Testing

### Responsive Design Testing
- Mobile-first breakpoints (xs, mobile, tablet, desktop)
- Touch-friendly interactions (44px minimum targets)
- Gesture support and haptic feedback
- iOS-specific optimizations

### Testing Coverage
- Mobile Chrome and Safari in E2E tests
- Responsive design unit tests
- Touch interaction validation

## Performance Testing

### Metrics Tracked
- Bundle size analysis
- Lighthouse performance scores
- Core Web Vitals
- Database query performance

### Tools
- Vite bundle analyzer
- Lighthouse CI integration
- Performance budgets in CI

## Debugging Tests

### Frontend Debug Mode
```bash
# Run tests in debug mode
npm run test:ui

# Run with browser dev tools
npm run test -- --inspect-brk
```

### Backend Debug Mode
```bash
# Run pytest with debugging
pytest --pdb

# Run with coverage and HTML report
pytest --cov=. --cov-report=html
```

### E2E Debug Mode
```bash
# Run with headed browser
npx playwright test --headed

# Debug specific test
npx playwright test --debug e2e/auth.spec.ts
```

## Best Practices

### Test Organization
- Group related tests in describe blocks
- Use descriptive test names
- One assertion per test when possible
- Mock external dependencies

### Performance
- Run tests in parallel when possible
- Use test fixtures for common setup
- Clean up after tests to prevent leaks

### Maintainability
- Keep tests simple and focused
- Use page object model for E2E tests
- Regular test review and refactoring
- Document complex test scenarios

## Continuous Improvement

### Metrics to Monitor
- Test execution time
- Flaky test identification
- Coverage trends
- CI/CD pipeline performance

### Regular Activities
- Review and update test coverage
- Refactor outdated test patterns
- Update testing dependencies
- Performance optimization