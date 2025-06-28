"""
Demo data seeding for Rhiz platform
Creates realistic sample data for demonstration purposes
"""
import sqlite3
import json
from datetime import datetime, timedelta
import random

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def create_demo_user():
    """Create demo user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if demo user exists
    user = cursor.execute(
        'SELECT id FROM users WHERE email = ?', ('demo@rhiz.app',)
    ).fetchone()
    
    if not user:
        cursor.execute(
            'INSERT INTO users (email, subscription_tier, created_at) VALUES (?, ?, ?)',
            ('demo@rhiz.app', 'founder_plus', datetime.now().isoformat())
        )
        user_id = cursor.lastrowid
        conn.commit()
        print(f"Created demo user with ID: {user_id}")
    else:
        user_id = user['id']
        print(f"Demo user already exists with ID: {user_id}")
    
    # Also ensure demo_user exists for session compatibility
    demo_user = cursor.execute(
        'SELECT id FROM users WHERE email = ?', ('demo_user',)
    ).fetchone()
    
    if not demo_user:
        cursor.execute(
            'INSERT INTO users (email, subscription_tier, created_at) VALUES (?, ?, ?)',
            ('demo_user', 'founder_plus', datetime.now().isoformat())
        )
        demo_user_id = cursor.lastrowid
        conn.commit() 
        print(f"Created demo_user with ID: {demo_user_id}")
        # Use demo_user ID for consistency with session
        user_id = demo_user_id
    else:
        demo_user_id = demo_user['id']
        print(f"Demo_user already exists with ID: {demo_user_id}")
        user_id = demo_user_id
    
    conn.close()
    return user_id

def create_demo_goals(user_id):
    """Create demo goals"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    demo_goals = [
        {
            'title': 'Raise $250k Angel Round',
            'description': 'Seeking angel investors for our AI-powered relationship intelligence platform. Looking for investors with SaaS experience and network in the AI space.'
        },
        {
            'title': 'Hire Senior Backend Engineer', 
            'description': 'Need an experienced Python/Flask developer with AI/ML background to scale our backend infrastructure and implement advanced features.'
        },
        {
            'title': 'Find Beta Customers',
            'description': 'Looking for 10-15 early-stage founders and VCs to beta test our platform and provide feedback on product-market fit.'
        },
        {
            'title': 'Partnership with CRM Platform',
            'description': 'Explore integration partnerships with major CRM platforms like HubSpot or Salesforce to expand our reach.'
        }
    ]
    
    goal_ids = []
    for goal in demo_goals:
        # Check if goal exists
        existing = cursor.execute(
            'SELECT id FROM goals WHERE user_id = ? AND title = ?',
            (user_id, goal['title'])
        ).fetchone()
        
        if not existing:
            cursor.execute(
                'INSERT INTO goals (user_id, title, description, created_at) VALUES (?, ?, ?, ?)',
                (user_id, goal['title'], goal['description'], datetime.now().isoformat())
            )
            goal_ids.append(cursor.lastrowid)
        else:
            goal_ids.append(existing['id'])
    
    conn.commit()
    conn.close()
    print(f"Created/verified {len(goal_ids)} demo goals")
    return goal_ids

