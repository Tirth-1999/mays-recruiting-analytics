# Deployment Guide - Mays Analytics Platform

## Streamlit Cloud Deployment

### Prerequisites
- GitHub repository with the code
- Streamlit Cloud account (https://streamlit.io/cloud)
- Resend API key for email functionality

### Step 1: Configure Secrets on Streamlit Cloud

The Contact & Feedback form requires API credentials to send emails. These must be configured as secrets in Streamlit Cloud.

1. **Go to your Streamlit Cloud dashboard**
   - Navigate to https://share.streamlit.io/
   - Select your deployed app

2. **Open App Settings**
   - Click the "⋮" menu (three dots) on your app
   - Select "Settings"

3. **Add Secrets**
   - Go to the "Secrets" section
   - Add the following secrets in TOML format:

```toml
# Resend API Configuration
RESEND_API_KEY = "re_7w31ZmLe_BsmkaumUndFED35R5zT4pMmJ"
CONTACT_EMAIL = "tirth.shah@tamu.edu"
FROM_EMAIL = "onboarding@resend.dev"
```

4. **Save and Deploy**
   - Click "Save"
   - Streamlit will automatically redeploy your app with the new secrets

### Step 2: Verify Email Functionality

After deployment:
1. Navigate to the Documentation page
2. Scroll to "Contact & Feedback" section
3. Fill out and submit a test form
4. Check tirth.shah@tamu.edu for the test email

### Local Development Setup

For local development, create a `config_secrets.py` file in the root directory:

```python
# config_secrets.py (DO NOT COMMIT)
RESEND_API_KEY = "re_7w31ZmLe_BsmkaumUndFED35R5zT4pMmJ"
CONTACT_EMAIL = "tirth.shah@tamu.edu"
FROM_EMAIL = "onboarding@resend.dev"
```

The code automatically detects whether it's running on Streamlit Cloud or locally and uses the appropriate secret source.

### How It Works

The application uses a fallback mechanism:
1. **First**: Try to load secrets from Streamlit Cloud (`st.secrets`)
2. **Fallback**: If not on Streamlit Cloud, load from local `config_secrets.py`

This ensures the app works in both environments without code changes.

### Security Notes

✅ **Secrets are secure**:
- Never committed to version control
- Encrypted at rest on Streamlit Cloud
- Only accessible to your deployed app
- Not visible in logs or error messages

✅ **Files excluded from git**:
- `config_secrets.py` (local development)
- `.streamlit/secrets.toml` (local Streamlit secrets)

### Troubleshooting

**Error: "Email service is not configured"**
- Verify secrets are added in Streamlit Cloud settings
- Check secret names match exactly (case-sensitive)
- Ensure TOML format is correct (no extra quotes or spaces)
- Redeploy the app after adding secrets

**Email not sending**
- Verify Resend API key is valid
- Check Resend dashboard for API usage/errors
- Ensure FROM_EMAIL is authorized in Resend
- Check spam folder for test emails

**Local development not working**
- Ensure `config_secrets.py` exists in root directory
- Verify file contains all required variables
- Check Python can import the file: `python3 -c "from config_secrets import RESEND_API_KEY"`

### Environment Variables (Alternative)

If you prefer environment variables over secrets files, you can also set:

```bash
export RESEND_API_KEY="your_key_here"
export CONTACT_EMAIL="your.email@example.com"
export FROM_EMAIL="onboarding@resend.dev"
```

Then modify the code to read from `os.environ` instead.

### Updating Secrets

To update secrets on Streamlit Cloud:
1. Go to App Settings → Secrets
2. Edit the TOML content
3. Click "Save"
4. App will automatically redeploy

### Additional Resources

- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Resend API Documentation](https://resend.com/docs)
- [Resend Dashboard](https://resend.com/dashboard)
