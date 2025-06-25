"""
CSV Import functionality for bulk contact uploads.
Supports various CSV formats and provides data validation and error handling.
"""

import csv
import io
from models import Database, Contact
import logging

class CSVContactImporter:
    def __init__(self, user_id):
        self.db = Database()
        self.contact_model = Contact(self.db)
        self.user_id = user_id
        self.import_stats = {
            'total_rows': 0,
            'successful_imports': 0,
            'errors': [],
            'warnings': []
        }
    
    def detect_csv_format(self, csv_content):
        """Detect the CSV format and field mappings"""
        # Try to parse first few lines to detect format
        lines = csv_content.strip().split('\n')
        if len(lines) < 2:
            raise ValueError("CSV file must have at least a header row and one data row")
        
        # Get header row
        header = lines[0].lower()
        
        # Common field mappings
        field_mappings = {
            'name': ['name', 'full_name', 'contact_name', 'first_name', 'fname'],
            'email': ['email', 'email_address', 'e-mail'],
            'phone': ['phone', 'phone_number', 'mobile', 'telephone'],
            'company': ['company', 'organization', 'employer', 'company_name'],
            'title': ['title', 'job_title', 'position', 'role'],
            'linkedin': ['linkedin', 'linkedin_url', 'linkedin_profile'],
            'twitter': ['twitter', 'twitter_handle', 'twitter_url'],
            'notes': ['notes', 'description', 'comments', 'bio'],
            'location': ['location', 'city', 'address', 'country'],
            'interests': ['interests', 'skills', 'expertise', 'tags'],
            'relationship_type': ['relationship', 'relationship_type', 'connection_type', 'type'],
            'introduced_by': ['introduced_by', 'referrer', 'source', 'introduction_source']
        }
        
        detected_fields = {}
        csv_reader = csv.reader([header])
        header_row = next(csv_reader)
        
        for i, column in enumerate(header_row):
            column_lower = column.lower().strip()
            for field, variations in field_mappings.items():
                if column_lower in variations:
                    detected_fields[field] = i
                    break
        
        return detected_fields, header_row
    
    def validate_contact_data(self, row_data, row_number):
        """Validate contact data and return cleaned data with any warnings"""
        warnings = []
        
        # Name is required
        if not row_data.get('name', '').strip():
            raise ValueError(f"Row {row_number}: Name is required")
        
        # Clean and validate email
        email = row_data.get('email', '').strip()
        if email and '@' not in email:
            warnings.append(f"Row {row_number}: Invalid email format: {email}")
            email = None
        
        # Clean phone number
        phone = row_data.get('phone', '').strip()
        if phone:
            # Remove common phone formatting
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                warnings.append(f"Row {row_number}: Phone number may be incomplete: {phone}")
        
        # Validate LinkedIn URL
        linkedin = row_data.get('linkedin', '').strip()
        if linkedin and not linkedin.startswith('http'):
            if 'linkedin.com' not in linkedin:
                linkedin = f"linkedin.com/in/{linkedin}"
        
        # Clean Twitter handle
        twitter = row_data.get('twitter', '').strip()
        if twitter and twitter.startswith('@'):
            twitter = twitter[1:]  # Remove @ symbol
        
        # Set default relationship type
        relationship_type = row_data.get('relationship_type', '').strip() or 'Contact'
        
        cleaned_data = {
            'name': row_data.get('name', '').strip(),
            'email': email,
            'phone': phone,
            'company': row_data.get('company', '').strip() or None,
            'title': row_data.get('title', '').strip() or None,
            'linkedin': linkedin or None,
            'twitter': twitter or None,
            'notes': row_data.get('notes', '').strip() or None,
            'location': row_data.get('location', '').strip() or None,
            'interests': row_data.get('interests', '').strip() or None,
            'relationship_type': relationship_type,
            'introduced_by': row_data.get('introduced_by', '').strip() or None,
            'warmth_status': 1,  # Default to Cold
            'warmth_label': 'Cold',
            'priority_level': 'Medium'
        }
        
        return cleaned_data, warnings
    
    def import_from_csv(self, csv_content, skip_duplicates=True):
        """Import contacts from CSV content"""
        try:
            # Detect CSV format
            field_mappings, header_row = self.detect_csv_format(csv_content)
            
            if not field_mappings:
                raise ValueError("Could not detect any recognizable contact fields in CSV")
            
            # Parse CSV content
            csv_reader = csv.reader(io.StringIO(csv_content))
            next(csv_reader)  # Skip header row
            
            for row_number, row in enumerate(csv_reader, start=2):
                self.import_stats['total_rows'] += 1
                
                try:
                    # Map CSV row to contact fields
                    row_data = {}
                    for field, column_index in field_mappings.items():
                        if column_index < len(row):
                            row_data[field] = row[column_index]
                    
                    # Validate and clean data
                    cleaned_data, warnings = self.validate_contact_data(row_data, row_number)
                    self.import_stats['warnings'].extend(warnings)
                    
                    # Check for duplicates
                    if skip_duplicates and cleaned_data['email']:
                        existing_contacts = self.contact_model.get_all(self.user_id)
                        for contact in existing_contacts:
                            if contact.get('email') == cleaned_data['email']:
                                self.import_stats['warnings'].append(
                                    f"Row {row_number}: Skipped duplicate email: {cleaned_data['email']}"
                                )
                                continue
                    
                    # Create contact
                    contact_id = self.contact_model.create(
                        user_id=self.user_id,
                        **cleaned_data
                    )
                    
                    if contact_id:
                        self.import_stats['successful_imports'] += 1
                        logging.info(f"Imported contact: {cleaned_data['name']}")
                    else:
                        self.import_stats['errors'].append(
                            f"Row {row_number}: Failed to create contact {cleaned_data['name']}"
                        )
                
                except Exception as e:
                    error_msg = f"Row {row_number}: {str(e)}"
                    self.import_stats['errors'].append(error_msg)
                    logging.error(error_msg)
                    continue
        
        except Exception as e:
            self.import_stats['errors'].append(f"CSV parsing error: {str(e)}")
            logging.error(f"CSV import failed: {str(e)}")
        
        return self.import_stats
    
    def get_sample_csv_format(self):
        """Return a sample CSV format for user reference"""
        sample_csv = """name,email,company,title,phone,linkedin,notes,relationship_type
John Smith,john@example.com,TechCorp,CEO,555-1234,linkedin.com/in/johnsmith,Met at conference,Investor
Jane Doe,jane@startup.com,StartupInc,CTO,,jane-doe,Technical advisor,Mentor
Mike Johnson,mike@vc.com,VC Partners,Partner,555-5678,mike-johnson,Potential investor,Investor"""
        return sample_csv
    
    def generate_import_summary(self):
        """Generate a summary of the import process"""
        summary = {
            'total_processed': self.import_stats['total_rows'],
            'successful': self.import_stats['successful_imports'],
            'failed': len(self.import_stats['errors']),
            'warnings': len(self.import_stats['warnings']),
            'success_rate': 0
        }
        
        if summary['total_processed'] > 0:
            summary['success_rate'] = (summary['successful'] / summary['total_processed']) * 100
        
        return summary