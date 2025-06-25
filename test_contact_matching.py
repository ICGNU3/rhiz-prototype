#!/usr/bin/env python3
"""
Test script for enhanced contact bio embedding and goal matching functionality.
Demonstrates the comprehensive contact bio loading and cosine similarity matching.
"""

import logging
from database_utils import load_contact_bio, generate_contact_embedding, match_contacts_to_goal
from models import Database, Contact, Goal

def test_contact_bio_loading():
    """Test the comprehensive contact bio loading functionality"""
    print("Testing Contact Bio Loading")
    print("=" * 40)
    
    db = Database()
    conn = db.get_connection()
    
    # Get all contacts
    contacts = conn.execute("SELECT id, name FROM contacts").fetchall()
    
    for contact in contacts:
        print(f"\nContact: {contact['name']}")
        print("-" * 30)
        
        # Load comprehensive bio
        bio = load_contact_bio(contact['id'])
        print(f"Bio: {bio[:200]}...")
        
        # Generate embedding
        embedding = generate_contact_embedding(contact['id'])
        if embedding:
            print(f"Embedding generated: {len(embedding)} characters")
        else:
            print("Failed to generate embedding")
    
    conn.close()

def test_goal_matching():
    """Test the enhanced goal-to-contact matching"""
    print("\n\nTesting Goal-to-Contact Matching")
    print("=" * 40)
    
    db = Database()
    conn = db.get_connection()
    
    # Get all goals
    goals = conn.execute("SELECT id, title, description FROM goals").fetchall()
    
    for goal in goals:
        print(f"\nGoal: {goal['title']}")
        print(f"Description: {goal['description'][:100]}...")
        print("-" * 50)
        
        # Find matching contacts
        matches = match_contacts_to_goal(goal['id'])
        
        print(f"Found {len(matches)} contact matches:")
        for i, (contact_id, name, score) in enumerate(matches[:5]):
            print(f"  {i+1}. {name} - Score: {score:.3f}")
    
    conn.close()

def demonstrate_bio_enhancement():
    """Demonstrate the improvement in bio quality for matching"""
    print("\n\nDemonstrating Bio Enhancement")
    print("=" * 40)
    
    db = Database()
    conn = db.get_connection()
    
    # Get a sample contact
    contact = conn.execute("SELECT * FROM contacts LIMIT 1").fetchone()
    
    if contact:
        print(f"Sample Contact: {contact['name']}")
        print("-" * 30)
        
        # Show basic vs comprehensive bio
        basic_bio = contact['name']
        if contact['notes']:
            basic_bio += f" - {contact['notes']}"
        
        comprehensive_bio = load_contact_bio(contact['id'])
        
        print(f"Basic bio: {basic_bio}")
        print(f"\nComprehensive bio: {comprehensive_bio}")
        
        print(f"\nBio enhancement: {len(comprehensive_bio)} vs {len(basic_bio)} characters")
        print(f"Enhancement ratio: {len(comprehensive_bio) / len(basic_bio):.1f}x more detailed")
    
    conn.close()

if __name__ == "__main__":
    print("Contact Bio Embedding & Matching Test")
    print("=" * 50)
    
    # Configure logging to see the matching process
    logging.basicConfig(level=logging.INFO)
    
    try:
        test_contact_bio_loading()
        test_goal_matching()
        demonstrate_bio_enhancement()
        
        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        print("\nEnhanced Features:")
        print("- Comprehensive contact bio loading from all fields")
        print("- OpenAI embedding generation for full contact profiles")
        print("- Cosine similarity matching with improved accuracy")
        print("- Support for LinkedIn bios, Twitter profiles, and rich notes")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        logging.error(f"Test error: {e}")