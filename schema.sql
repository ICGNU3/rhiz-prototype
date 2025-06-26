-- Enhanced Users table with authentication and subscription tiers
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  google_id TEXT,
  magic_link_token TEXT,
  magic_link_expires TIMESTAMP,
  subscription_tier TEXT DEFAULT 'explorer', -- explorer (free), founder_plus (paid)
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  subscription_status TEXT DEFAULT 'active', -- active, canceled, past_due
  subscription_expires TIMESTAMP,
  goals_count INTEGER DEFAULT 0,
  contacts_count INTEGER DEFAULT 0,
  ai_suggestions_used INTEGER DEFAULT 0,
  is_guest BOOLEAN DEFAULT FALSE,
  guest_actions_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced Contacts table with CRM intelligence
CREATE TABLE IF NOT EXISTS contacts (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  twitter TEXT,
  linkedin TEXT,
  handle TEXT, -- Generic social handle
  relationship_type TEXT DEFAULT 'Contact', -- Ally, Investor, Collaborator, Press, etc.
  warmth_status INTEGER DEFAULT 1, -- 1-5 scale (1=Cold, 2=Aware, 3=Warm, 4=Active, 5=Contributor)
  warmth_label TEXT DEFAULT 'Cold', -- Cold, Aware, Warm, Active, Contributor
  last_interaction_date TIMESTAMP,
  last_contact_method TEXT, -- Email, Call, Social, In-Person
  priority_level TEXT DEFAULT 'Medium', -- High, Medium, Low
  notes TEXT,
  narrative_thread TEXT, -- Brief context and tone cues
  follow_up_action TEXT,
  follow_up_due_date TIMESTAMP,
  tags TEXT, -- Interests, Geography, Introduced By, etc.
  introduced_by TEXT,
  location TEXT,
  company TEXT,
  title TEXT,
  interests TEXT,
  interaction_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Goals table
CREATE TABLE IF NOT EXISTS goals (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  embedding TEXT, -- JSON array of floats
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id)
);

-- AI suggestions table
CREATE TABLE IF NOT EXISTS ai_suggestions (
  id TEXT PRIMARY KEY,
  contact_id TEXT,
  goal_id TEXT,
  suggestion TEXT,
  confidence REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contact_id) REFERENCES contacts (id),
  FOREIGN KEY (goal_id) REFERENCES goals (id)
);

