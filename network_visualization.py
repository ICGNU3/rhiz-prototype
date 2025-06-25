"""
Contact relationship mapping and network visualization module.
Provides graph-based network analysis and visualization for founder networking.
"""

from models import Database, Contact, ContactRelationship, ContactInteraction
import json
import logging
from collections import defaultdict

class NetworkMapper:
    def __init__(self, db):
        self.db = db
        self.contact_model = Contact(db)
        self.relationship_model = ContactRelationship(db)
        self.interaction_model = ContactInteraction(db)
    
    def build_network_graph(self, user_id):
        """Build a network graph structure from contacts and relationships"""
        # Get all contacts
        contacts = self.contact_model.get_all(user_id)
        
        # Get all relationships
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT contact_a_id, contact_b_id, relationship_type, strength, notes
            FROM contact_relationships 
            WHERE user_id = ?
        """, (user_id,))
        
        relationships = cursor.fetchall()
        
        # Build nodes (contacts)
        nodes = []
        node_map = {}
        
        for i, contact in enumerate(contacts):
            node_id = contact['id']
            node_map[node_id] = i
            
            # Get interaction count for node sizing
            cursor.execute("""
                SELECT COUNT(*) FROM contact_interactions 
                WHERE contact_id = ?
            """, (node_id,))
            
            interaction_count = cursor.fetchone()[0]
            
            # Determine node color based on warmth
            warmth_colors = {
                'Cold': '#6c757d',      # Gray
                'Aware': '#ffc107',     # Yellow
                'Warm': '#fd7e14',      # Orange
                'Active': '#20c997',    # Teal
                'Contributor': '#198754' # Green
            }
            
            color = warmth_colors.get(contact.get('warmth_label', 'Cold'), '#6c757d')
            
            nodes.append({
                'id': node_id,
                'label': contact['name'],
                'title': f"{contact['name']}<br>{contact.get('company', 'Unknown')}<br>{contact.get('relationship_type', 'Contact')}",
                'color': color,
                'size': max(10, min(30, 10 + interaction_count * 2)),  # Size based on interactions
                'warmth': contact.get('warmth_label', 'Cold'),
                'company': contact.get('company', ''),
                'relationship_type': contact.get('relationship_type', 'Contact'),
                'interactions': interaction_count
            })
        
        # Build edges (relationships)
        edges = []
        for rel in relationships:
            contact_a_id, contact_b_id, rel_type, strength, notes = rel
            
            if contact_a_id in node_map and contact_b_id in node_map:
                # Edge color based on relationship strength
                strength_colors = {
                    1: '#dee2e6',  # Light gray - weak
                    2: '#adb5bd',  # Gray - moderate
                    3: '#495057',  # Dark gray - strong
                    4: '#212529',  # Very dark - very strong
                    5: '#000000'   # Black - extremely strong
                }
                
                color = strength_colors.get(strength or 1, '#dee2e6')
                
                edges.append({
                    'from': contact_a_id,
                    'to': contact_b_id,
                    'label': rel_type,
                    'color': color,
                    'width': max(1, (strength or 1)),
                    'title': f"{rel_type}<br>Strength: {strength or 1}/5{f'<br>{notes}' if notes else ''}",
                    'strength': strength or 1
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_contacts': len(nodes),
                'total_relationships': len(edges),
                'avg_connections': len(edges) * 2 / len(nodes) if len(nodes) > 0 else 0
            }
        }
    
    def get_network_clusters(self, user_id):
        """Identify clusters/communities in the network"""
        contacts = self.contact_model.get_all(user_id)
        
        # Group by company and relationship type
        company_clusters = defaultdict(list)
        relationship_clusters = defaultdict(list)
        
        for contact in contacts:
            company = contact.get('company', 'Unknown')
            rel_type = contact.get('relationship_type', 'Contact')
            
            if company and company != 'Unknown':
                company_clusters[company].append(contact)
            
            relationship_clusters[rel_type].append(contact)
        
        # Format clusters for visualization
        clusters = []
        
        # Company clusters
        for company, contacts_list in company_clusters.items():
            if len(contacts_list) > 1:  # Only show clusters with multiple contacts
                clusters.append({
                    'type': 'company',
                    'name': company,
                    'contacts': [c['name'] for c in contacts_list],
                    'count': len(contacts_list),
                    'warmth_distribution': self._get_warmth_distribution(contacts_list)
                })
        
        # Relationship type clusters
        for rel_type, contacts_list in relationship_clusters.items():
            if len(contacts_list) > 2:  # Only show significant clusters
                clusters.append({
                    'type': 'relationship',
                    'name': rel_type,
                    'contacts': [c['name'] for c in contacts_list],
                    'count': len(contacts_list),
                    'warmth_distribution': self._get_warmth_distribution(contacts_list)
                })
        
        return sorted(clusters, key=lambda x: x['count'], reverse=True)
    
    def _get_warmth_distribution(self, contacts):
        """Get warmth level distribution for a group of contacts"""
        warmth_count = defaultdict(int)
        for contact in contacts:
            warmth_count[contact.get('warmth_label', 'Cold')] += 1
        return dict(warmth_count)
    
    def get_network_metrics(self, user_id):
        """Calculate network analysis metrics"""
        graph = self.build_network_graph(user_id)
        nodes = graph['nodes']
        edges = graph['edges']
        
        if not nodes:
            return {
                'total_contacts': 0,
                'total_relationships': 0,
                'network_density': 0,
                'avg_connections_per_contact': 0,
                'most_connected_contact': None,
                'warmth_distribution': {},
                'relationship_type_distribution': {}
            }
        
        # Connection counts per contact
        connection_counts = defaultdict(int)
        for edge in edges:
            connection_counts[edge['from']] += 1
            connection_counts[edge['to']] += 1
        
        # Find most connected contact
        most_connected_id = max(connection_counts.keys(), key=lambda x: connection_counts[x]) if connection_counts else None
        most_connected_contact = next((n for n in nodes if n['id'] == most_connected_id), None) if most_connected_id else None
        
        # Calculate network density
        max_possible_edges = len(nodes) * (len(nodes) - 1) / 2
        network_density = len(edges) / max_possible_edges if max_possible_edges > 0 else 0
        
        # Warmth distribution
        warmth_dist = defaultdict(int)
        relationship_dist = defaultdict(int)
        
        for node in nodes:
            warmth_dist[node['warmth']] += 1
            relationship_dist[node['relationship_type']] += 1
        
        return {
            'total_contacts': len(nodes),
            'total_relationships': len(edges),
            'network_density': round(network_density * 100, 1),
            'avg_connections_per_contact': round(sum(connection_counts.values()) / len(nodes), 1) if nodes else 0,
            'most_connected_contact': most_connected_contact,
            'warmth_distribution': dict(warmth_dist),
            'relationship_type_distribution': dict(relationship_dist),
            'connection_counts': dict(connection_counts)
        }
    
    def suggest_introductions(self, user_id, limit=10):
        """Suggest potential introductions based on network analysis"""
        graph = self.build_network_graph(user_id)
        nodes = graph['nodes']
        edges = graph['edges']
        
        # Build adjacency list
        adjacency = defaultdict(set)
        for edge in edges:
            adjacency[edge['from']].add(edge['to'])
            adjacency[edge['to']].add(edge['from'])
        
        suggestions = []
        
        # Find mutual connections for introduction opportunities
        for node_a in nodes:
            for node_b in nodes:
                if node_a['id'] != node_b['id'] and node_b['id'] not in adjacency[node_a['id']]:
                    # Find mutual connections
                    mutual = adjacency[node_a['id']].intersection(adjacency[node_b['id']])
                    
                    if mutual:
                        # Get mutual contact names
                        mutual_contacts = [n['label'] for n in nodes if n['id'] in mutual]
                        
                        # Calculate introduction score based on warmth and relationship types
                        score = self._calculate_introduction_score(node_a, node_b, mutual_contacts)
                        
                        suggestions.append({
                            'contact_a': node_a['label'],
                            'contact_b': node_b['label'],
                            'mutual_connections': mutual_contacts,
                            'score': score,
                            'reason': self._generate_introduction_reason(node_a, node_b, mutual_contacts)
                        })
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:limit]
    
    def _calculate_introduction_score(self, node_a, node_b, mutual_contacts):
        """Calculate a score for introduction potential"""
        score = 0
        
        # Base score from mutual connections
        score += len(mutual_contacts) * 10
        
        # Warmth bonus
        warmth_scores = {'Cold': 1, 'Aware': 2, 'Warm': 3, 'Active': 4, 'Contributor': 5}
        score += warmth_scores.get(node_a['warmth'], 1) * 2
        score += warmth_scores.get(node_b['warmth'], 1) * 2
        
        # Relationship type synergy
        if node_a['relationship_type'] == 'Investor' and node_b['relationship_type'] == 'Founder':
            score += 20
        elif node_a['relationship_type'] == 'Mentor' and node_b['relationship_type'] == 'Founder':
            score += 15
        elif node_a['relationship_type'] == node_b['relationship_type']:
            score += 5
        
        # Company diversity bonus
        if node_a['company'] != node_b['company']:
            score += 5
        
        return score
    
    def _generate_introduction_reason(self, node_a, node_b, mutual_contacts):
        """Generate a reason for the introduction suggestion"""
        reasons = []
        
        if node_a['relationship_type'] == 'Investor' and node_b['relationship_type'] == 'Founder':
            reasons.append("Potential investment opportunity")
        elif node_a['relationship_type'] == 'Mentor' and node_b['relationship_type'] == 'Founder':
            reasons.append("Mentorship opportunity")
        elif node_a['company'] and node_b['company'] and node_a['company'] != node_b['company']:
            reasons.append("Cross-company collaboration potential")
        
        if len(mutual_contacts) > 1:
            reasons.append(f"Strong mutual network ({len(mutual_contacts)} shared connections)")
        
        return "; ".join(reasons) if reasons else "Network expansion opportunity"
    
    def export_network_data(self, user_id, format='json'):
        """Export network data in various formats"""
        graph = self.build_network_graph(user_id)
        metrics = self.get_network_metrics(user_id)
        clusters = self.get_network_clusters(user_id)
        
        export_data = {
            'network_graph': graph,
            'metrics': metrics,
            'clusters': clusters,
            'generated_at': self.db.get_connection().execute('SELECT datetime("now")').fetchone()[0]
        }
        
        if format == 'json':
            return json.dumps(export_data, indent=2)
        elif format == 'dict':
            return export_data
        
        return export_data