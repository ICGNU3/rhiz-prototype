import sqlite3
import json
import numpy as np
from numpy.linalg import norm
import logging
from datetime import datetime, timedelta
from models import Database, Contact, Goal
from openai_utils import OpenAIUtils

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    try:
        return np.dot(a, b) / (norm(a) * norm(b))
    except:
        return 0.0

def match_contacts_to_goal(goal_id):
    """Match contacts to a goal using cosine similarity"""
    db = Database()
    openai_utils = OpenAIUtils()
    
    conn = db.get_connection()
    try:
        # Get goal embedding
        goal_row = conn.execute("SELECT embedding, user_id FROM goals WHERE id = ?", (goal_id,)).fetchone()
        if not goal_row or not goal_row['embedding']:
            logging.error(f"Goal {goal_id} not found or has no embedding")
            return []
        
        goal_vector = np.array(json.loads(goal_row['embedding']))
        user_id = goal_row['user_id']
        
        matches = []
        
        # Get all contacts for the user
        contacts = conn.execute(
            "SELECT id, name, notes, linkedin, twitter FROM contacts WHERE user_id = ?", 
            (user_id,)
        ).fetchall()
        
        for contact in contacts:
            try:
                # Create contact description from available data
                description_parts = [contact['name']]
                if contact['notes']:
                    description_parts.append(contact['notes'])
                if contact['linkedin']:
                    description_parts.append(f"LinkedIn: {contact['linkedin']}")
                if contact['twitter']:
                    description_parts.append(f"Twitter: {contact['twitter']}")
                
                contact_description = " | ".join(description_parts)
                
                # Generate embedding for contact
                contact_embedding_json = openai_utils.generate_embedding(contact_description)
                contact_vector = np.array(json.loads(contact_embedding_json))
                
                # Calculate similarity
                score = cosine_similarity(goal_vector, contact_vector)
                matches.append((contact['id'], contact['name'], float(score)))
                
            except Exception as e:
                logging.error(f"Failed to process contact {contact['id']}: {e}")
                # Add with low score if processing fails
                matches.append((contact['id'], contact['name'], 0.0))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches
    
    finally:
        conn.close()

