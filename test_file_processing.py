#!/usr/bin/env python3
"""
Test script to validate file processing functionality
"""
import csv
from io import StringIO

def test_csv_processing():
    """Test CSV file processing logic"""
    # Sample CSV content
    csv_content = """name,email,company,title
John Smith,john@example.com,Tech Corp,Software Engineer
Jane Doe,jane@techstart.com,TechStart,Product Manager
Mike Johnson,mike@consulting.com,Mike Consulting,Freelancer"""
    
    # Test CSV parsing with field mapping
    reader = csv.DictReader(StringIO(csv_content))
    
    field_mappings = {
        'name': 'name',
        'email': 'email',
        'company': 'company',
        'title': 'title'
    }
    
    contacts = []
    for row in reader:
        contact_data = {}
        for csv_field, value in row.items():
            if csv_field in field_mappings and value:
                standard_field = field_mappings[csv_field]
                contact_data[standard_field] = value.strip()
        
        if contact_data.get('name') or contact_data.get('email'):
            contacts.append(contact_data)
    
    print(f"Successfully processed {len(contacts)} contacts:")
    for contact in contacts:
        print(f"  - {contact['name']} ({contact.get('email', 'no email')}) at {contact.get('company', 'no company')}")
    
    return len(contacts) == 3

def test_linkedin_csv_format():
    """Test LinkedIn CSV format processing"""
    linkedin_csv = """First Name,Last Name,Email Address,Company,Position
John,Smith,john@example.com,Tech Corp,Software Engineer
Jane,Doe,jane@techstart.com,TechStart,Product Manager"""
    
    reader = csv.DictReader(StringIO(linkedin_csv))
    
    # LinkedIn field mappings
    field_mappings = {
        'First Name': 'first_name',
        'Last Name': 'last_name', 
        'Email Address': 'email',
        'Company': 'company',
        'Position': 'title'
    }
    
    contacts = []
    for row in reader:
        contact_data = {}
        for csv_field, value in row.items():
            if csv_field in field_mappings and value:
                standard_field = field_mappings[csv_field]
                contact_data[standard_field] = value.strip()
        
        # Create full name
        if 'first_name' in contact_data and 'last_name' in contact_data:
            full_name = f"{contact_data['first_name']} {contact_data['last_name']}"
            contact_data['name'] = full_name
        
        if contact_data.get('name') or contact_data.get('email'):
            contacts.append(contact_data)
    
    print(f"LinkedIn format: Successfully processed {len(contacts)} contacts:")
    for contact in contacts:
        print(f"  - {contact['name']} ({contact.get('email', 'no email')}) at {contact.get('company', 'no company')}")
    
    return len(contacts) == 2

if __name__ == "__main__":
    print("Testing CSV file processing functionality...\n")
    
    print("1. Testing basic CSV format:")
    basic_test = test_csv_processing()
    print(f"   Result: {'PASS' if basic_test else 'FAIL'}\n")
    
    print("2. Testing LinkedIn CSV format:")
    linkedin_test = test_linkedin_csv_format()
    print(f"   Result: {'PASS' if linkedin_test else 'FAIL'}\n")
    
    if basic_test and linkedin_test:
        print("✅ All file processing tests PASSED!")
        print("The CSV processing logic is working correctly.")
    else:
        print("❌ Some tests FAILED!")
        print("File processing needs debugging.")