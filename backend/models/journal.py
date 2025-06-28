"""
Journal Entry Model
Handles journal entries tied to contacts, goals, or insights
"""
from datetime import datetime
from typing import Optional
import uuid

class JournalEntry:
    """Model for journal entries with AI reflection capabilities"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
    
    @staticmethod
    def get_schema():
        """Get the database schema for journal entries"""
        return """
        CREATE TABLE IF NOT EXISTS journal_entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            entry_type VARCHAR(50) DEFAULT 'reflection' CHECK (entry_type IN ('reflection', 'gratitude', 'insight', 'relationship')),
            related_contact_id UUID,
            related_goal_id UUID,
            related_insight_id UUID,
            ai_reflection TEXT,
            ai_insights TEXT,
            mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
            energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
            tags TEXT[], -- Array of tags
            is_private BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (related_contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
            FOREIGN KEY (related_goal_id) REFERENCES goals(id) ON DELETE SET NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_journal_entries_user_id ON journal_entries(user_id);
        CREATE INDEX IF NOT EXISTS idx_journal_entries_created_at ON journal_entries(created_at);
        CREATE INDEX IF NOT EXISTS idx_journal_entries_type ON journal_entries(entry_type);
        CREATE INDEX IF NOT EXISTS idx_journal_entries_related_contact ON journal_entries(related_contact_id);
        CREATE INDEX IF NOT EXISTS idx_journal_entries_related_goal ON journal_entries(related_goal_id);
        
        -- Journal prompts table for weekly/periodic prompts
        CREATE TABLE IF NOT EXISTS journal_prompts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            prompt_text TEXT NOT NULL,
            prompt_type VARCHAR(50) DEFAULT 'weekly' CHECK (prompt_type IN ('daily', 'weekly', 'monthly', 'custom')),
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_journal_prompts_user_id ON journal_prompts(user_id);
        CREATE INDEX IF NOT EXISTS idx_journal_prompts_type ON journal_prompts(prompt_type);
        
        -- Journal reflection sessions for AI interactions
        CREATE TABLE IF NOT EXISTS journal_reflections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            journal_entry_id UUID NOT NULL,
            user_question TEXT,
            ai_response TEXT NOT NULL,
            reflection_type VARCHAR(50) DEFAULT 'general' CHECK (reflection_type IN ('general', 'relationship', 'growth', 'insight')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_journal_reflections_entry_id ON journal_reflections(journal_entry_id);
        """
    
    def create_entry(self, user_id: str, title: str, content: str, 
                     entry_type: str = 'reflection', related_contact_id: Optional[str] = None,
                     related_goal_id: Optional[str] = None, mood_score: Optional[int] = None,
                     energy_level: Optional[int] = None, tags: Optional[list] = None) -> str:
        """Create a new journal entry"""
        if not self.db:
            raise Exception("Database connection required")
        
        try:
            cursor = self.db.cursor()
            entry_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO journal_entries 
                (id, user_id, title, content, entry_type, related_contact_id, 
                 related_goal_id, mood_score, energy_level, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (entry_id, user_id, title, content, entry_type, 
                  related_contact_id, related_goal_id, mood_score, energy_level, tags))
            
            self.db.commit()
            return entry_id
            
        except Exception as e:
            if self.db:
                self.db.rollback()
            raise Exception(f"Failed to create journal entry: {str(e)}")
    
    def get_entries_by_user(self, user_id: str, limit: int = 20, offset: int = 0) -> list:
        """Get journal entries for a user"""
        if not self.db:
            raise Exception("Database connection required")
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT 
                    je.id, je.title, je.content, je.entry_type, je.mood_score, 
                    je.energy_level, je.tags, je.ai_reflection, je.created_at,
                    je.related_contact_id, je.related_goal_id,
                    c.name as contact_name,
                    g.title as goal_title
                FROM journal_entries je
                LEFT JOIN contacts c ON je.related_contact_id = c.id
                LEFT JOIN goals g ON je.related_goal_id = g.id
                WHERE je.user_id = %s
                ORDER BY je.created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
            
            return cursor.fetchall()
            
        except Exception as e:
            raise Exception(f"Failed to get journal entries: {str(e)}")
    
    def get_entry_by_id(self, entry_id: str, user_id: str) -> dict:
        """Get a specific journal entry by ID"""
        if not self.db:
            raise Exception("Database connection required")
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT 
                    je.*, 
                    c.name as contact_name,
                    g.title as goal_title
                FROM journal_entries je
                LEFT JOIN contacts c ON je.related_contact_id = c.id
                LEFT JOIN goals g ON je.related_goal_id = g.id
                WHERE je.id = %s AND je.user_id = %s
            """, (entry_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            # Get reflections for this entry
            cursor.execute("""
                SELECT id, user_question, ai_response, reflection_type, created_at
                FROM journal_reflections
                WHERE journal_entry_id = %s
                ORDER BY created_at DESC
            """, (entry_id,))
            
            reflections = cursor.fetchall()
            
            return {
                'entry': result,
                'reflections': reflections
            }
            
        except Exception as e:
            raise Exception(f"Failed to get journal entry: {str(e)}")
    
    def add_ai_reflection(self, entry_id: str, user_id: str, ai_reflection: str):
        """Add AI reflection to a journal entry"""
        if not self.db:
            raise Exception("Database connection required")
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE journal_entries 
                SET ai_reflection = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
            """, (ai_reflection, entry_id, user_id))
            
            self.db.commit()
            
        except Exception as e:
            if self.db:
                self.db.rollback()
            raise Exception(f"Failed to add AI reflection: {str(e)}")
    
    def create_reflection_session(self, entry_id: str, user_question: str, 
                                  ai_response: str, reflection_type: str = 'general') -> str:
        """Create a new reflection session"""
        if not self.db:
            raise Exception("Database connection required")
        
        try:
            cursor = self.db.cursor()
            reflection_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO journal_reflections 
                (id, journal_entry_id, user_question, ai_response, reflection_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (reflection_id, entry_id, user_question, ai_response, reflection_type))
            
            self.db.commit()
            return reflection_id
            
        except Exception as e:
            if self.db:
                self.db.rollback()
            raise Exception(f"Failed to create reflection session: {str(e)}")
    
    def get_weekly_insights(self, user_id: str) -> dict:
        """Get weekly insights from journal entries"""
        if not self.db:
            raise Exception("Database connection required")
        
        try:
            cursor = self.db.cursor()
            
            # Get entries from the last 7 days
            cursor.execute("""
                SELECT 
                    COUNT(*) as entry_count,
                    AVG(mood_score) as avg_mood,
                    AVG(energy_level) as avg_energy,
                    STRING_AGG(DISTINCT entry_type, ', ') as entry_types,
                    COUNT(DISTINCT related_contact_id) as contacts_mentioned
                FROM journal_entries
                WHERE user_id = %s 
                AND created_at >= CURRENT_DATE - INTERVAL '7 days'
            """, (user_id,))
            
            weekly_stats = cursor.fetchone()
            
            # Get most mentioned contacts
            cursor.execute("""
                SELECT c.name, COUNT(*) as mention_count
                FROM journal_entries je
                JOIN contacts c ON je.related_contact_id = c.id
                WHERE je.user_id = %s 
                AND je.created_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY c.id, c.name
                ORDER BY mention_count DESC
                LIMIT 5
            """, (user_id,))
            
            top_contacts = cursor.fetchall()
            
            return {
                'weekly_stats': weekly_stats,
                'top_contacts': top_contacts
            }
            
        except Exception as e:
            raise Exception(f"Failed to get weekly insights: {str(e)}")