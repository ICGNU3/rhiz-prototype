"""
Google Contacts OAuth2 Sync Service
Real contact integration with Google Contacts API using OAuth2 flow
"""

import os
import json
import secrets
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode, quote
import psycopg2
import psycopg2.extras

class GoogleContactsSync:
    def __init__(self):
        self.client_id = None  # Will be set from environment
        self.client_secret = None  # Will be set from environment
        self.redirect_uri = self._get_redirect_uri()
        self.scopes = [
            'https://www.googleapis.com/auth/contacts.readonly',
            'https://www.googleapis.com/auth/userinfo.email'
        ]
        
    def _get_redirect_uri(self):
        """Generate OAuth redirect URI based on environment"""
        base_url = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        if not base_url.startswith('http'):
            if 'replit.dev' in base_url:
                base_url = f'https://{base_url}'
            else:
                base_url = f'http://{base_url}'
        return f'{base_url}/api/oauth/google/callback'
    
    def _get_db_connection(self):
        """Get PostgreSQL database connection"""
        return psycopg2.connect(
            os.environ.get('DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    def check_credentials(self) -> bool:
        """Check if Google OAuth credentials are configured"""
        self.client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
        return bool(self.client_id and self.client_secret)
    
    def generate_oauth_url(self, user_id: str) -> str:
        """Generate OAuth authorization URL for Google Contacts"""
        if not self.check_credentials():
            raise ValueError("Google OAuth credentials not configured")
        
        # Generate secure state token
        state_token = secrets.token_urlsafe(32)
        
        # Store state in database with expiration
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO oauth_states (state_token, user_id, provider, redirect_uri, expires_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    state_token,
                    user_id,
                    'google',
                    self.redirect_uri,
                    datetime.now() + timedelta(minutes=10)
                ))
                conn.commit()
        finally:
            conn.close()
        
        # Build OAuth URL
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'state': state_token,
            'access_type': 'offline',
            'prompt': 'consent'  # Force consent to get refresh token
        }
        
        auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
        return auth_url
    
    def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens"""
        # Verify state token
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT user_id, expires_at FROM oauth_states 
                    WHERE state_token = %s AND provider = 'google'
                """, (state,))
                result = cur.fetchone()
                
                if not result:
                    raise ValueError("Invalid or expired state token")
                
                if datetime.now() > result['expires_at']:
                    raise ValueError("OAuth state expired")
                
                user_id = result['user_id']
                
                # Clean up used state token
                cur.execute("DELETE FROM oauth_states WHERE state_token = %s", (state,))
                conn.commit()
        finally:
            conn.close()
        
        # Exchange code for tokens
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if not response.ok:
            raise ValueError(f"Token exchange failed: {response.text}")
        
        tokens = response.json()
        
        # Store tokens and create/update contact source
        source_id = self._store_tokens(user_id, tokens)
        
        return {
            'user_id': user_id,
            'source_id': source_id,
            'status': 'connected',
            'message': 'Google Contacts connected successfully'
        }
    
    def _store_tokens(self, user_id: str, tokens: Dict[str, Any]) -> str:
        """Store OAuth tokens and create/update contact source"""
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 3600)
        
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                # Check if Google source already exists for user
                cur.execute("""
                    SELECT id FROM contact_sources 
                    WHERE user_id = %s AND source_type = 'google'
                """, (user_id,))
                existing = cur.fetchone()
                
                if existing:
                    # Update existing source
                    cur.execute("""
                        UPDATE contact_sources SET
                            access_token = %s,
                            refresh_token = %s,
                            token_expires_at = %s,
                            is_active = true,
                            sync_status = 'pending',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (access_token, refresh_token, expires_at, existing['id']))
                    source_id = existing['id']
                else:
                    # Create new source
                    source_id = f"google_{user_id}_{secrets.token_hex(8)}"
                    cur.execute("""
                        INSERT INTO contact_sources (
                            id, user_id, source_type, source_id, access_token, 
                            refresh_token, token_expires_at, is_active, sync_status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        source_id, user_id, 'google', 'google_contacts',
                        access_token, refresh_token, expires_at, True, 'pending'
                    ))
                
                conn.commit()
                return source_id
        finally:
            conn.close()
    
    def refresh_access_token(self, source_id: str) -> bool:
        """Refresh expired access token using refresh token"""
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT refresh_token FROM contact_sources 
                    WHERE id = %s AND source_type = 'google'
                """, (source_id,))
                result = cur.fetchone()
                
                if not result or not result['refresh_token']:
                    return False
                
                refresh_token = result['refresh_token']
                
                # Request new access token
                token_data = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                }
                
                response = requests.post(
                    'https://oauth2.googleapis.com/token',
                    data=token_data
                )
                
                if not response.ok:
                    return False
                
                tokens = response.json()
                access_token = tokens.get('access_token')
                expires_in = tokens.get('expires_in', 3600)
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update stored tokens
                cur.execute("""
                    UPDATE contact_sources SET
                        access_token = %s,
                        token_expires_at = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (access_token, expires_at, source_id))
                conn.commit()
                
                return True
        finally:
            conn.close()
    
    def sync_contacts(self, user_id: str, source_id: str) -> Dict[str, Any]:
        """Sync contacts from Google Contacts API"""
        conn = self._get_db_connection()
        
        try:
            # Get source details
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT access_token, token_expires_at FROM contact_sources 
                    WHERE id = %s AND user_id = %s AND source_type = 'google'
                """, (source_id, user_id))
                source = cur.fetchone()
                
                if not source:
                    raise ValueError("Google Contacts source not found")
                
                # Check if token needs refresh
                if datetime.now() >= source['token_expires_at']:
                    if not self.refresh_access_token(source_id):
                        raise ValueError("Failed to refresh access token")
                    
                    # Get updated token
                    cur.execute("""
                        SELECT access_token FROM contact_sources WHERE id = %s
                    """, (source_id,))
                    source = cur.fetchone()
                
                access_token = source['access_token']
            
            # Create sync job
            job_id = self._create_sync_job(user_id, source_id, 'manual')
            
            try:
                # Fetch contacts from Google
                contacts_data = self._fetch_google_contacts(access_token)
                
                # Process and store contacts
                results = self._process_contacts(user_id, source_id, job_id, contacts_data)
                
                # Complete sync job
                self._complete_sync_job(job_id, 'completed', results)
                
                return {
                    'status': 'success',
                    'job_id': job_id,
                    'total_contacts': results['total'],
                    'new_contacts': results['new'],
                    'updated_contacts': results['updated'],
                    'failed_contacts': results['failed']
                }
                
            except Exception as e:
                self._complete_sync_job(job_id, 'failed', {'error': str(e)})
                raise
                
        finally:
            conn.close()
    
    def _create_sync_job(self, user_id: str, source_id: str, job_type: str) -> str:
        """Create a new sync job record"""
        job_id = f"job_{secrets.token_hex(8)}"
        
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sync_jobs (id, user_id, source_id, job_type, status)
                    VALUES (%s, %s, %s, %s, 'running')
                """, (job_id, user_id, source_id, job_type))
                conn.commit()
        finally:
            conn.close()
        
        return job_id
    
    def _fetch_google_contacts(self, access_token: str) -> List[Dict[str, Any]]:
        """Fetch contacts from Google Contacts API"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        all_contacts = []
        next_page_token = None
        
        while True:
            url = 'https://people.googleapis.com/v1/people/me/connections'
            params = {
                'personFields': 'names,emailAddresses,phoneNumbers,organizations,metadata',
                'pageSize': 100
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            response = requests.get(url, headers=headers, params=params)
            
            if not response.ok:
                raise ValueError(f"Google API error: {response.text}")
            
            data = response.json()
            contacts = data.get('connections', [])
            all_contacts.extend(contacts)
            
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
        
        return all_contacts
    
    def _process_contacts(self, user_id: str, source_id: str, job_id: str, contacts_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process and store Google contacts"""
        results = {'total': 0, 'new': 0, 'updated': 0, 'failed': 0}
        
        conn = self._get_db_connection()
        try:
            for contact_data in contacts_data:
                try:
                    self._process_single_contact(conn, user_id, source_id, job_id, contact_data, results)
                except Exception as e:
                    results['failed'] += 1
                    self._log_sync_error(conn, job_id, contact_data, str(e))
                
                results['total'] += 1
        finally:
            conn.close()
        
        return results
    
    def _process_single_contact(self, conn, user_id: str, source_id: str, job_id: str, contact_data: Dict[str, Any], results: Dict[str, int]):
        """Process a single Google contact"""
        # Extract contact information
        resource_name = contact_data.get('resourceName', '')
        external_id = resource_name.split('/')[-1] if resource_name else None
        
        if not external_id:
            raise ValueError("No resource name found")
        
        # Get name
        names = contact_data.get('names', [])
        name = ''
        if names:
            name_parts = []
            if names[0].get('givenName'):
                name_parts.append(names[0]['givenName'])
            if names[0].get('familyName'):
                name_parts.append(names[0]['familyName'])
            name = ' '.join(name_parts)
        
        # Get email
        email = ''
        emails = contact_data.get('emailAddresses', [])
        if emails:
            email = emails[0].get('value', '')
        
        # Get organization
        company = ''
        organizations = contact_data.get('organizations', [])
        if organizations:
            company = organizations[0].get('name', '')
        
        # Skip contacts without name or email
        if not name and not email:
            raise ValueError("Contact has no name or email")
        
        with conn.cursor() as cur:
            # Check if contact already exists
            cur.execute("""
                SELECT id FROM contacts 
                WHERE user_id = %s AND (email = %s OR name = %s)
                LIMIT 1
            """, (user_id, email, name))
            existing = cur.fetchone()
            
            if existing:
                # Update existing contact
                cur.execute("""
                    UPDATE contacts SET
                        name = COALESCE(NULLIF(%s, ''), name),
                        email = COALESCE(NULLIF(%s, ''), email),
                        company = COALESCE(NULLIF(%s, ''), company),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (name, email, company, existing['id']))
                
                contact_id = existing['id']
                action = 'updated'
                results['updated'] += 1
            else:
                # Create new contact
                contact_id = f"contact_{secrets.token_hex(8)}"
                cur.execute("""
                    INSERT INTO contacts (id, user_id, name, email, company, source)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (contact_id, user_id, name, email, company, 'google'))
                
                action = 'created'
                results['new'] += 1
            
            # Log sync action
            self._log_sync_action(conn, job_id, external_id, contact_id, action, f"Google contact: {name}")
            
            conn.commit()
    
    def _log_sync_action(self, conn, job_id: str, external_id: str, contact_id: str, action: str, details: str):
        """Log a successful sync action"""
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_logs (job_id, contact_external_id, contact_id, action, details)
                VALUES (%s, %s, %s, %s, %s)
            """, (job_id, external_id, contact_id, action, details))
    
    def _log_sync_error(self, conn, job_id: str, contact_data: Dict[str, Any], error: str):
        """Log a sync error"""
        external_id = contact_data.get('resourceName', '').split('/')[-1] if contact_data.get('resourceName') else 'unknown'
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_logs (job_id, contact_external_id, action, error_message)
                VALUES (%s, %s, %s, %s)
            """, (job_id, external_id, 'failed', error))
    
    def _complete_sync_job(self, job_id: str, status: str, results: Dict[str, Any]):
        """Complete a sync job with results"""
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sync_jobs SET
                        status = %s,
                        completed_at = CURRENT_TIMESTAMP,
                        total_contacts = %s,
                        new_contacts = %s,
                        updated_contacts = %s,
                        failed_contacts = %s,
                        error_message = %s,
                        metadata = %s
                    WHERE id = %s
                """, (
                    status,
                    results.get('total', 0),
                    results.get('new', 0),
                    results.get('updated', 0),
                    results.get('failed', 0),
                    results.get('error'),
                    json.dumps(results),
                    job_id
                ))
                conn.commit()
        finally:
            conn.close()
    
    def get_sync_status(self, user_id: str) -> List[Dict[str, Any]]:
        """Get sync status for user's Google Contacts"""
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        cs.id,
                        cs.source_type,
                        cs.is_active,
                        cs.last_sync_at,
                        cs.sync_status,
                        cs.sync_error,
                        cs.total_contacts_synced,
                        cs.created_at
                    FROM contact_sources cs
                    WHERE cs.user_id = %s AND cs.source_type = 'google'
                    ORDER BY cs.created_at DESC
                """, (user_id,))
                
                sources = cur.fetchall()
                
                # Get recent sync jobs for each source
                for source in sources:
                    cur.execute("""
                        SELECT status, started_at, completed_at, total_contacts, error_message
                        FROM sync_jobs
                        WHERE source_id = %s
                        ORDER BY started_at DESC
                        LIMIT 5
                    """, (source['id'],))
                    source['recent_jobs'] = cur.fetchall()
                
                return [dict(source) for source in sources]
        finally:
            conn.close()
    
    def get_sync_logs(self, user_id: str, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get detailed sync logs for transparency"""
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                if job_id:
                    cur.execute("""
                        SELECT sl.*, sj.source_id
                        FROM sync_logs sl
                        JOIN sync_jobs sj ON sl.job_id = sj.id
                        WHERE sl.job_id = %s AND sj.user_id = %s
                        ORDER BY sl.created_at DESC
                    """, (job_id, user_id))
                else:
                    cur.execute("""
                        SELECT sl.*, sj.source_id
                        FROM sync_logs sl
                        JOIN sync_jobs sj ON sl.job_id = sj.id
                        WHERE sj.user_id = %s
                        ORDER BY sl.created_at DESC
                        LIMIT 100
                    """, (user_id,))
                
                return [dict(log) for log in cur.fetchall()]
        finally:
            conn.close()