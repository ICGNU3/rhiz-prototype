#!/usr/bin/env python3

import sqlite3
import uuid
from datetime import datetime, timedelta

def seed_demo_data():
    """Seed database with demo data matching the actual schema"""
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Create demo user with the ID that matches the session
    demo_user_id = 'demo_user'
    
    # Insert demo user
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, email, subscription_tier)
        VALUES (?, ?, ?)
    ''', (demo_user_id, 'demo@rhiz.app', 'founder_plus'))
    
    print(f"Created demo user with ID: {demo_user_id}")
    
    # Create demo goals (matching actual schema: id, user_id, title, description, embedding, created_at)
    goals_data = [
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'title': 'Raise $250k angel round',
            'description': 'Looking for 5-10 angel investors to complete our pre-seed round with strategic value'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'title': 'Find technical co-founder',
            'description': 'Need a full-stack engineer who can lead product development'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'title': 'Launch beta with 100 users',
            'description': 'Get initial user feedback and iterate on product-market fit'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'title': 'Build media presence',
            'description': 'Connect with tech journalists and thought leaders for visibility'
        }
    ]
    
    for goal in goals_data:
        cursor.execute('''
            INSERT OR REPLACE INTO goals (id, user_id, title, description)
            VALUES (?, ?, ?, ?)
        ''', (goal['id'], goal['user_id'], goal['title'], goal['description']))
    
    print(f"Created {len(goals_data)} demo goals")
    
    # Create demo contacts (using existing schema)
    contacts_data = [
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'name': 'Sarah Chen',
            'email': 'sarah@venture.fund',
            'company': 'Venture Fund Partners',
            'title': 'Principal',
            'relationship_type': 'Investor',
            'warmth_status': 3,
            'warmth_label': 'Warm',
            'priority_level': 'High',
            'notes': 'Former founder, now investing in early-stage B2B companies. Interested in our space.',
            'tags': 'investor,b2b,former-founder'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'name': 'Mike Rodriguez',
            'email': 'mike@techstartup.com',
            'company': 'TechStartup Inc',
            'title': 'Senior Full-Stack Engineer',
            'relationship_type': 'Potential Hire',
            'warmth_status': 2,
            'warmth_label': 'Aware',
            'priority_level': 'High',
            'notes': 'Excellent engineer with 5+ years experience. Open to new opportunities.',
            'tags': 'engineer,fullstack,javascript'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'name': 'Dr. Emily Watson',
            'email': 'emily@techcrunch.com',
            'company': 'TechCrunch',
            'title': 'Senior Reporter',
            'relationship_type': 'Press',
            'warmth_status': 1,
            'warmth_label': 'Cold',
            'priority_level': 'Medium',
            'notes': 'Covers early-stage startups. Could be good for launch coverage.',
            'tags': 'press,techcrunch,reporter'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'name': 'Alex Kumar',
            'email': 'alex@earlycustomer.com',
            'company': 'Early Customer Co',
            'title': 'Product Manager',
            'relationship_type': 'Potential Customer',
            'warmth_status': 4,
            'warmth_label': 'Active',
            'priority_level': 'High',
            'notes': 'Very interested in our beta. Could be a design partner.',
            'tags': 'customer,beta,product-manager'
        }
    ]
    
    for contact in contacts_data:
        cursor.execute('''
            INSERT OR REPLACE INTO contacts 
            (id, user_id, name, email, company, title, relationship_type, warmth_status, 
             warmth_label, priority_level, notes, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (contact['id'], contact['user_id'], contact['name'], contact['email'], 
              contact['company'], contact['title'], contact['relationship_type'], 
              contact['warmth_status'], contact['warmth_label'], contact['priority_level'],
              contact['notes'], contact['tags']))
    
    print(f"Created {len(contacts_data)} demo contacts")
    
    # Create demo AI suggestions (matching schema: id, contact_id, goal_id, suggestion, confidence, created_at)
    ai_suggestions_data = [
        {
            'id': str(uuid.uuid4()),
            'contact_id': contacts_data[0]['id'],
            'goal_id': goals_data[0]['id'],
            'suggestion': 'Perfect investor match for angel round - Sarah has strong track record investing in B2B companies at your stage',
            'confidence': 0.92
        },
        {
            'id': str(uuid.uuid4()),
            'contact_id': contacts_data[1]['id'],
            'goal_id': goals_data[1]['id'],
            'suggestion': 'Strong technical co-founder candidate - Mike has the full-stack skills and startup interest you need',
            'confidence': 0.87
        },
        {
            'id': str(uuid.uuid4()),
            'contact_id': contacts_data[3]['id'],
            'goal_id': goals_data[2]['id'],
            'suggestion': 'Excellent beta user candidate - Alex is actively looking for tools like yours and could provide valuable feedback',
            'confidence': 0.84
        }
    ]
    
    for suggestion in ai_suggestions_data:
        cursor.execute('''
            INSERT OR REPLACE INTO ai_suggestions (id, contact_id, goal_id, suggestion, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (suggestion['id'], suggestion['contact_id'], suggestion['goal_id'], 
              suggestion['suggestion'], suggestion['confidence']))
    
    print(f"Created {len(ai_suggestions_data)} AI suggestions")
    
    # Create some interaction history
    interactions_data = [
        {
            'id': str(uuid.uuid4()),
            'contact_id': contacts_data[0]['id'],
            'user_id': demo_user_id,
            'interaction_type': 'Email',
            'status': 'replied',
            'direction': 'outbound',
            'subject': 'Initial pitch deck',
            'summary': 'Sent initial pitch deck for review',
            'sentiment': 'positive',
            'notes': 'Sarah responded positively, wants to schedule a call'
        },
        {
            'id': str(uuid.uuid4()),
            'contact_id': contacts_data[3]['id'],
            'user_id': demo_user_id,
            'interaction_type': 'Call',
            'status': 'completed',
            'direction': 'outbound',
            'subject': 'Product demo call',
            'summary': 'Demo call went very well',
            'sentiment': 'positive',
            'notes': 'Very interested in becoming a design partner',
            'duration_minutes': 30
        }
    ]
    
    for interaction in interactions_data:
        cursor.execute('''
            INSERT OR REPLACE INTO contact_interactions 
            (id, contact_id, user_id, interaction_type, status, direction, subject, 
             summary, sentiment, notes, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (interaction['id'], interaction['contact_id'], interaction['user_id'],
              interaction['interaction_type'], interaction['status'], interaction['direction'],
              interaction['subject'], interaction['summary'], interaction['sentiment'],
              interaction['notes'], interaction.get('duration_minutes')))
    
    print(f"Created {len(interactions_data)} demo interactions")
    
    conn.commit()
    conn.close()
    
    print("Demo data seeding completed successfully!")
    print(f"Demo user '{demo_user_id}' ready with {len(goals_data)} goals, {len(contacts_data)} contacts")

if __name__ == "__main__":
    seed_demo_data()