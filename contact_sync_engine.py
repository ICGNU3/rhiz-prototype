"""
Multi-Source Contact Sync Engine for Rhiz
Handles intelligent syncing, deduplication, and enrichment from multiple platforms
"""

import sqlite3
import json
import logging
import requests
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import difflib
import re
from urllib.parse import urljoin
import base64
import io
from PIL import Image

@dataclass
class ContactSource:
    """Represents a contact from a specific source"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    social_handles: Optional[Dict[str, str]] = None
    source: str = 'manual'  # manual, google, linkedin, twitter, gmail, outlook, csv
    source_id: Optional[str] = None
    raw_data: Optional[Dict] = None
    sync_timestamp: Optional[str] = None

@dataclass
class MergeCandidate:
    """Represents a potential duplicate contact merge"""
    contact_id_1: str
    contact_id_2: str
    confidence_score: float
    matching_fields: List[str]
    conflicts: Dict[str, Tuple[Any, Any]]
    recommended_action: str  # 'auto_merge', 'manual_review', 'skip'

class ContactSyncEngine:
    """Main engine for multi-source contact synchronization"""
    
    def __init__(self, db_path: str = 'db.sqlite3'):
        self.db_path = db_path
        self.similarity_threshold = 0.75
        self.auto_merge_threshold = 0.90
        self.enrichment_apis = {
            'gravatar': 'https://www.gravatar.com/avatar/',
            'clearbit': 'https://person.clearbit.com/v1/people/email/',
        }
        
    def get_db(self):
        """Get database connection"""
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db
    
    def init_sync_tables(self):
        """Initialize tables for contact syncing"""
        db = self.get_db()
        
        # Contact sources table
        db.execute('''
            CREATE TABLE IF NOT EXISTS contact_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                source TEXT NOT NULL,
                source_id TEXT,
                raw_data TEXT,
                sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_primary BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        # Sync jobs table
        db.execute('''
            CREATE TABLE IF NOT EXISTS sync_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
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
        db.execute('''
            CREATE TABLE IF NOT EXISTS merge_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contact_id_1 INTEGER,
                contact_id_2 INTEGER,
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
        db.execute('''
            CREATE TABLE IF NOT EXISTS contact_enrichment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                enrichment_type TEXT,
                data TEXT,
                confidence_score REAL,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        # Add new columns to existing contacts table if they don't exist
        try:
            db.execute('ALTER TABLE contacts ADD COLUMN sync_status TEXT DEFAULT "manual"')
            db.execute('ALTER TABLE contacts ADD COLUMN enrichment_status TEXT DEFAULT "none"')
            db.execute('ALTER TABLE contacts ADD COLUMN profile_picture_url TEXT')
            db.execute('ALTER TABLE contacts ADD COLUMN social_handles TEXT')
            db.execute('ALTER TABLE contacts ADD COLUMN last_sync DATETIME')
        except sqlite3.OperationalError:
            # Columns already exist
            pass
        
        db.commit()
        db.close()
        
    def normalize_contact_data(self, contact_source: ContactSource) -> Dict[str, Any]:
        """Normalize contact data for comparison and storage"""
        normalized = {
            'name': self._normalize_name(contact_source.name),
            'email': self._normalize_email(contact_source.email),
            'phone': self._normalize_phone(contact_source.phone),
            'company': self._normalize_company(contact_source.company),
            'title': contact_source.title.strip() if contact_source.title else None,
            'bio': contact_source.bio.strip() if contact_source.bio else None,
            'source': contact_source.source,
            'source_id': contact_source.source_id,
            'profile_picture_url': contact_source.profile_picture_url,
            'social_handles': json.dumps(contact_source.social_handles) if contact_source.social_handles else None,
            'raw_data': json.dumps(contact_source.raw_data) if contact_source.raw_data else None,
            'sync_timestamp': contact_source.sync_timestamp or datetime.now().isoformat()
        }
        return {k: v for k, v in normalized.items() if v is not None}
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        # Remove extra spaces, title case
        return ' '.join(name.strip().split()).title()
    
    def _normalize_email(self, email: str) -> Optional[str]:
        """Normalize email for comparison"""
        if not email:
            return None
        return email.strip().lower()
    
    def _normalize_phone(self, phone: str) -> Optional[str]:
        """Normalize phone number for comparison"""
        if not phone:
            return None
        # Remove all non-digits
        digits_only = re.sub(r'\D', '', phone)
        # Handle US numbers
        if len(digits_only) == 10:
            return f"+1{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            return f"+{digits_only}"
        return digits_only
    
    def _normalize_company(self, company: str) -> Optional[str]:
        """Normalize company name for comparison"""
        if not company:
            return None
        # Remove common suffixes and normalize
        normalized = company.strip()
        suffixes = ['Inc', 'Inc.', 'LLC', 'Ltd', 'Ltd.', 'Corp', 'Corp.', 'Company', 'Co.']
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        return normalized
    
    def find_duplicate_candidates(self, user_id: int, contact_source: ContactSource) -> List[MergeCandidate]:
        """Find potential duplicate contacts for a new contact source"""
        db = self.get_db()
        
        # Get existing contacts for user
        existing_contacts = db.execute(
            'SELECT * FROM contacts WHERE user_id = ?', (user_id,)
        ).fetchall()
        
        candidates = []
        
        for existing in existing_contacts:
            confidence_score, matching_fields, conflicts = self._calculate_similarity(
                contact_source, existing
            )
            
            if confidence_score >= self.similarity_threshold:
                recommended_action = 'auto_merge' if confidence_score >= self.auto_merge_threshold else 'manual_review'
                
                candidate = MergeCandidate(
                    contact_id_1=str(existing['id']),
                    contact_id_2='new',
                    confidence_score=confidence_score,
                    matching_fields=matching_fields,
                    conflicts=conflicts,
                    recommended_action=recommended_action
                )
                candidates.append(candidate)
        
        db.close()
        return sorted(candidates, key=lambda x: x.confidence_score, reverse=True)
    
    def _calculate_similarity(self, source: ContactSource, existing: sqlite3.Row) -> Tuple[float, List[str], Dict[str, Tuple[Any, Any]]]:
        """Calculate similarity between contact source and existing contact"""
        scores = []
        matching_fields = []
        conflicts = {}
        
        # Name similarity
        if source.name and existing['name']:
            name_similarity = difflib.SequenceMatcher(None, 
                self._normalize_name(source.name),
                self._normalize_name(existing['name'])
            ).ratio()
            scores.append(('name', name_similarity, 0.4))  # 40% weight
            if name_similarity > 0.8:
                matching_fields.append('name')
            elif name_similarity > 0.3:
                conflicts['name'] = (source.name, existing['name'])
        
        # Email exact match
        if source.email and existing['email']:
            if self._normalize_email(source.email) == self._normalize_email(existing['email']):
                scores.append(('email', 1.0, 0.3))  # 30% weight
                matching_fields.append('email')
            else:
                conflicts['email'] = (source.email, existing['email'])
        
        # Phone similarity
        if source.phone and existing['phone']:
            norm_source_phone = self._normalize_phone(source.phone)
            norm_existing_phone = self._normalize_phone(existing['phone'])
            if norm_source_phone == norm_existing_phone:
                scores.append(('phone', 1.0, 0.2))  # 20% weight
                matching_fields.append('phone')
            else:
                conflicts['phone'] = (source.phone, existing['phone'])
        
        # Company similarity
        if source.company and existing['company']:
            company_similarity = difflib.SequenceMatcher(None,
                self._normalize_company(source.company) or "",
                self._normalize_company(existing['company']) or ""
            ).ratio()
            scores.append(('company', company_similarity, 0.1))  # 10% weight
            if company_similarity > 0.8:
                matching_fields.append('company')
            elif company_similarity > 0.3:
                conflicts['company'] = (source.company, existing['company'])
        
        # Calculate weighted confidence score
        if scores:
            total_weight = sum(weight for _, _, weight in scores)
            confidence_score = sum(score * weight for _, score, weight in scores) / total_weight
        else:
            confidence_score = 0.0
        
        return confidence_score, matching_fields, conflicts
    
    def enrich_contact(self, contact_id: int) -> Dict[str, Any]:
        """Enrich contact with additional data from various sources"""
        db = self.get_db()
        
        contact = db.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
        if not contact:
            return {'error': 'Contact not found'}
        
        enrichment_results = {}
        
        # Enrich profile picture
        if contact['email'] and not contact.get('profile_picture_url'):
            profile_pic = self._get_profile_picture(contact['email'])
            if profile_pic:
                enrichment_results['profile_picture_url'] = profile_pic
                db.execute(
                    'UPDATE contacts SET profile_picture_url = ? WHERE id = ?',
                    (profile_pic, contact_id)
                )
        
        # Enrich with Clearbit data (if available)
        if contact['email']:
            clearbit_data = self._get_clearbit_data(contact['email'])
            if clearbit_data:
                enrichment_results['clearbit'] = clearbit_data
                
                # Store enrichment data
                db.execute(
                    '''INSERT INTO contact_enrichment (contact_id, enrichment_type, data, source)
                       VALUES (?, ?, ?, ?)''',
                    (contact_id, 'profile', json.dumps(clearbit_data), 'clearbit')
                )
        
        # Update enrichment status
        db.execute(
            'UPDATE contacts SET enrichment_status = ?, updated_at = ? WHERE id = ?',
            ('enriched', datetime.now().isoformat(), contact_id)
        )
        
        db.commit()
        db.close()
        
        return enrichment_results
    
    def _get_profile_picture(self, email: str) -> Optional[str]:
        """Get profile picture from Gravatar"""
        try:
            email_hash = hashlib.md5(email.lower().encode()).hexdigest()
            gravatar_url = f"{self.enrichment_apis['gravatar']}{email_hash}?s=200&d=404"
            
            response = requests.get(gravatar_url, timeout=5)
            if response.status_code == 200:
                return gravatar_url
        except Exception as e:
            logging.warning(f"Failed to get Gravatar for {email}: {e}")
        
        return None
    
    def _get_clearbit_data(self, email: str) -> Optional[Dict]:
        """Get enrichment data from Clearbit (requires API key)"""
        # This would require a Clearbit API key
        # For now, return None
        return None
    
    def create_sync_job(self, user_id: int, source: str) -> int:
        """Create a new sync job"""
        db = self.get_db()
        
        cursor = db.execute(
            'INSERT INTO sync_jobs (user_id, source) VALUES (?, ?)',
            (user_id, source)
        )
        job_id = cursor.lastrowid
        
        db.commit()
        db.close()
        
        return job_id
    
    def update_sync_job(self, job_id: int, status: str, total_contacts: int = None, 
                       processed_contacts: int = None, errors: str = None):
        """Update sync job status"""
        db = self.get_db()
        
        updates = ['status = ?']
        params = [status]
        
        if total_contacts is not None:
            updates.append('total_contacts = ?')
            params.append(total_contacts)
            
        if processed_contacts is not None:
            updates.append('processed_contacts = ?')
            params.append(processed_contacts)
            
        if errors is not None:
            updates.append('errors = ?')
            params.append(errors)
            
        if status == 'completed':
            updates.append('completed_at = ?')
            params.append(datetime.now().isoformat())
        
        params.append(job_id)
        
        db.execute(f'UPDATE sync_jobs SET {", ".join(updates)} WHERE id = ?', params)
        db.commit()
        db.close()
    
    def process_csv_contacts(self, user_id: int, csv_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process contacts from CSV data"""
        job_id = self.create_sync_job(user_id, 'csv')
        
        try:
            self.update_sync_job(job_id, 'processing', total_contacts=len(csv_data))
            
            processed = 0
            created = 0
            merged = 0
            errors = []
            
            for row in csv_data:
                try:
                    # Map CSV fields to ContactSource
                    contact_source = ContactSource(
                        name=row.get('name', '').strip(),
                        email=row.get('email', '').strip() or None,
                        phone=row.get('phone', '').strip() or None,
                        company=row.get('company', '').strip() or None,
                        title=row.get('title', '').strip() or None,
                        source='csv',
                        raw_data=row
                    )
                    
                    # Find duplicates
                    candidates = self.find_duplicate_candidates(user_id, contact_source)
                    
                    if candidates and candidates[0].recommended_action == 'auto_merge':
                        # Auto-merge with existing contact
                        self._merge_contacts(user_id, candidates[0].contact_id_1, contact_source)
                        merged += 1
                    else:
                        # Create new contact
                        contact_id = self._create_contact_from_source(user_id, contact_source)
                        created += 1
                        
                        # Store potential duplicates for manual review
                        for candidate in candidates:
                            self._store_merge_candidate(user_id, contact_id, candidate)
                    
                    processed += 1
                    self.update_sync_job(job_id, 'processing', processed_contacts=processed)
                    
                except Exception as e:
                    errors.append(f"Row {processed + 1}: {str(e)}")
                    processed += 1
            
            self.update_sync_job(job_id, 'completed', processed_contacts=processed,
                               errors=json.dumps(errors) if errors else None)
            
            return {
                'job_id': job_id,
                'total_processed': processed,
                'created': created,
                'merged': merged,
                'errors': errors
            }
            
        except Exception as e:
            self.update_sync_job(job_id, 'failed', errors=str(e))
            raise
    
    def _create_contact_from_source(self, user_id: int, contact_source: ContactSource) -> int:
        """Create a new contact from ContactSource"""
        db = self.get_db()
        
        normalized = self.normalize_contact_data(contact_source)
        
        # Create contact
        cursor = db.execute(
            '''INSERT INTO contacts (
                user_id, name, email, phone, company, title, notes,
                sync_status, profile_picture_url, social_handles,
                created_at, updated_at, last_sync
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                user_id,
                normalized['name'],
                normalized.get('email'),
                normalized.get('phone'),
                normalized.get('company'),
                normalized.get('title'),
                normalized.get('bio'),
                'synced',
                normalized.get('profile_picture_url'),
                normalized.get('social_handles'),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                normalized['sync_timestamp']
            )
        )
        contact_id = cursor.lastrowid
        
        # Store source information
        db.execute(
            '''INSERT INTO contact_sources (contact_id, source, source_id, raw_data)
               VALUES (?, ?, ?, ?)''',
            (contact_id, contact_source.source, contact_source.source_id, normalized.get('raw_data'))
        )
        
        db.commit()
        db.close()
        
        return contact_id
    
    def _merge_contacts(self, user_id: int, existing_contact_id: str, contact_source: ContactSource):
        """Merge contact source data with existing contact"""
        db = self.get_db()
        
        # Get existing contact
        existing = db.execute(
            'SELECT * FROM contacts WHERE id = ? AND user_id = ?',
            (existing_contact_id, user_id)
        ).fetchone()
        
        if not existing:
            return
        
        # Merge data (prefer new data where available)
        normalized = self.normalize_contact_data(contact_source)
        
        updates = []
        params = []
        
        for field in ['email', 'phone', 'company', 'title', 'profile_picture_url']:
            if normalized.get(field) and not existing[field]:
                updates.append(f'{field} = ?')
                params.append(normalized[field])
        
        # Always update sync info
        updates.extend(['sync_status = ?', 'last_sync = ?', 'updated_at = ?'])
        params.extend(['synced', normalized['sync_timestamp'], datetime.now().isoformat()])
        params.append(existing_contact_id)
        
        if updates:
            db.execute(f'UPDATE contacts SET {", ".join(updates)} WHERE id = ?', params)
        
        # Add source record
        db.execute(
            '''INSERT INTO contact_sources (contact_id, source, source_id, raw_data)
               VALUES (?, ?, ?, ?)''',
            (existing_contact_id, contact_source.source, contact_source.source_id, normalized.get('raw_data'))
        )
        
        db.commit()
        db.close()
    
    def _store_merge_candidate(self, user_id: int, contact_id: int, candidate: MergeCandidate):
        """Store merge candidate for manual review"""
        db = self.get_db()
        
        db.execute(
            '''INSERT INTO merge_candidates (
                user_id, contact_id_1, contact_id_2, confidence_score,
                matching_fields, conflicts
            ) VALUES (?, ?, ?, ?, ?, ?)''',
            (
                user_id,
                candidate.contact_id_1,
                contact_id,
                candidate.confidence_score,
                json.dumps(candidate.matching_fields),
                json.dumps({k: list(v) for k, v in candidate.conflicts.items()})
            )
        )
        
        db.commit()
        db.close()
    
    def get_merge_candidates(self, user_id: int, status: str = 'pending') -> List[Dict[str, Any]]:
        """Get merge candidates for review"""
        db = self.get_db()
        
        candidates = db.execute(
            '''SELECT mc.*, 
                      c1.name as contact_1_name, c1.email as contact_1_email,
                      c2.name as contact_2_name, c2.email as contact_2_email
               FROM merge_candidates mc
               JOIN contacts c1 ON mc.contact_id_1 = c1.id
               JOIN contacts c2 ON mc.contact_id_2 = c2.id
               WHERE mc.user_id = ? AND mc.status = ?
               ORDER BY mc.confidence_score DESC''',
            (user_id, status)
        ).fetchall()
        
        db.close()
        
        return [dict(candidate) for candidate in candidates]