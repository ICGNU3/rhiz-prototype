"""
Social Integrations Service
Handles OAuth and API integrations with social platforms
"""

import logging
import json
import requests
from typing import Dict, List, Any, Optional
import os
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class SocialIntegrations:
    """Handles integrations with social platforms"""
    
    def __init__(self):
        self.supported_platforms = ['google', 'linkedin', 'twitter', 'outlook']
        self.oauth_configs = self._load_oauth_configs()
    
    def get_status(self) -> Dict[str, str]:
        """Return service status"""
        return {
            "status": "operational",
            "service": "social_integrations",
            "platforms": len(self.supported_platforms)
        }
    
    def _load_oauth_configs(self) -> Dict[str, Dict[str, str]]:
        """Load OAuth configurations for supported platforms"""
        return {
            'google': {
                'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
                'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'scope': 'https://www.googleapis.com/auth/contacts.readonly',
                'api_base': 'https://people.googleapis.com/v1'
            },
            'linkedin': {
                'client_id': os.environ.get('LINKEDIN_CLIENT_ID', ''),
                'client_secret': os.environ.get('LINKEDIN_CLIENT_SECRET', ''),
                'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
                'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
                'scope': 'r_liteprofile r_emailaddress',
                'api_base': 'https://api.linkedin.com/v2'
            },
            'twitter': {
                'client_id': os.environ.get('TWITTER_CLIENT_ID', ''),
                'client_secret': os.environ.get('TWITTER_CLIENT_SECRET', ''),
                'auth_url': 'https://twitter.com/i/oauth2/authorize',
                'token_url': 'https://api.twitter.com/2/oauth2/token',
                'scope': 'users.read follows.read',
                'api_base': 'https://api.twitter.com/2'
            },
            'outlook': {
                'client_id': os.environ.get('OUTLOOK_CLIENT_ID', ''),
                'client_secret': os.environ.get('OUTLOOK_CLIENT_SECRET', ''),
                'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                'scope': 'https://graph.microsoft.com/contacts.read',
                'api_base': 'https://graph.microsoft.com/v1.0'
            }
        }
    
    def get_oauth_url(self, platform: str, user_id: str, redirect_uri: str) -> Dict[str, Any]:
        """Generate OAuth authorization URL for platform"""
        try:
            if platform not in self.oauth_configs:
                return {'error': f'Unsupported platform: {platform}'}
            
            config = self.oauth_configs[platform]
            if not config['client_id']:
                return {'error': f'{platform.title()} OAuth not configured'}
            
            params = {
                'client_id': config['client_id'],
                'redirect_uri': redirect_uri,
                'scope': config['scope'],
                'response_type': 'code',
                'state': f"{user_id}:{platform}",
                'access_type': 'offline',  # For Google
                'prompt': 'consent'  # Force consent screen
            }
            
            oauth_url = f"{config['auth_url']}?{urlencode(params)}"
            
            return {
                'url': oauth_url,
                'platform': platform,
                'status': 'ready'
            }
            
        except Exception as e:
            logger.error(f"Error generating OAuth URL for {platform}: {e}")
            return {'error': str(e)}
    
    def exchange_code_for_token(self, platform: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange OAuth code for access token"""
        try:
            if platform not in self.oauth_configs:
                return {'error': f'Unsupported platform: {platform}'}
            
            config = self.oauth_configs[platform]
            
            token_data = {
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            response = requests.post(config['token_url'], data=token_data)
            
            if response.status_code == 200:
                token_info = response.json()
                return {
                    'access_token': token_info.get('access_token'),
                    'refresh_token': token_info.get('refresh_token'),
                    'expires_in': token_info.get('expires_in'),
                    'platform': platform
                }
            else:
                return {'error': f'Failed to exchange code: {response.text}'}
                
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return {'error': str(e)}
    
    def fetch_contacts(self, platform: str, access_token: str) -> Dict[str, Any]:
        """Fetch contacts from platform using access token"""
        try:
            if platform == 'google':
                return self._fetch_google_contacts(access_token)
            elif platform == 'linkedin':
                return self._fetch_linkedin_connections(access_token)
            elif platform == 'outlook':
                return self._fetch_outlook_contacts(access_token)
            else:
                return {'error': f'Contact fetching not implemented for {platform}'}
                
        except Exception as e:
            logger.error(f"Error fetching contacts from {platform}: {e}")
            return {'error': str(e)}
    
    def _fetch_google_contacts(self, access_token: str) -> Dict[str, Any]:
        """Fetch contacts from Google Contacts API"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = 'https://people.googleapis.com/v1/people/me/connections'
            params = {
                'personFields': 'names,emailAddresses,phoneNumbers,organizations,urls',
                'pageSize': 1000
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                contacts = []
                
                for person in data.get('connections', []):
                    contact = self._parse_google_contact(person)
                    if contact:
                        contacts.append(contact)
                
                return {
                    'contacts': contacts,
                    'count': len(contacts),
                    'platform': 'google'
                }
            else:
                return {'error': f'Google API error: {response.text}'}
                
        except Exception as e:
            logger.error(f"Error fetching Google contacts: {e}")
            return {'error': str(e)}
    
    def _parse_google_contact(self, person: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Google contact data to standard format"""
        try:
            contact = {}
            
            # Name
            names = person.get('names', [])
            if names:
                contact['name'] = names[0].get('displayName', '')
            
            # Email
            emails = person.get('emailAddresses', [])
            if emails:
                contact['email'] = emails[0].get('value', '')
            
            # Phone
            phones = person.get('phoneNumbers', [])
            if phones:
                contact['phone'] = phones[0].get('value', '')
            
            # Organization
            orgs = person.get('organizations', [])
            if orgs:
                org = orgs[0]
                contact['company'] = org.get('name', '')
                contact['title'] = org.get('title', '')
            
            # LinkedIn URL
            urls = person.get('urls', [])
            for url in urls:
                if 'linkedin' in url.get('value', '').lower():
                    contact['linkedin'] = url.get('value', '')
                    break
            
            return contact if contact.get('name') or contact.get('email') else None
            
        except Exception as e:
            logger.error(f"Error parsing Google contact: {e}")
            return None
    
    def _fetch_linkedin_connections(self, access_token: str) -> Dict[str, Any]:
        """Fetch connections from LinkedIn API"""
        # Note: LinkedIn has restricted their connections API
        # This would require LinkedIn Partner Program access
        return {
            'error': 'LinkedIn connections API requires partner access',
            'suggestion': 'Use CSV export from LinkedIn instead'
        }
    
    def _fetch_outlook_contacts(self, access_token: str) -> Dict[str, Any]:
        """Fetch contacts from Outlook/Microsoft Graph API"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = 'https://graph.microsoft.com/v1.0/me/contacts'
            params = {'$top': 1000}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                contacts = []
                
                for contact_data in data.get('value', []):
                    contact = self._parse_outlook_contact(contact_data)
                    if contact:
                        contacts.append(contact)
                
                return {
                    'contacts': contacts,
                    'count': len(contacts),
                    'platform': 'outlook'
                }
            else:
                return {'error': f'Outlook API error: {response.text}'}
                
        except Exception as e:
            logger.error(f"Error fetching Outlook contacts: {e}")
            return {'error': str(e)}
    
    def _parse_outlook_contact(self, contact_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Outlook contact data to standard format"""
        try:
            contact = {}
            
            # Name
            contact['name'] = contact_data.get('displayName', '')
            
            # Email
            emails = contact_data.get('emailAddresses', [])
            if emails:
                contact['email'] = emails[0].get('address', '')
            
            # Phone
            phones = contact_data.get('businessPhones', [])
            if phones:
                contact['phone'] = phones[0]
            
            # Company
            contact['company'] = contact_data.get('companyName', '')
            contact['title'] = contact_data.get('jobTitle', '')
            
            return contact if contact.get('name') or contact.get('email') else None
            
        except Exception as e:
            logger.error(f"Error parsing Outlook contact: {e}")
            return None
    
    def get_platform_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all platform integrations"""
        status = {}
        
        for platform, config in self.oauth_configs.items():
            status[platform] = {
                'configured': bool(config['client_id'] and config['client_secret']),
                'available': platform in self.supported_platforms,
                'features': self._get_platform_features(platform)
            }
        
        return status
    
    def _get_platform_features(self, platform: str) -> List[str]:
        """Get available features for platform"""
        features = {
            'google': ['contacts', 'sync', 'oauth'],
            'linkedin': ['csv_import'],  # API restricted
            'twitter': ['oauth'],  # Limited contact data
            'outlook': ['contacts', 'sync', 'oauth']
        }
        
        return features.get(platform, [])
    
    def get_integration_status(self, user_id: str) -> Dict[str, Any]:
        """Get integration status for a specific user"""
        try:
            logger.info(f"Getting integration status for user {user_id}")
            
            # Get platform configurations
            platform_status = self.get_platform_status()
            
            # Return integration status per platform
            integrations = {}
            for platform in self.supported_platforms:
                integrations[platform] = {
                    'connected': False,  # Would check user-specific tokens in real implementation
                    'available': platform_status.get(platform, {}).get('available', False),
                    'configured': platform_status.get(platform, {}).get('configured', False),
                    'features': platform_status.get(platform, {}).get('features', []),
                    'last_sync': None,
                    'contact_count': 0
                }
            
            return integrations
            
        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            return {platform: {'connected': False, 'available': False} for platform in self.supported_platforms}

# Global instance
social_integrations = SocialIntegrations()