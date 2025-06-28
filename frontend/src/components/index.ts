/**
 * Unified Component Index - Centralized Export System
 * 
 * This file organizes all components into logical groups and provides
 * a single source for importing components throughout the application.
 * 
 * Component Organization:
 * - Authentication: Login and auth-related components
 * - Contact Management: All contact-related functionality unified
 * - Trust & Insights: Relationship intelligence and trust scoring
 * - Onboarding: User onboarding workflow components
 * - Layout & Navigation: App structure components
 * - Intelligence: AI-powered features and interfaces
 * - Network Visualization: Graph and network displays
 * - Goals: Goal management and tracking
 * - Settings: User preferences and configuration
 */

// Authentication Components
export { default as Login } from './auth/Login';

// Contact Management (Unified)
export { default as UnifiedContactImport } from './contacts/UnifiedContactImport';

// Trust & Relationship Intelligence (Unified)
export { default as UnifiedTrustDashboard } from './trust/UnifiedTrustDashboard';

// Onboarding Components
export { default as NetworkOnboarding } from './onboarding/NetworkOnboarding';

// Layout & Navigation
export { default as Navbar } from './layout/Navbar';

// AI & Intelligence Features
export { default as AIConversationInterface } from './intelligence/AIConversationInterface';

// Network Visualization
export { default as RhizomaticGraph } from './network/RhizomaticGraph';

// Goal Management
export { default as GoalList } from './goals/GoalList';

// Settings (Remaining component from features)
export { default as SettingsPanel } from './features/SettingsPanel';

/**
 * Component Consolidation Notes:
 * 
 * REMOVED REDUNDANT COMPONENTS:
 * - ContactImportModal.tsx → Replaced by UnifiedContactImport
 * - TrustPanel.tsx → Replaced by UnifiedTrustDashboard
 * - TrustInsightsDashboard.tsx → Replaced by UnifiedTrustDashboard
 * 
 * CONSOLIDATED FUNCTIONALITY:
 * 1. Contact Import: All import methods (Google, LinkedIn, Apple, CSV, Manual) 
 *    unified into single UnifiedContactImport component
 * 2. Trust Intelligence: All trust features (scoring, insights, tiers, actions)
 *    unified into single UnifiedTrustDashboard component
 * 
 * COMPONENT DESIGN STANDARDS:
 * - All components follow glassmorphism design system
 * - TypeScript for type safety
 * - Modular prop interfaces for flexibility
 * - Consistent naming conventions
 * - Single responsibility principle
 * - Reusable across different contexts (modal, page, onboarding)
 */

// Type exports for convenience
export type { ContactImportSource } from '../types/api';

// Style exports for CSS-in-JS components
export { UnifiedContactImportStyles } from './contacts/UnifiedContactImport';
export { UnifiedTrustDashboardStyles } from './trust/UnifiedTrustDashboard';