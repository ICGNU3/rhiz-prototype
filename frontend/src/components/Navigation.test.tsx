import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Navigation from './Navigation'

const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  subscription_tier: 'explorer',
  goals_count: 3,
  contacts_count: 5,
  ai_suggestions_used: 12
}

const mockOnLogout = vi.fn()

const renderNavigation = (initialPath = '/dashboard') => {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Navigation user={mockUser} onLogout={mockOnLogout} />
    </MemoryRouter>
  )
}

describe('Navigation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the Rhiz logo', () => {
    renderNavigation()
    expect(screen.getByText('Rhiz')).toBeInTheDocument()
  })

  it('displays navigation items on desktop', () => {
    renderNavigation()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Contacts')).toBeInTheDocument()
    expect(screen.getByText('Goals')).toBeInTheDocument()
    expect(screen.getByText('AI Intelligence')).toBeInTheDocument()
  })

  it('displays user email', () => {
    renderNavigation()
    expect(screen.getByText(mockUser.email)).toBeInTheDocument()
  })

  it('calls onLogout when logout button is clicked', () => {
    renderNavigation()
    const logoutButton = screen.getByText('Logout')
    fireEvent.click(logoutButton)
    expect(mockOnLogout).toHaveBeenCalledTimes(1)
  })

  it('shows mobile menu button on small screens', () => {
    renderNavigation()
    const mobileMenuButton = screen.getByLabelText('Toggle main menu')
    expect(mobileMenuButton).toBeInTheDocument()
  })

  it('toggles mobile menu when hamburger is clicked', () => {
    renderNavigation()
    const mobileMenuButton = screen.getByLabelText('Toggle main menu')
    
    // Mobile menu should not be visible initially
    expect(screen.queryByText('Signed in as')).not.toBeInTheDocument()
    
    // Click to open menu
    fireEvent.click(mobileMenuButton)
    expect(screen.getByText('Signed in as')).toBeInTheDocument()
    
    // Click to close menu
    fireEvent.click(mobileMenuButton)
    expect(screen.queryByText('Signed in as')).not.toBeInTheDocument()
  })

  it('highlights active navigation item', () => {
    renderNavigation('/contacts')
    const contactsLink = screen.getByRole('link', { name: /contacts/i })
    expect(contactsLink).toHaveClass('text-blue-400')
  })

  it('has proper accessibility attributes', () => {
    renderNavigation()
    
    // Check ARIA labels
    expect(screen.getByLabelText('Toggle main menu')).toBeInTheDocument()
    expect(screen.getByLabelText('Rhiz - Go to dashboard')).toBeInTheDocument()
    
    // Check navigation role
    const nav = screen.getByRole('navigation', { name: 'Main navigation' })
    expect(nav).toBeInTheDocument()
    
    // Check screen reader text
    expect(screen.getByText('Open main menu')).toHaveClass('sr-only')
  })

  it('closes mobile menu when navigation link is clicked', () => {
    renderNavigation()
    const mobileMenuButton = screen.getByLabelText('Toggle main menu')
    
    // Open mobile menu
    fireEvent.click(mobileMenuButton)
    expect(screen.getByText('Signed in as')).toBeInTheDocument()
    
    // Click a navigation link
    const contactsLink = screen.getAllByText('Contacts')[1] // Mobile menu version
    fireEvent.click(contactsLink)
    
    // Menu should be closed
    expect(screen.queryByText('Signed in as')).not.toBeInTheDocument()
  })

  it('handles keyboard navigation', () => {
    renderNavigation()
    const logoLink = screen.getByLabelText('Rhiz - Go to dashboard')
    
    // Focus should work
    logoLink.focus()
    expect(logoLink).toHaveFocus()
  })
})