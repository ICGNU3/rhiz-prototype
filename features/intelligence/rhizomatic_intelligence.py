"""
Rhizomatic Intelligence Layer - Living, Non-linear AI Network Analysis
Creates dynamic, care-based relationship suggestions without hierarchy
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
from openai import OpenAI
import os

class RhizomaticIntelligence:
    """
    A living, non-linear AI layer that maps goals, relationships, and activity
    into constantly updating webs of suggestions, connections, and meaning.
    """
    
    def __init__(self, db):
        self.db = db
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def generate_rhizomatic_insights(self, user_id: int) -> Dict[str, Any]:
        """
        Generate living, non-hierarchical relationship insights for a user
        """
        try:
            # Gather user context
            goals = self._get_user_goals(user_id)
            contacts = self._get_user_contacts_with_activity(user_id)
            interactions = self._get_recent_interactions(user_id)
            
            if not contacts:
                return self._create_empty_response()
            
            # Create rhizomatic prompt
            prompt = self._create_rhizomatic_prompt(goals, contacts, interactions)
            
            # Get AI insights
            ai_response = self._query_rhizomatic_ai(prompt)
            
            # Store insights for later use
            self._store_rhizomatic_insights(user_id, ai_response)
            
            # Enhance with network graph data
            graph_data = self._generate_network_graph_data(contacts, ai_response)
            
            return {
                "rhizomatic_insights": ai_response,
                "network_graph": graph_data,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logging.error(f"Error generating rhizomatic insights: {e}")
            return {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_user_goals(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's current goals with context"""
        sql = """
        SELECT id, title, description, created_at,
               (SELECT COUNT(*) FROM ai_suggestions WHERE goal_id = g.id) as suggestion_count
        FROM goals g 
        WHERE user_id = %s 
        ORDER BY created_at DESC
        LIMIT 5
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, [user_id])
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _get_user_contacts_with_activity(self, user_id: int) -> List[Dict[str, Any]]:
        """Get contacts with recent activity context"""
        sql = """
        SELECT c.*, 
               ci.interaction_date as last_interaction,
               ci.interaction_type as last_interaction_type,
               ci.notes as last_notes,
               COUNT(ci.id) as interaction_count,
               MAX(ci.interaction_date) as most_recent_contact
        FROM contacts c
        LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
        WHERE c.user_id = %s
        GROUP BY c.id, c.name, c.email, c.company, c.title, c.linkedin_url, c.tags, c.notes, c.relationship_type, c.warmth_level, c.created_at, ci.interaction_date, ci.interaction_type, ci.notes
        ORDER BY most_recent_contact DESC, c.created_at DESC
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, [user_id])
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _get_recent_interactions(self, user_id: int, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent interaction patterns"""
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        sql = """
        SELECT ci.*, c.name as contact_name, c.company
        FROM contact_interactions ci
        JOIN contacts c ON ci.contact_id = c.id
        WHERE c.user_id = %s AND ci.interaction_date >= %s
        ORDER BY ci.interaction_date DESC
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, [user_id, cutoff_date])
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _create_rhizomatic_prompt(self, goals: List[Dict], contacts: List[Dict], interactions: List[Dict]) -> str:
        """Create the rhizomatic intelligence prompt"""
        
        # Prepare context
        goals_context = self._format_goals_context(goals)
        contacts_context = self._format_contacts_context(contacts)
        interactions_context = self._format_interactions_context(interactions)
        
        prompt = f"""
You are a Rhizomatic Intelligence Layer embedded in a founder's relationship system.

Your job is to:
1. Understand the user's current goals, including tone, timing, and embedded intent.
2. Analyze the network of contacts without hierarchy—look for emotional ties, shared tags, mutual relevance, and overlooked nodes.
3. Track relationships as living, temporal, emergent structures—connections shift with time, attention, and relevance.
4. Surface connection suggestions not by rank or power, but by relevance to the user's evolving purpose.
5. Offer short, warm, goal-aligned messages the user can send to deepen a connection or rekindle momentum.

Act like a decentralized intelligence—explore all directions. Sometimes the most valuable connection is someone forgotten.

CURRENT CONTEXT:

Goals:
{goals_context}

Network Contacts:
{contacts_context}

Recent Interaction Patterns:
{interactions_context}

Respond with JSON containing:
- 3 suggested contacts (name, why now, what to say)
- 1 unexpected connection path (e.g. "Ana → Marcus → Jocelyn")
- 1 dormant relationship worth reactivating
- A message prompt for each (based on tone: warm / direct / subtle)

Use language rooted in care, clarity, and opportunity. Never assume hierarchy. This is not a CRM. This is a living system.

Format your response as valid JSON with this structure:
{{
  "primary_goal": "main goal title",
  "suggested_contacts": [
    {{
      "name": "Contact Name",
      "reason": "Why this connection matters now",
      "message": "Suggested message text",
      "tone": "warm/direct/subtle",
      "urgency": "high/medium/low"
    }}
  ],
  "connection_path": "Name → Name → Name (description of the path)",
  "dormant_contact": {{
    "name": "Contact Name",
    "last_contact": "timeframe",
    "note": "Why to reactivate",
    "message": "Suggested reactivation message"
  }},
  "network_insights": [
    "Brief insight about network patterns",
    "Another pattern or opportunity"
  ]
}}
"""
        return prompt
    
    def _format_goals_context(self, goals: List[Dict]) -> str:
        """Format goals for AI context"""
        if not goals:
            return "No active goals defined"
        
        formatted = []
        for goal in goals:
            days_old = (datetime.now() - datetime.fromisoformat(goal['created_at'].replace('Z', '+00:00'))).days
            formatted.append(f"- {goal['title']}: {goal['description']} (created {days_old} days ago)")
        
        return "\n".join(formatted)
    
    def _format_contacts_context(self, contacts: List[Dict]) -> str:
        """Format contacts for AI context"""
        if not contacts:
            return "No contacts in network"
        
        formatted = []
        for contact in contacts[:20]:  # Limit to prevent token overflow
            last_contact = "Never contacted"
            if contact.get('most_recent_contact'):
                try:
                    last_date = datetime.fromisoformat(contact['most_recent_contact'].replace('Z', '+00:00'))
                    days_ago = (datetime.now() - last_date).days
                    last_contact = f"{days_ago} days ago"
                except:
                    last_contact = "Recently"
            
            contact_info = f"- {contact['name']}"
            if contact.get('company'):
                contact_info += f" ({contact['company']})"
            if contact.get('title'):
                contact_info += f" - {contact['title']}"
            contact_info += f" | Last contact: {last_contact}"
            if contact.get('tags'):
                contact_info += f" | Tags: {contact['tags']}"
            
            formatted.append(contact_info)
        
        return "\n".join(formatted)
    
    def _format_interactions_context(self, interactions: List[Dict]) -> str:
        """Format recent interactions for AI context"""
        if not interactions:
            return "No recent interactions"
        
        # Group by contact and summarize
        contact_interactions = {}
        for interaction in interactions:
            name = interaction['contact_name']
            if name not in contact_interactions:
                contact_interactions[name] = []
            contact_interactions[name].append(interaction)
        
        formatted = []
        for contact_name, contact_interactions_list in list(contact_interactions.items())[:10]:
            recent = contact_interactions_list[0]
            count = len(contact_interactions_list)
            formatted.append(f"- {contact_name}: {count} interactions, latest: {recent['interaction_type']}")
        
        return "\n".join(formatted)
    
    def _query_rhizomatic_ai(self, prompt: str) -> Dict[str, Any]:
        """Query OpenAI with rhizomatic prompt"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            return ai_response
            
        except Exception as e:
            logging.error(f"Error querying rhizomatic AI: {e}")
            return self._create_fallback_response()
    
    def _create_fallback_response(self) -> Dict[str, Any]:
        """Create fallback response when AI fails"""
        return {
            "primary_goal": "Network growth and meaningful connections",
            "suggested_contacts": [
                {
                    "name": "Recent contact",
                    "reason": "Continue building momentum in your relationship",
                    "message": "Hey! Hope you're doing well. Wanted to check in and see how things are going.",
                    "tone": "warm",
                    "urgency": "medium"
                }
            ],
            "connection_path": "Explore → Connect → Discover",
            "dormant_contact": {
                "name": "Past collaborator",
                "last_contact": "Several months ago",
                "note": "Rekindle professional relationship",
                "message": "Hi! Been thinking about our past collaboration. Would love to catch up."
            },
            "network_insights": [
                "Your network shows potential for deeper connections",
                "Consider reaching out to dormant contacts with genuine care"
            ]
        }
    
    def _create_empty_response(self) -> Dict[str, Any]:
        """Create response when no data available"""
        return {
            "rhizomatic_insights": {
                "primary_goal": "Begin building your network",
                "suggested_contacts": [],
                "connection_path": "Start → Connect → Grow",
                "dormant_contact": None,
                "network_insights": ["Start by adding contacts to build your network"]
            },
            "network_graph": {
                "nodes": [],
                "edges": [],
                "metadata": {"total_nodes": 0, "total_edges": 0}
            },
            "status": "empty"
        }
    
    def _store_rhizomatic_insights(self, user_id: int, insights: Dict[str, Any]):
        """Store rhizomatic insights for historical tracking"""
        try:
            sql = """
            INSERT INTO rhizomatic_insights (user_id, insights_data, created_at)
            VALUES (?, ?, ?)
            """
            conn = self.db.get_connection()
            try:
                conn.execute(sql, [user_id, json.dumps(insights), datetime.now().isoformat()])
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            # Table might not exist yet, that's ok
            logging.warning(f"Could not store rhizomatic insights: {e}")
    
    def _generate_network_graph_data(self, contacts: List[Dict], insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Neo4j-style network graph data with bloom animations"""
        
        nodes = []
        edges = []
        
        # Create nodes for contacts
        for i, contact in enumerate(contacts[:15]):  # Limit for performance
            node_type = "suggested" if any(
                s.get("name") == contact["name"] 
                for s in insights.get("suggested_contacts", [])
            ) else "dormant" if (
                insights.get("dormant_contact", {}).get("name") == contact["name"]
            ) else "normal"
            
            # Calculate node properties
            interaction_count = contact.get('interaction_count', 0) or 0
            
            nodes.append({
                "id": f"contact_{contact['id']}",
                "label": contact['name'],
                "type": node_type,
                "size": max(10, min(30, 10 + interaction_count * 2)),
                "company": contact.get('company', ''),
                "title": contact.get('title', ''),
                "tags": contact.get('tags', ''),
                "last_interaction": contact.get('most_recent_contact', ''),
                "color": self._get_node_color(node_type),
                "physics": True,
                "x": random.uniform(-200, 200),
                "y": random.uniform(-200, 200)
            })
            
            # Create edges based on shared companies, tags, or interactions
            for j, other_contact in enumerate(contacts[i+1:15], i+1):
                if self._should_connect_contacts(contact, other_contact):
                    edges.append({
                        "id": f"edge_{contact['id']}_{other_contact['id']}",
                        "from": f"contact_{contact['id']}",
                        "to": f"contact_{other_contact['id']}",
                        "width": random.uniform(1, 3),
                        "color": {"color": "#666666", "opacity": 0.6},
                        "physics": True,
                        "smooth": {"type": "continuous"}
                    })
        
        # Add user node at center
        nodes.append({
            "id": "user_center",
            "label": "You",
            "type": "user",
            "size": 40,
            "color": "#4CAF50",
            "physics": True,
            "x": 0,
            "y": 0,
            "fixed": True
        })
        
        # Connect user to all contacts
        for contact in contacts[:15]:
            edges.append({
                "id": f"user_to_{contact['id']}",
                "from": "user_center",
                "to": f"contact_{contact['id']}",
                "width": 2,
                "color": {"color": "#4CAF50", "opacity": 0.4},
                "physics": True,
                "smooth": {"type": "continuous"}
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "suggested_count": len([n for n in nodes if n["type"] == "suggested"]),
                "dormant_count": len([n for n in nodes if n["type"] == "dormant"])
            },
            "layout": {
                "algorithm": "force-directed",
                "physics": {
                    "enabled": True,
                    "stabilization": {"iterations": 100}
                }
            }
        }
    
    def _get_node_color(self, node_type: str) -> str:
        """Get color for different node types"""
        colors = {
            "suggested": "#FF6B6B",    # Red for suggested contacts
            "dormant": "#4ECDC4",      # Teal for dormant contacts
            "normal": "#95E1D3",       # Light green for normal contacts
            "user": "#4CAF50"          # Green for user
        }
        return colors.get(node_type, "#95E1D3")
    
    def _should_connect_contacts(self, contact1: Dict, contact2: Dict) -> bool:
        """Determine if two contacts should be connected in the graph"""
        # Connect if same company
        if (contact1.get('company') and contact2.get('company') and 
            contact1['company'].lower() == contact2['company'].lower()):
            return True
        
        # Connect if shared tags
        if contact1.get('tags') and contact2.get('tags'):
            tags1 = set(tag.strip().lower() for tag in contact1['tags'].split(','))
            tags2 = set(tag.strip().lower() for tag in contact2['tags'].split(','))
            if tags1 & tags2:
                return True
        
        # Random connections for network effect (small chance)
        return random.random() < 0.1
    
    def get_network_insights_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get historical rhizomatic insights"""
        try:
            sql = """
            SELECT insights_data, created_at 
            FROM rhizomatic_insights 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """
            conn = self.db.get_connection()
            try:
                cursor = conn.execute(sql, [user_id, limit])
                results = []
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    row_dict['insights_data'] = json.loads(row_dict['insights_data'])
                    results.append(row_dict)
                return results
            finally:
                conn.close()
        except Exception as e:
            logging.error(f"Error getting rhizomatic history: {e}")
            return []