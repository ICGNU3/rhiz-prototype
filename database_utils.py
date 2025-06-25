import sqlite3
import json
import numpy as np
from numpy.linalg import norm
import logging
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
    
    # Demo contacts
    demo_contacts = [
        {
            "name": "Sarah Chen",
            "email": "sarah@techstartup.com",
            "linkedin": "linkedin.com/in/sarahchen",
            "notes": "Serial entrepreneur, founded 3 successful B2B SaaS companies. Expert in product-market fit and scaling teams. Currently advising early-stage startups.",
            "tags": "entrepreneur,saas,advisor"
        },
        {
            "name": "Marcus Rodriguez",
            "email": "marcus@vcfund.com",
            "phone": "+1-555-0123",
            "linkedin": "linkedin.com/in/marcusrodriguez",
            "notes": "Partner at Series A VC fund. Focuses on fintech and healthcare investments. Former Goldman Sachs analyst.",
            "tags": "vc,fintech,healthcare"
        },
        {
            "name": "Dr. Emily Watson",
            "email": "emily.watson@techcorp.com",
            "linkedin": "linkedin.com/in/emilywatson",
            "notes": "VP of Engineering at Fortune 500 tech company. PhD in Computer Science. Expert in AI/ML and distributed systems.",
            "tags": "engineering,ai,enterprise"
        },
        {
            "name": "James Park",
            "email": "james@designstudio.com",
            "twitter": "@jamespark",
            "linkedin": "linkedin.com/in/jamespark",
            "notes": "Creative director and UX designer. Led design for several unicorn startups. Specializes in consumer mobile apps.",
            "tags": "design,ux,mobile"
        },
        {
            "name": "Lisa Thompson",
            "email": "lisa@marketingpro.com",
            "phone": "+1-555-0199",
            "notes": "Growth marketing expert. Scaled 5 companies from zero to $10M+ ARR. Specialist in B2B marketing and lead generation.",
            "tags": "marketing,growth,b2b"
        }
    ]
    
    # Create demo contacts
    for contact_data in demo_contacts:
        contact_model.create(
            user_id=user_id,
            name=contact_data["name"],
            email=contact_data.get("email"),
            phone=contact_data.get("phone"),
            twitter=contact_data.get("twitter"),
            linkedin=contact_data.get("linkedin"),
            notes=contact_data.get("notes"),
            tags=contact_data.get("tags")
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
