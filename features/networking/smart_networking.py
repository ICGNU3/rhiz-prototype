"""
Smart Networking Intelligence - Advanced Contact Insights and Automation
Provides intelligent networking suggestions, relationship scoring, and automated follow-up recommendations
"""

import sqlite3
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from openai_utils import OpenAIUtils
import numpy as np

class SmartNetworkingEngine:
    """Advanced networking intelligence for relationship optimization"""
    
    def __init__(self, db_path: str = "db.sqlite3"):
        self.db_path = db_path
        self.openai_utils = OpenAIUtils()
        self.openai_client = self.openai_utils.client
        
    def get_relationship_health_score(self, user_id: int, contact_id: int) -> Dict[str, Any]:
        """Calculate comprehensive relationship health score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get contact and interaction data
        cursor.execute("""
            SELECT c.*, u.email as user_email 
            FROM contacts c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ? AND c.user_id = ?
        """, (contact_id, user_id))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return {"error": "Contact not found"}
        
        # Get interaction history
        cursor.execute("""
            SELECT * FROM contact_interactions 
            WHERE contact_id = ? 
            ORDER BY interaction_date DESC
        """, (contact_id,))
        interactions = cursor.fetchall()
        
        conn.close()
        
        # Calculate health metrics
        health_score = self._calculate_health_metrics(contact, interactions)
        
        # Generate AI insights
        ai_insights = self._generate_relationship_insights(contact, interactions, health_score)
        
        return {
            "contact_id": contact_id,
            "health_score": health_score,
            "ai_insights": ai_insights,
            "recommendations": self._generate_relationship_recommendations(health_score, ai_insights),
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_health_metrics(self, contact: Tuple, interactions: List[Tuple]) -> Dict[str, float]:
        """Calculate relationship health metrics"""
        metrics = {
            "recency_score": 0.0,
            "frequency_score": 0.0,
            "engagement_score": 0.0,
            "warmth_score": 0.0,
            "overall_score": 0.0
        }
        
        if not interactions:
            return metrics
        
        # Recency score (0-100)
        last_interaction = datetime.fromisoformat(interactions[0][3])  # interaction_date
        days_since = (datetime.now() - last_interaction).days
        metrics["recency_score"] = max(0, 100 - (days_since * 2))
        
        # Frequency score (0-100)
        interaction_count = len(interactions)
        last_30_days = [i for i in interactions if 
                       (datetime.now() - datetime.fromisoformat(i[3])).days <= 30]
        metrics["frequency_score"] = min(100, len(last_30_days) * 20)
        
        # Engagement score (0-100)
        response_interactions = [i for i in interactions if i[4] == 'response']  # interaction_type
        if interaction_count > 0:
            metrics["engagement_score"] = (len(response_interactions) / interaction_count) * 100
        
        # Warmth score (0-100)
        warmth_mapping = {"cold": 20, "aware": 40, "warm": 60, "active": 80, "contributor": 100}
        warmth = contact[7] if len(contact) > 7 else "cold"  # warmth field
        metrics["warmth_score"] = warmth_mapping.get(warmth, 20)
        
        # Overall score (weighted average)
        metrics["overall_score"] = (
            metrics["recency_score"] * 0.3 +
            metrics["frequency_score"] * 0.2 +
            metrics["engagement_score"] * 0.3 +
            metrics["warmth_score"] * 0.2
        )
        
        return metrics
    
    def _generate_relationship_insights(self, contact: Tuple, interactions: List[Tuple], 
                                      health_score: Dict[str, float]) -> Dict[str, Any]:
        """Generate AI-powered relationship insights"""
        if not self.openai_client:
            return {"error": "OpenAI client not available"}
        
        try:
            # Build context for AI analysis
            contact_context = {
                "name": contact[1],
                "company": contact[2],
                "title": contact[3],
                "warmth": contact[7] if len(contact) > 7 else "unknown",
                "tags": contact[9] if len(contact) > 9 else "",
                "interaction_count": len(interactions),
                "health_metrics": health_score
            }
            
            # Generate insights using AI
            prompt = f"""
            Analyze this professional relationship and provide strategic networking insights:
            
            Contact: {contact_context['name']} at {contact_context['company']} ({contact_context['title']})
            Relationship Warmth: {contact_context['warmth']}
            Recent Interactions: {contact_context['interaction_count']} total
            Health Score: {health_score['overall_score']:.1f}/100
            
            Provide insights in JSON format:
            {{
                "relationship_stage": "string (emerging/developing/established/declining)",
                "networking_potential": "string (high/medium/low)",
                "key_strengths": ["strength1", "strength2"],
                "growth_opportunities": ["opportunity1", "opportunity2"],
                "strategic_value": "string describing strategic importance",
                "next_best_action": "specific actionable recommendation"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Error generating relationship insights: {e}")
            return {"error": "Unable to generate insights"}
    
    def _generate_relationship_recommendations(self, health_score: Dict[str, float], 
                                             insights: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable relationship recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if health_score["recency_score"] < 30:
            recommendations.append({
                "type": "reconnect",
                "priority": "high",
                "action": "Schedule a catch-up call or coffee meeting",
                "reason": "Haven't connected recently - relationship may be cooling"
            })
        
        if health_score["engagement_score"] < 40:
            recommendations.append({
                "type": "engagement",
                "priority": "medium",
                "action": "Try a different communication approach or channel",
                "reason": "Low response rate - may need to adjust outreach style"
            })
        
        if health_score["frequency_score"] > 80:
            recommendations.append({
                "type": "value",
                "priority": "low",
                "action": "Focus on providing value rather than frequent contact",
                "reason": "High interaction frequency - ensure you're adding value"
            })
        
        # AI-driven recommendations
        if insights.get("next_best_action"):
            recommendations.append({
                "type": "ai_strategic",
                "priority": "high",
                "action": insights["next_best_action"],
                "reason": "AI-powered strategic recommendation"
            })
        
        return recommendations
    
    def get_network_intelligence_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive network intelligence dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all contacts for user
        cursor.execute("""
            SELECT id, name, company, title, warmth, relationship_type 
            FROM contacts WHERE user_id = ?
        """, (user_id,))
        contacts = cursor.fetchall()
        
        conn.close()
        
        if not contacts:
            return {"error": "No contacts found"}
        
        # Analyze network composition
        network_analysis = self._analyze_network_composition(contacts)
        
        # Get relationship health for top contacts
        top_contacts = []
        for contact in contacts[:10]:  # Analyze top 10 contacts
            health = self.get_relationship_health_score(user_id, contact[0])
            if "error" not in health:
                top_contacts.append({
                    "contact": {
                        "id": contact[0],
                        "name": contact[1],
                        "company": contact[2],
                        "title": contact[3]
                    },
                    "health_score": health["health_score"]["overall_score"],
                    "status": self._get_health_status(health["health_score"]["overall_score"])
                })
        
        # Sort by health score
        top_contacts.sort(key=lambda x: x["health_score"], reverse=True)
        
        # Generate network insights
        network_insights = self._generate_network_insights(network_analysis, top_contacts)
        
        return {
            "network_analysis": network_analysis,
            "top_relationships": top_contacts[:5],
            "at_risk_relationships": [c for c in top_contacts if c["health_score"] < 40],
            "network_insights": network_insights,
            "recommended_actions": self._get_network_action_plan(network_analysis, top_contacts),
            "last_updated": datetime.now().isoformat()
        }
    
    def _analyze_network_composition(self, contacts: List[Tuple]) -> Dict[str, Any]:
        """Analyze network composition and diversity"""
        total_contacts = len(contacts)
        
        # Analyze by warmth
        warmth_distribution = {}
        for contact in contacts:
            warmth = contact[4] if contact[4] else "unknown"
            warmth_distribution[warmth] = warmth_distribution.get(warmth, 0) + 1
        
        # Analyze by relationship type
        relationship_distribution = {}
        for contact in contacts:
            rel_type = contact[5] if contact[5] else "unknown"
            relationship_distribution[rel_type] = relationship_distribution.get(rel_type, 0) + 1
        
        # Analyze by company
        company_distribution = {}
        for contact in contacts:
            company = contact[2] if contact[2] else "unknown"
            company_distribution[company] = company_distribution.get(company, 0) + 1
        
        return {
            "total_contacts": total_contacts,
            "warmth_distribution": warmth_distribution,
            "relationship_distribution": relationship_distribution,
            "company_diversity": len(company_distribution),
            "largest_company_group": max(company_distribution.values()) if company_distribution else 0
        }
    
    def _get_health_status(self, score: float) -> str:
        """Convert health score to status"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "needs_attention"
    
    def _generate_network_insights(self, analysis: Dict[str, Any], 
                                 top_contacts: List[Dict]) -> List[str]:
        """Generate high-level network insights"""
        insights = []
        
        # Network size insights
        if analysis["total_contacts"] < 10:
            insights.append("Your network is still growing. Focus on quality connections in your target industry.")
        elif analysis["total_contacts"] > 100:
            insights.append("You have a substantial network. Focus on deepening key relationships.")
        
        # Warmth distribution insights
        warmth_dist = analysis["warmth_distribution"]
        active_warm = warmth_dist.get("active", 0) + warmth_dist.get("warm", 0)
        if active_warm / analysis["total_contacts"] < 0.3:
            insights.append("Consider warming up more relationships - only 30% are currently warm or active.")
        
        # Company diversity insights
        if analysis["company_diversity"] / analysis["total_contacts"] > 0.8:
            insights.append("Great company diversity! This provides broad networking opportunities.")
        
        # Relationship health insights
        avg_health = sum(c["health_score"] for c in top_contacts) / len(top_contacts) if top_contacts else 0
        if avg_health < 50:
            insights.append("Several key relationships need attention. Consider scheduling reconnection calls.")
        
        return insights
    
    def _get_network_action_plan(self, analysis: Dict[str, Any], 
                               top_contacts: List[Dict]) -> List[Dict[str, str]]:
        """Generate actionable network development plan"""
        actions = []
        
        # Immediate actions based on health scores
        at_risk = [c for c in top_contacts if c["health_score"] < 40]
        if at_risk:
            actions.append({
                "priority": "high",
                "action": f"Reconnect with {len(at_risk)} at-risk relationships",
                "timeline": "This week",
                "impact": "Prevent relationship decay"
            })
        
        # Medium-term strategic actions
        if analysis["total_contacts"] < 50:
            actions.append({
                "priority": "medium",
                "action": "Expand network by attending 2-3 industry events",
                "timeline": "Next month",
                "impact": "Increase networking opportunities"
            })
        
        # Long-term relationship development
        actions.append({
            "priority": "low",
            "action": "Schedule quarterly relationship reviews",
            "timeline": "Ongoing",
            "impact": "Maintain relationship health"
        })
        
        return actions

def initialize_smart_networking():
    """Initialize smart networking features"""
    logging.info("Smart Networking Intelligence initialized")
    return SmartNetworkingEngine()