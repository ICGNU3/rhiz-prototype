"""
Social Integrations Service
OAuth sync scaffolds for LinkedIn, Google Contacts, and X.com
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
sys.path.append('.')
from database_helpers import DatabaseHelper

logger = logging.getLogger(__name__)

class SocialIntegrations:
    """Social platform integration manager"""
    
    def __init__(self):
        self.supported_platforms = ['linkedin', 'google_contacts', 'x_twitter']
    
    def get_oauth_url(self, platform: str, user_id: str) -> Dict[str, Any]:
        """Generate OAuth URL for social platform"""
        if platform not in self.supported_platforms:
            return {'error': f'Platform {platform} not supported'}
        
        # For now, return scaffold URLs for development
        oauth_urls = {
            'linkedin': {
                'auth_url': 'https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=r_liteprofile%20r_emailaddress%20w_member_social',
                'platform': 'LinkedIn',
                'description': 'Import your LinkedIn connections and professional network',
                'features': ['Contact import', 'Profile enrichment', 'Job change notifications']
            },
            'google_contacts': {
                'auth_url': 'https://accounts.google.com/oauth2/auth?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=https://www.googleapis.com/auth/contacts.readonly',
                'platform': 'Google Contacts',
                'description': 'Sync your Google contacts and maintain unified contact list',
                'features': ['Contact sync', 'Photo sync', 'Phone numbers and emails']
            },
            'x_twitter': {
                'auth_url': 'https://twitter.com/i/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=tweet.read%20users.read%20follows.read',
                'platform': 'X (Twitter)',
                'description': 'Track interactions with your Twitter/X network',
                'features': ['Following list', 'Interaction tracking', 'Social signals']
            }
        }
        
        if platform in oauth_urls:
            # Store integration attempt for tracking
            self._track_integration_attempt(user_id, platform)
            return oauth_urls[platform]
        
        return {'error': 'Platform configuration not found'}
    
    def get_integration_status(self, user_id: str) -> List[Dict[str, Any]]:
        """Get status of all social integrations for user"""
        integrations = []
        
        for platform in self.supported_platforms:
            status = self._get_platform_status(user_id, platform)
            integrations.append({
                'platform': platform,
                'display_name': self._get_platform_display_name(platform),
                'connected': status['connected'],
                'last_sync': status['last_sync'],
                'contact_count': status['contact_count'],
                'available_features': self._get_platform_features(platform)
            })
        
        return integrations
    
    def _track_integration_attempt(self, user_id: str, platform: str):
        """Track OAuth integration attempt"""
        try:
            DatabaseHelper.execute_insert(
                '''
                INSERT INTO integration_attempts (user_id, platform, attempted_at, status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, platform) 
                DO UPDATE SET attempted_at = EXCLUDED.attempted_at, status = EXCLUDED.status
                ''',
                (user_id, platform, datetime.now().isoformat(), 'attempted')
            )
        except Exception as e:
            logger.error(f"Error tracking integration attempt: {e}")
    
    def _get_platform_status(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Get integration status for specific platform"""
        try:
            # Check if user has connected this platform
            integration = DatabaseHelper.execute_query(
                'SELECT * FROM social_integrations WHERE user_id = %s AND platform = %s',
                (user_id, platform),
                fetch_one=True
            )
            
            if integration:
                # Count contacts from this source
                contact_count = DatabaseHelper.execute_query(
                    'SELECT COUNT(*) as count FROM contact_sources WHERE user_id = %s AND source = %s',
                    (user_id, platform),
                    fetch_one=True
                )
                
                return {
                    'connected': True,
                    'last_sync': integration.get('last_sync_at'),
                    'contact_count': contact_count.get('count', 0) if contact_count else 0
                }
            else:
                return {
                    'connected': False,
                    'last_sync': None,
                    'contact_count': 0
                }
        except Exception as e:
            logger.error(f"Error getting platform status: {e}")
            return {
                'connected': False,
                'last_sync': None,
                'contact_count': 0
            }
    
    def _get_platform_display_name(self, platform: str) -> str:
        """Get human-readable platform name"""
        display_names = {
            'linkedin': 'LinkedIn',
            'google_contacts': 'Google Contacts',
            'x_twitter': 'X (Twitter)'
        }
        return display_names.get(platform, platform.title())
    
    def _get_platform_features(self, platform: str) -> List[str]:
        """Get available features for platform"""
        features = {
            'linkedin': [
                'Professional network import',
                'Job change notifications',
                'Company updates',
                'Skill endorsements tracking'
            ],
            'google_contacts': [
                'Contact synchronization',
                'Profile photo sync',
                'Phone and email sync',
                'Contact groups import'
            ],
            'x_twitter': [
                'Following/followers import',
                'Interaction tracking',
                'Social engagement signals',
                'Content engagement analysis'
            ]
        }
        return features.get(platform, [])
    
    def simulate_sync(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Simulate contact sync for demo purposes"""
        if platform not in self.supported_platforms:
            return {'error': 'Platform not supported'}
        
        # Create demo sync job
        sync_data = {
            'linkedin': {
                'contacts_found': 45,
                'new_contacts': 12,
                'updated_contacts': 8,
                'sync_duration': '2.3 seconds'
            },
            'google_contacts': {
                'contacts_found': 127,
                'new_contacts': 23,
                'updated_contacts': 15,
                'sync_duration': '1.8 seconds'
            },
            'x_twitter': {
                'contacts_found': 89,
                'new_contacts': 18,
                'updated_contacts': 6,
                'sync_duration': '3.1 seconds'
            }
        }
        
        result = sync_data.get(platform, {})
        result.update({
            'platform': self._get_platform_display_name(platform),
            'status': 'completed',
            'synced_at': datetime.now().isoformat()
        })
        
        # Track the sync simulation
        try:
            DatabaseHelper.execute_insert(
                '''
                INSERT INTO sync_simulations (user_id, platform, contacts_found, new_contacts, simulated_at)
                VALUES (%s, %s, %s, %s, %s)
                ''',
                (user_id, platform, result.get('contacts_found', 0), result.get('new_contacts', 0), datetime.now().isoformat())
            )
        except Exception as e:
            logger.warning(f"Could not track sync simulation: {e}")
        
        return result
    
    def get_sync_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get sync history for user"""
        try:
            history = DatabaseHelper.execute_query(
                '''
                SELECT * FROM sync_simulations 
                WHERE user_id = %s 
                ORDER BY simulated_at DESC 
                LIMIT 10
                ''',
                (user_id,),
                fetch_all=True
            ) or []
            
            return [dict(record) for record in history]
        except Exception as e:
            logger.error(f"Error getting sync history: {e}")
            return []
    
    def disconnect_platform(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Disconnect social platform integration"""
        try:
            # Remove integration record
            DatabaseHelper.execute_query(
                'DELETE FROM social_integrations WHERE user_id = %s AND platform = %s',
                (user_id, platform)
            )
            
            # Optionally remove synced contacts (for demo, we'll keep them)
            return {
                'success': True,
                'platform': self._get_platform_display_name(platform),
                'message': f'{self._get_platform_display_name(platform)} integration disconnected successfully'
            }
        except Exception as e:
            logger.error(f"Error disconnecting platform: {e}")
            return {
                'success': False,
                'error': 'Failed to disconnect platform integration'
            }