def create_demo_contacts(user_id):
    """Create demo contacts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    demo_contacts = [
        {
            'name': 'Sarah Chen',
            'email': 'sarah@vectorcapital.com',
            'company': 'Vector Capital',
            'title': 'Partner',
            'relationship_type': 'investor',
            'warmth_status': 4,
            'warmth_label': 'Warm',
            'priority_level': 'high',
            'notes': 'Met at TechCrunch Disrupt. Interested in AI/SaaS. Invested in 3 AI startups last year.',
            'tags': 'investor,ai,saas,techcrunch',
            'location': 'San Francisco, CA',
            'interests': 'AI, SaaS, early-stage startups'
        },
        {
            'name': 'Marcus Rodriguez',
            'email': 'marcus@stripe.com',
            'company': 'Stripe',
            'title': 'Senior Engineering Manager',
            'relationship_type': 'professional',
            'warmth_status': 3,
            'warmth_label': 'Aware',
            'priority_level': 'high',
            'notes': 'Former colleague from Google. Excellent at scaling backend systems. Currently at Stripe.',
            'tags': 'engineer,backend,python,stripe',
            'location': 'Seattle, WA',
            'interests': 'Backend architecture, payments, fintech'
        },
        {
            'name': 'Jessica Wu',
            'email': 'jessica@founderfund.com',
            'company': 'Founder Fund',
            'title': 'Principal',
            'relationship_type': 'investor',
            'warmth_status': 2,
            'warmth_label': 'Cold',
            'priority_level': 'medium',
            'notes': 'Connected via LinkedIn. Focuses on enterprise SaaS and AI tools.',
            'tags': 'investor,enterprise,saas,ai',
            'location': 'Palo Alto, CA',
            'interests': 'Enterprise software, AI, automation'
        },
        {
            'name': 'David Kim',
            'email': 'david@techstars.com',
            'company': 'Techstars',
            'title': 'Managing Director',
            'relationship_type': 'mentor',
            'warmth_status': 5,
            'warmth_label': 'Champion',
            'priority_level': 'high',
            'notes': 'Techstars mentor. Has been incredibly helpful with fundraising strategy and intros.',
            'tags': 'mentor,techstars,fundraising,intros',
            'location': 'Boulder, CO',
            'interests': 'Startup mentoring, fundraising, product strategy'
        },
        {
            'name': 'Amanda Foster',
            'email': 'amanda@hubspot.com',
            'company': 'HubSpot',
            'title': 'VP of Partnerships',
            'relationship_type': 'business',
            'warmth_status': 3,
            'warmth_label': 'Aware',
            'priority_level': 'medium',
            'notes': 'Potential integration partner. Interested in AI-powered CRM enhancements.',
            'tags': 'partnership,crm,integration,hubspot',
            'location': 'Boston, MA',
            'interests': 'CRM, partnerships, SaaS integrations'
        },
        {
            'name': 'Alex Thompson',
            'email': 'alex@openai.com',
            'company': 'OpenAI',
            'title': 'Product Manager',
            'relationship_type': 'professional',
            'warmth_status': 4,
            'warmth_label': 'Warm',
            'priority_level': 'high',
            'notes': 'Stanford alum. Working on enterprise AI products. Great contact for AI trends.',
            'tags': 'ai,product,openai,stanford',
            'location': 'San Francisco, CA',
            'interests': 'AI products, enterprise software, ML'
        },
        {
            'name': 'Rachel Green',
            'email': 'rachel@accel.com',
            'company': 'Accel Partners',
            'title': 'Associate',
            'relationship_type': 'investor',
            'warmth_status': 2,
            'warmth_label': 'Cold',
            'priority_level': 'medium',
            'notes': 'Focused on seed and Series A investments in AI and productivity tools.',
            'tags': 'investor,seed,series-a,ai,productivity',
            'location': 'Palo Alto, CA',
            'interests': 'Early-stage investing, AI, productivity software'
        },
        {
            'name': 'Michael Chang',
            'email': 'michael@figma.com',
            'company': 'Figma',
            'title': 'Senior Full-Stack Engineer',
            'relationship_type': 'professional',
            'warmth_status': 3,
            'warmth_label': 'Aware',
            'priority_level': 'high',
            'notes': 'Excellent engineer with experience in collaborative tools. Could be potential hire.',
            'tags': 'engineer,fullstack,figma,collaborative-tools',
            'location': 'San Francisco, CA',
            'interests': 'Full-stack development, collaborative tools, design systems'
        }
    ]
    
    contact_ids = []
    for contact in demo_contacts:
        # Check if contact exists
        existing = cursor.execute(
            'SELECT id FROM contacts WHERE user_id = ? AND email = ?',
            (user_id, contact['email'])
        ).fetchone()
        
        if not existing:
            contact['user_id'] = user_id
            contact['created_at'] = datetime.now().isoformat()
            contact['updated_at'] = datetime.now().isoformat()
            
            columns = ', '.join(contact.keys())
            placeholders = ', '.join(['?' for _ in contact])
            
            cursor.execute(
                f'INSERT INTO contacts ({columns}) VALUES ({placeholders})',
                list(contact.values())
            )
            contact_ids.append(cursor.lastrowid)
        else:
            contact_ids.append(existing['id'])
    
    conn.commit()
    conn.close()
    print(f"Created/verified {len(contact_ids)} demo contacts")
    return contact_ids

def create_demo_ai_suggestions(user_id, goal_ids, contact_ids):
    """Create demo AI suggestions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing suggestions for demo user
    cursor.execute(
        '''DELETE FROM ai_suggestions WHERE goal_id IN (
            SELECT id FROM goals WHERE user_id = ?
        )''', (user_id,)
    )
    
    # Create realistic AI suggestions
    suggestions = [
        {
            'goal_index': 0,  # Fundraising
            'contact_index': 0,  # Sarah Chen
            'confidence': 0.92,
            'suggestion': 'Sarah is a perfect match for your angel round. Her portfolio includes 3 AI startups and she specifically looks for SaaS companies with strong technical teams. Mention your AI-powered approach and traction metrics.'
        },
        {
            'goal_index': 0,  # Fundraising  
            'contact_index': 3,  # David Kim
            'confidence': 0.88,
            'suggestion': 'David can provide valuable introductions to angel investors in his network. As a Techstars MD, he has deep connections in the funding ecosystem and has already shown support for your venture.'
        },
        {
            'goal_index': 1,  # Backend Engineer
            'contact_index': 1,  # Marcus Rodriguez
            'confidence': 0.95,
            'suggestion': 'Marcus is an ideal candidate for your backend role. His experience scaling Stripe\'s payment infrastructure and Python expertise align perfectly with your needs. He might be open to new opportunities.'
        },
        {
            'goal_index': 1,  # Backend Engineer
            'contact_index': 7,  # Michael Chang
            'confidence': 0.82,
            'suggestion': 'Michael has strong full-stack skills and experience with collaborative tools at Figma. His background could bring valuable perspective to your relationship intelligence platform.'
        },
        {
            'goal_index': 2,  # Beta Customers
            'contact_index': 3,  # David Kim
            'confidence': 0.87,
            'suggestion': 'David can connect you with Techstars portfolio companies who would be ideal beta customers. Many early-stage founders struggle with relationship management and would benefit from your platform.'
        },
        {
            'goal_index': 3,  # CRM Partnership
            'contact_index': 4,  # Amanda Foster
            'confidence': 0.94,
            'suggestion': 'Amanda leads partnerships at HubSpot and has expressed interest in AI-powered CRM enhancements. Your relationship intelligence features could be a perfect integration for their platform.'
        }
    ]
    
    for suggestion in suggestions:
        goal_id = goal_ids[suggestion['goal_index']]
        contact_id = contact_ids[suggestion['contact_index']]
        
        cursor.execute(
            'INSERT INTO ai_suggestions (goal_id, contact_id, suggestion, confidence, created_at) VALUES (?, ?, ?, ?, ?)',
            (goal_id, contact_id, suggestion['suggestion'], suggestion['confidence'], datetime.now().isoformat())
        )
    
    conn.commit()
    conn.close()
    print(f"Created {len(suggestions)} AI suggestions")

