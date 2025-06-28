/**
 * Centralized state management for Rhiz application
 * Provides user session, contacts, goals, and insights state
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { User, Contact, Goal, TrustInsight, NetworkGraph } from '../types';

// State interface
interface AppState {
  // Auth state
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Data state
  contacts: Contact[];
  goals: Goal[];
  trustInsights: TrustInsight[];
  networkGraph: NetworkGraph | null;
  
  // UI state
  selectedContact: Contact | null;
  selectedGoal: Goal | null;
  filters: {
    contacts: any;
    goals: any;
  };
}

// Action types
type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_CONTACTS'; payload: Contact[] }
  | { type: 'ADD_CONTACT'; payload: Contact }
  | { type: 'UPDATE_CONTACT'; payload: Contact }
  | { type: 'DELETE_CONTACT'; payload: string }
  | { type: 'SET_GOALS'; payload: Goal[] }
  | { type: 'ADD_GOAL'; payload: Goal }
  | { type: 'UPDATE_GOAL'; payload: Goal }
  | { type: 'DELETE_GOAL'; payload: string }
  | { type: 'SET_TRUST_INSIGHTS'; payload: TrustInsight[] }
  | { type: 'SET_NETWORK_GRAPH'; payload: NetworkGraph }
  | { type: 'SELECT_CONTACT'; payload: Contact | null }
  | { type: 'SELECT_GOAL'; payload: Goal | null }
  | { type: 'SET_CONTACT_FILTERS'; payload: any }
  | { type: 'SET_GOAL_FILTERS'; payload: any };

// Initial state
const initialState: AppState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  contacts: [],
  goals: [],
  trustInsights: [],
  networkGraph: null,
  selectedContact: null,
  selectedGoal: null,
  filters: {
    contacts: {},
    goals: {}
  }
};

// Reducer
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_USER':
      return { 
        ...state, 
        user: action.payload,
        isAuthenticated: !!action.payload,
        isLoading: false
      };
    
    case 'SET_CONTACTS':
      return { ...state, contacts: action.payload };
    
    case 'ADD_CONTACT':
      return { ...state, contacts: [...state.contacts, action.payload] };
    
    case 'UPDATE_CONTACT':
      return {
        ...state,
        contacts: state.contacts.map(contact =>
          contact.id === action.payload.id ? action.payload : contact
        )
      };
    
    case 'DELETE_CONTACT':
      return {
        ...state,
        contacts: state.contacts.filter(contact => contact.id !== action.payload)
      };
    
    case 'SET_GOALS':
      return { ...state, goals: action.payload };
    
    case 'ADD_GOAL':
      return { ...state, goals: [...state.goals, action.payload] };
    
    case 'UPDATE_GOAL':
      return {
        ...state,
        goals: state.goals.map(goal =>
          goal.id === action.payload.id ? action.payload : goal
        )
      };
    
    case 'DELETE_GOAL':
      return {
        ...state,
        goals: state.goals.filter(goal => goal.id !== action.payload)
      };
    
    case 'SET_TRUST_INSIGHTS':
      return { ...state, trustInsights: action.payload };
    
    case 'SET_NETWORK_GRAPH':
      return { ...state, networkGraph: action.payload };
    
    case 'SELECT_CONTACT':
      return { ...state, selectedContact: action.payload };
    
    case 'SELECT_GOAL':
      return { ...state, selectedGoal: action.payload };
    
    case 'SET_CONTACT_FILTERS':
      return { 
        ...state, 
        filters: { ...state.filters, contacts: action.payload }
      };
    
    case 'SET_GOAL_FILTERS':
      return { 
        ...state, 
        filters: { ...state.filters, goals: action.payload }
      };
    
    default:
      return state;
  }
};

// Context
const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  actions: {
    // Auth actions
    setUser: (user: User | null) => void;
    setLoading: (loading: boolean) => void;
    logout: () => void;
    
    // Contact actions
    setContacts: (contacts: Contact[]) => void;
    addContact: (contact: Contact) => void;
    updateContact: (contact: Contact) => void;
    deleteContact: (contactId: string) => void;
    selectContact: (contact: Contact | null) => void;
    setContactFilters: (filters: any) => void;
    
    // Goal actions
    setGoals: (goals: Goal[]) => void;
    addGoal: (goal: Goal) => void;
    updateGoal: (goal: Goal) => void;
    deleteGoal: (goalId: string) => void;
    selectGoal: (goal: Goal | null) => void;
    setGoalFilters: (filters: any) => void;
    
    // Trust & Network actions
    setTrustInsights: (insights: TrustInsight[]) => void;
    setNetworkGraph: (graph: NetworkGraph) => void;
  };
} | null>(null);

// Provider component
export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Action creators
  const actions = {
    // Auth actions
    setUser: (user: User | null) => dispatch({ type: 'SET_USER', payload: user }),
    setLoading: (loading: boolean) => dispatch({ type: 'SET_LOADING', payload: loading }),
    logout: async () => {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          credentials: 'include'
        });
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        dispatch({ type: 'SET_USER', payload: null });
      }
    },
    
    // Contact actions
    setContacts: (contacts: Contact[]) => dispatch({ type: 'SET_CONTACTS', payload: contacts }),
    addContact: (contact: Contact) => dispatch({ type: 'ADD_CONTACT', payload: contact }),
    updateContact: (contact: Contact) => dispatch({ type: 'UPDATE_CONTACT', payload: contact }),
    deleteContact: (contactId: string) => dispatch({ type: 'DELETE_CONTACT', payload: contactId }),
    selectContact: (contact: Contact | null) => dispatch({ type: 'SELECT_CONTACT', payload: contact }),
    setContactFilters: (filters: any) => dispatch({ type: 'SET_CONTACT_FILTERS', payload: filters }),
    
    // Goal actions
    setGoals: (goals: Goal[]) => dispatch({ type: 'SET_GOALS', payload: goals }),
    addGoal: (goal: Goal) => dispatch({ type: 'ADD_GOAL', payload: goal }),
    updateGoal: (goal: Goal) => dispatch({ type: 'UPDATE_GOAL', payload: goal }),
    deleteGoal: (goalId: string) => dispatch({ type: 'DELETE_GOAL', payload: goalId }),
    selectGoal: (goal: Goal | null) => dispatch({ type: 'SELECT_GOAL', payload: goal }),
    setGoalFilters: (filters: any) => dispatch({ type: 'SET_GOAL_FILTERS', payload: filters }),
    
    // Trust & Network actions
    setTrustInsights: (insights: TrustInsight[]) => dispatch({ type: 'SET_TRUST_INSIGHTS', payload: insights }),
    setNetworkGraph: (graph: NetworkGraph) => dispatch({ type: 'SET_NETWORK_GRAPH', payload: graph }),
  };

  // Auto-load user session on app start
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include'
        });
        
        if (response.ok) {
          const userData = await response.json();
          actions.setUser(userData);
        } else {
          actions.setUser(null);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        actions.setUser(null);
      }
    };

    checkAuth();
  }, []);

  // Auto-load data when user is authenticated
  useEffect(() => {
    if (state.isAuthenticated && state.user) {
      loadAppData();
    }
  }, [state.isAuthenticated]);

  const loadAppData = async () => {
    try {
      // Load contacts, goals, and insights in parallel
      const [contactsRes, goalsRes, insightsRes, networkRes] = await Promise.all([
        fetch('/api/contacts', { credentials: 'include' }),
        fetch('/api/goals', { credentials: 'include' }),
        fetch('/api/trust/insights', { credentials: 'include' }),
        fetch('/api/network/graph', { credentials: 'include' })
      ]);

      if (contactsRes.ok) {
        const contacts = await contactsRes.json();
        actions.setContacts(contacts);
      }

      if (goalsRes.ok) {
        const goals = await goalsRes.json();
        actions.setGoals(goals);
      }

      if (insightsRes.ok) {
        const insights = await insightsRes.json();
        actions.setTrustInsights(insights);
      }

      if (networkRes.ok) {
        const network = await networkRes.json();
        actions.setNetworkGraph(network);
      }
    } catch (error) {
      console.error('Failed to load app data:', error);
    }
  };

  return (
    <AppContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </AppContext.Provider>
  );
};

// Hook to use the app context
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

// Selector hooks for specific state slices
export const useAuth = () => {
  const { state, actions } = useApp();
  return {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    logout: actions.logout
  };
};

export const useContacts = () => {
  const { state, actions } = useApp();
  return {
    contacts: state.contacts,
    selectedContact: state.selectedContact,
    filters: state.filters.contacts,
    actions: {
      setContacts: actions.setContacts,
      addContact: actions.addContact,
      updateContact: actions.updateContact,
      deleteContact: actions.deleteContact,
      selectContact: actions.selectContact,
      setFilters: actions.setContactFilters
    }
  };
};

export const useGoals = () => {
  const { state, actions } = useApp();
  return {
    goals: state.goals,
    selectedGoal: state.selectedGoal,
    filters: state.filters.goals,
    actions: {
      setGoals: actions.setGoals,
      addGoal: actions.addGoal,
      updateGoal: actions.updateGoal,
      deleteGoal: actions.deleteGoal,
      selectGoal: actions.selectGoal,
      setFilters: actions.setGoalFilters
    }
  };
};

export const useNetwork = () => {
  const { state, actions } = useApp();
  return {
    networkGraph: state.networkGraph,
    trustInsights: state.trustInsights,
    actions: {
      setNetworkGraph: actions.setNetworkGraph,
      setTrustInsights: actions.setTrustInsights
    }
  };
};