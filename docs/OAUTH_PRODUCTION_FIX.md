# Fixing OAuth 403 Error in Production

## Problem
Getting "403. That's an error. We're sorry, but you do not have access to this page" when trying to authenticate on Streamlit Cloud.

## Root Cause
The OAuth redirect URI in Google Cloud Console doesn't match your production Streamlit Cloud URL.

---

## Solution: Update Google Cloud Console

### Step 1: Get Your Streamlit Cloud URL
Your app URL is: `https://mays-recruiting-analytics.streamlit.app`

### Step 2: Update Google Cloud Console

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/
   - Select your project

2. **Navigate to OAuth Consent Screen**:
   - Go to: APIs & Services → OAuth consent screen
   - Make sure your app is published (or add test users if in testing mode)

3. **Update Authorized Redirect URIs**:
   - Go to: APIs & Services → Credentials
   - Click on your OAuth 2.0 Client ID
   - Under "Authorized redirect URIs", add:
     ```
     https://mays-recruiting-analytics.streamlit.app
     ```
   - Keep the localhost URI for local development:
     ```
     http://localhost:8501
     ```
   - Click "Save"

### Step 3: Update Streamlit Secrets

1. **Go to Streamlit Cloud Dashboard**:
   - Visit: https://share.streamlit.io/
   - Select your app: mays-recruiting-analytics

2. **Update Secrets**:
   - Click on "Settings" → "Secrets"
   - Update the `redirect_uri` to match your production URL:
   
   ```toml
   [google_oauth]
   client_id = "YOUR_CLIENT_ID"
   client_secret = "YOUR_CLIENT_SECRET"
   redirect_uri = "https://mays-recruiting-analytics.streamlit.app"
   ```

3. **Save and Restart**:
   - Click "Save"
   - App will automatically restart

---

## Verification

1. Visit your production app: https://mays-recruiting-analytics.streamlit.app
2. Click "Sign in with Google"
3. You should be redirected to Google's login page
4. After login, you should be redirected back to your app (not a 403 error)

---

## Important Notes

### Multiple Redirect URIs
You can have multiple redirect URIs in Google Cloud Console:
- `http://localhost:8501` - For local development
- `https://mays-recruiting-analytics.streamlit.app` - For production

### Testing Mode vs Production
- **Testing Mode**: Only allows specific test users (add emails in OAuth consent screen)
- **Production Mode**: Requires Google verification but allows all users
- For internal use, Testing Mode is fine (just add all user emails)

### Common Mistakes
1. ❌ Forgetting to add the production URL to Google Cloud Console
2. ❌ Using HTTP instead of HTTPS for production
3. ❌ Not updating Streamlit secrets after changing redirect URI
4. ❌ Typos in the redirect URI (must match exactly)

---

## Quick Checklist

- [ ] Added production URL to Google Cloud Console Authorized Redirect URIs
- [ ] Updated Streamlit Cloud secrets with production redirect_uri
- [ ] Verified OAuth consent screen is configured
- [ ] Added test users (if in Testing mode)
- [ ] Restarted Streamlit app
- [ ] Tested login flow in production

---

## Still Having Issues?

### Check OAuth Consent Screen
- Make sure app is published or you're added as a test user
- Verify all required scopes are added:
  - `openid`
  - `https://www.googleapis.com/auth/userinfo.email`
  - `https://www.googleapis.com/auth/userinfo.profile`

### Check Credentials
- Client ID and Client Secret are correct in Streamlit secrets
- OAuth 2.0 Client ID type is "Web application"

### Check Redirect URI Format
- Must be exact match (no trailing slashes)
- Must use HTTPS for production
- Must match what's in Streamlit secrets

---

**Last Updated**: January 24, 2026
