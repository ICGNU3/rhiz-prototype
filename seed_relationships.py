"""
Seed sample relationship data for network visualization demonstration.
Creates realistic connections between existing contacts.
"""

from models import Database
import uuid
import logging

def seed_sample_relationships():
    """Create sample relationships between existing contacts"""
    db = Database()
    conn = db.get_connection()
    
    try:
        # Get existing contacts
        contacts = conn.execute("SELECT id, name, company FROM contacts ORDER BY name").fetchall()
        
        if len(contacts) < 2:
            logging.info("Not enough contacts to create relationships")
            return
        
        # Sample relationships to create
        relationships = [
            # Tech founder connections
            (0, 1, "worked_with", 4, "Co-founded a startup together"),
            (1, 2, "investor_founder", 3, "Series A investment relationship"),
            (2, 3, "mentor_mentee", 4, "Long-term mentorship"),
            (3, 4, "business_partners", 3, "Strategic partnership"),
            (4, 5, "introduced_by", 2, "Met at tech conference"),
            (5, 6, "colleagues", 3, "Worked at same company"),
            (6, 7, "knows", 2, "Industry connections"),
            (7, 8, "friends", 4, "Personal friendship"),
            (0, 3, "knows", 2, "Met through mutual connections"),
            (1, 4, "business_partners", 3, "Joint venture"),
            (2, 5, "mentor_mentee", 3, "Advisory relationship"),
            (4, 7, "worked_with", 3, "Previous startup collaboration"),
            (5, 8, "introduced_by", 2, "Introduction for potential deal"),
            (0, 6, "colleagues", 2, "Industry peers"),
            (3, 8, "investor_founder", 4, "Investment relationship"),
        ]
        
        # Create relationships
        created_count = 0
        for contact_a_idx, contact_b_idx, rel_type, strength, notes in relationships:
            if contact_a_idx < len(contacts) and contact_b_idx < len(contacts):
                contact_a = contacts[contact_a_idx]
                contact_b = contacts[contact_b_idx]
                
                # Check if relationship already exists
                existing = conn.execute(
                    """SELECT id FROM contact_relationships 
                       WHERE (contact_a_id = ? AND contact_b_id = ?) 
                          OR (contact_a_id = ? AND contact_b_id = ?)""",
                    (contact_a['id'], contact_b['id'], contact_b['id'], contact_a['id'])
                ).fetchone()
                
                if not existing:
                    relationship_id = str(uuid.uuid4())
                    conn.execute(
                        """INSERT INTO contact_relationships 
                           (id, user_id, contact_a_id, contact_b_id, relationship_type, strength, notes) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (relationship_id, "default-user", contact_a['id'], contact_b['id'], 
                         rel_type, strength, notes)
                    )
                    created_count += 1
                    logging.info(f"Created relationship: {contact_a['name']} -> {contact_b['name']} ({rel_type})")
        
        conn.commit()
        logging.info(f"Successfully created {created_count} relationships")
        
        # Display summary
        total_relationships = conn.execute("SELECT COUNT(*) FROM contact_relationships").fetchone()[0]
        print(f"Network now has {total_relationships} total relationships")
        
        return created_count
        
    except Exception as e:
        logging.error(f"Error seeding relationships: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = seed_sample_relationships()
    print(f"Seeded {count} new relationships for network visualization")