def seed_demo_data(user_id):
    """Seed the database with demo contacts and goals"""
    db = Database()
    contact_model = Contact(db)
    goal_model = Goal(db)
    openai_utils = OpenAIUtils()
    
    logging.info("Seeding demo data...")
    
    # Enhanced demo contacts with CRM intelligence data
    demo_contacts = [
        {
            "name": "Sarah Chen",
            "email": "sarah@techstartup.com",
            "linkedin": "linkedin.com/in/sarahchen",
            "relationship_type": "Ally",
            "warmth_status": 4,
            "warmth_label": "Active",
            "priority_level": "High",
            "company": "TechStartup Inc",
            "title": "CEO & Founder",
            "location": "San Francisco, CA",
            "notes": "Serial entrepreneur, founded 3 successful B2B SaaS companies. Expert in product-market fit and scaling teams. Currently advising early-stage startups.",
            "narrative_thread": "Met at TechCrunch Disrupt. Very responsive and helpful. Offered to make introductions to her investor network.",
            "tags": "entrepreneur,saas,advisor,san-francisco",
            "interests": "product-market-fit,scaling,mentorship",
            "introduced_by": "Alex from YC",
            "follow_up_action": "Share our latest metrics and ask for investor intros",
            "follow_up_due_date": (datetime.now() + timedelta(days=3)).isoformat()
        },
        {
            "name": "Marcus Rodriguez",
            "email": "marcus@vcfund.com",
            "phone": "+1-555-0123",
            "linkedin": "linkedin.com/in/marcusrodriguez",
            "relationship_type": "Investor",
            "warmth_status": 3,
            "warmth_label": "Warm",
            "priority_level": "High",
            "company": "Vertex Ventures",
            "title": "Partner",
            "location": "New York, NY",
            "notes": "Partner at Series A VC fund. Focuses on fintech and healthcare investments. Former Goldman Sachs analyst.",
            "narrative_thread": "Had great coffee meeting last month. Interested in our healthcare AI approach. Asked for follow-up on user traction.",
            "tags": "vc,fintech,healthcare,new-york",
            "interests": "healthcare-ai,fintech,series-a",
            "introduced_by": "Sarah Chen",
            "follow_up_action": "Send updated deck with traction metrics",
            "follow_up_due_date": (datetime.now() + timedelta(days=7)).isoformat()
        },
        {
            "name": "Dr. Emily Watson",
            "email": "emily.watson@techcorp.com",
            "linkedin": "linkedin.com/in/emilywatson",
            "relationship_type": "Collaborator",
            "warmth_status": 2,
            "warmth_label": "Aware",
            "priority_level": "Medium",
            "company": "TechCorp",
            "title": "VP of Engineering",
            "location": "Seattle, WA",
            "notes": "VP of Engineering at Fortune 500 tech company. PhD in Computer Science. Expert in AI/ML and distributed systems.",
            "narrative_thread": "Connected through LinkedIn. Expressed interest in our technical approach. Could be potential technical advisor or customer.",
            "tags": "engineering,ai,enterprise,seattle",
            "interests": "ai-ml,distributed-systems,technical-advisory",
            "follow_up_action": "Schedule technical deep-dive call",
            "follow_up_due_date": (datetime.now() + timedelta(days=14)).isoformat()
        },
        {
            "name": "James Park",
            "email": "james@designstudio.com",
            "twitter": "@jamespark",
            "linkedin": "linkedin.com/in/jamespark",
            "relationship_type": "Collaborator",
            "warmth_status": 3,
            "warmth_label": "Warm",
            "priority_level": "Medium",
            "company": "DesignStudio",
            "title": "Creative Director",
            "location": "Los Angeles, CA",
            "notes": "Creative director and UX designer. Led design for several unicorn startups. Specializes in consumer mobile apps.",
            "narrative_thread": "Met at design conference. Loved our product vision. Offered to help with UX review and potential design partnership.",
            "tags": "design,ux,mobile,los-angeles",
            "interests": "product-design,mobile-ux,design-systems",
            "follow_up_action": "Share wireframes for UX feedback",
            "follow_up_due_date": (datetime.now() + timedelta(days=10)).isoformat()
        },
        {
            "name": "Lisa Thompson",
            "email": "lisa@marketingpro.com",
            "phone": "+1-555-0199",
            "relationship_type": "Ally",
            "warmth_status": 4,
            "warmth_label": "Active",
            "priority_level": "High",
            "company": "MarketingPro",
            "title": "Head of Growth",
            "location": "Austin, TX",
            "notes": "Growth marketing expert. Scaled 5 companies from zero to $10M+ ARR. Specialist in B2B marketing and lead generation.",
            "narrative_thread": "Regular advisor calls. Helping with our go-to-market strategy. Very engaged and provides excellent advice.",
            "tags": "marketing,growth,b2b,austin",
            "interests": "growth-marketing,b2b-sales,go-to-market",
            "follow_up_action": "Monthly advisor check-in call",
            "follow_up_due_date": (datetime.now() + timedelta(days=5)).isoformat()
        },
        {
            "name": "David Kim",
            "email": "david@coldoutreach.com",
            "linkedin": "linkedin.com/in/davidkim",
            "relationship_type": "Contact",
            "warmth_status": 1,
            "warmth_label": "Cold",
            "priority_level": "Low",
            "company": "TechCorp",
            "title": "Product Manager",
            "location": "Boston, MA",
            "notes": "Product manager at mid-size tech company. Found through mutual connections. Potential customer for our enterprise solution.",
            "narrative_thread": "Initial LinkedIn connection. No response to first outreach. Need to find better angle.",
            "tags": "product-management,enterprise,boston",
            "interests": "product-strategy,enterprise-software",
            "follow_up_action": "Try different outreach angle through warm intro",
            "follow_up_due_date": (datetime.now() + timedelta(days=21)).isoformat()
        },
        {
            "name": "Anna Foster",
            "email": "anna@presstech.com",
            "twitter": "@annafoster",
            "relationship_type": "Press",
            "warmth_status": 3,
            "warmth_label": "Warm",
            "priority_level": "Medium",
            "company": "TechPress",
            "title": "Senior Reporter",
            "location": "San Francisco, CA",
            "notes": "Senior tech reporter covering AI and startups. Wrote about our competitors. Could be good for coverage when we have news.",
            "narrative_thread": "Brief Twitter exchange about AI trends. Seemed interested in our approach. Good relationship for future PR.",
            "tags": "press,journalist,ai-coverage,san-francisco",
            "interests": "ai-trends,startup-stories,tech-news",
            "follow_up_action": "Share company updates for potential story",
            "follow_up_due_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
    ]
    
    # Create demo contacts with enhanced CRM data
    for contact_data in demo_contacts:
        contact_model.create(
            user_id=user_id,
            name=contact_data["name"],
            email=contact_data.get("email"),
            phone=contact_data.get("phone"),
            twitter=contact_data.get("twitter"),
            linkedin=contact_data.get("linkedin"),
            handle=contact_data.get("handle"),
            relationship_type=contact_data.get("relationship_type", "Contact"),
            warmth_status=contact_data.get("warmth_status", 1),
            warmth_label=contact_data.get("warmth_label", "Cold"),
            priority_level=contact_data.get("priority_level", "Medium"),
            notes=contact_data.get("notes"),
            narrative_thread=contact_data.get("narrative_thread"),
            tags=contact_data.get("tags"),
            introduced_by=contact_data.get("introduced_by"),
            location=contact_data.get("location"),
            company=contact_data.get("company"),
            title=contact_data.get("title"),
            interests=contact_data.get("interests"),
            follow_up_action=contact_data.get("follow_up_action"),
            follow_up_due_date=contact_data.get("follow_up_due_date")
        )
    
    # Demo goals
    demo_goals = [
        {
            "title": "Raise Series A funding",
            "description": "Looking to raise $5M Series A round for our B2B SaaS platform. Need introductions to VCs who focus on early-stage enterprise software companies."
        },
        {
            "title": "Find technical co-founder",
            "description": "Seeking an experienced engineering leader to join as CTO. Need someone with experience in AI/ML and scalable system architecture for our healthcare AI startup."
        },
        {
            "title": "Improve product design",
            "description": "Looking for expert UX/UI design guidance to improve our mobile app user experience. Want to connect with designers who have experience with consumer applications."
        },
        {
            "title": "Scale marketing efforts",
            "description": "Need strategic marketing advice to grow from 100K to 1M users. Looking for growth marketing experts who understand B2B customer acquisition."
        }
    ]
    
    # Create demo goals with embeddings
    for goal_data in demo_goals:
        try:
            embedding = openai_utils.generate_embedding(goal_data["description"])
            goal_model.create(
                user_id=user_id,
                title=goal_data["title"],
                description=goal_data["description"],
                embedding=embedding
            )
        except Exception as e:
            logging.error(f"Failed to create demo goal '{goal_data['title']}': {e}")
            # Create without embedding as fallback
            goal_model.create(
                user_id=user_id,
                title=goal_data["title"],
                description=goal_data["description"]
            )
    
    logging.info("Demo data seeded successfully")
