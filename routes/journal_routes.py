"""
Journal Routes Module
Handles journal entry CRUD operations and AI reflections
"""

import json
import os
from datetime import datetime, timedelta
from flask import request, jsonify, session
from routes import RouteBase, login_required, get_current_user_id
from backend.models.journal import JournalEntry
from utils.database_helpers import get_db_connection
from openai import OpenAI

class JournalRoutes(RouteBase):
    def __init__(self):
        super().__init__()
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Create instance for route registration
journal_routes = JournalRoutes()

@login_required
def create_journal_entry():
    """Create a new journal entry"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400
        
        # Validate required fields
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400
        
        # Optional fields
        entry_type = data.get('entry_type', 'reflection')
        related_contact_id = data.get('related_contact_id')
        related_goal_id = data.get('related_goal_id')
        mood_score = data.get('mood_score')
        energy_level = data.get('energy_level')
        tags = data.get('tags', [])
        
        # Validate numeric fields
        if mood_score is not None:
            mood_score = int(mood_score)
            if mood_score < 1 or mood_score > 10:
                return jsonify({"error": "Mood score must be between 1 and 10"}), 400
        
        if energy_level is not None:
            energy_level = int(energy_level)
            if energy_level < 1 or energy_level > 10:
                return jsonify({"error": "Energy level must be between 1 and 10"}), 400
        
        # Create journal entry
        db = get_db_connection()
        journal = JournalEntry(db)
        
        entry_id = journal.create_entry(
            user_id=user_id,
            title=title,
            content=content,
            entry_type=entry_type,
            related_contact_id=related_contact_id,
            related_goal_id=related_goal_id,
            mood_score=mood_score,
            energy_level=energy_level,
            tags=tags
        )
        
        # Award XP for journaling
        journal_routes.award_xp("journal_entry", 10, {"entry_type": entry_type})
        
        return jsonify({
            "success": True,
            "entry_id": entry_id,
            "message": "Journal entry created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to create journal entry: {str(e)}"}), 500

@login_required
def get_journal_entries():
    """Get journal entries for the current user"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        db = get_db_connection()
        journal = JournalEntry(db)
        
        entries = journal.get_entries_by_user(user_id, limit, offset)
        
        # Format entries for frontend
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry[0],
                "title": entry[1],
                "content": entry[2],
                "entry_type": entry[3],
                "mood_score": entry[4],
                "energy_level": entry[5],
                "tags": entry[6] or [],
                "ai_reflection": entry[7],
                "created_at": entry[8].isoformat() if entry[8] else None,
                "related_contact_id": entry[9],
                "related_goal_id": entry[10],
                "contact_name": entry[11],
                "goal_title": entry[12]
            })
        
        return jsonify({
            "success": True,
            "entries": formatted_entries,
            "total": len(formatted_entries)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get journal entries: {str(e)}"}), 500

@login_required
def get_journal_entry(entry_id):
    """Get a specific journal entry with reflections"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        db = get_db_connection()
        journal = JournalEntry(db)
        
        result = journal.get_entry_by_id(entry_id, user_id)
        
        if not result:
            return jsonify({"error": "Journal entry not found"}), 404
        
        entry = result['entry']
        reflections = result['reflections']
        
        # Format entry data
        formatted_entry = {
            "id": entry[0],
            "title": entry[2],
            "content": entry[3],
            "entry_type": entry[4],
            "mood_score": entry[8],
            "energy_level": entry[9],
            "tags": entry[10] or [],
            "ai_reflection": entry[11],
            "created_at": entry[13].isoformat() if entry[13] else None,
            "related_contact_id": entry[5],
            "related_goal_id": entry[6],
            "contact_name": entry[15] if len(entry) > 15 else None,
            "goal_title": entry[16] if len(entry) > 16 else None
        }
        
        # Format reflections
        formatted_reflections = []
        for reflection in reflections:
            formatted_reflections.append({
                "id": reflection[0],
                "user_question": reflection[1],
                "ai_response": reflection[2],
                "reflection_type": reflection[3],
                "created_at": reflection[4].isoformat() if reflection[4] else None
            })
        
        return jsonify({
            "success": True,
            "entry": formatted_entry,
            "reflections": formatted_reflections
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get journal entry: {str(e)}"}), 500

@login_required
def reflect_with_ai():
    """Generate AI reflection on a journal entry"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400
        
        entry_id = data.get('entry_id')
        user_question = data.get('user_question', '')
        reflection_type = data.get('reflection_type', 'general')
        
        if not entry_id:
            return jsonify({"error": "Entry ID is required"}), 400
        
        db = get_db_connection()
        journal = JournalEntry(db)
        
        # Get the journal entry
        result = journal.get_entry_by_id(entry_id, user_id)
        if not result:
            return jsonify({"error": "Journal entry not found"}), 404
        
        entry = result['entry']
        entry_content = entry[3]  # content field
        entry_title = entry[2]    # title field
        
        # Generate AI reflection
        ai_response = generate_ai_reflection(
            entry_title, entry_content, user_question, reflection_type, journal_routes.openai_client
        )
        
        # Save the reflection session
        reflection_id = journal.create_reflection_session(
            entry_id, user_question, ai_response, reflection_type
        )
        
        # Update the main entry with AI reflection if it's the first one
        if not entry[11]:  # ai_reflection field is empty
            journal.add_ai_reflection(entry_id, user_id, ai_response)
        
        # Award XP for AI reflection
        journal_routes.award_xp("ai_reflection", 5, {"reflection_type": reflection_type})
        
        return jsonify({
            "success": True,
            "reflection_id": reflection_id,
            "ai_response": ai_response,
            "message": "AI reflection generated successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate AI reflection: {str(e)}"}), 500

@login_required
def get_weekly_prompt():
    """Get weekly journaling prompt"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        # Get current week's insights
        db = get_db_connection()
        journal = JournalEntry(db)
        
        weekly_insights = journal.get_weekly_insights(user_id)
        
        # Generate contextual weekly prompt
        prompt = generate_weekly_prompt(weekly_insights)
        
        return jsonify({
            "success": True,
            "prompt": prompt,
            "weekly_insights": weekly_insights
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get weekly prompt: {str(e)}"}), 500

@login_required
def get_journal_analytics():
    """Get journal analytics and insights"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        db = get_db_connection()
        journal = JournalEntry(db)
        
        # Get comprehensive analytics
        weekly_insights = journal.get_weekly_insights(user_id)
        
        # Calculate additional metrics
        cursor = db.cursor()
        
        # Entry frequency over time
        cursor.execute("""
            SELECT 
                DATE_TRUNC('day', created_at) as day,
                COUNT(*) as entry_count
            FROM journal_entries
            WHERE user_id = %s 
            AND created_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE_TRUNC('day', created_at)
            ORDER BY day
        """, (user_id,))
        
        daily_entries = cursor.fetchall()
        
        # Mood and energy trends
        cursor.execute("""
            SELECT 
                DATE_TRUNC('day', created_at) as day,
                AVG(mood_score) as avg_mood,
                AVG(energy_level) as avg_energy
            FROM journal_entries
            WHERE user_id = %s 
            AND created_at >= CURRENT_DATE - INTERVAL '30 days'
            AND (mood_score IS NOT NULL OR energy_level IS NOT NULL)
            GROUP BY DATE_TRUNC('day', created_at)
            ORDER BY day
        """, (user_id,))
        
        mood_trends = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "weekly_insights": weekly_insights,
            "daily_entries": [{"day": row[0].isoformat(), "count": row[1]} for row in daily_entries],
            "mood_trends": [{"day": row[0].isoformat(), "mood": float(row[1]) if row[1] else None, "energy": float(row[2]) if row[2] else None} for row in mood_trends]
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get journal analytics: {str(e)}"}), 500

# Helper methods for JournalRoutes class
def generate_ai_reflection(title: str, content: str, user_question: str, reflection_type: str, openai_client) -> str:
    """Generate AI reflection on journal entry"""
    try:
        # Create contextual prompt based on reflection type
        if reflection_type == "relationship":
            system_prompt = """You are a wise relationship coach helping someone reflect on their relationships and social connections. 
            Focus on relationship patterns, communication insights, and social growth opportunities."""
        elif reflection_type == "growth":
            system_prompt = """You are a personal development coach helping someone reflect on their growth and learning. 
            Focus on progress, challenges overcome, and future development opportunities."""
        elif reflection_type == "insight":
            system_prompt = """You are a thoughtful advisor helping someone extract deeper insights from their experiences. 
            Focus on patterns, underlying meanings, and actionable wisdom."""
        else:
            system_prompt = """You are a compassionate reflection partner helping someone process their thoughts and experiences. 
            Provide gentle, insightful guidance that encourages self-discovery."""
        
        user_prompt = f"""
        Journal Entry Title: {title}
        
        Journal Entry Content: {content}
        
        User's Question: {user_question if user_question else "Help me reflect on this entry and find insights."}
        
        Please provide a thoughtful, personalized reflection that:
        1. Acknowledges the emotions and experiences shared
        2. Offers gentle insights or questions for deeper reflection
        3. Suggests practical next steps or considerations
        4. Maintains a supportive and encouraging tone
        
        Keep your response between 150-300 words and make it personal and actionable.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Unable to generate AI reflection at this time. Please try again later. ({str(e)})"

def generate_weekly_prompt(weekly_insights: dict) -> str:
    """Generate contextual weekly journaling prompt"""
    stats = weekly_insights.get('weekly_stats')
    top_contacts = weekly_insights.get('top_contacts', [])
    
    if not stats:
        return "Who helped you this week? Reflect on the people who made a positive impact on your journey."
    
    entry_count = stats[0] if stats[0] else 0
    avg_mood = stats[1] if stats[1] else None
    contacts_mentioned = stats[4] if stats[4] else 0
    
    # Generate contextual prompt based on weekly patterns
    if entry_count == 0:
        return "Let's start your week with reflection: Who has been most supportive of your goals lately?"
    elif entry_count >= 5:
        return "You've been actively journaling this week! Looking back, what relationship patterns are you noticing?"
    elif contacts_mentioned >= 3:
        return "You've mentioned several people this week. Who among them would you like to show more appreciation to?"
    elif avg_mood and avg_mood >= 7:
        return "Your mood has been positive this week! Who contributed to that positive energy?"
    elif avg_mood and avg_mood < 5:
        return "This week seems challenging. Who in your network could offer support or perspective?"
    else:
        return "Who helped you this week? Take a moment to acknowledge the people who made a difference."

# Add helper methods to the class
JournalRoutes._generate_ai_reflection = _generate_ai_reflection
JournalRoutes._generate_weekly_prompt = _generate_weekly_prompt