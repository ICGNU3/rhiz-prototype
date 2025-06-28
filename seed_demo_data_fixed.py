#!/usr/bin/env python3

import sqlite3
import uuid
from datetime import datetime, timedelta

def seed_demo_data():
    """Seed database with demo data using the correct user_id"""
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
    
    # Create demo goals
    goals = [
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'title': 'Raise $250k angel round',
            'description': 'Looking for 5-10 angel investors to complete our pre-seed round with strategic value',
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'title': 'Find technical co-founder',
            'description': 'Need a full-stack engineer who can lead product development',
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'title': 'Launch beta with 100 users',
            'description': 'Get initial user feedback and iterate on product-market fit',
            'status': 'in_progress',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'title': 'Build media presence',
            'description': 'Connect with tech journalists and thought leaders for visibility',
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ]
    
    for goal in goals:
        columns = ', '.join(goal.keys())
        placeholders = ', '.join(['?' for _ in goal])
        cursor.execute(f'INSERT OR REPLACE INTO goals ({columns}) VALUES ({placeholders})', list(goal.values()))
    
    print(f"Created {len(goals)} demo goals")
    
    # Create demo contacts
    contacts = [
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
            'tags': 'investor,b2b,former-founder',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
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
            'tags': 'engineer,fullstack,javascript',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
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
            'tags': 'press,techcrunch,reporter',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
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
            'tags': 'customer,beta,product-manager',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ]
    
    for contact in contacts:
        columns = ', '.join(contact.keys())
        placeholders = ', '.join(['?' for _ in contact])
        cursor.execute(f'INSERT OR REPLACE INTO contacts ({columns}) VALUES ({placeholders})', list(contact.values()))
    
    print(f"Created {len(contacts)} demo contacts")
    
    # Create demo AI suggestions
    ai_suggestions = [
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'goal_id': goals[0]['id'],
            'contact_id': contacts[0]['id'],
            'confidence_score': 0.92,
            'suggestion_type': 'goal_match',
            'title': 'Perfect investor match for angel round',
            'description': 'Sarah has a strong track record investing in B2B companies at your stage',
            'action_items': 'Send personalized intro highlighting traction metrics',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'goal_id': goals[1]['id'],
            'contact_id': contacts[1]['id'],
            'confidence_score': 0.87,
            'suggestion_type': 'goal_match',
            'title': 'Strong technical co-founder candidate',
            'description': 'Mike has the full-stack skills and startup interest you need',
            'action_items': 'Schedule coffee chat to discuss the opportunity',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ]
    
    for suggestion in ai_suggestions:
        columns = ', '.join(suggestion.keys())
        placeholders = ', '.join(['?' for _ in suggestion])
        cursor.execute(f'INSERT OR REPLACE INTO ai_suggestions ({columns}) VALUES ({placeholders})', list(suggestion.values()))
    
    print(f"Created {len(ai_suggestions)} AI suggestions")
    
    # Create some interaction history
    interactions = [
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'contact_id': contacts[0]['id'],
            'interaction_type': 'email',
            'interaction_date': (datetime.now() - timedelta(days=3)).isoformat(),
            'notes': 'Sent initial pitch deck',
            'outcome': 'positive',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': demo_user_id,
            'contact_id': contacts[3]['id'],
            'interaction_type': 'call',
            'interaction_date': (datetime.now() - timedelta(days=1)).isoformat(),
            'notes': 'Demo call went well, very interested',
            'outcome': 'positive',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ]
    
    for interaction in interactions:
        columns = ', '.join(interaction.keys())
        placeholders = ', '.join(['?' for _ in interaction])
        cursor.execute(f'INSERT OR REPLACE INTO contact_interactions ({columns}) VALUES ({placeholders})', list(interaction.values()))
    
    print(f"Created {len(interactions)} demo interactions")
    
    conn.commit()
    conn.close()
    
    print("Demo data seeding completed successfully!")
    print(f"Created demo user '{demo_user_id}' with {len(goals)} goals, {len(contacts)} contacts")

if __name__ == "__main__":
    seed_demo_data()