"""
Advanced contact filtering and search functionality.
Provides real-time search, multi-criteria filtering, and intelligent suggestions.
"""

import sqlite3
import re
from typing import List, Dict, Any, Optional
from models import Database

class ContactSearchEngine:
    """Advanced search and filtering engine for contacts"""
    
    def __init__(self, db):
        self.db = db
    
    def search_contacts(self, query: str, user_id: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Comprehensive contact search with multiple search strategies
        """
        if not query and not filters:
            return self.get_all_contacts(user_id)
        
        # Combine different search strategies
        results = []
        
        # 1. Full-text search across all text fields
        if query:
            text_results = self._full_text_search(query, user_id)
            results.extend(text_results)
        
        # 2. Apply filters
        if filters:
            filtered_results = self._apply_filters(results or self.get_all_contacts(user_id), filters)
            results = filtered_results
        
        # 3. Remove duplicates and rank results
        unique_results = self._deduplicate_and_rank(results, query)
        
        return unique_results
    
    def _full_text_search(self, query: str, user_id: int) -> List[Dict[str, Any]]:
        """Full-text search across name, company, notes, and tags"""
        search_terms = self._parse_search_query(query)
        
        sql = """
        SELECT c.*, 
               CASE
                   WHEN LOWER(c.name) LIKE ? THEN 100
                   WHEN LOWER(c.company) LIKE ? THEN 90
                   WHEN LOWER(c.title) LIKE ? THEN 80
                   WHEN LOWER(c.email) LIKE ? THEN 70
                   WHEN LOWER(c.tags) LIKE ? THEN 60
                   WHEN LOWER(c.notes) LIKE ? THEN 50
                   ELSE 25
               END as relevance_score
        FROM contacts c
        WHERE c.user_id = ?
        AND (
            LOWER(c.name) LIKE ? OR
            LOWER(c.company) LIKE ? OR
            LOWER(c.title) LIKE ? OR
            LOWER(c.email) LIKE ? OR
            LOWER(c.tags) LIKE ? OR
            LOWER(c.notes) LIKE ? OR
            LOWER(c.linkedin) LIKE ?
        )
        ORDER BY relevance_score DESC, c.name ASC
        """
        
        search_pattern = f"%{query.lower()}%"
        params = [search_pattern] * 6 + [user_id] + [search_pattern] * 7
        
        cursor = self.db.execute(sql, params)
        contacts = []
        
        for row in cursor.fetchall():
            contact = dict(row)
            contact['search_highlights'] = self._generate_highlights(contact, query)
            contacts.append(contact)
        
        return contacts
    
    def _parse_search_query(self, query: str) -> List[str]:
        """Parse search query into individual terms and phrases"""
        # Handle quoted phrases
        phrases = re.findall(r'"([^"]*)"', query)
        # Remove quoted phrases from query and get individual words
        remaining = re.sub(r'"[^"]*"', '', query)
        words = remaining.split()
        
        return phrases + words
    
    def _apply_filters(self, contacts: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply various filters to contact list"""
        filtered_contacts = contacts.copy()
        
        # Company filter
        if filters.get('company'):
            company_filter = filters['company'].lower()
            filtered_contacts = [
                c for c in filtered_contacts 
                if company_filter in (c.get('company') or '').lower()
            ]
        
        # Relationship type filter
        if filters.get('relationship_type'):
            rel_type = filters['relationship_type']
            filtered_contacts = [
                c for c in filtered_contacts 
                if c.get('relationship_type') == rel_type
            ]
        
        # Warmth level filter
        if filters.get('warmth'):
            warmth_levels = filters['warmth'] if isinstance(filters['warmth'], list) else [filters['warmth']]
            filtered_contacts = [
                c for c in filtered_contacts 
                if c.get('warmth') in warmth_levels
            ]
        
        # Tags filter
        if filters.get('tags'):
            tag_filters = [tag.strip().lower() for tag in filters['tags'].split(',')]
            filtered_contacts = [
                c for c in filtered_contacts 
                if any(tag in (c.get('tags') or '').lower() for tag in tag_filters)
            ]
        
        # Location filter (if stored in notes or new field)
        if filters.get('location'):
            location_filter = filters['location'].lower()
            filtered_contacts = [
                c for c in filtered_contacts 
                if location_filter in (c.get('notes') or '').lower()
            ]
        
        # Last interaction date range
        if filters.get('last_interaction_days'):
            days = int(filters['last_interaction_days'])
            cutoff_date = self._get_date_cutoff(days)
            
            # Get contacts with recent interactions
            sql = """
            SELECT DISTINCT contact_id 
            FROM contact_interactions 
            WHERE user_id = ? AND interaction_date >= ?
            """
            cursor = self.db.execute(sql, [filters.get('user_id', 1), cutoff_date])
            recent_contact_ids = {row[0] for row in cursor.fetchall()}
            
            filtered_contacts = [
                c for c in filtered_contacts 
                if c.get('id') in recent_contact_ids
            ]
        
        # Follow-up due filter
        if filters.get('follow_up_due'):
            today = self._get_today_date()
            sql = """
            SELECT DISTINCT contact_id 
            FROM contact_interactions 
            WHERE user_id = ? AND follow_up_date <= ? AND follow_up_date IS NOT NULL
            """
            cursor = self.db.connection.execute(sql, [filters.get('user_id', 1), today])
            due_contact_ids = {row[0] for row in cursor.fetchall()}
            
            filtered_contacts = [
                c for c in filtered_contacts 
                if c.get('id') in due_contact_ids
            ]
        
        return filtered_contacts
    
    def _generate_highlights(self, contact: Dict[str, Any], query: str) -> Dict[str, str]:
        """Generate search highlights for display"""
        highlights = {}
        query_lower = query.lower()
        
        for field in ['name', 'company', 'title', 'notes', 'tags']:
            value = contact.get(field, '')
            if value and query_lower in value.lower():
                highlighted = self._highlight_text(value, query)
                highlights[field] = highlighted
        
        return highlights
    
    def _highlight_text(self, text: str, query: str) -> str:
        """Add HTML highlighting to matching text"""
        if not text or not query:
            return text
        
        # Case-insensitive replacement with highlighting
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(lambda m: f'<mark>{m.group()}</mark>', text)
    
    def _deduplicate_and_rank(self, contacts: List[Dict[str, Any]], query: str = None) -> List[Dict[str, Any]]:
        """Remove duplicates and rank results by relevance"""
        seen_ids = set()
        unique_contacts = []
        
        for contact in contacts:
            contact_id = contact.get('id')
            if contact_id not in seen_ids:
                seen_ids.add(contact_id)
                unique_contacts.append(contact)
        
        # Sort by relevance score if available, then by name
        unique_contacts.sort(
            key=lambda c: (-c.get('relevance_score', 0), c.get('name', '').lower())
        )
        
        return unique_contacts
    
    def get_search_suggestions(self, partial_query: str, user_id: int) -> Dict[str, List[str]]:
        """Get search suggestions for autocomplete"""
        suggestions = {
            'companies': [],
            'titles': [],
            'tags': [],
            'names': []
        }
        
        if len(partial_query) < 2:
            return suggestions
        
        query_lower = partial_query.lower()
        
        # Get company suggestions
        sql = """
        SELECT DISTINCT company 
        FROM contacts 
        WHERE user_id = ? AND LOWER(company) LIKE ? AND company IS NOT NULL
        ORDER BY company
        LIMIT 5
        """
        cursor = self.db.connection.execute(sql, [user_id, f"{query_lower}%"])
        suggestions['companies'] = [row[0] for row in cursor.fetchall() if row[0]]
        
        # Get title suggestions
        sql = """
        SELECT DISTINCT title 
        FROM contacts 
        WHERE user_id = ? AND LOWER(title) LIKE ? AND title IS NOT NULL
        ORDER BY title
        LIMIT 5
        """
        cursor = self.db.connection.execute(sql, [user_id, f"{query_lower}%"])
        suggestions['titles'] = [row[0] for row in cursor.fetchall() if row[0]]
        
        # Get name suggestions
        sql = """
        SELECT name 
        FROM contacts 
        WHERE user_id = ? AND LOWER(name) LIKE ?
        ORDER BY name
        LIMIT 5
        """
        cursor = self.db.connection.execute(sql, [user_id, f"{query_lower}%"])
        suggestions['names'] = [row[0] for row in cursor.fetchall()]
        
        # Get tag suggestions
        sql = """
        SELECT DISTINCT tags 
        FROM contacts 
        WHERE user_id = ? AND tags IS NOT NULL AND tags != ''
        """
        cursor = self.db.connection.execute(sql, [user_id])
        all_tags = []
        for row in cursor.fetchall():
            if row[0]:
                tags = [tag.strip() for tag in row[0].split(',')]
                all_tags.extend(tags)
        
        # Filter tags that start with query
        matching_tags = [
            tag for tag in set(all_tags) 
            if tag.lower().startswith(query_lower)
        ]
        suggestions['tags'] = sorted(matching_tags)[:5]
        
        return suggestions
    
    def get_filter_options(self, user_id: int) -> Dict[str, List[str]]:
        """Get available filter options from existing data"""
        options = {}
        
        # Get unique companies
        sql = "SELECT DISTINCT company FROM contacts WHERE user_id = ? AND company IS NOT NULL ORDER BY company"
        cursor = self.db.connection.execute(sql, [user_id])
        options['companies'] = [row[0] for row in cursor.fetchall() if row[0]]
        
        # Get unique relationship types
        sql = "SELECT DISTINCT relationship_type FROM contacts WHERE user_id = ? AND relationship_type IS NOT NULL ORDER BY relationship_type"
        cursor = self.db.connection.execute(sql, [user_id])
        options['relationship_types'] = [row[0] for row in cursor.fetchall() if row[0]]
        
        # Get unique warmth levels
        sql = "SELECT DISTINCT warmth FROM contacts WHERE user_id = ? AND warmth IS NOT NULL ORDER BY warmth"
        cursor = self.db.connection.execute(sql, [user_id])
        options['warmth_levels'] = [row[0] for row in cursor.fetchall() if row[0]]
        
        # Get all unique tags
        sql = "SELECT DISTINCT tags FROM contacts WHERE user_id = ? AND tags IS NOT NULL AND tags != ''"
        cursor = self.db.connection.execute(sql, [user_id])
        all_tags = []
        for row in cursor.fetchall():
            if row[0]:
                tags = [tag.strip() for tag in row[0].split(',')]
                all_tags.extend(tags)
        options['tags'] = sorted(list(set(all_tags)))
        
        return options
    
    def get_all_contacts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all contacts for a user"""
        sql = "SELECT * FROM contacts WHERE user_id = ? ORDER BY name"
        cursor = self.db.connection.execute(sql, [user_id])
        return [dict(row) for row in cursor.fetchall()]
    
    def save_search_history(self, user_id: int, query: str, filter_data: str = None):
        """Save search history for analytics and suggestions"""
        sql = """
        INSERT INTO search_history (user_id, query, filters, search_date)
        VALUES (?, ?, ?, datetime('now'))
        """
        self.db.connection.execute(sql, [user_id, query, filter_data])
        self.db.connection.commit()
    
    def get_popular_searches(self, user_id: int, limit: int = 5) -> List[str]:
        """Get popular search queries for the user"""
        sql = """
        SELECT query, COUNT(*) as frequency
        FROM search_history 
        WHERE user_id = ? AND query != ''
        GROUP BY query
        ORDER BY frequency DESC, search_date DESC
        LIMIT ?
        """
        cursor = self.db.connection.execute(sql, [user_id, limit])
        return [row[0] for row in cursor.fetchall()]
    
    def _get_date_cutoff(self, days: int) -> str:
        """Get date cutoff for filtering (SQLite format)"""
        return f"date('now', '-{days} days')"
    
    def _get_today_date(self) -> str:
        """Get today's date in SQLite format"""
        return "date('now')"