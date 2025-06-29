import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import Dashboard from './Dashboard'
import { User } from '../types'

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    getDashboardAnalytics: vi.fn(),
    getContacts: vi.fn(),
    getGoals: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock the components that have complex dependencies
vi.mock('../components/Navigation', () => ({
  default: ({ user, onLogout }: { user: User; onLogout: () => void }) => (
    <nav data-testid="navigation">
      <span>Welcome, {user.email}</span>
      <button onClick={onLogout}>Logout</button>
    </nav>
  )
}))

vi.mock('../components/LoadingSpinner', () => ({
  default: ({ className }: { className?: string }) => (
    <div data-testid="loading-spinner" className={className}>Loading...</div>
  )
}))

describe('Dashboard', () => {
  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    subscription_tier: 'pro',
    goals_count: 3,
    contacts_count: 25,
    ai_suggestions_used: 12
  }

  const mockOnLogout = vi.fn()

  const renderDashboard = () => {
    return render(<Dashboard user={mockUser} onLogout={mockOnLogout} />)
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders welcome message with user name', async () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue({
      contacts: 5,
      goals: 3,
      interactions: 12,
      ai_suggestions: 7
    })

    renderDashboard()

    expect(screen.getByText('Welcome back!')).toBeInTheDocument()
    expect(screen.getByTestId('navigation')).toBeInTheDocument()
  })

  it('displays analytics data correctly', async () => {
    const { apiService } = await import('../services/api')
    const mockAnalytics = {
      contacts: 25,
      goals: 5,
      interactions: 150,
      ai_suggestions: 12
    }

    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue(mockAnalytics)

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByLabelText('25 contacts')).toBeInTheDocument()
      expect(screen.getByLabelText('5 goals')).toBeInTheDocument()
      expect(screen.getByLabelText('150 interactions')).toBeInTheDocument()
      expect(screen.getByLabelText('12 AI suggestions')).toBeInTheDocument()
    })
  })

  it('shows loading state initially', () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 100))
    )

    renderDashboard()

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
  })

  it('handles API error gracefully', async () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockRejectedValue(
      new Error('API Error')
    )

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByLabelText('0 contacts')).toBeInTheDocument()
      expect(screen.getByLabelText('0 goals')).toBeInTheDocument()
    })
  })

  it('displays recent activity when available', async () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue({
      contacts: 5,
      goals: 3,
      interactions: 12,
      ai_suggestions: 7,
      recent_activity: {
        contacts_added: 2,
        goals_completed: 1,
        messages_sent: 5
      }
    })

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Recent Activity')).toBeInTheDocument()
    })
  })

  it('handles logout action', async () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue({
      contacts: 5,
      goals: 3,
      interactions: 12,
      ai_suggestions: 7
    })

    renderDashboard()

    const logoutButton = screen.getByText('Logout')
    await userEvent.click(logoutButton)

    expect(mockOnLogout).toHaveBeenCalled()
  })
})