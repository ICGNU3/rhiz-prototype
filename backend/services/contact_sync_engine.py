"""
Contact Sync Engine - Handle CSV imports and external contact synchronization
"""
import csv
import io
import uuid
from datetime import datetime
from typing import List, Dict, Any
from backend.models import Contact
from backend.extensions import db


class ContactSyncEngine:
    """Service for syncing contacts from various sources"""
    
    def __init__(self):
        self.supported_sources = ['csv', 'google', 'linkedin', 'outlook']
    
    def process_parsed_contacts(self, user_id: str, contacts_data: List[Dict]) -> Dict[str, Any]:
        """Process parsed contact data and save to database"""
        try:
            created_count = 0
            updated_count = 0
            errors = []
            
            for contact_data in contacts_data:
                try:
                    # Validate required fields
                    if not contact_data.get('name'):
                        errors.append(f"Contact missing name: {contact_data}")
                        continue
                    
                    # Check for existing contact by email
                    existing_contact = None
                    if contact_data.get('email'):
                        existing_contact = Contact.query.filter_by(
                            user_id=user_id,
                            email=contact_data['email']
                        ).first()
                    
                    if existing_contact:
                        # Update existing contact
                        self._update_contact_from_data(existing_contact, contact_data)
                        updated_count += 1
                    else:
                        # Create new contact
                        contact = Contact(
                            user_id=user_id,
                            name=contact_data['name'],
                            email=contact_data.get('email'),
                            phone=contact_data.get('phone'),
                            company=contact_data.get('company'),
                            title=contact_data.get('title'),
                            linkedin=contact_data.get('linkedin'),
                            notes=contact_data.get('notes'),
                            source='csv'
                        )
                        db.session.add(contact)
                        created_count += 1
                
                except Exception as e:
                    errors.append(f"Error processing contact {contact_data.get('name', 'Unknown')}: {str(e)}")
            
            db.session.commit()
            
            # Build contacts list for response
            created_contacts = []
            if created_count > 0:
                # Get recently created contacts for this user
                recent_contacts = Contact.query.filter_by(
                    user_id=user_id, 
                    source='csv'
                ).order_by(Contact.created_at.desc()).limit(created_count).all()
                
                created_contacts = [{
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'company': contact.company
                } for contact in recent_contacts]
            
            return {
                'success': True,
                'imported': created_count,
                'duplicates': updated_count,  # treating updates as duplicates for frontend compatibility
                'errors': len(errors),
                'contacts': created_contacts,
                'error_details': errors if errors else None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'imported': 0,
                'duplicates': 0,
                'errors': 1,
                'contacts': []
            }
    
    def import_csv_file(self, user_id: str, file) -> Dict[str, Any]:
        """Import contacts from CSV file"""
        try:
            # Read file content
            content = file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(content))
            
            # Convert to list of dictionaries
            contacts_data = []
            for row in csv_data:
                # Map common CSV field variations
                contact_data = self._map_csv_fields(row)
                if contact_data:
                    contacts_data.append(contact_data)
            
            # Process the parsed data
            return self.process_parsed_contacts(user_id, contacts_data)
            
        except Exception as e:
            return {
                'success': False,
                'error': f"CSV parsing error: {str(e)}",
                'created': 0,
                'updated': 0
            }
    
    def _map_csv_fields(self, row: Dict[str, str]) -> Dict[str, str]:
        """Map CSV fields to contact fields"""
        # Common field mappings
        field_mappings = {
            'name': ['name', 'full name', 'display name', 'contact name'],
            'email': ['email', 'email address', 'e-mail'],
            'phone': ['phone', 'phone number', 'mobile', 'telephone'],
            'company': ['company', 'organization', 'employer', 'workplace'],
            'title': ['title', 'job title', 'position', 'role'],
            'linkedin': ['linkedin', 'linkedin url', 'linkedin profile'],
            'notes': ['notes', 'description', 'comments']
        }
        
        contact_data = {}
        
        # Convert row keys to lowercase for matching
        row_lower = {k.lower(): v for k, v in row.items() if v and v.strip()}
        
        for field, variations in field_mappings.items():
            for variation in variations:
                if variation in row_lower:
                    contact_data[field] = row_lower[variation].strip()
                    break
        
        # Handle LinkedIn CSV format specifically
        if 'first name' in row_lower and 'last name' in row_lower:
            contact_data['name'] = f"{row_lower['first name']} {row_lower['last name']}".strip()
        
        return contact_data if contact_data.get('name') else None
    
    def _update_contact_from_data(self, contact: Contact, data: Dict[str, str]):
        """Update existing contact with new data"""
        for field in ['name', 'phone', 'company', 'title', 'linkedin', 'notes']:
            if field in data and data[field]:
                setattr(contact, field, data[field])
        
        contact.updated_at = datetime.utcnow()
    
    def sync_google_contacts(self, user_id: str) -> Dict[str, Any]:
        """Sync contacts from Google Contacts (stub)"""
        # TODO: Implement Google Contacts API integration
        return {
            'success': False,
            'error': 'Google Contacts sync not yet implemented',
            'created': 0,
            'updated': 0
        }
    
    def sync_linkedin_contacts(self, user_id: str) -> Dict[str, Any]:
        """Sync contacts from LinkedIn (stub)"""
        # TODO: Implement LinkedIn API integration
        return {
            'success': False,
            'error': 'LinkedIn sync not yet implemented',
            'created': 0,
            'updated': 0
        }
    
    def get_sync_status(self, user_id: str) -> Dict[str, Any]:
        """Get current sync status for user"""
        try:
            contact_count = Contact.query.filter_by(user_id=user_id).count()
            
            # Get source breakdown
            sources = db.session.query(
                Contact.source, 
                db.func.count(Contact.id)
            ).filter_by(user_id=user_id).group_by(Contact.source).all()
            
            source_counts = {source: count for source, count in sources}
            
            return {
                'total_contacts': contact_count,
                'sources': source_counts,
                'last_sync': None,  # TODO: Track sync times
                'sync_in_progress': False
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_contacts': 0,
                'sources': {}
            }