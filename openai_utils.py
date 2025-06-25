import os
import json
import logging
from openai import OpenAI

class OpenAIUtils:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "default_key")
        self.client = OpenAI(api_key=self.api_key)
        logging.info("OpenAI client initialized")
    
    def generate_embedding(self, text):
        """Generate embedding for text using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
            return json.dumps(embedding)
        except Exception as e:
            logging.error(f"Failed to generate embedding: {e}")
            raise e
    
    def generate_outreach_message(self, contact_name, goal_title, goal_description, contact_notes="", tone="warm"):
        """Generate personalized outreach message"""
        try:
            # Prepare context from contact notes
            context = f" Based on what I know: {contact_notes}" if contact_notes else ""
            
            prompt = f"""You are helping a founder craft a personalized outreach message.

Contact: {contact_name}
Founder's Goal: "{goal_title}"
Goal Details: {goal_description}{context}

Write a {tone} and professional message that:
1. References the founder's specific goal
2. Explains why this contact might be valuable for achieving it
3. Suggests a clear next step (call, coffee, introduction, etc.)
4. Keeps it concise (2-3 paragraphs max)
5. Feels personal, not templated

Do not include subject line or greetings like "Hi [Name]" - just the message body."""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logging.error(f"Failed to generate outreach message: {e}")
            raise e
    
    def analyze_contact_relevance(self, contact_description, goal_description):
        """Analyze how relevant a contact is for a specific goal"""
        try:
            prompt = f"""Analyze how relevant this contact is for achieving the given goal.

Contact Description: {contact_description}
Goal: {goal_description}

Rate the relevance on a scale of 0-1 where:
- 0.0 = Not relevant at all
- 0.5 = Somewhat relevant, might be helpful
- 1.0 = Highly relevant, perfect match

Respond with only a decimal number between 0 and 1."""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            relevance_score = float(response.choices[0].message.content.strip())
            return max(0.0, min(1.0, relevance_score))
        
        except Exception as e:
            logging.error(f"Failed to analyze contact relevance: {e}")
            return 0.0
