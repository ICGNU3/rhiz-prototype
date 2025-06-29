"""
Contact Sync Engine
Handles multi-source contact synchronization and deduplication
"""

import logging
import json
import csv
import io
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class ContactSyncEngine:
    """Contact synchronization engine with intelligent deduplication"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.supported_sources = ['csv', 'google', 'linkedin', 'outlook', 'manual']
    
    def get_status(self) -> Dict[str, str]:
        """Return service status"""
        return {
            "status": "operational",
            "service": "contact_sync_engine",
            "sources": len(self.supported_sources)
        }
        
    def import_csv_contacts(self, user_id: str, csv_content: str, source: str = 'csv') -> Dict[str, Any]:
        """Import contacts from CSV content"""
        try:
            results = {
                'imported': 0,
                'duplicates': 0,
                'errors': 0,
                'contacts': []
            }
            
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    contact_data = self._normalize_csv_row(row)
                    if not contact_data.get('name') and not contact_data.get('email'):
                        results['errors'] += 1
                        continue
                    
                    # Check for duplicates
                    if self._is_duplicate_contact(user_id, contact_data):
                        results['duplicates'] += 1
                        continue
                    
                    # Create contact
                    contact_id = self._create_contact(user_id, contact_data, source)
                    if contact_id:
                        results['imported'] += 1
                        results['contacts'].append({
                            'id': contact_id,
                            'name': contact_data.get('name'),
                            'email': contact_data.get('email'),
                            'company': contact_data.get('company')
                        })
                    else:
                        results['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing CSV row {row_num}: {e}")
                    results['errors'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error importing CSV contacts: {e}")
            return {'error': str(e), 'imported': 0, 'duplicates': 0, 'errors': 1}

    def _normalize_csv_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normalize CSV row to standard contact format"""
        # Common field mappings
        field_mappings = {
            'name': ['name', 'full_name', 'display_name', 'contact_name', 'first_name'],
            'email': ['email', 'email_address', 'primary_email', 'work_email'],
            'phone': ['phone', 'phone_number', 'mobile', 'cell_phone', 'work_phone'],
            'company': ['company', 'organization', 'employer', 'work_company'],
            'title': ['title', 'job_title', 'position', 'role', 'work_title'],
            'linkedin': ['linkedin', 'linkedin_url', 'linkedin_profile'],
            'location': ['location', 'city', 'address', 'work_location'],
            'notes': ['notes', 'description', 'bio', 'about']
        }
        
        contact_data = {}
        
        # Normalize field names (case-insensitive)
        normalized_row = {k.lower().strip(): v.strip() for k, v in row.items() if v and v.strip()}
        
        for standard_field, possible_fields in field_mappings.items():
            for field in possible_fields:
                if field in normalized_row and normalized_row[field]:
                    contact_data[standard_field] = normalized_row[field]
                    break
        
        # Handle name fields specially
        if 'name' not in contact_data:
            first_name = normalized_row.get('first_name', '')
            last_name = normalized_row.get('last_name', '')
            if first_name or last_name:
                contact_data['name'] = f"{first_name} {last_name}".strip()
        
        return contact_data

    def _is_duplicate_contact(self, user_id: str, contact_data: Dict[str, Any]) -> bool:
        """Check if contact already exists"""
        try:
            if not self.db:
                return False
                
            cursor = self.db.cursor()
            
            # Check by email first (most reliable)
            email = contact_data.get('email')
            if email:
                cursor.execute("""
                    SELECT id FROM contacts 
                    WHERE user_id = %s AND LOWER(email) = LOWER(%s)
                """, (user_id, email))
                if cursor.fetchone():
                    return True
            
            # Check by name if no email
            name = contact_data.get('name')
            if name and not email:
                cursor.execute("""
                    SELECT id FROM contacts 
                    WHERE user_id = %s AND LOWER(name) = LOWER(%s)
                """, (user_id, name))
                if cursor.fetchone():
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for duplicate contact: {e}")
            return False

    def _create_contact(self, user_id: str, contact_data: Dict[str, Any], source: str) -> Optional[str]:
        """Create new contact in database"""
        try:
            if not self.db:
                return None
                
            cursor = self.db.cursor()
            
            # Generate contact ID
            contact_id = self._generate_contact_id(contact_data)
            
            cursor.execute("""
                INSERT INTO contacts (
                    id, user_id, name, email, phone, company, title, 
                    linkedin, location, notes, relationship_type, 
                    warmth_status, warmth_label, priority_level, 
                    created_at, source
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, 
                    %s, %s, %s, 
                    %s, %s
                )
            """, (
                contact_id, user_id,
                contact_data.get('name'),
                contact_data.get('email'),
                contact_data.get('phone'),
                contact_data.get('company'),
                contact_data.get('title'),
                contact_data.get('linkedin'),
                contact_data.get('location'),
                contact_data.get('notes'),
                'Contact',  # default relationship_type
                1,  # default warmth_status (Cold)
                'Cold',  # default warmth_label
                'Medium',  # default priority_level
                datetime.now(),
                source
            ))
            
            self.db.commit()
            return contact_id
            
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            self.db.rollback()
            return None

    def _generate_contact_id(self, contact_data: Dict[str, Any]) -> str:
        """Generate unique contact ID"""
        # Use email if available, otherwise name + timestamp
        identifier = contact_data.get('email') or contact_data.get('name') or str(datetime.now())
        return hashlib.md5(f"{identifier}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]

    def get_sync_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        """Get sync job history for user"""
        try:
            if not self.db:
                return []
                
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, source, status, imported_count, duplicate_count, error_count, 
                       created_at, completed_at, error_message
                FROM sync_jobs 
                WHERE user_id = %s 
                ORDER BY created_at DESC
                LIMIT 20
            """, (user_id,))
            
            jobs = []
            for row in cursor.fetchall():
                jobs.append({
                    'id': row[0],
                    'source': row[1],
                    'status': row[2],
                    'imported_count': row[3],
                    'duplicate_count': row[4],
                    'error_count': row[5],
                    'created_at': row[6],
                    'completed_at': row[7],
                    'error_message': row[8]
                })
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting sync jobs: {e}")
            return []

    def create_sync_job(self, user_id: str, source: str) -> str:
        """Create new sync job record"""
        try:
            if not self.db:
                return None
                
            cursor = self.db.cursor()
            job_id = hashlib.md5(f"{user_id}_{source}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            cursor.execute("""
                INSERT INTO sync_jobs (id, user_id, source, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (job_id, user_id, source, 'pending', datetime.now()))
            
            self.db.commit()
            return job_id
            
        except Exception as e:
            logger.error(f"Error creating sync job: {e}")
            return None

    def update_sync_job(self, job_id: str, status: str, results: Dict[str, Any] = None):
        """Update sync job with results"""
        try:
            if not self.db:
                return
                
            cursor = self.db.cursor()
            
            if results:
                cursor.execute("""
                    UPDATE sync_jobs 
                    SET status = %s, imported_count = %s, duplicate_count = %s, 
                        error_count = %s, completed_at = %s, error_message = %s
                    WHERE id = %s
                """, (
                    status,
                    results.get('imported', 0),
                    results.get('duplicates', 0),
                    results.get('errors', 0),
                    datetime.now(),
                    results.get('error'),
                    job_id
                ))
            else:
                cursor.execute("""
                    UPDATE sync_jobs SET status = %s WHERE id = %s
                """, (status, job_id))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating sync job: {e}")

    def get_merge_candidates(self, user_id: str) -> List[Dict[str, Any]]:
        """Find potential duplicate contacts for merging"""
        try:
            if not self.db:
                return []
                
            cursor = self.db.cursor()
            
            # Find contacts with similar names or emails
            cursor.execute("""
                SELECT c1.id as id1, c1.name as name1, c1.email as email1, c1.company as company1,
                       c2.id as id2, c2.name as name2, c2.email as email2, c2.company as company2,
                       CASE 
                           WHEN c1.email = c2.email THEN 'email'
                           WHEN LOWER(c1.name) = LOWER(c2.name) THEN 'name'
                           ELSE 'similar'
                       END as match_type
                FROM contacts c1
                JOIN contacts c2 ON c1.user_id = c2.user_id 
                WHERE c1.user_id = %s 
                AND c1.id < c2.id
                AND (
                    (c1.email IS NOT NULL AND c1.email = c2.email) OR
                    (LOWER(c1.name) = LOWER(c2.name))
                )
                LIMIT 50
            """, (user_id,))
            
            candidates = []
            for row in cursor.fetchall():
                candidates.append({
                    'contact1': {
                        'id': row[0],
                        'name': row[1],
                        'email': row[2],
                        'company': row[3]
                    },
                    'contact2': {
                        'id': row[4],
                        'name': row[5],
                        'email': row[6],
                        'company': row[7]
                    },
                    'match_type': row[8],
                    'confidence': 0.9 if row[8] == 'email' else 0.7
                })
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error finding merge candidates: {e}")
            return []

    def get_oauth_url(self, source: str, user_id: str) -> Dict[str, Any]:
        """Get OAuth URL for external service integration"""
        # This would integrate with actual OAuth providers
        # For now, return placeholder URLs
        oauth_urls = {
            'google': f"https://accounts.google.com/oauth/authorize?client_id=your_google_client_id&redirect_uri=your_redirect_uri&scope=https://www.googleapis.com/auth/contacts.readonly&response_type=code&state={user_id}",
            'linkedin': f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=your_linkedin_client_id&redirect_uri=your_redirect_uri&state={user_id}&scope=r_liteprofile%20r_emailaddress",
            'outlook': f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=your_outlook_client_id&response_type=code&redirect_uri=your_redirect_uri&scope=https://graph.microsoft.com/contacts.read&state={user_id}"
        }
        
        if source in oauth_urls:
            return {
                'url': oauth_urls[source],
                'source': source,
                'status': 'ready'
            }
        else:
            return {
                'error': f'Unsupported OAuth source: {source}',
                'status': 'error'
            }
    
    def init_sync_tables(self):
        """Initialize tables for contact syncing"""
        import sqlite3
        
        try:
            # Use SQLite connection
            db = sqlite3.connect('db.sqlite3')
            cursor = db.cursor()
            
            # Contact sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id TEXT,
                    source TEXT NOT NULL,
                    source_id TEXT,
                    raw_data TEXT,
                    sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_primary BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (contact_id) REFERENCES contacts (id)
                )
            ''')
            
            # Sync jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    source TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    total_contacts INTEGER DEFAULT 0,
                    processed_contacts INTEGER DEFAULT 0,
                    errors TEXT,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Merge candidates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS merge_candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    contact_id_1 TEXT,
                    contact_id_2 TEXT,
                    confidence_score REAL,
                    matching_fields TEXT,
                    conflicts TEXT,
                    status TEXT DEFAULT 'pending',
                    reviewed_at DATETIME,
                    action_taken TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (contact_id_1) REFERENCES contacts (id),
                    FOREIGN KEY (contact_id_2) REFERENCES contacts (id)
                )
            ''')
            
            # Contact enrichment table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_enrichment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id TEXT,
                    enrichment_type TEXT,
                    data TEXT,
                    confidence_score REAL,
                    source TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts (id)
                )
            ''')
            
            db.commit()
            db.close()
            logger.info("Sync tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing sync tables: {e}")

# Global instance
contact_sync_engine = ContactSyncEngine()