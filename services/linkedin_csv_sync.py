"""
LinkedIn CSV Import Service
Scaffold for LinkedIn connections import with CSV fallback
"""

import os
import csv
import json
import secrets
from datetime import datetime
from typing import Optional, Dict, List, Any, IO
import psycopg2
import psycopg2.extras

class LinkedInCSVSync:
    def __init__(self):
        self.supported_formats = [
            'linkedin_connections',  # LinkedIn's native export format
            'linkedin_basic',        # Basic name, email, company format
            'generic_csv'           # Generic CSV with automatic field mapping
        ]
    
    def _get_db_connection(self):
        """Get PostgreSQL database connection"""
        return psycopg2.connect(
            os.environ.get('DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    def detect_csv_format(self, csv_content: str) -> Dict[str, Any]:
        """Detect CSV format and map fields automatically"""
        lines = csv_content.strip().split('\n')
        if not lines:
            raise ValueError("Empty CSV file")
        
        # Parse header
        reader = csv.DictReader(lines)
        headers = reader.fieldnames or []
        
        # Analyze first few rows to understand data
        sample_rows = []
        for i, row in enumerate(reader):
            if i >= 3:  # Only check first 3 rows
                break
            sample_rows.append(row)
        
        # Detect LinkedIn export format
        if 'First Name' in headers and 'Last Name' in headers and 'Email Address' in headers:
            return {
                'format': 'linkedin_connections',
                'mapping': {
                    'first_name': 'First Name',
                    'last_name': 'Last Name',
                    'email': 'Email Address',
                    'company': 'Company',
                    'position': 'Position',
                    'connected_on': 'Connected On'
                },
                'confidence': 0.95
            }
        
        # Detect basic name/email format
        name_fields = [h for h in headers if 'name' in h.lower()]
        email_fields = [h for h in headers if 'email' in h.lower() or 'mail' in h.lower()]
        company_fields = [h for h in headers if any(word in h.lower() for word in ['company', 'organization', 'org'])]
        
        if name_fields and email_fields:
            return {
                'format': 'linkedin_basic',
                'mapping': {
                    'name': name_fields[0],
                    'email': email_fields[0],
                    'company': company_fields[0] if company_fields else None
                },
                'confidence': 0.8
            }
        
        # Generic CSV fallback
        return {
            'format': 'generic_csv',
            'mapping': self._auto_map_fields(headers, sample_rows),
            'confidence': 0.6
        }
    
    def _auto_map_fields(self, headers: List[str], sample_rows: List[Dict[str, str]]) -> Dict[str, str]:
        """Automatically map CSV fields to contact fields"""
        mapping = {}
        
        # Common field variations
        field_patterns = {
            'name': ['name', 'full name', 'contact name', 'person'],
            'first_name': ['first name', 'first', 'fname', 'given name'],
            'last_name': ['last name', 'last', 'lname', 'surname', 'family name'],
            'email': ['email', 'email address', 'e-mail', 'mail'],
            'company': ['company', 'organization', 'org', 'employer', 'workplace'],
            'position': ['position', 'title', 'job title', 'role'],
            'phone': ['phone', 'mobile', 'cell', 'telephone', 'contact']
        }
        
        for field, patterns in field_patterns.items():
            for header in headers:
                header_lower = header.lower().strip()
                for pattern in patterns:
                    if pattern in header_lower:
                        mapping[field] = header
                        break
                if field in mapping:
                    break
        
        return mapping
    
    def import_linkedin_csv(self, user_id: str, csv_file: IO[str], filename: str) -> Dict[str, Any]:
        """Import LinkedIn connections from CSV file"""
        try:
            # Read CSV content
            csv_content = csv_file.read()
            
            # Detect format
            format_info = self.detect_csv_format(csv_content)
            
            # Create import job
            job_id = self._create_import_job(user_id, 'linkedin_csv', filename, format_info)
            
            # Process CSV
            results = self._process_csv_content(user_id, job_id, csv_content, format_info)
            
            # Complete job
            self._complete_import_job(job_id, 'completed', results)
            
            return {
                'status': 'success',
                'job_id': job_id,
                'format_detected': format_info['format'],
                'confidence': format_info['confidence'],
                'total_contacts': results['total'],
                'new_contacts': results['new'],
                'updated_contacts': results['updated'],
                'failed_contacts': results['failed']
            }
            
        except Exception as e:
            if 'job_id' in locals():
                self._complete_import_job(job_id, 'failed', {'error': str(e)})
            raise
    
    def _create_import_job(self, user_id: str, source_type: str, filename: str, format_info: Dict[str, Any]) -> str:
        """Create import job record"""
        job_id = f"import_{secrets.token_hex(8)}"
        source_id = f"linkedin_csv_{user_id}_{secrets.token_hex(8)}"
        
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                # Create/update contact source
                cur.execute("""
                    INSERT INTO contact_sources (
                        id, user_id, source_type, source_id, sync_status, 
                        sync_metadata, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        sync_status = 'syncing',
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    source_id, user_id, source_type, filename,
                    'syncing', json.dumps(format_info), True
                ))
                
                # Create sync job
                cur.execute("""
                    INSERT INTO sync_jobs (id, user_id, source_id, job_type, status, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    job_id, user_id, source_id, 'csv_import', 
                    'running', json.dumps({'filename': filename, 'format': format_info})
                ))
                
                conn.commit()
        finally:
            conn.close()
        
        return job_id
    
    def _process_csv_content(self, user_id: str, job_id: str, csv_content: str, format_info: Dict[str, Any]) -> Dict[str, int]:
        """Process CSV content and create contacts"""
        results = {'total': 0, 'new': 0, 'updated': 0, 'failed': 0}
        
        lines = csv_content.strip().split('\n')
        reader = csv.DictReader(lines)
        mapping = format_info['mapping']
        
        conn = self._get_db_connection()
        try:
            for row in reader:
                try:
                    self._process_csv_row(conn, user_id, job_id, row, mapping, results)
                except Exception as e:
                    results['failed'] += 1
                    self._log_import_error(conn, job_id, row, str(e))
                
                results['total'] += 1
        finally:
            conn.close()
        
        return results
    
    def _process_csv_row(self, conn, user_id: str, job_id: str, row: Dict[str, str], mapping: Dict[str, str], results: Dict[str, int]):
        """Process a single CSV row"""
        # Extract contact information based on mapping
        if 'first_name' in mapping and 'last_name' in mapping:
            # LinkedIn format with separate name fields
            first_name = row.get(mapping.get('first_name', ''), '').strip()
            last_name = row.get(mapping.get('last_name', ''), '').strip()
            name = f"{first_name} {last_name}".strip()
        else:
            # Single name field
            name = row.get(mapping.get('name', ''), '').strip()
        
        email = row.get(mapping.get('email', ''), '').strip()
        company = row.get(mapping.get('company', ''), '').strip()
        position = row.get(mapping.get('position', ''), '').strip()
        
        # Validation
        if not name and not email:
            raise ValueError("Row has no name or email")
        
        if not name:
            name = email.split('@')[0] if email else 'Unknown'
        
        with conn.cursor() as cur:
            # Check for existing contact
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
                        notes = COALESCE(NULLIF(%s, ''), notes),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (name, email, company, position, existing['id']))
                
                contact_id = existing['id']
                action = 'updated'
                results['updated'] += 1
            else:
                # Create new contact
                contact_id = f"contact_{secrets.token_hex(8)}"
                cur.execute("""
                    INSERT INTO contacts (id, user_id, name, email, company, notes, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (contact_id, user_id, name, email, company, position, 'linkedin_csv'))
                
                action = 'created'
                results['new'] += 1
            
            # Log import action
            self._log_import_action(conn, job_id, contact_id, action, f"LinkedIn CSV: {name}")
            
            conn.commit()
    
    def _log_import_action(self, conn, job_id: str, contact_id: str, action: str, details: str):
        """Log successful import action"""
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_logs (job_id, contact_id, action, details)
                VALUES (%s, %s, %s, %s)
            """, (job_id, contact_id, action, details))
    
    def _log_import_error(self, conn, job_id: str, row: Dict[str, str], error: str):
        """Log import error"""
        details = f"Row data: {json.dumps(row)}"
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_logs (job_id, action, details, error_message)
                VALUES (%s, %s, %s, %s)
            """, (job_id, 'failed', details, error))
    
    def _complete_import_job(self, job_id: str, status: str, results: Dict[str, Any]):
        """Complete import job with results"""
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
    
    def get_import_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get CSV import history for user"""
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        sj.id,
                        sj.job_type,
                        sj.status,
                        sj.started_at,
                        sj.completed_at,
                        sj.total_contacts,
                        sj.new_contacts,
                        sj.updated_contacts,
                        sj.failed_contacts,
                        sj.error_message,
                        sj.metadata,
                        cs.source_type,
                        cs.source_id as filename
                    FROM sync_jobs sj
                    JOIN contact_sources cs ON sj.source_id = cs.id
                    WHERE sj.user_id = %s AND sj.job_type = 'csv_import'
                    ORDER BY sj.started_at DESC
                    LIMIT 20
                """, (user_id,))
                
                return [dict(job) for job in cur.fetchall()]
        finally:
            conn.close()
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """Get information about supported CSV formats"""
        return {
            'formats': [
                {
                    'id': 'linkedin_connections',
                    'name': 'LinkedIn Connections Export',
                    'description': 'Native LinkedIn connections export CSV',
                    'required_fields': ['First Name', 'Last Name', 'Email Address'],
                    'optional_fields': ['Company', 'Position', 'Connected On'],
                    'instructions': [
                        'Go to LinkedIn > Settings & Privacy > Data Privacy > Download your data',
                        'Select "Connections" and download CSV',
                        'Upload the Connections.csv file here'
                    ]
                },
                {
                    'id': 'linkedin_basic',
                    'name': 'Basic Contact CSV',
                    'description': 'Simple CSV with name, email, company',
                    'required_fields': ['Name or First/Last Name', 'Email'],
                    'optional_fields': ['Company', 'Position', 'Phone'],
                    'instructions': [
                        'Create CSV with columns: Name, Email, Company',
                        'First row should contain column headers',
                        'One contact per row'
                    ]
                },
                {
                    'id': 'generic_csv',
                    'name': 'Generic CSV (Auto-detected)',
                    'description': 'Any CSV format with automatic field mapping',
                    'required_fields': ['Any name field', 'Any email field'],
                    'optional_fields': ['Company, Organization, Position, etc.'],
                    'instructions': [
                        'Upload any CSV with contact information',
                        'System will automatically detect and map fields',
                        'Preview will show detected mapping'
                    ]
                }
            ],
            'max_file_size': '10MB',
            'supported_encodings': ['UTF-8', 'Latin-1'],
            'tips': [
                'Remove duplicate contacts before uploading',
                'Ensure email addresses are valid',
                'Company names will be standardized automatically'
            ]
        }

# Additional Twitter/X CSV Support
class TwitterCSVSync(LinkedInCSVSync):
    def __init__(self):
        super().__init__()
        self.supported_formats = [
            'twitter_following',  # Twitter following export
            'twitter_followers',  # Twitter followers export  
            'generic_csv'        # Generic CSV fallback
        ]
    
    def detect_csv_format(self, csv_content: str) -> Dict[str, Any]:
        """Detect Twitter CSV format"""
        lines = csv_content.strip().split('\n')
        if not lines:
            raise ValueError("Empty CSV file")
        
        reader = csv.DictReader(lines)
        headers = reader.fieldnames or []
        
        # Twitter following/followers format
        if 'username' in headers and 'name' in headers:
            return {
                'format': 'twitter_following',
                'mapping': {
                    'name': 'name',
                    'username': 'username',
                    'bio': 'bio',
                    'followers_count': 'followers_count'
                },
                'confidence': 0.9
            }
        
        # Fallback to parent class
        return super().detect_csv_format(csv_content)
    
    def _process_csv_row(self, conn, user_id: str, job_id: str, row: Dict[str, str], mapping: Dict[str, str], results: Dict[str, int]):
        """Process Twitter CSV row"""
        name = row.get(mapping.get('name', ''), '').strip()
        username = row.get(mapping.get('username', ''), '').strip()
        bio = row.get(mapping.get('bio', ''), '').strip()
        
        # Create email from username for Twitter contacts
        email = f"{username}@twitter.com" if username else ''
        
        if not name and not username:
            raise ValueError("Row has no name or username")
        
        if not name:
            name = username
        
        with conn.cursor() as cur:
            # Check for existing contact
            cur.execute("""
                SELECT id FROM contacts 
                WHERE user_id = %s AND (name = %s OR email = %s)
                LIMIT 1
            """, (user_id, name, email))
            existing = cur.fetchone()
            
            # Build notes with Twitter info
            notes = f"Twitter: @{username}"
            if bio:
                notes += f"\nBio: {bio}"
            
            if existing:
                # Update existing contact
                cur.execute("""
                    UPDATE contacts SET
                        name = COALESCE(NULLIF(%s, ''), name),
                        email = COALESCE(NULLIF(%s, ''), email),
                        notes = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (name, email, notes, existing['id']))
                
                contact_id = existing['id']
                action = 'updated'
                results['updated'] += 1
            else:
                # Create new contact
                contact_id = f"contact_{secrets.token_hex(8)}"
                cur.execute("""
                    INSERT INTO contacts (id, user_id, name, email, notes, source)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (contact_id, user_id, name, email, notes, 'twitter_csv'))
                
                action = 'created'
                results['new'] += 1
            
            # Log import action
            self._log_import_action(conn, job_id, contact_id, action, f"Twitter: @{username}")
            
            conn.commit()