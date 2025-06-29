#!/usr/bin/env python3
"""
Database Seed Script for Rhiz Platform
Creates demo user and sample contacts/goals for development and testing
"""
import os
import uuid
from datetime import datetime, timedelta
from backend import create_app
from backend.extensions import db
from backend.models import User, Contact, Goal

def create_demo_user():
    """Create a demo user for testing"""
    demo_email = "demo@rhiz.app"
    
    # Check if demo user already exists
    existing_user = User.query.filter_by(email=demo_email).first()
    if existing_user:
        print(f"Demo user {demo_email} already exists with ID: {existing_user.id}")
        return existing_user
    
    # Create new demo user
    demo_user = User()
    demo_user.id = str(uuid.uuid4())
    demo_user.email = demo_email
    demo_user.subscription_tier = "explorer"
    demo_user.is_guest = False
    demo_user.created_at = datetime.utcnow()
    
    db.session.add(demo_user)
    db.session.commit()
    print(f"Created demo user: {demo_email} with ID: {demo_user.id}")
    return demo_user

def create_demo_contacts(user):
    """Create 3 sample contacts for the demo user"""
    contacts_data = [
        {
            "name": "Sarah Chen",
            "email": "sarah.chen@techstartup.com",
            "company": "TechStartup Inc",
            "title": "VP of Engineering",
            "linkedin_url": "linkedin.com/in/sarahchen",
            "notes": "Met at TechCrunch Disrupt. Very interested in AI and machine learning applications. Has experience scaling engineering teams from 5 to 50+ people.",
            "warmth_status": "warm",
            "source": "conference"
        },
        {
            "name": "Marcus Rodriguez",
            "email": "marcus.r@venturecap.vc",
            "company": "Venture Capital Partners",
            "title": "Senior Partner",
            "linkedin_url": "linkedin.com/in/marcusrodriguez",
            "notes": "Investor focused on B2B SaaS. Previously founded two successful startups. Looking for Series A opportunities in the relationship intelligence space.",
            "warmth_status": "growing",
            "source": "referral"
        },
        {
            "name": "Jennifer Kim",
            "email": "jen.kim@designstudio.co",
            "company": "Creative Design Studio",
            "title": "Creative Director",
            "linkedin_url": "linkedin.com/in/jenniferkim",
            "notes": "Award-winning designer with expertise in user experience and product design. Could be valuable for improving platform UI/UX. Interested in collaborating on design systems.",
            "warmth_status": "rooted",
            "source": "social_media"
        }
    ]
    
    created_contacts = []
    for contact_data in contacts_data:
        # Check if contact already exists
        existing_contact = Contact.query.filter_by(email=contact_data["email"], user_id=user.id).first()
        if existing_contact:
            print(f"Contact {contact_data['name']} already exists")
            created_contacts.append(existing_contact)
            continue
        
        # Create new contact
        contact = Contact()
        contact.id = str(uuid.uuid4())
        contact.user_id = user.id
        contact.name = contact_data["name"]
        contact.email = contact_data["email"]
        contact.company = contact_data["company"]
        contact.title = contact_data["title"]
        contact.linkedin = contact_data["linkedin_url"]
        contact.notes = contact_data["notes"]
        contact.warmth_level = contact_data["warmth_status"]
        contact.source = contact_data["source"]
        contact.created_at = datetime.utcnow()
        contact.updated_at = datetime.utcnow()
        
        db.session.add(contact)
        created_contacts.append(contact)
        print(f"Created contact: {contact_data['name']}")
    
    db.session.commit()
    return created_contacts

def create_demo_goals(user):
    """Create sample goals for the demo user"""
    goals_data = [
        {
            "title": "Raise Series A Funding",
            "description": "Secure $5M Series A funding round from strategic investors who understand the relationship intelligence market and can provide valuable connections and guidance.",
            "goal_type": "fundraising",
            "timeline": "6_months",
            "status": "active",
            "priority_level": "high"
        },
        {
            "title": "Build Strategic Partnership with CRM Platform",
            "description": "Establish integration partnership with major CRM provider (Salesforce, HubSpot, or Pipedrive) to expand our reach and provide native relationship intelligence within existing workflows.",
            "goal_type": "partnerships",
            "timeline": "3_months",
            "status": "active",
            "priority_level": "medium"
        }
    ]
    
    created_goals = []
    for goal_data in goals_data:
        # Check if similar goal already exists
        existing_goal = Goal.query.filter_by(title=goal_data["title"], user_id=user.id).first()
        if existing_goal:
            print(f"Goal '{goal_data['title']}' already exists")
            created_goals.append(existing_goal)
            continue
        
        # Create new goal
        goal = Goal()
        goal.id = str(uuid.uuid4())
        goal.user_id = user.id
        goal.title = goal_data["title"]
        goal.description = goal_data["description"]
        goal.goal_type = goal_data["goal_type"]
        goal.timeline = goal_data["timeline"]
        goal.status = goal_data["status"]
        goal.priority_level = goal_data["priority_level"]
        goal.progress_percentage = 0
        goal.created_at = datetime.utcnow()
        goal.updated_at = datetime.utcnow()
        
        db.session.add(goal)
        created_goals.append(goal)
        print(f"Created goal: {goal_data['title']}")
    
    db.session.commit()
    return created_goals

def main():
    """Main seed function"""
    app = create_app()
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Create demo user
        demo_user = create_demo_user()
        
        # Create demo contacts
        demo_contacts = create_demo_contacts(demo_user)
        
        # Create demo goals
        demo_goals = create_demo_goals(demo_user)
        
        print(f"\nSeeding completed successfully!")
        print(f"Demo user: {demo_user.email}")
        print(f"Created {len(demo_contacts)} contacts")
        print(f"Created {len(demo_goals)} goals")
        print(f"\nYou can now test the application with these demo data.")

if __name__ == "__main__":
    main()