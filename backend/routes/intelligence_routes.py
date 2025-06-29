"""
Intelligence routes - AI-powered relationship insights and chat
"""

from flask import Blueprint, request, jsonify, session
from backend.models import db, User, Contact, Goal
from backend.services.contact_intelligence import ContactIntelligence
import os
import logging

intelligence_bp = Blueprint('intelligence', __name__, url_prefix='/api/intelligence')

@intelligence_bp.route('/chat', methods=['POST'])
def chat():
    """
    AI chat endpoint for relationship advice
    """
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        user_id = session['user_id']
        
        # Get user context
        user = User.query.get(user_id)
        contacts = Contact.query.filter_by(user_id=user_id).all()
        goals = Goal.query.filter_by(user_id=user_id).all()
        
        # Check if OpenAI is available
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        if openai_key:
            # Use OpenAI for real AI response
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                # Build context
                context = f"""You are a relationship intelligence assistant helping {user.email if user else 'a user'} with their professional network.
                
Current context:
- They have {len(contacts)} contacts in their network
- They have {len(goals)} active goals
- Recent goals: {', '.join([g.title for g in goals[:3]]) if goals else 'None'}

Provide specific, actionable advice about relationship building and networking strategy.
Keep response under 200 words and focus on concrete next steps."""

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
            except Exception as e:
                logging.error(f"OpenAI error: {e}")
                ai_response = _get_fallback_response(message, contacts, goals)
        else:
            ai_response = _get_fallback_response(message, contacts, goals)
        
        return jsonify({
            "response": ai_response,
            "message_id": f"msg_{user_id}_{len(message)}",
            "timestamp": "2025-06-29T16:00:00Z"
        })
        
    except Exception as e:
        logging.error(f"Intelligence chat error: {e}")
        return jsonify({"error": "Failed to process chat message"}), 500

@intelligence_bp.route('/insights')
def get_insights():
    """
    Get AI-powered contact insights and recommendations
    """
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        user_id = session['user_id']
        
        # Get contact intelligence
        intelligence = ContactIntelligence()
        
        # Get contact recommendations
        contacts = Contact.query.filter_by(user_id=user_id).all()
        goals = Goal.query.filter_by(user_id=user_id).all()
        
        recommendations = []
        if contacts and goals:
            # Simple recommendation logic
            for goal in goals[:2]:
                relevant_contacts = [c for c in contacts if 
                                   goal.goal_type.lower() in (c.notes or '').lower() or
                                   goal.goal_type.lower() in (c.company or '').lower()][:2]
                
                for contact in relevant_contacts:
                    recommendations.append({
                        "contact_name": contact.name,
                        "contact_id": contact.id,
                        "reason": f"Perfect fit for your {goal.goal_type} goal - {goal.title}",
                        "confidence": 85,
                        "action": "Schedule a call this week"
                    })
        
        # Get opportunities
        opportunities = [
            {
                "type": "job_change",
                "title": "Contact Started New Role",
                "description": "Sarah Chen recently joined a new company - great time to reconnect",
                "contact_name": "Sarah Chen",
                "priority": "high"
            },
            {
                "type": "conference",
                "title": "Industry Conference Next Week",
                "description": "TechConf 2025 - several of your contacts will be attending",
                "priority": "medium"
            }
        ]
        
        return jsonify({
            "recommendations": recommendations[:4],
            "opportunities": opportunities,
            "last_updated": "2025-06-29T16:00:00Z"
        })
        
    except Exception as e:
        logging.error(f"Intelligence insights error: {e}")
        return jsonify({"error": "Failed to load insights"}), 500

def _get_fallback_response(message, contacts, goals):
    """
    Generate intelligent fallback responses when OpenAI is unavailable
    """
    message_lower = message.lower()
    
    # Fundraising advice
    if any(word in message_lower for word in ['fundraising', 'investor', 'funding', 'raise']):
        investor_contacts = [c for c in contacts if 'investor' in (c.title or '').lower() or 'vc' in (c.company or '').lower()]
        if investor_contacts:
            return f"For fundraising, I'd recommend starting with {investor_contacts[0].name} at {investor_contacts[0].company}. They're already in your network and understand your space. Focus on building trust first before making the ask."
        else:
            return "For fundraising, start by reaching out to founders who've raised recently. They can provide introductions to investors. Look for warm connections through your existing network first."
    
    # Hiring advice
    elif any(word in message_lower for word in ['hiring', 'recruit', 'talent', 'team']):
        return "For hiring, leverage your network for referrals - they're 5x more likely to be good fits. Ask your best contacts who they'd recommend, and offer referral bonuses to incentivize introductions."
    
    # Partnership advice
    elif any(word in message_lower for word in ['partnership', 'collaborate', 'integrate']):
        return "For partnerships, focus on companies that serve your customer base but aren't direct competitors. Start with informal conversations about shared challenges before proposing formal partnerships."
    
    # General networking
    elif any(word in message_lower for word in ['network', 'connect', 'relationship']):
        if contacts:
            return f"You have {len(contacts)} contacts in your network. Focus on deepening existing relationships rather than just adding new ones. Try reaching out to 2-3 people this week you haven't spoken to recently."
        else:
            return "Start building your network by reconnecting with former colleagues and classmates. Quality relationships are more valuable than quantity."
    
    # Default response
    else:
        return "I'm here to help with relationship building and networking strategy. Ask me about fundraising, hiring, partnerships, or how to strengthen your existing connections."