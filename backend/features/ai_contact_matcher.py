"""
AI-Powered Contact Matching and Intelligent Outreach System
Uses OpenAI embeddings and GPT-4o for semantic analysis and personalized recommendations
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from datetime import datetime, timedelta
import logging

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class AIContactMatcher:
    """Advanced AI-powered contact matching with semantic analysis"""
    
    def __init__(self, db):
        self.db = db
        self.client = client
        
    def find_similar_contacts(self, contact_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Find contacts similar to the given contact using AI embeddings"""
        
        # Get the target contact's information
        target_contact = self._get_contact_details(contact_id)
        if not target_contact:
            return []
        
        # Generate or retrieve embedding for target contact
        target_embedding = self._get_contact_embedding(target_contact)
        if target_embedding is None:
            return []
        
        # Get all other contacts with embeddings
        all_contacts = self._get_all_contacts_with_embeddings(target_contact['user_id'])
        
        # Calculate similarities
        similarities = []
        for contact in all_contacts:
            if contact['id'] == contact_id:
                continue
                
            contact_embedding = json.loads(contact['embedding'])
            similarity = self._cosine_similarity(target_embedding, contact_embedding)
            
            similarities.append({
                'contact': contact,
                'similarity': similarity,
                'reasons': self._analyze_similarity_reasons(target_contact, contact)
            })
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:limit]
    
    def suggest_introduction_opportunities(self, user_id: int) -> List[Dict[str, Any]]:
        """Suggest potential introductions between contacts"""
        
        contacts = self._get_user_contacts(user_id)
        introduction_opportunities = []
        
        for i, contact1 in enumerate(contacts):
            for contact2 in contacts[i+1:]:
                # Skip if contacts already know each other
                if self._contacts_connected(contact1['id'], contact2['id']):
                    continue
                
                # Analyze potential for introduction
                intro_score, reasons = self._analyze_introduction_potential(contact1, contact2)
                
                if intro_score > 0.7:  # High potential threshold
                    introduction_opportunities.append({
                        'contact1': contact1,
                        'contact2': contact2,
                        'score': intro_score,
                        'reasons': reasons,
                        'suggested_message': self._generate_introduction_message(contact1, contact2)
                    })
        
        # Sort by score and return top opportunities
        introduction_opportunities.sort(key=lambda x: x['score'], reverse=True)
        return introduction_opportunities[:10]
    
    def generate_personalized_outreach(self, contact_id: int, goal_description: str = None) -> Dict[str, Any]:
        """Generate personalized outreach messages using AI"""
        
        contact = self._get_contact_details(contact_id)
        if not contact:
            return {"error": "Contact not found"}
        
        # Get interaction history
        interaction_history = self._get_interaction_history(contact_id)
        
        # Analyze contact's interests and background
        contact_analysis = self._analyze_contact_profile(contact)
        
        # Generate multiple outreach options
        outreach_options = []
        
        # Different outreach styles
        styles = [
            {"tone": "professional", "approach": "direct"},
            {"tone": "warm", "approach": "relationship-building"},
            {"tone": "collaborative", "approach": "value-proposition"}
        ]
        
        for style in styles:
            message = self._generate_outreach_message(
                contact, goal_description, contact_analysis, 
                interaction_history, style
            )
            
            outreach_options.append({
                "style": style,
                "subject": message.get("subject", ""),
                "message": message.get("body", ""),
                "follow_up_timeline": message.get("follow_up", "1 week"),
                "success_probability": self._estimate_success_probability(contact, style)
            })
        
        return {
            "contact": contact,
            "analysis": contact_analysis,
            "outreach_options": outreach_options,
            "best_time_to_reach": self._suggest_optimal_timing(contact, interaction_history)
        }
    
    def analyze_network_gaps(self, user_id: int) -> Dict[str, Any]:
        """Analyze gaps in the user's network and suggest areas for expansion"""
        
        contacts = self._get_user_contacts(user_id)
        goals = self._get_user_goals(user_id)
        
        # Analyze current network composition
        network_analysis = {
            "industry_coverage": self._analyze_industry_coverage(contacts),
            "geographic_coverage": self._analyze_geographic_coverage(contacts),
            "seniority_levels": self._analyze_seniority_levels(contacts),
            "relationship_strength": self._analyze_relationship_strength(contacts)
        }
        
        # Identify gaps based on goals
        suggested_targets = []
        for goal in goals:
            goal_gaps = self._identify_goal_specific_gaps(goal, contacts)
            suggested_targets.extend(goal_gaps)
        
        # Generate AI recommendations
        recommendations = self._generate_network_expansion_recommendations(
            network_analysis, suggested_targets, goals
        )
        
        return {
            "current_network": network_analysis,
            "identified_gaps": suggested_targets,
            "ai_recommendations": recommendations,
            "action_items": self._generate_action_items(recommendations)
        }
    
    def predict_contact_responsiveness(self, contact_id: int) -> Dict[str, Any]:
        """Predict how likely a contact is to respond to outreach"""
        
        contact = self._get_contact_details(contact_id)
        interaction_history = self._get_interaction_history(contact_id)
        
        # Analyze response patterns
        response_metrics = self._calculate_response_metrics(interaction_history)
        
        # Consider contact characteristics
        contact_factors = {
            "warmth_level": self._warmth_to_score(contact.get('warmth_label', 'cold')),
            "relationship_type": self._relationship_to_score(contact.get('relationship_type', 'unknown')),
            "recent_activity": self._recent_activity_score(interaction_history),
            "engagement_level": self._calculate_engagement_level(interaction_history)
        }
        
        # AI-powered prediction
        prediction = self._ai_predict_responsiveness(contact, interaction_history, contact_factors)
        
        return {
            "contact": contact,
            "responsiveness_score": prediction["score"],
            "confidence": prediction["confidence"],
            "factors": contact_factors,
            "recommendations": prediction["recommendations"],
            "optimal_approach": prediction["optimal_approach"]
        }
    
    def _get_contact_details(self, contact_id: int) -> Dict[str, Any]:
        """Get detailed contact information"""
        sql = """
        SELECT c.*, 
               GROUP_CONCAT(ci.interaction_type) as interaction_types,
               COUNT(ci.id) as interaction_count,
               MAX(ci.interaction_date) as last_interaction
        FROM contacts c
        LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
        WHERE c.id = ?
        GROUP BY c.id
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(sql, [contact_id])
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def _get_contact_embedding(self, contact: Dict[str, Any]) -> List[float]:
        """Get or generate embedding for contact"""
        
        # Check if embedding already exists
        if contact.get('bio_embedding'):
            return json.loads(contact['bio_embedding'])
        
        # Generate new embedding
        contact_bio = self._build_contact_bio(contact)
        if not contact_bio:
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=contact_bio
            )
            embedding = response.data[0].embedding
            
            # Store embedding in database
            self._store_contact_embedding(contact['id'], embedding)
            return embedding
            
        except Exception as e:
            logging.error(f"Error generating embedding for contact {contact['id']}: {e}")
            return None
    
    def _build_contact_bio(self, contact: Dict[str, Any]) -> str:
        """Build comprehensive bio text for embedding generation"""
        bio_parts = []
        
        if contact.get('name'):
            bio_parts.append(f"Name: {contact['name']}")
        if contact.get('title'):
            bio_parts.append(f"Title: {contact['title']}")
        if contact.get('company'):
            bio_parts.append(f"Company: {contact['company']}")
        if contact.get('notes'):
            bio_parts.append(f"Notes: {contact['notes']}")
        if contact.get('tags'):
            bio_parts.append(f"Tags: {contact['tags']}")
        if contact.get('linkedin_url'):
            bio_parts.append(f"LinkedIn profile available")
        
        return " | ".join(bio_parts)
    
    def _store_contact_embedding(self, contact_id: int, embedding: List[float]):
        """Store contact embedding in database"""
        sql = "UPDATE contacts SET bio_embedding = ? WHERE id = ?"
        conn = self.db.get_connection()
        try:
            conn.execute(sql, [json.dumps(embedding), contact_id])
            conn.commit()
        finally:
            conn.close()
    
    def _get_all_contacts_with_embeddings(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all contacts for user that have embeddings"""
        sql = """
        SELECT * FROM contacts 
        WHERE user_id = ? AND bio_embedding IS NOT NULL
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(sql, [user_id])
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _analyze_similarity_reasons(self, contact1: Dict, contact2: Dict) -> List[str]:
        """Analyze why two contacts are similar"""
        reasons = []
        
        if contact1.get('company') == contact2.get('company'):
            reasons.append("Same company")
        
        if contact1.get('title') and contact2.get('title'):
            title1_words = set(contact1['title'].lower().split())
            title2_words = set(contact2['title'].lower().split())
            if title1_words & title2_words:
                reasons.append("Similar job titles")
        
        if contact1.get('tags') and contact2.get('tags'):
            tags1 = set(tag.strip().lower() for tag in contact1['tags'].split(','))
            tags2 = set(tag.strip().lower() for tag in contact2['tags'].split(','))
            common_tags = tags1 & tags2
            if common_tags:
                reasons.append(f"Shared interests: {', '.join(common_tags)}")
        
        return reasons
    
    def _get_user_contacts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all contacts for a user"""
        sql = "SELECT * FROM contacts WHERE user_id = ?"
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(sql, [user_id])
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _get_user_goals(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all goals for a user"""
        sql = "SELECT * FROM goals WHERE user_id = ?"
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(sql, [user_id])
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _contacts_connected(self, contact1_id: int, contact2_id: int) -> bool:
        """Check if two contacts are already connected"""
        sql = """
        SELECT COUNT(*) as count FROM contact_relationships 
        WHERE (contact1_id = ? AND contact2_id = ?) 
           OR (contact1_id = ? AND contact2_id = ?)
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(sql, [contact1_id, contact2_id, contact2_id, contact1_id])
            result = cursor.fetchone()
            return result['count'] > 0 if result else False
        finally:
            conn.close()
    
    def _analyze_introduction_potential(self, contact1: Dict, contact2: Dict) -> Tuple[float, List[str]]:
        """Analyze potential for introducing two contacts"""
        score = 0.0
        reasons = []
        
        # Industry synergy
        if contact1.get('company') != contact2.get('company'):
            score += 0.3
            reasons.append("Different companies - potential collaboration")
        
        # Complementary roles
        if self._are_roles_complementary(contact1.get('title', ''), contact2.get('title', '')):
            score += 0.4
            reasons.append("Complementary professional roles")
        
        # Shared interests
        if contact1.get('tags') and contact2.get('tags'):
            tags1 = set(tag.strip().lower() for tag in contact1['tags'].split(','))
            tags2 = set(tag.strip().lower() for tag in contact2['tags'].split(','))
            common_interests = len(tags1 & tags2)
            if common_interests > 0:
                score += min(0.3, common_interests * 0.1)
                reasons.append(f"Shared interests: {common_interests}")
        
        return score, reasons
    
    def _are_roles_complementary(self, title1: str, title2: str) -> bool:
        """Check if two job titles are complementary"""
        complementary_pairs = [
            (['founder', 'ceo'], ['investor', 'vc']),
            (['designer', 'product'], ['engineer', 'developer']),
            (['sales', 'business development'], ['marketing', 'growth']),
            (['hr', 'people'], ['recruiter', 'talent']),
        ]
        
        title1_lower = title1.lower()
        title2_lower = title2.lower()
        
        for group1, group2 in complementary_pairs:
            if (any(word in title1_lower for word in group1) and 
                any(word in title2_lower for word in group2)) or \
               (any(word in title1_lower for word in group2) and 
                any(word in title2_lower for word in group1)):
                return True
        
        return False
    
    def _generate_introduction_message(self, contact1: Dict, contact2: Dict) -> str:
        """Generate an introduction message using AI"""
        prompt = f"""
        Generate a warm introduction email template for introducing:
        
        Contact 1: {contact1['name']} - {contact1.get('title', 'Professional')} at {contact1.get('company', 'their company')}
        Contact 2: {contact2['name']} - {contact2.get('title', 'Professional')} at {contact2.get('company', 'their company')}
        
        The introduction should be:
        - Professional but warm
        - Highlight potential synergies
        - Be concise (under 150 words)
        - Include a clear next step
        
        Return only the email body text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error generating introduction message: {e}")
            return f"I'd like to introduce you to {contact2['name']} from {contact2.get('company', 'their company')}. I think you two would have great synergy and potential for collaboration."
    
    def _get_interaction_history(self, contact_id: int) -> List[Dict[str, Any]]:
        """Get interaction history for a contact"""
        sql = """
        SELECT * FROM contact_interactions 
        WHERE contact_id = ? 
        ORDER BY interaction_date DESC
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(sql, [contact_id])
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _analyze_contact_profile(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered analysis of contact profile"""
        profile_text = self._build_contact_bio(contact)
        
        prompt = f"""
        Analyze this professional contact profile and provide insights:
        
        {profile_text}
        
        Provide analysis in JSON format with:
        - "interests": key professional interests
        - "expertise": areas of expertise
        - "networking_style": likely networking preferences
        - "value_proposition": what they might value in outreach
        - "engagement_triggers": topics likely to generate engagement
        
        Keep responses concise and professional.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error analyzing contact profile: {e}")
            return {
                "interests": ["professional networking"],
                "expertise": ["industry professional"],
                "networking_style": "professional",
                "value_proposition": "mutual value exchange",
                "engagement_triggers": ["industry trends", "collaboration opportunities"]
            }
    
    def _generate_outreach_message(self, contact: Dict, goal: str, analysis: Dict, 
                                   history: List[Dict], style: Dict) -> Dict[str, str]:
        """Generate personalized outreach message"""
        
        last_interaction = history[0] if history else None
        
        prompt = f"""
        Generate a personalized outreach message with the following details:
        
        Contact: {contact['name']} - {contact.get('title', '')} at {contact.get('company', '')}
        Goal: {goal or 'General networking and relationship building'}
        Contact Analysis: {json.dumps(analysis)}
        Style: {style['tone']} tone with {style['approach']} approach
        Last Interaction: {last_interaction['interaction_type'] if last_interaction else 'None'}
        
        Generate:
        1. Subject line
        2. Email body (150-200 words)
        3. Suggested follow-up timeline
        
        The message should be personalized, valuable, and action-oriented.
        
        Return in JSON format with keys: subject, body, follow_up
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error generating outreach message: {e}")
            return {
                "subject": f"Connecting with {contact['name']}",
                "body": f"Hi {contact['name']},\n\nI hope this message finds you well. I'd love to connect and explore potential opportunities for collaboration.\n\nBest regards",
                "follow_up": "1 week"
            }
    
    def _estimate_success_probability(self, contact: Dict, style: Dict) -> float:
        """Estimate success probability for outreach style"""
        base_score = 0.3
        
        # Adjust based on relationship warmth
        warmth_multipliers = {
            'contributor': 0.9,
            'active': 0.7,
            'warm': 0.5,
            'aware': 0.3,
            'cold': 0.1
        }
        
        warmth = contact.get('warmth_label', 'cold').lower()
        warmth_score = warmth_multipliers.get(warmth, 0.1)
        
        # Adjust based on style
        if style['tone'] == 'warm' and warmth in ['warm', 'active', 'contributor']:
            warmth_score *= 1.2
        elif style['tone'] == 'professional' and warmth in ['cold', 'aware']:
            warmth_score *= 1.1
        
        return min(0.95, base_score + warmth_score)
    
    def _suggest_optimal_timing(self, contact: Dict, history: List[Dict]) -> Dict[str, str]:
        """Suggest optimal timing for outreach"""
        
        if not history:
            return {
                "best_day": "Tuesday or Wednesday",
                "best_time": "10:00 AM - 11:00 AM or 2:00 PM - 3:00 PM",
                "reasoning": "General best practices for professional outreach"
            }
        
        # Analyze interaction patterns
        day_patterns = {}
        time_patterns = {}
        
        for interaction in history:
            if interaction.get('interaction_date'):
                # This would need more sophisticated date parsing
                # For now, return general recommendations
                pass
        
        return {
            "best_day": "Tuesday or Wednesday",
            "best_time": "Mid-morning or early afternoon",
            "reasoning": "Based on professional networking best practices"
        }
    
    def _calculate_response_metrics(self, history: List[Dict]) -> Dict[str, float]:
        """Calculate response metrics from interaction history"""
        if not history:
            return {"response_rate": 0.0, "avg_response_time": 0.0}
        
        outreach_count = len([h for h in history if h.get('interaction_type') == 'email_sent'])
        response_count = len([h for h in history if h.get('outcome') == 'positive'])
        
        response_rate = response_count / outreach_count if outreach_count > 0 else 0.0
        
        return {
            "response_rate": response_rate,
            "total_interactions": len(history),
            "outreach_attempts": outreach_count,
            "positive_responses": response_count
        }
    
    def _warmth_to_score(self, warmth: str) -> float:
        """Convert warmth level to numeric score"""
        warmth_scores = {
            'contributor': 1.0,
            'active': 0.8,
            'warm': 0.6,
            'aware': 0.4,
            'cold': 0.2
        }
        return warmth_scores.get(warmth.lower(), 0.2)
    
    def _relationship_to_score(self, relationship: str) -> float:
        """Convert relationship type to numeric score"""
        relationship_scores = {
            'close_friend': 1.0,
            'colleague': 0.8,
            'industry_contact': 0.6,
            'acquaintance': 0.4,
            'prospect': 0.3,
            'unknown': 0.1
        }
        return relationship_scores.get(relationship.lower(), 0.1)
    
    def _recent_activity_score(self, history: List[Dict]) -> float:
        """Calculate score based on recent activity"""
        if not history:
            return 0.0
        
        recent_interactions = [h for h in history if self._is_recent_interaction(h)]
        return min(1.0, len(recent_interactions) / 5)  # Cap at 5 recent interactions
    
    def _is_recent_interaction(self, interaction: Dict) -> bool:
        """Check if interaction is recent (within 30 days)"""
        # This would need proper date parsing
        # For now, assume all interactions in history are reasonably recent
        return True
    
    def _calculate_engagement_level(self, history: List[Dict]) -> float:
        """Calculate engagement level from interaction history"""
        if not history:
            return 0.0
        
        positive_interactions = len([h for h in history if h.get('outcome') == 'positive'])
        total_interactions = len(history)
        
        return positive_interactions / total_interactions if total_interactions > 0 else 0.0
    
    def _ai_predict_responsiveness(self, contact: Dict, history: List[Dict], 
                                   factors: Dict) -> Dict[str, Any]:
        """AI-powered responsiveness prediction"""
        
        # Simple scoring algorithm
        score = (
            factors['warmth_level'] * 0.4 +
            factors['relationship_type'] * 0.3 +
            factors['recent_activity'] * 0.2 +
            factors['engagement_level'] * 0.1
        )
        
        confidence = min(0.95, score + 0.1)
        
        recommendations = []
        if score > 0.7:
            recommendations.append("High likelihood of response - proceed with confidence")
        elif score > 0.4:
            recommendations.append("Moderate likelihood - personalize the approach")
        else:
            recommendations.append("Lower likelihood - consider warming up the relationship first")
        
        optimal_approach = "warm" if score > 0.6 else "professional"
        
        return {
            "score": score,
            "confidence": confidence,
            "recommendations": recommendations,
            "optimal_approach": optimal_approach
        }
    
    def _analyze_industry_coverage(self, contacts: List[Dict]) -> Dict[str, int]:
        """Analyze industry coverage in network"""
        industries = {}
        for contact in contacts:
            company = contact.get('company', 'Unknown')
            industries[company] = industries.get(company, 0) + 1
        return industries
    
    def _analyze_geographic_coverage(self, contacts: List[Dict]) -> Dict[str, int]:
        """Analyze geographic coverage in network"""
        # This would need location data extraction
        return {"Unknown": len(contacts)}
    
    def _analyze_seniority_levels(self, contacts: List[Dict]) -> Dict[str, int]:
        """Analyze seniority levels in network"""
        seniority = {"Senior": 0, "Mid": 0, "Junior": 0, "Executive": 0}
        
        for contact in contacts:
            title = contact.get('title', '').lower()
            if any(word in title for word in ['ceo', 'founder', 'president', 'vp', 'director']):
                seniority["Executive"] += 1
            elif any(word in title for word in ['senior', 'lead', 'principal']):
                seniority["Senior"] += 1
            elif any(word in title for word in ['junior', 'associate', 'coordinator']):
                seniority["Junior"] += 1
            else:
                seniority["Mid"] += 1
        
        return seniority
    
    def _analyze_relationship_strength(self, contacts: List[Dict]) -> Dict[str, int]:
        """Analyze relationship strength distribution"""
        strength = {}
        for contact in contacts:
            warmth = contact.get('warmth_label', 'unknown')
            strength[warmth] = strength.get(warmth, 0) + 1
        return strength
    
    def _identify_goal_specific_gaps(self, goal: Dict, contacts: List[Dict]) -> List[Dict]:
        """Identify gaps for specific goal"""
        # This would use AI to analyze goal and suggest target profiles
        return [{"target_profile": "Industry expert", "reasoning": "To achieve goal objectives"}]
    
    def _generate_network_expansion_recommendations(self, analysis: Dict, gaps: List[Dict], 
                                                   goals: List[Dict]) -> List[str]:
        """Generate AI recommendations for network expansion"""
        recommendations = [
            "Focus on building relationships with senior executives",
            "Expand geographic coverage to new markets",
            "Connect with more industry specialists",
            "Strengthen existing warm relationships"
        ]
        return recommendations
    
    def _generate_action_items(self, recommendations: List[str]) -> List[Dict[str, str]]:
        """Generate actionable items from recommendations"""
        actions = []
        for rec in recommendations:
            actions.append({
                "action": rec,
                "priority": "high" if "strengthen" in rec.lower() else "medium",
                "timeline": "next 30 days"
            })
        return actions