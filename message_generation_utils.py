#!/usr/bin/env python3
"""
Enhanced message generation utilities that connect goals with contacts using comprehensive context.
Includes contact bio, interaction history, and relationship context for personalized messaging.
"""

import logging
from models import Database, Contact, Goal, ContactInteraction
from openai_utils import OpenAIUtils
from database_utils import load_contact_bio

def get_contact_interaction_history(contact_id, limit=5):
    """Get recent interaction history for a contact"""
    db = Database()
    conn = db.get_connection()
    
    try:
        interactions = conn.execute(
            """SELECT interaction_type, subject, summary, sentiment, timestamp, direction
               FROM contact_interactions 
               WHERE contact_id = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""", 
            (contact_id, limit)
        ).fetchall()
        
        if not interactions:
            return ""
        
        history_parts = []
        for interaction in interactions:
            timestamp = interaction['timestamp'][:10]  # Just the date
            direction = "Outbound" if interaction['direction'] == 'outbound' else "Inbound"
            
            history_entry = f"{timestamp}: {direction} {interaction['interaction_type']}"
            if interaction['subject']:
                history_entry += f" - {interaction['subject']}"
            if interaction['summary']:
                history_entry += f". {interaction['summary']}"
            if interaction['sentiment']:
                history_entry += f" (Sentiment: {interaction['sentiment']})"
            
            history_parts.append(history_entry)
        
        return "; ".join(history_parts)
        
    except Exception as e:
        logging.error(f"Error getting interaction history for contact {contact_id}: {e}")
        return ""
    finally:
        conn.close()

def generate_personalized_message(contact_id, goal_id, tone="warm"):
    """Generate a personalized message connecting a contact to a specific goal"""
    db = Database()
    openai_utils = OpenAIUtils()
    
    conn = db.get_connection()
    try:
        # Get contact information
        contact = conn.execute(
            "SELECT name, relationship_type FROM contacts WHERE id = ?", 
            (contact_id,)
        ).fetchone()
        
        # Get goal information
        goal = conn.execute(
            "SELECT title, description FROM goals WHERE id = ?", 
            (goal_id,)
        ).fetchone()
        
        if not contact or not goal:
            logging.error(f"Contact {contact_id} or goal {goal_id} not found")
            return None
        
        # Load comprehensive contact bio
        contact_bio = load_contact_bio(contact_id)
        
        # Get interaction history
        interaction_history = get_contact_interaction_history(contact_id)
        
        # Generate the message
        message = openai_utils.generate_message(
            contact_name=contact['name'],
            goal_title=goal['title'],
            goal_description=goal['description'],
            contact_bio=contact_bio,
            interaction_history=interaction_history,
            tone=tone
        )
        
        return {
            'contact_name': contact['name'],
            'relationship_type': contact['relationship_type'],
            'goal_title': goal['title'],
            'message': message,
            'tone': tone,
            'has_history': bool(interaction_history),
            'bio_length': len(contact_bio)
        }
        
    except Exception as e:
        logging.error(f"Error generating message for contact {contact_id}, goal {goal_id}: {e}")
        return None
    finally:
        conn.close()

def generate_messages_for_goal_matches(goal_id, max_contacts=5, tone="warm"):
    """Generate messages for the top contacts matched to a goal"""
    from database_utils import match_contacts_to_goal
    
    # Get top matches for the goal
    matches = match_contacts_to_goal(goal_id)
    
    messages = []
    for contact_id, contact_name, score in matches[:max_contacts]:
        message_data = generate_personalized_message(contact_id, goal_id, tone)
        if message_data:
            message_data['similarity_score'] = score
            messages.append(message_data)
    
    return messages

def test_message_generation():
    """Test the enhanced message generation with different tones and contexts"""
    print("Testing Enhanced Message Generation")
    print("=" * 50)
    
    db = Database()
    conn = db.get_connection()
    
    # Get a sample goal and contact
    goal = conn.execute("SELECT id, title FROM goals LIMIT 1").fetchone()
    contact = conn.execute("SELECT id, name FROM contacts LIMIT 1").fetchone()
    
    if not goal or not contact:
        print("No goals or contacts found for testing")
        return
    
    print(f"Goal: {goal['title']}")
    print(f"Contact: {contact['name']}")
    print("-" * 30)
    
    # Test different tones
    tones = ["warm", "professional", "casual", "urgent"]
    
    for tone in tones:
        print(f"\n{tone.upper()} TONE:")
        print("-" * 20)
        
        message_data = generate_personalized_message(contact['id'], goal['id'], tone)
        if message_data:
            print(message_data['message'])
            print(f"\nContext: Bio ({message_data['bio_length']} chars), History: {message_data['has_history']}")
        else:
            print("Failed to generate message")
    
    conn.close()

def demonstrate_goal_matching_messages():
    """Demonstrate message generation for all matched contacts of a goal"""
    print("\n\nDemonstrating Goal-Contact Message Generation")
    print("=" * 50)
    
    db = Database()
    conn = db.get_connection()
    
    # Get a sample goal
    goal = conn.execute("SELECT id, title, description FROM goals LIMIT 1").fetchone()
    
    if not goal:
        print("No goals found")
        return
    
    print(f"Goal: {goal['title']}")
    print(f"Description: {goal['description'][:100]}...")
    print("-" * 50)
    
    # Generate messages for top matches
    messages = generate_messages_for_goal_matches(goal['id'], max_contacts=3, tone="warm")
    
    for i, msg_data in enumerate(messages, 1):
        print(f"\n{i}. {msg_data['contact_name']} ({msg_data['relationship_type']}) - Score: {msg_data['similarity_score']:.3f}")
        print("-" * 40)
        print(msg_data['message'])
        print(f"\nGenerated with {msg_data['bio_length']} char bio, History: {msg_data['has_history']}")
    
    conn.close()

if __name__ == "__main__":
    print("Enhanced Message Generation Test Suite")
    print("=" * 50)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        test_message_generation()
        demonstrate_goal_matching_messages()
        
        print("\n" + "=" * 50)
        print("✓ Message generation tests completed!")
        print("\nFeatures demonstrated:")
        print("- Personalized messages using comprehensive contact bios")
        print("- Integration with interaction history and relationship context")
        print("- Multiple tone options (warm, professional, casual, urgent)")
        print("- Goal-to-contact matching with message generation")
        print("- Modern OpenAI GPT-4o integration")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        logging.error(f"Test error: {e}")