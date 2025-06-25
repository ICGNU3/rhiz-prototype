#!/usr/bin/env python3
"""
Utility script to ensure all goals have OpenAI embeddings generated.
This script can be run to backfill embeddings for any existing goals.
"""

import os
import sys
import logging
from models import Database, Goal
from openai_utils import OpenAIUtils

def embed_existing_goals():
    """Generate embeddings for any goals that don't have them"""
    
    # Initialize components
    db = Database()
    goal_model = Goal(db)
    openai_utils = OpenAIUtils()
    
    # Get all goals
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, embedding FROM goals")
    goals = cursor.fetchall()
    
    updated_count = 0
    
    for goal_id, description, embedding in goals:
        if not embedding or embedding.strip() == "":
            print(f"Generating embedding for goal: {goal_id}")
            try:
                # Generate embedding
                new_embedding = openai_utils.generate_embedding(description)
                
                # Update goal with embedding
                goal_model.update_embedding(goal_id, new_embedding)
                updated_count += 1
                print(f"✓ Updated goal {goal_id}")
                
            except Exception as e:
                print(f"✗ Failed to update goal {goal_id}: {e}")
        else:
            print(f"✓ Goal {goal_id} already has embedding")
    
    conn.close()
    print(f"\nCompleted: {updated_count} goals updated with embeddings")
    return updated_count

def verify_embeddings():
    """Verify all goals have valid embeddings"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, embedding FROM goals")
    goals = cursor.fetchall()
    
    missing_embeddings = []
    valid_embeddings = 0
    
    for goal_id, title, embedding in goals:
        if not embedding or embedding.strip() == "":
            missing_embeddings.append((goal_id, title))
        else:
            try:
                # Try to parse the embedding JSON
                import json
                parsed = json.loads(embedding)
                if isinstance(parsed, list) and len(parsed) > 0:
                    valid_embeddings += 1
                else:
                    missing_embeddings.append((goal_id, title))
            except:
                missing_embeddings.append((goal_id, title))
    
    conn.close()
    
    print(f"Embedding Status:")
    print(f"✓ {valid_embeddings} goals with valid embeddings")
    print(f"✗ {len(missing_embeddings)} goals missing embeddings")
    
    if missing_embeddings:
        print("\nGoals missing embeddings:")
        for goal_id, title in missing_embeddings:
            print(f"  - {title} ({goal_id})")
    
    return len(missing_embeddings) == 0

if __name__ == "__main__":
    print("Goal Embedding Utility")
    print("=" * 50)
    
    # Check current status
    all_have_embeddings = verify_embeddings()
    
    if not all_have_embeddings:
        print("\nGenerating missing embeddings...")
        embed_existing_goals()
        print("\nRe-checking status...")
        verify_embeddings()
    else:
        print("\n✓ All goals already have embeddings!")