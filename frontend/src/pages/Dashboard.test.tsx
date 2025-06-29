import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from './Dashboard'

const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User'
}

const mockOnLogout = vi.fn()

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    getDashboardAnalytics: vi.fn()
  }
}))

// Mock the Navigation component since it's tested separately
vi.mock('../components/Navigation', () => ({
  default: ({ user, onLogout }: any) => (
    <nav data-testid="navigation">
      <span>{user.email}</span>
      <button onClick={onLogout}>Logout</button>
    </nav>
  )
}))

const renderDashboard = () => {
  return render(
    <MemoryRouter>
      <Dashboard user={mockUser} onLogout={mockOnLogout} />
    </MemoryRouter>
  )
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders welcome message with user name', async () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue({
      success: true,
      data: {
        contacts: 5,
        goals: 3,
        interactions: 12,
        ai_suggestions: 7
      }
    })

    renderDashboard()
    
    expect(screen.getByText(/Welcome back/)).toBeInTheDocument()
    expect(screen.getByText('test')).toBeInTheDocument() // email prefix
  })

  it('displays loading state initially', () => {
    const { apiService } = import('../services/api')
    vi.mocked(apiService).then(api => {
      vi.mocked(api.apiService.getDashboardAnalytics).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )
    })

    renderDashboard()
    
    // Check for loading skeleton elements
    const loadingElements = screen.getAllByLabelText(/Loading/)
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('displays analytics data when loaded', async () => {
    const { apiService } = await import('../services/api')
    const mockAnalytics = {
      contacts: 25,
      goals: 5,
      interactions: 150,
      ai_suggestions: 12
    }

    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue({
      success: true,
      data: mockAnalytics
    })

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByLabelText('25 contacts')).toBeInTheDocument()
      expect(screen.getByLabelText('5 goals')).toBeInTheDocument()
      expect(screen.getByLabelText('150 interactions')).toBeInTheDocument()
      expect(screen.getByLabelText('12 AI suggestions')).toBeInTheDocument()
    })
  })

  it('displays quick action buttons', () => {
    renderDashboard()
    
    expect(screen.getByLabelText('Go to contacts page to add new contacts')).toBeInTheDocument()
    expect(screen.getByLabelText('Go to goals page to create new goals')).toBeInTheDocument()
    expect(screen.getByLabelText('Go to AI intelligence page for recommendations')).toBeInTheDocument()
  })

  it('has proper accessibility structure', () => {
    renderDashboard()
    
    // Check for main landmark
    expect(screen.getByRole('main')).toBeInTheDocument()
    
    // Check for section landmarks
    expect(screen.getByLabelText('Dashboard statistics')).toBeInTheDocument()
    expect(screen.getByLabelText('Quick actions')).toBeInTheDocument()
    expect(screen.getByLabelText('Recent activity')).toBeInTheDocument()
    
    // Check for proper heading structure
    const headings = screen.getAllByRole('heading')
    expect(headings.length).toBeGreaterThan(0)
  })

  it('handles analytics loading failure gracefully', async () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue({
      success: false,
      data: null
    })

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByLabelText('0 contacts')).toBeInTheDocument()
      expect(screen.getByLabelText('0 goals')).toBeInTheDocument()
    })
  })

  it('displays recent activity when available', async () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue({
      success: true,
      data: {
        contacts: 5,
        goals: 3,
        interactions: 12,
        ai_suggestions: 7,
        recent_activity: {
          contacts_added: 2,
          goals_completed: 1
        }
      }
    })

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Added 2 new contacts/)).toBeInTheDocument()
      expect(screen.getByText(/Completed 1 goals/)).toBeInTheDocument()
    })
  })

  it('shows empty state when no recent activity', async () => {
    const { apiService } = await import('../services/api')
    vi.mocked(apiService.getDashboardAnalytics).mockResolvedValue({
      success: true,
      data: {
        contacts: 5,
        goals: 3,
        interactions: 12,
        ai_suggestions: 7,
        recent_activity: null
      }
    })

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('No recent activity to display')).toBeInTheDocument()
      expect(screen.getByText('Start by adding contacts or creating goals')).toBeInTheDocument()
    })
  })
})