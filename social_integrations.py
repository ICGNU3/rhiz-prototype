"""
Social Platform Integrations for Rhiz Contact Sync
Handles OAuth and API connections for Google, LinkedIn, Twitter, Gmail, Outlook
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
import base64
import os
from contact_sync_engine import ContactSource

class GoogleContactsIntegration:
    """Google People API integration for contacts and profile data"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.api_base = "https://people.googleapis.com/v1"
        
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/contacts.readonly https://www.googleapis.com/auth/userinfo.profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_contacts(self, access_token: str, page_token: str = None, page_size: int = 1000) -> Dict[str, Any]:
        """Fetch contacts from Google People API"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        params = {
            'personFields': 'names,emailAddresses,phoneNumbers,organizations,photos,biographies,urls',
            'pageSize': page_size
        }
        
        if page_token:
            params['pageToken'] = page_token
            
        response = requests.get(f"{self.api_base}/people/me/connections", 
                              headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def parse_google_contact(self, person: Dict[str, Any]) -> ContactSource:
        """Parse Google People API person object into ContactSource"""
        # Extract name
        name = ""
        if person.get('names'):
            name_obj = person['names'][0]
            name = name_obj.get('displayName', '')
        
        # Extract email
        email = None
        if person.get('emailAddresses'):
            email = person['emailAddresses'][0].get('value')
        
        # Extract phone
        phone = None
        if person.get('phoneNumbers'):
            phone = person['phoneNumbers'][0].get('value')
        
        # Extract organization info
        company = None
        title = None
        if person.get('organizations'):
            org = person['organizations'][0]
            company = org.get('name')
            title = org.get('title')
        
        # Extract bio
        bio = None
        if person.get('biographies'):
            bio = person['biographies'][0].get('value')
        
        # Extract profile picture
        profile_picture_url = None
        if person.get('photos'):
            profile_picture_url = person['photos'][0].get('url')
        
        # Extract social handles from URLs
        social_handles = {}
        if person.get('urls'):
            for url_obj in person['urls']:
                url = url_obj.get('value', '')
                if 'linkedin.com' in url:
                    social_handles['linkedin'] = url
                elif 'twitter.com' in url or 'x.com' in url:
                    social_handles['twitter'] = url
        
        return ContactSource(
            name=name,
            email=email,
            phone=phone,
            company=company,
            title=title,
            bio=bio,
            profile_picture_url=profile_picture_url,
            social_handles=social_handles if social_handles else None,
            source='google',
            source_id=person.get('resourceName'),
            raw_data=person,
            sync_timestamp=datetime.now().isoformat()
        )

class LinkedInIntegration:
    """LinkedIn API integration (limited access) with scraping fallback"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.api_base = "https://api.linkedin.com/v2"
    
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'r_liteprofile r_emailaddress w_member_social'
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_profile(self, access_token: str) -> Dict[str, Any]:
        """Get user's LinkedIn profile"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(f"{self.api_base}/people/~", headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_connections(self, access_token: str) -> List[ContactSource]:
        """Get LinkedIn connections (limited by API access)"""
        # Note: LinkedIn severely restricts connection access
        # This would typically only return basic profile info
        # Real implementation would need partner-level access
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(f"{self.api_base}/people/~/connections", headers=headers)
            response.raise_for_status()
            connections = response.json()
            
            contacts = []
            for connection in connections.get('values', []):
                contact = self.parse_linkedin_profile(connection)
                contacts.append(contact)
            
            return contacts
        except requests.RequestException as e:
            logging.warning(f"LinkedIn API access limited: {e}")
            return []
    
    def parse_linkedin_profile(self, profile: Dict[str, Any]) -> ContactSource:
        """Parse LinkedIn profile into ContactSource"""
        name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()
        
        # Extract headline/title
        title = profile.get('headline', '')
        
        # Extract profile picture
        profile_picture_url = None
        if profile.get('pictureUrl'):
            profile_picture_url = profile['pictureUrl']
        
        # Build LinkedIn URL
        public_profile_url = profile.get('publicProfileUrl', '')
        social_handles = {'linkedin': public_profile_url} if public_profile_url else None
        
        return ContactSource(
            name=name,
            title=title,
            profile_picture_url=profile_picture_url,
            social_handles=social_handles,
            source='linkedin',
            source_id=profile.get('id'),
            raw_data=profile,
            sync_timestamp=datetime.now().isoformat()
        )

class TwitterIntegration:
    """Twitter/X.com API v2 integration for followers and following"""
    
    def __init__(self, bearer_token: str, api_key: str, api_secret: str):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_base = "https://api.twitter.com/2"
    
    def get_followers(self, user_id: str, max_results: int = 1000) -> List[ContactSource]:
        """Get Twitter followers"""
        headers = {'Authorization': f'Bearer {self.bearer_token}'}
        
        params = {
            'max_results': min(max_results, 1000),
            'user.fields': 'name,username,description,profile_image_url,url,verified,public_metrics'
        }
        
        contacts = []
        next_token = None
        
        while len(contacts) < max_results:
            if next_token:
                params['pagination_token'] = next_token
            
            response = requests.get(f"{self.api_base}/users/{user_id}/followers", 
                                  headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data:
                for user in data['data']:
                    contact = self.parse_twitter_user(user)
                    contacts.append(contact)
            
            next_token = data.get('meta', {}).get('next_token')
            if not next_token:
                break
        
        return contacts[:max_results]
    
    def get_following(self, user_id: str, max_results: int = 1000) -> List[ContactSource]:
        """Get Twitter following"""
        headers = {'Authorization': f'Bearer {self.bearer_token}'}
        
        params = {
            'max_results': min(max_results, 1000),
            'user.fields': 'name,username,description,profile_image_url,url,verified,public_metrics'
        }
        
        contacts = []
        next_token = None
        
        while len(contacts) < max_results:
            if next_token:
                params['pagination_token'] = next_token
            
            response = requests.get(f"{self.api_base}/users/{user_id}/following", 
                                  headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data:
                for user in data['data']:
                    contact = self.parse_twitter_user(user)
                    contacts.append(contact)
            
            next_token = data.get('meta', {}).get('next_token')
            if not next_token:
                break
        
        return contacts[:max_results]
    
    def parse_twitter_user(self, user: Dict[str, Any]) -> ContactSource:
        """Parse Twitter user object into ContactSource"""
        name = user.get('name', '')
        username = user.get('username', '')
        bio = user.get('description', '')
        profile_picture_url = user.get('profile_image_url', '').replace('_normal', '_400x400')
        
        # Build social handles
        social_handles = {
            'twitter': f"https://twitter.com/{username}",
            'x': f"https://x.com/{username}"
        }
        
        # Extract website URL if available
        if user.get('url'):
            social_handles['website'] = user['url']
        
        return ContactSource(
            name=name,
            bio=bio,
            profile_picture_url=profile_picture_url,
            social_handles=social_handles,
            source='twitter',
            source_id=user.get('id'),
            raw_data=user,
            sync_timestamp=datetime.now().isoformat()
        )

class GmailIntegration:
    """Gmail API integration for contact extraction"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.api_base = "https://gmail.googleapis.com/gmail/v1"
    
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/gmail.readonly',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def extract_email_contacts(self, access_token: str, max_messages: int = 1000) -> List[ContactSource]:
        """Extract contacts from email headers and signatures"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Get recent messages
        params = {
            'maxResults': min(max_messages, 1000),
            'q': 'in:sent OR in:inbox'
        }
        
        response = requests.get(f"{self.api_base}/users/me/messages", 
                              headers=headers, params=params)
        response.raise_for_status()
        messages = response.json()
        
        contacts = {}  # Use dict to dedupe by email
        
        for message in messages.get('messages', []):
            message_id = message['id']
            
            # Get message details
            msg_response = requests.get(f"{self.api_base}/users/me/messages/{message_id}", 
                                      headers=headers)
            msg_response.raise_for_status()
            msg_data = msg_response.json()
            
            # Extract contacts from headers
            payload = msg_data.get('payload', {})
            headers_list = payload.get('headers', [])
            
            for header in headers_list:
                if header['name'].lower() in ['from', 'to', 'cc', 'bcc']:
                    contact = self.parse_email_header(header['value'])
                    if contact and contact.email:
                        contacts[contact.email] = contact
        
        return list(contacts.values())
    
    def parse_email_header(self, header_value: str) -> Optional[ContactSource]:
        """Parse email header into ContactSource"""
        import re
        
        # Pattern to match "Name <email@domain.com>" format
        pattern = r'(?:"?([^"<>]+?)"?\s*)?<([^<>]+@[^<>]+)>'
        match = re.search(pattern, header_value)
        
        if match:
            name = match.group(1).strip() if match.group(1) else ""
            email = match.group(2).strip()
            
            return ContactSource(
                name=name or email.split('@')[0],
                email=email,
                source='gmail',
                source_id=email,
                sync_timestamp=datetime.now().isoformat()
            )
        
        # Fallback for plain email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, header_value)
        
        if email_match:
            email = email_match.group()
            return ContactSource(
                name=email.split('@')[0],
                email=email,
                source='gmail',
                source_id=email,
                sync_timestamp=datetime.now().isoformat()
            )
        
        return None

class OutlookIntegration:
    """Microsoft Graph API integration for Outlook contacts"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.api_base = "https://graph.microsoft.com/v1.0"
    
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'response_mode': 'query',
            'scope': 'https://graph.microsoft.com/Contacts.Read https://graph.microsoft.com/User.Read',
            'state': state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_contacts(self, access_token: str) -> List[ContactSource]:
        """Get Outlook contacts"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        contacts = []
        url = f"{self.api_base}/me/contacts"
        
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            for contact in data.get('value', []):
                parsed_contact = self.parse_outlook_contact(contact)
                contacts.append(parsed_contact)
            
            url = data.get('@odata.nextLink')
        
        return contacts
    
    def parse_outlook_contact(self, contact: Dict[str, Any]) -> ContactSource:
        """Parse Outlook contact into ContactSource"""
        name = contact.get('displayName', '')
        
        # Extract email
        email = None
        if contact.get('emailAddresses'):
            email = contact['emailAddresses'][0].get('address')
        
        # Extract phone
        phone = None
        if contact.get('businessPhones'):
            phone = contact['businessPhones'][0]
        elif contact.get('homePhones'):
            phone = contact['homePhones'][0]
        elif contact.get('mobilePhone'):
            phone = contact['mobilePhone']
        
        # Extract organization info
        company = contact.get('companyName')
        title = contact.get('jobTitle')
        
        return ContactSource(
            name=name,
            email=email,
            phone=phone,
            company=company,
            title=title,
            source='outlook',
            source_id=contact.get('id'),
            raw_data=contact,
            sync_timestamp=datetime.now().isoformat()
        )

class SocialIntegrationManager:
    """Manages all social platform integrations"""
    
    def __init__(self):
        self.integrations = {}
        self._load_credentials()
    
    def _load_credentials(self):
        """Load OAuth credentials from environment variables"""
        # Google
        if os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'):
            self.integrations['google'] = GoogleContactsIntegration(
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')
            )
        
        # LinkedIn
        if os.getenv('LINKEDIN_CLIENT_ID') and os.getenv('LINKEDIN_CLIENT_SECRET'):
            self.integrations['linkedin'] = LinkedInIntegration(
                client_id=os.getenv('LINKEDIN_CLIENT_ID'),
                client_secret=os.getenv('LINKEDIN_CLIENT_SECRET'),
                redirect_uri=os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:5000/auth/linkedin/callback')
            )
        
        # Twitter
        if os.getenv('TWITTER_BEARER_TOKEN'):
            self.integrations['twitter'] = TwitterIntegration(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                api_key=os.getenv('TWITTER_API_KEY', ''),
                api_secret=os.getenv('TWITTER_API_SECRET', '')
            )
        
        # Gmail (uses same Google credentials)
        if os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'):
            self.integrations['gmail'] = GmailIntegration(
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                redirect_uri=os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:5000/auth/gmail/callback')
            )
        
        # Outlook
        if os.getenv('OUTLOOK_CLIENT_ID') and os.getenv('OUTLOOK_CLIENT_SECRET'):
            self.integrations['outlook'] = OutlookIntegration(
                client_id=os.getenv('OUTLOOK_CLIENT_ID'),
                client_secret=os.getenv('OUTLOOK_CLIENT_SECRET'),
                redirect_uri=os.getenv('OUTLOOK_REDIRECT_URI', 'http://localhost:5000/auth/outlook/callback')
            )
    
    def get_integration(self, platform: str):
        """Get integration for specific platform"""
        return self.integrations.get(platform)
    
    def get_available_integrations(self) -> List[str]:
        """Get list of available integrations"""
        return list(self.integrations.keys())
    
    def get_auth_url(self, platform: str, state: str) -> Optional[str]:
        """Get OAuth URL for platform"""
        integration = self.get_integration(platform)
        if integration and hasattr(integration, 'get_auth_url'):
            return integration.get_auth_url(state)
        return None