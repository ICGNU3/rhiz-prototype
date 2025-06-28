# Google Contacts OAuth2 Setup Guide

This guide explains how to configure Google OAuth2 credentials for Google Contacts sync integration in the Rhiz platform.

## Prerequisites

- Google Cloud Console access
- Administrative access to your Replit environment

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **People API** (Google Contacts API)
   - Go to "APIs & Services" > "Library"
   - Search for "People API"
   - Click "Enable"

## Step 2: Create OAuth2 Credentials

1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure the OAuth consent screen:
   - Choose "External" for user type
   - Fill in app name: "Rhiz Contact Intelligence"
   - Add your email as developer contact
   - Add scopes: `auth/contacts.readonly` and `auth/userinfo.email`

## Step 3: Configure OAuth Client

1. Application type: **Web application**
2. Name: "Rhiz Production"
3. Authorized redirect URIs:
   ```
   https://YOUR_REPLIT_DOMAIN.replit.app/api/oauth/google/callback
   ```
   Replace `YOUR_REPLIT_DOMAIN` with your actual Replit domain

## Step 4: Set Environment Variables

Add these secrets to your Replit environment:

```bash
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

## Step 5: Test Integration

1. Start your Replit app
2. Check OAuth status:
   ```bash
   curl -X GET https://YOUR_DOMAIN/api/oauth/google/status
   ```
3. Should return `"credentials_configured": true`

## API Endpoints

Once configured, users can access:

- **Connect**: `POST /api/oauth/google/connect` - Start OAuth flow
- **Status**: `GET /api/oauth/google/status` - Check connection status
- **Sync**: `POST /api/contacts/sources/google/sync` - Manual sync trigger
- **Logs**: `GET /api/contacts/sync/logs` - View sync history

## Security Notes

- Credentials are securely stored in PostgreSQL with encryption
- Refresh tokens enable long-term access without re-authorization
- All OAuth flows use secure state tokens to prevent CSRF attacks
- User can revoke access anytime through Google Account settings

## Troubleshooting

**Error: "Credentials not configured"**
- Verify environment variables are set correctly
- Check that CLIENT_ID and CLIENT_SECRET are from the same OAuth app

**Error: "Redirect URI mismatch"**  
- Ensure redirect URI in Google Console exactly matches your domain
- Include both HTTP (development) and HTTPS (production) variants if needed

**Error: "API not enabled"**
- Enable People API in Google Cloud Console
- Wait up to 5 minutes for API activation

## Privacy Compliance

- Only contacts with email addresses are synced
- No contact data is shared between users
- Users maintain full control over their connected accounts
- Sync logs provide complete transparency of all operations