def create_demo_interactions(user_id, contact_ids):
    """Create demo contact interactions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sample interactions for the last 30 days
    interactions = [
        {
            'contact_index': 0,  # Sarah Chen
            'interaction_type': 'email_sent',
            'direction': 'outbound',
            'status': 'completed',
            'subject': 'Introduction and funding opportunity',
            'summary': 'Sent initial pitch deck and introduction email',
            'days_ago': 5
        },
        {
            'contact_index': 0,  # Sarah Chen
            'interaction_type': 'email_received',
            'direction': 'inbound', 
            'status': 'completed',
            'subject': 'Re: Introduction and funding opportunity',
            'summary': 'Positive response, requested detailed financials',
            'days_ago': 3
        },
        {
            'contact_index': 3,  # David Kim
            'interaction_type': 'meeting',
            'direction': 'mutual',
            'status': 'completed',
            'subject': 'Monthly mentor check-in',
            'summary': 'Discussed fundraising strategy and potential investor intros',
            'days_ago': 7
        },
        {
            'contact_index': 1,  # Marcus Rodriguez
            'interaction_type': 'linkedin_message',
            'direction': 'outbound',
            'status': 'completed',
            'subject': 'Catching up and new opportunity',
            'summary': 'Reached out about potential backend engineering role',
            'days_ago': 10
        }
    ]
    
    for interaction in interactions:
        contact_id = contact_ids[interaction['contact_index']]
        timestamp = (datetime.now() - timedelta(days=interaction['days_ago'])).isoformat()
        
        cursor.execute(
            '''INSERT INTO contact_interactions 
               (contact_id, user_id, interaction_type, direction, status, subject, summary, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (contact_id, user_id, interaction['interaction_type'], interaction['direction'],
             interaction['status'], interaction['subject'], interaction['summary'], timestamp)
        )
    
    conn.commit()
    conn.close()
    print(f"Created {len(interactions)} demo interactions")

def main():
    """Main seeding function"""
    print("Starting demo data seeding...")
    
    # Create demo user
    user_id = create_demo_user()
    
    # Create demo goals
    goal_ids = create_demo_goals(user_id)
    
    # Create demo contacts
    contact_ids = create_demo_contacts(user_id)
    
    # Create AI suggestions
    create_demo_ai_suggestions(user_id, goal_ids, contact_ids)
    
    # Create interactions
    create_demo_interactions(user_id, contact_ids)
    
    print("Demo data seeding completed successfully!")
    print(f"Created demo user with {len(goal_ids)} goals, {len(contact_ids)} contacts")

if __name__ == "__main__":
    main()