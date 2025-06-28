#!/usr/bin/env python3
"""
Test contact import functionality directly
"""
import os
import psycopg2
from datetime import datetime
import uuid
import csv

def test_contact_import():
    """Test the contact import with actual database"""
    # Connect to PostgreSQL database
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    cursor = conn.cursor()
    
    # Read the CSV file
    with open('attached_assets/Connections_1751086868128.csv', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"CSV content length: {len(content)} characters")
        print(f"First 200 characters:\n{content[:200]}")
    
    # Process CSV - skip the notes section and find the header
    lines = content.strip().split('\n')
    
    # Find the actual header line
    header_line = None
    header_index = 0
    for i, line in enumerate(lines):
        if 'First Name' in line and 'Last Name' in line:
            header_line = line
            header_index = i
            break
    
    if not header_line:
        print("Could not find header line in CSV")
        return 0
    
    # Process CSV starting from header
    csv_content = '\n'.join(lines[header_index:])
    import io
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    
    user_id = "test_user"  # Define user_id at top level
    contacts_imported = 0
    for row in csv_reader:
        # Skip empty rows
        if not any(row.values()):
            continue
            
        print(f"Processing row: {dict(row)}")
        
        # Extract data
        first_name = row.get('First Name', '').strip()
        last_name = row.get('Last Name', '').strip()
        email = row.get('Email Address', '').strip()
        company = row.get('Company', '').strip()
        position = row.get('Position', '').strip()
        
        # Create full name
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name
        elif last_name:
            full_name = last_name
        elif email:
            full_name = email
        else:
            continue
            
        # Generate unique ID
        contact_id = str(uuid.uuid4())
        user_id = "test_user"
        
        # Insert contact
        try:
            cursor.execute('''
                INSERT INTO contacts (id, user_id, name, email, phone, company, title, 
                                    notes, warmth_status, warmth_label, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contact_id,
                user_id,
                full_name,
                email,
                '',  # phone
                company,
                position,
                'Imported from LinkedIn CSV test',
                3,  # Warm
                'Warm',
                'linkedin',
                datetime.now().isoformat()
            ))
            contacts_imported += 1
            print(f"Imported: {full_name}")
            
        except Exception as e:
            print(f"Error importing {full_name}: {e}")
            
    conn.commit()
    print(f"\nTotal contacts imported: {contacts_imported}")
    
    # Verify import
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    print(f"Contacts in database for test_user: {count}")
    
    # Show sample contacts
    cursor.execute("SELECT name, email, company, warmth_label FROM contacts WHERE user_id = ? LIMIT 5", (user_id,))
    samples = cursor.fetchall()
    print("\nSample imported contacts:")
    for sample in samples:
        print(f"  {sample[0]} - {sample[1]} - {sample[2]} ({sample[3]})")
    
    conn.close()
    return contacts_imported

if __name__ == "__main__":
    result = test_contact_import()
    print(f"Import test completed. Imported {result} contacts.")