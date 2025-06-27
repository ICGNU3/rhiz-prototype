"""
LinkedIn Contact Import Module
Handles LinkedIn CSV exports and various contact file formats
"""

import csv
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from database_utils import Database

class LinkedInContactImporter:
    """Import contacts from LinkedIn CSV exports and other formats"""
    
    def __init__(self):
        self.db = Database()
        self.logger = logging.getLogger(__name__)
        
        # LinkedIn CSV field mappings
        self.linkedin_field_mappings = {
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email Address': 'email',
            'Company': 'company',
            'Position': 'title',
            'Connected On': 'connected_date',
            'Website': 'website',
            'LinkedIn Profile': 'linkedin_url',
            'Twitter': 'twitter',
            'Industry': 'industry',
            'Location': 'location',
            'Notes': 'notes'
        }
        
        # Alternative field name variations
        self.field_variations = {
            'name': ['Name', 'Full Name', 'Contact Name'],
            'first_name': ['First Name', 'First', 'Given Name', 'FirstName'],
            'last_name': ['Last Name', 'Last', 'Surname', 'Family Name', 'LastName'],
            'email': ['Email', 'Email Address', 'E-mail', 'Email Address 1'],
            'company': ['Company', 'Organization', 'Employer', 'Current Company'],
            'title': ['Title', 'Position', 'Job Title', 'Role', 'Current Position'],
            'linkedin_url': ['LinkedIn URL', 'LinkedIn Profile', 'LinkedIn', 'Profile URL'],
            'phone': ['Phone', 'Phone Number', 'Mobile', 'Cell Phone'],
            'location': ['Location', 'City', 'Address', 'Geographic Location']
        }

    def import_linkedin_csv(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """Import contacts from LinkedIn CSV export"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                delimiter = self._detect_delimiter(sample)
                
                reader = csv.DictReader(file, delimiter=delimiter)
                return self._process_contact_rows(reader, user_id, source='LinkedIn')
                
        except Exception as e:
            self.logger.error(f"LinkedIn CSV import error: {e}")
            return {
                'success': False,
                'error': f"Failed to import LinkedIn CSV: {str(e)}",
                'imported': 0,
                'skipped': 0,
                'errors': []
            }

    def import_generic_csv(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """Import contacts from generic CSV file with field detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter and encoding
                sample = file.read(1024)
                file.seek(0)
                delimiter = self._detect_delimiter(sample)
                
                reader = csv.DictReader(file, delimiter=delimiter)
                return self._process_contact_rows(reader, user_id, source='CSV Import')
                
        except Exception as e:
            self.logger.error(f"Generic CSV import error: {e}")
            return {
                'success': False,
                'error': f"Failed to import CSV: {str(e)}",
                'imported': 0,
                'skipped': 0,
                'errors': []
            }

    def _detect_delimiter(self, sample: str) -> str:
        """Detect CSV delimiter from sample text"""
        delimiters = [',', ';', '\t', '|']
        delimiter_counts = {}
        
        for delimiter in delimiters:
            delimiter_counts[delimiter] = sample.count(delimiter)
        
        # Return delimiter with highest count
        return max(delimiter_counts, key=delimiter_counts.get)

    def _process_contact_rows(self, reader: csv.DictReader, user_id: int, source: str) -> Dict[str, Any]:
        """Process CSV rows and import contacts"""
        imported = 0
        skipped = 0
        errors = []
        duplicates = 0
        
        # Map CSV headers to our field names
        field_mapping = self._create_field_mapping(reader.fieldnames)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 for header row
            try:
                contact_data = self._extract_contact_data(row, field_mapping)
                
                if not self._is_valid_contact(contact_data):
                    skipped += 1
                    errors.append(f"Row {row_num}: Missing required fields (name or email)")
                    continue
                
                # Check for duplicates
                if self._contact_exists(contact_data.get('email'), user_id):
                    duplicates += 1
                    continue
                
                # Create contact
                contact_id = self._create_contact(contact_data, user_id, source)
                if contact_id:
                    imported += 1
                else:
                    skipped += 1
                    errors.append(f"Row {row_num}: Failed to create contact")
                    
            except Exception as e:
                skipped += 1
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            'success': True,
            'imported': imported,
            'skipped': skipped,
            'duplicates': duplicates,
            'errors': errors,
            'field_mapping': field_mapping
        }

    def _create_field_mapping(self, headers: List[str]) -> Dict[str, str]:
        """Create mapping from CSV headers to our field names"""
        mapping = {}
        
        for header in headers:
            # Direct mapping check
            if header in self.linkedin_field_mappings:
                mapping[header] = self.linkedin_field_mappings[header]
                continue
            
            # Check variations
            mapped = False
            for our_field, variations in self.field_variations.items():
                if header in variations or header.lower() in [v.lower() for v in variations]:
                    mapping[header] = our_field
                    mapped = True
                    break
            
            # Fuzzy matching for common patterns
            if not mapped:
                header_lower = header.lower()
                if 'email' in header_lower:
                    mapping[header] = 'email'
                elif 'phone' in header_lower or 'mobile' in header_lower:
                    mapping[header] = 'phone'
                elif 'company' in header_lower or 'organization' in header_lower:
                    mapping[header] = 'company'
                elif 'title' in header_lower or 'position' in header_lower:
                    mapping[header] = 'title'
                elif 'linkedin' in header_lower:
                    mapping[header] = 'linkedin_url'
                elif 'twitter' in header_lower:
                    mapping[header] = 'twitter'
                elif 'note' in header_lower:
                    mapping[header] = 'notes'
        
        return mapping

    def _extract_contact_data(self, row: Dict[str, str], field_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Extract and normalize contact data from CSV row"""
        contact_data = {}
        
        for csv_field, our_field in field_mapping.items():
            value = row.get(csv_field, '').strip()
            if value:
                contact_data[our_field] = value
        
        # Handle name splitting if full name is provided
        if 'name' in contact_data and 'first_name' not in contact_data:
            first, last = self._split_name(contact_data['name'])
            contact_data['first_name'] = first
            contact_data['last_name'] = last
            del contact_data['name']
        
        # Clean and validate data
        contact_data = self._clean_contact_data(contact_data)
        
        return contact_data

    def _split_name(self, full_name: str) -> Tuple[str, str]:
        """Split full name into first and last name"""
        parts = full_name.strip().split()
        if len(parts) == 0:
            return '', ''
        elif len(parts) == 1:
            return parts[0], ''
        else:
            return parts[0], ' '.join(parts[1:])

    def _clean_contact_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate contact data"""
        cleaned = {}
        
        for field, value in data.items():
            if isinstance(value, str):
                value = value.strip()
                
                # Clean email
                if field == 'email':
                    value = self._clean_email(value)
                
                # Clean LinkedIn URL
                elif field == 'linkedin_url':
                    value = self._clean_linkedin_url(value)
                
                # Clean phone number
                elif field == 'phone':
                    value = self._clean_phone(value)
                
                # Remove empty values
                if value:
                    cleaned[field] = value
        
        return cleaned

    def _clean_email(self, email: str) -> str:
        """Clean and validate email address"""
        email = email.lower().strip()
        # Basic email validation
        if '@' in email and '.' in email.split('@')[1]:
            return email
        return ''

    def _clean_linkedin_url(self, url: str) -> str:
        """Clean LinkedIn URL"""
        if not url.startswith('http'):
            if url.startswith('linkedin.com') or url.startswith('www.linkedin.com'):
                url = 'https://' + url
            elif '/in/' in url:
                url = 'https://linkedin.com' + url
        return url

    def _clean_phone(self, phone: str) -> str:
        """Clean phone number"""
        # Remove non-digit characters except + and spaces
        cleaned = re.sub(r'[^\d+\s()-]', '', phone)
        return cleaned.strip()

    def _is_valid_contact(self, contact_data: Dict[str, Any]) -> bool:
        """Check if contact has minimum required data"""
        has_name = contact_data.get('first_name') or contact_data.get('last_name')
        has_email = contact_data.get('email')
        has_company = contact_data.get('company')
        
        # Must have either name+email, or name+company
        return (has_name and has_email) or (has_name and has_company)

    def _contact_exists(self, email: str, user_id: int) -> bool:
        """Check if contact already exists"""
        if not email:
            return False
            
        existing = self.db.execute_query(
            "SELECT id FROM contacts WHERE user_id = ? AND email = ?",
            (user_id, email)
        )
        return len(existing) > 0

    def _create_contact(self, contact_data: Dict[str, Any], user_id: int, source: str) -> Optional[int]:
        """Create new contact in database"""
        try:
            # Prepare contact fields
            name = f"{contact_data.get('first_name', '')} {contact_data.get('last_name', '')}".strip()
            if not name:
                name = contact_data.get('company', 'Unknown')
            
            # Set default relationship and warmth for imported contacts
            relationship_type = 'professional'
            warmth = 'cold'  # LinkedIn connections typically start as cold
            
            # Determine relationship type from source
            if source == 'LinkedIn':
                relationship_type = 'linkedin_connection'
                warmth = 'aware'  # LinkedIn connections are typically aware
            
            # Build notes
            notes_parts = []
            if contact_data.get('notes'):
                notes_parts.append(contact_data['notes'])
            notes_parts.append(f"Imported from {source}")
            
            # Create contact
            contact_id = self.db.execute_query(
                """
                INSERT INTO contacts (
                    user_id, name, email, company, title, phone, 
                    linkedin_url, twitter, location, notes, 
                    relationship_type, warmth, source, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    user_id,
                    name,
                    contact_data.get('email'),
                    contact_data.get('company'),
                    contact_data.get('title'),
                    contact_data.get('phone'),
                    contact_data.get('linkedin_url'),
                    contact_data.get('twitter'),
                    contact_data.get('location'),
                    '\n'.join(notes_parts),
                    relationship_type,
                    warmth,
                    source
                ),
                return_lastrowid=True
            )
            
            return contact_id
            
        except Exception as e:
            self.logger.error(f"Error creating contact: {e}")
            return None

    def get_import_template(self) -> Dict[str, Any]:
        """Get template information for CSV imports"""
        return {
            'linkedin_fields': list(self.linkedin_field_mappings.keys()),
            'supported_fields': [
                'First Name', 'Last Name', 'Email Address', 'Company', 
                'Position', 'Phone Number', 'LinkedIn URL', 'Twitter', 
                'Location', 'Notes', 'Industry'
            ],
            'required_fields': 'At least one of: Name+Email or Name+Company',
            'sample_csv': self._generate_sample_csv()
        }

    def _generate_sample_csv(self) -> str:
        """Generate sample CSV content"""
        return """First Name,Last Name,Email Address,Company,Position,LinkedIn URL,Notes
John,Smith,john.smith@example.com,Tech Corp,Software Engineer,https://linkedin.com/in/johnsmith,Met at conference
Jane,Doe,jane.doe@startup.com,Innovation Inc,Product Manager,https://linkedin.com/in/janedoe,Potential collaboration
"""

    def analyze_csv_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze CSV structure and suggest field mappings"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)
                delimiter = self._detect_delimiter(sample)
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                # Analyze first few rows
                rows = []
                for i, row in enumerate(reader):
                    if i >= 3:  # Analyze first 3 rows
                        break
                    rows.append(row)
                
                field_mapping = self._create_field_mapping(headers)
                
                return {
                    'success': True,
                    'headers': headers,
                    'delimiter': delimiter,
                    'field_mapping': field_mapping,
                    'sample_rows': rows,
                    'total_rows': sum(1 for _ in open(file_path, 'r')) - 1,  # Exclude header
                    'recommendations': self._get_mapping_recommendations(field_mapping, headers)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _get_mapping_recommendations(self, field_mapping: Dict[str, str], headers: List[str]) -> List[str]:
        """Get recommendations for improving field mapping"""
        recommendations = []
        
        mapped_fields = set(field_mapping.values())
        unmapped_headers = [h for h in headers if h not in field_mapping]
        
        if 'email' not in mapped_fields:
            recommendations.append("No email field detected. This may limit contact quality.")
        
        if 'first_name' not in mapped_fields and 'last_name' not in mapped_fields:
            recommendations.append("No name fields detected. Consider mapping name columns.")
        
        if unmapped_headers:
            recommendations.append(f"Unmapped columns: {', '.join(unmapped_headers[:3])}")
        
        return recommendations