-- Enhanced Contact interactions table for detailed CRM tracking
CREATE TABLE IF NOT EXISTS contact_interactions (
  id TEXT PRIMARY KEY,
  contact_id TEXT,
  user_id TEXT,
  interaction_type TEXT, -- Email, Call, Social, In-Person, Meeting, Text, etc.
  status TEXT, -- sent, replied, ignored, scheduled, completed, missed
  direction TEXT, -- inbound, outbound
  subject TEXT, -- Email subject or call topic
  summary TEXT, -- Brief summary of interaction
  sentiment TEXT, -- positive, neutral, negative
  notes TEXT,
  follow_up_needed BOOLEAN DEFAULT FALSE,
  follow_up_action TEXT,
  follow_up_date TIMESTAMP,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  duration_minutes INTEGER, -- For calls/meetings
  FOREIGN KEY (contact_id) REFERENCES contacts (id),
  FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Contact relationship mapping for introductions
CREATE TABLE IF NOT EXISTS contact_relationships (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  contact_a_id TEXT,
  contact_b_id TEXT,
  relationship_type TEXT, -- knows, worked_with, invested_in, introduced, etc.
  strength INTEGER DEFAULT 1, -- 1-5 scale
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (contact_a_id) REFERENCES contacts (id),
  FOREIGN KEY (contact_b_id) REFERENCES contacts (id)
);

-- Contact warming pipeline stages
CREATE TABLE IF NOT EXISTS contact_pipeline_history (
  id TEXT PRIMARY KEY,
  contact_id TEXT,
  user_id TEXT,
  from_stage TEXT,
  to_stage TEXT,
  notes TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contact_id) REFERENCES contacts (id),
  FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Daily/weekly outreach suggestions
CREATE TABLE IF NOT EXISTS outreach_suggestions (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  contact_id TEXT,
  suggestion_type TEXT, -- follow_up, nurture, introduction, check_in
  priority_score REAL,
  reason TEXT,
  suggested_action TEXT,
  suggested_message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  acted_on BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (contact_id) REFERENCES contacts (id)
);

-- Create indexes for better CRM performance
CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON contacts (user_id);
CREATE INDEX IF NOT EXISTS idx_contacts_warmth_status ON contacts (warmth_status);
CREATE INDEX IF NOT EXISTS idx_contacts_priority_level ON contacts (priority_level);
CREATE INDEX IF NOT EXISTS idx_contacts_relationship_type ON contacts (relationship_type);
CREATE INDEX IF NOT EXISTS idx_contacts_last_interaction ON contacts (last_interaction_date);
CREATE INDEX IF NOT EXISTS idx_contacts_follow_up_due ON contacts (follow_up_due_date);
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals (user_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_contact_id ON ai_suggestions (contact_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_goal_id ON ai_suggestions (goal_id);
CREATE INDEX IF NOT EXISTS idx_contact_interactions_contact_id ON contact_interactions (contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_interactions_timestamp ON contact_interactions (timestamp);
CREATE INDEX IF NOT EXISTS idx_contact_relationships_user_id ON contact_relationships (user_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_history_contact_id ON contact_pipeline_history (contact_id);
CREATE INDEX IF NOT EXISTS idx_outreach_suggestions_user_id ON outreach_suggestions (user_id);
CREATE INDEX IF NOT EXISTS idx_outreach_suggestions_priority ON outreach_suggestions (priority_score DESC);

-- Conference Mode Tables
CREATE TABLE IF NOT EXISTS conferences (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    location TEXT,
    start_date TEXT,
    end_date TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS conference_contacts (
    id TEXT PRIMARY KEY,
    conference_id TEXT NOT NULL,
    contact_id TEXT NOT NULL,
    conversation_notes TEXT,
    voice_memo TEXT,
    badge_photo_text TEXT,
    captured_at TEXT NOT NULL,
    FOREIGN KEY (conference_id) REFERENCES conferences (id),
    FOREIGN KEY (contact_id) REFERENCES contacts (id)
);

CREATE TABLE IF NOT EXISTS conference_ai_analysis (
    id TEXT PRIMARY KEY,
    contact_id TEXT NOT NULL,
    analysis_data TEXT, -- JSON object with AI insights
    created_at TEXT NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts (id)
);

CREATE TABLE IF NOT EXISTS conference_follow_ups (
    id TEXT PRIMARY KEY,
    conference_id TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    reason TEXT,
    message TEXT,
    timing TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (conference_id) REFERENCES conferences (id)
);

-- Conference Mode Indexes
CREATE INDEX IF NOT EXISTS idx_conferences_user ON conferences(user_id);
CREATE INDEX IF NOT EXISTS idx_conferences_active ON conferences(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_conference_contacts_conference ON conference_contacts(conference_id);
CREATE INDEX IF NOT EXISTS idx_conference_contacts_contact ON conference_contacts(contact_id);
CREATE INDEX IF NOT EXISTS idx_conference_follow_ups_conference ON conference_follow_ups(conference_id);
CREATE INDEX IF NOT EXISTS idx_conference_follow_ups_timing ON conference_follow_ups(timing, completed);

-- Usage tracking for tier enforcement
CREATE TABLE IF NOT EXISTS usage_tracking (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  action_type TEXT NOT NULL, -- goal_created, contact_imported, ai_suggestion_generated, outreach_sent
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata TEXT, -- JSON object with additional context
  FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Magic link authentication
CREATE TABLE IF NOT EXISTS magic_links (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL,
  token TEXT UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guest sessions tracking
CREATE TABLE IF NOT EXISTS guest_sessions (
  id TEXT PRIMARY KEY,
  session_token TEXT UNIQUE NOT NULL,
  goals_created INTEGER DEFAULT 0,
  contacts_added INTEGER DEFAULT 0,
  actions_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP
);

-- Subscription history for analytics
CREATE TABLE IF NOT EXISTS subscription_history (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  action TEXT NOT NULL, -- upgraded, downgraded, canceled, renewed
  from_tier TEXT,
  to_tier TEXT,
  stripe_event_id TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Monica-Inspired CRM Features

-- 1. Automatic Reminders & Notifications
CREATE TABLE IF NOT EXISTS reminders (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  reminder_type TEXT NOT NULL, -- birthday, anniversary, follow_up, custom
  due_date TIMESTAMP NOT NULL,
  is_recurring BOOLEAN DEFAULT FALSE,
  recurrence_pattern TEXT, -- weekly, monthly, yearly
  is_completed BOOLEAN DEFAULT FALSE,
  notification_sent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (contact_id) REFERENCES contacts (id)
);

-- 2. Relationship Labels + History Tracking (enhancing existing interaction_logs)
-- Adding birthday and anniversary fields to contacts
ALTER TABLE contacts ADD COLUMN birthday TEXT;
ALTER TABLE contacts ADD COLUMN anniversary TEXT;
ALTER TABLE contacts ADD COLUMN relationship_labels TEXT; -- JSON array of labels like ["investor", "advisor", "collaborator"]

-- 3. Private Journal Entries
CREATE TABLE IF NOT EXISTS journal_entries (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  title TEXT,
  content TEXT NOT NULL,
  entry_type TEXT DEFAULT 'note', -- note, observation, meeting_notes, personal
  is_private BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (contact_id) REFERENCES contacts (id)
);

-- 4. Task Management / To-Dos per Contact
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  contact_id TEXT,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'todo', -- todo, in_progress, done
  priority TEXT DEFAULT 'medium', -- low, medium, high
  due_date TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (contact_id) REFERENCES contacts (id)
);

-- 5. File Attachments or Document Links per Contact
CREATE TABLE IF NOT EXISTS attachments (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  filename TEXT NOT NULL,
  original_filename TEXT NOT NULL,
  file_path TEXT,
  file_url TEXT, -- For links instead of uploads
  file_size INTEGER,
  file_type TEXT,
  description TEXT,
  is_link BOOLEAN DEFAULT FALSE, -- TRUE for URLs, FALSE for uploads
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (contact_id) REFERENCES contacts (id)
);

-- Indexes for Monica-inspired features
CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders (user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_contact_id ON reminders (contact_id);
CREATE INDEX IF NOT EXISTS idx_reminders_due_date ON reminders (due_date);
CREATE INDEX IF NOT EXISTS idx_reminders_is_completed ON reminders (is_completed);

CREATE INDEX IF NOT EXISTS idx_journal_entries_user_id ON journal_entries (user_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_contact_id ON journal_entries (contact_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_created_at ON journal_entries (created_at);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks (user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_contact_id ON tasks (contact_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date);

CREATE INDEX IF NOT EXISTS idx_attachments_user_id ON attachments (user_id);
CREATE INDEX IF NOT EXISTS idx_attachments_contact_id ON attachments (contact_id);

-- Additional indexes for authentication and billing
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer ON users (stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users (subscription_tier);
CREATE INDEX IF NOT EXISTS idx_magic_links_token ON magic_links (token);
CREATE INDEX IF NOT EXISTS idx_magic_links_email ON magic_links (email);
CREATE INDEX IF NOT EXISTS idx_guest_sessions_token ON guest_sessions (session_token);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user ON usage_tracking (user_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_action ON usage_tracking (action_type);
CREATE INDEX IF NOT EXISTS idx_subscription_history_user ON subscription_history (user_id);
