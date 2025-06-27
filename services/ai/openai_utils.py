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
    
    def generate_message(self, contact_name, goal_title, goal_description, contact_bio="", interaction_history="", tone="warm"):
        """Generate a message that connects the user's goal with a suggested contact, based on tone and history"""
        try:
            # Build comprehensive context from contact bio and interaction history
            context_parts = []
            
            if contact_bio:
                context_parts.append(f"Contact Background: {contact_bio}")
            
            if interaction_history:
                context_parts.append(f"Previous Interactions: {interaction_history}")
            
            context = "\n\n".join(context_parts) if context_parts else ""
            
            prompt = f"""You are helping a founder deepen a connection with {contact_name}.
The founder's goal is: "{goal_title}".

Details: {goal_description}

{context}

Write a {tone} message to re-engage this contact that:
1. References their specific background and expertise
2. Connects naturally to the founder's goal
3. Acknowledges any previous interactions if mentioned
4. Suggests a concrete next step
5. Feels authentic and relationship-focused, not transactional
6. Keeps it conversational and concise (2-3 paragraphs)

Do not include subject line or formal greetings - just the message body that could be used in email, LinkedIn, or text."""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip() if response.choices[0].message.content else "No message generated"
        
        except Exception as e:
            logging.error(f"Failed to generate message: {e}")
            raise e

    def generate_outreach_message(self, contact_name, goal_title, goal_description, contact_notes="", tone="warm"):
        """Generate personalized outreach message (legacy method for backward compatibility)"""
        return self.generate_message(contact_name, goal_title, goal_description, contact_notes, "", tone)
    
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
