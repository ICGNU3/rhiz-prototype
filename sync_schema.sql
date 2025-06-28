-- Sync Integrations Schema Extensions
-- Add real contact sync capabilities with OAuth2 support

-- Contact Sources and Integration Status
CREATE TABLE IF NOT EXISTS contact_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL, -- 'google', 'linkedin', 'twitter', 'csv'
    source_name VARCHAR(100) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'syncing', 'completed', 'failed'
    sync_error TEXT,
    total_contacts_synced INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sync Jobs - Track individual sync operations
CREATE TABLE IF NOT EXISTS sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_id UUID REFERENCES contact_sources(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL, -- 'full_sync', 'incremental', 'manual'
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed', 'cancelled'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_contacts INTEGER DEFAULT 0,
    processed_contacts INTEGER DEFAULT 0,
    new_contacts INTEGER DEFAULT 0,
    updated_contacts INTEGER DEFAULT 0,
    failed_contacts INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB -- Store additional sync details
);

-- Sync Logs - Detailed transparency logs
CREATE TABLE IF NOT EXISTS sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES sync_jobs(id) ON DELETE CASCADE,
    contact_external_id VARCHAR(255),
    contact_id UUID REFERENCES contacts(id),
    action VARCHAR(50) NOT NULL, -- 'created', 'updated', 'skipped', 'failed'
    details TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OAuth States - Secure OAuth flow tracking
CREATE TABLE IF NOT EXISTS oauth_states (
    state_token VARCHAR(255) PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    redirect_uri VARCHAR(500),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contact External IDs - Map external provider IDs to internal contacts
CREATE TABLE IF NOT EXISTS contact_external_ids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES contact_sources(id) ON DELETE CASCADE,
    external_id VARCHAR(255) NOT NULL,
    external_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, external_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_contact_sources_user_id ON contact_sources(user_id);
CREATE INDEX IF NOT EXISTS idx_contact_sources_source_type ON contact_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_user_id ON sync_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON sync_jobs(status);
CREATE INDEX IF NOT EXISTS idx_sync_logs_job_id ON sync_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_oauth_states_expires_at ON oauth_states(expires_at);
CREATE INDEX IF NOT EXISTS idx_contact_external_ids_contact_id ON contact_external_ids(contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_external_ids_source_id ON contact_external_ids(source_id);

-- Update function for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_contact_sources_updated_at BEFORE UPDATE ON contact_sources FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();