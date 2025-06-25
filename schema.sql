-- Users table
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contacts table
CREATE TABLE IF NOT EXISTS contacts (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  twitter TEXT,
  linkedin TEXT,
  notes TEXT,
  last_interaction TIMESTAMP,
  tags TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

-- Contact interactions table for follow-up tracking
CREATE TABLE IF NOT EXISTS contact_interactions (
  id TEXT PRIMARY KEY,
  contact_id TEXT,
  user_id TEXT,
  status TEXT, -- 'sent', 'replied', 'ignored', 'scheduled', 'completed'
  notes TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contact_id) REFERENCES contacts (id),
  FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON contacts (user_id);
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals (user_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_contact_id ON ai_suggestions (contact_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_goal_id ON ai_suggestions (goal_id);
CREATE INDEX IF NOT EXISTS idx_contact_interactions_contact_id ON contact_interactions (contact_id);
