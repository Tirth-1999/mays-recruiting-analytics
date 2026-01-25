# Google OAuth Authentication - Requirements Document

## Feature Overview
Implement Google OAuth 2.0 authentication for the Mays Analytics Platform to enable user identification, personalized experiences, and secure access. This will serve as the foundation for the AI chatbot's chat history and user-specific features.

## Target Users
- **Program Directors**: Personalized dashboards and saved preferences
- **Admissions Staff**: Role-based access to data
- **Marketing Team**: Tracked usage and preferences
- **Executive Leadership**: Secure access to sensitive metrics

## Core Objectives
1. **Secure Authentication**: Google OAuth 2.0 for trusted identity verification
2. **User Profiles**: Store user information (name, email, profile picture)
3. **Session Management**: Maintain login state across page navigation
4. **Database Integration**: User table for storing profiles and preferences
5. **Seamless UX**: Non-intrusive login flow that doesn't disrupt current experience

---

## User Stories

### US-1: Google Sign-In
**As a** new user  
**I want to** sign in with my Google account  
**So that** I can access personalized features without creating a new password

**Acceptance Criteria:**
- AC-1.1: "Sign in with Google" button is prominently displayed
- AC-1.2: Clicking button opens Google OAuth consent screen
- AC-1.3: After authorization, user is redirected back to the platform
- AC-1.4: User profile (name, email, picture) is retrieved from Google
- AC-1.5: User record is created in database on first login
- AC-1.6: Login process completes in < 5 seconds

### US-2: Persistent Session
**As a** logged-in user  
**I want to** stay logged in across page navigation  
**So that** I don't have to re-authenticate constantly

**Acceptance Criteria:**
- AC-2.1: Session persists across all pages in the platform
- AC-2.2: Session remains active for 7 days (configurable)
- AC-2.3: User can manually log out at any time
- AC-2.4: Session expires after inactivity period (optional)
- AC-2.5: Expired sessions redirect to login page

### US-3: User Profile Display
**As a** logged-in user  
**I want to** see my profile information  
**So that** I know I'm logged in and can access my account

**Acceptance Criteria:**
- AC-3.1: User's name and profile picture displayed in header/sidebar
- AC-3.2: Dropdown menu shows full profile details
- AC-3.3: Menu includes "Logout" option
- AC-3.4: Profile picture loads quickly (< 1 second)
- AC-3.5: Graceful fallback if profile picture unavailable

### US-4: Optional Authentication
**As a** casual user  
**I want to** use the platform without logging in  
**So that** I can explore features before committing to sign in

**Acceptance Criteria:**
- AC-4.1: Platform is fully functional without authentication
- AC-4.2: Login prompt appears for features requiring authentication (chatbot)
- AC-4.3: Non-authenticated users see "Sign In" button
- AC-4.4: No data is lost if user signs in mid-session
- AC-4.5: Clear indication of which features require login

### US-5: User Data Management
**As a** user  
**I want to** manage my account data  
**So that** I can control my privacy and preferences

**Acceptance Criteria:**
- AC-5.1: User can view their stored data
- AC-5.2: User can delete their account and all associated data
- AC-5.3: User can update preferences (optional)
- AC-5.4: Data deletion is immediate and complete
- AC-5.5: Confirmation required before account deletion

---

## Technical Requirements

### TR-1: Google OAuth 2.0 Integration
- TR-1.1: Use Google OAuth 2.0 authorization code flow
- TR-1.2: Register application in Google Cloud Console
- TR-1.3: Configure OAuth consent screen
- TR-1.4: Set authorized redirect URIs (local + production)
- TR-1.5: Request minimal scopes: `openid`, `email`, `profile`
- TR-1.6: Handle OAuth errors gracefully

### TR-2: Database Schema
- TR-2.1: Create `users` table with fields:
  - `user_id` (PRIMARY KEY, auto-increment)
  - `google_id` (UNIQUE, from Google)
  - `email` (UNIQUE)
  - `name`
  - `profile_picture_url`
  - `created_at` (timestamp)
  - `last_login` (timestamp)
  - `is_active` (boolean, default true)
- TR-2.2: Create indexes on `google_id` and `email`
- TR-2.3: Migration script for adding table to existing database

### TR-3: Session Management
- TR-3.1: Use Streamlit session state for user data
- TR-3.2: Store user_id in session after successful login
- TR-3.3: Session persists across page reloads
- TR-3.4: Implement session timeout (optional)
- TR-3.5: Secure session data (no sensitive info in client)

### TR-4: Security Requirements
- TR-4.1: Store OAuth credentials in Streamlit secrets
- TR-4.2: Use HTTPS for all OAuth redirects
- TR-4.3: Validate OAuth state parameter to prevent CSRF
- TR-4.4: Never expose client secret in client-side code
- TR-4.5: Implement rate limiting on login attempts
- TR-4.6: Log authentication events for security monitoring

### TR-5: UI/UX Requirements
- TR-5.1: "Sign in with Google" button with Google branding
- TR-5.2: User profile dropdown in top-right corner
- TR-5.3: Loading indicator during authentication
- TR-5.4: Error messages for failed authentication
- TR-5.5: Responsive design (mobile-friendly)
- TR-5.6: Consistent styling with platform theme (maroon/gold)

### TR-6: API Integration
- TR-6.1: Use `google-auth` and `google-auth-oauthlib` libraries
- TR-6.2: Implement token refresh mechanism
- TR-6.3: Handle token expiration gracefully
- TR-6.4: Cache user profile data to minimize API calls

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    profile_picture_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    preferences TEXT  -- JSON string for future use
);

CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);
```

---

## Google Cloud Console Setup

### Steps Required:
1. **Create Project**: "Mays Analytics Platform"
2. **Enable APIs**: Google+ API, Google Identity
3. **Configure OAuth Consent Screen**:
   - App name: "Mays Analytics Platform"
   - User support email: tirth.shah@tamu.edu
   - Scopes: `openid`, `email`, `profile`
   - Test users: Add your email for testing
4. **Create OAuth 2.0 Credentials**:
   - Application type: Web application
   - Authorized redirect URIs:
     - `http://localhost:8501` (local development)
     - `https://your-app.streamlit.app` (production)
5. **Download Credentials**: Save client ID and client secret

---

## Configuration (Streamlit Secrets)

### `.streamlit/secrets.toml`
```toml
[google_oauth]
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"
redirect_uri_local = "http://localhost:8501"
redirect_uri_production = "https://your-app.streamlit.app"
```

### `config_secrets.py` (Local Development)
```python
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"
GOOGLE_REDIRECT_URI = "http://localhost:8501"
```

---

## Implementation Flow

### Login Flow:
1. User clicks "Sign in with Google"
2. App redirects to Google OAuth consent screen
3. User authorizes the application
4. Google redirects back with authorization code
5. App exchanges code for access token
6. App retrieves user profile from Google
7. App creates/updates user record in database
8. App stores user_id in session state
9. User is redirected to original page

### Session Check Flow:
1. On every page load, check if `user_id` in session state
2. If yes, load user data from database
3. If no, show "Sign In" button
4. For protected features, redirect to login if not authenticated

### Logout Flow:
1. User clicks "Logout"
2. Clear session state
3. Redirect to home page
4. Show "Sign In" button

---

## UI Components

### 1. Sign In Button (Unauthenticated State)
```
┌─────────────────────────────────┐
│  🔐 Sign in with Google         │
└─────────────────────────────────┘
```
- Location: Top-right corner of header
- Style: Google brand colors (white background, blue text)
- Icon: Google "G" logo

### 2. User Profile Dropdown (Authenticated State)
```
┌─────────────────────────────────┐
│  👤 John Doe ▼                  │
│  ├─ Profile                     │
│  ├─ Settings (future)           │
│  └─ Logout                      │
└─────────────────────────────────┘
```
- Location: Top-right corner of header
- Shows: Profile picture + name
- Dropdown: Profile, Logout

### 3. Protected Feature Prompt
```
┌─────────────────────────────────┐
│  🔒 Sign in to use AI Chatbot   │
│                                 │
│  [Sign in with Google]          │
└─────────────────────────────────┘
```
- Shows when unauthenticated user tries to access chatbot
- Clear call-to-action

---

## Error Handling

### Common Errors:
1. **OAuth Denied**: User cancels authorization
   - Show: "Sign in cancelled. You can try again anytime."
   
2. **Invalid Credentials**: Wrong client ID/secret
   - Show: "Authentication error. Please contact support."
   
3. **Network Error**: Can't reach Google
   - Show: "Connection error. Please check your internet and try again."
   
4. **Database Error**: Can't save user
   - Show: "Error saving profile. Please try again."
   
5. **Session Expired**: Token expired
   - Show: "Session expired. Please sign in again."

---

## Testing Checklist

### Functional Tests:
- [ ] User can sign in with Google account
- [ ] User profile is saved to database
- [ ] Session persists across page navigation
- [ ] User can log out successfully
- [ ] Unauthenticated users can still use platform
- [ ] Protected features show login prompt
- [ ] Profile picture loads correctly
- [ ] Error messages display appropriately

### Security Tests:
- [ ] OAuth state parameter validated
- [ ] Client secret not exposed in client code
- [ ] HTTPS used for all OAuth redirects
- [ ] Session data is secure
- [ ] Rate limiting works on login attempts

### Performance Tests:
- [ ] Login completes in < 5 seconds
- [ ] Profile picture loads in < 1 second
- [ ] No performance impact on unauthenticated users
- [ ] Database queries are optimized

---

## Success Metrics

### Quantitative:
- **Login Success Rate**: > 95% of attempts succeed
- **Login Time**: < 5 seconds average
- **Session Persistence**: > 99% of sessions persist correctly
- **User Adoption**: 30%+ of users sign in within first week

### Qualitative:
- Users find login process "easy" or "very easy"
- No complaints about authentication flow
- Positive feedback on personalized experience

---

## Dependencies

### Python Libraries:
```
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
```

### External Services:
- Google Cloud Console (OAuth 2.0 credentials)
- Google Identity API

### Infrastructure:
- Existing SQLite database
- Streamlit secrets management
- HTTPS for production deployment

---

## Implementation Phases

### Phase 1: Setup (Day 1)
- Create Google Cloud project
- Configure OAuth consent screen
- Generate OAuth credentials
- Add credentials to secrets

### Phase 2: Database (Day 1)
- Create users table
- Write migration script
- Test database operations

### Phase 3: Core Authentication (Day 2-3)
- Implement OAuth flow
- Create login/logout functions
- Session management
- User profile retrieval

### Phase 4: UI Integration (Day 3-4)
- Add "Sign in with Google" button
- Create user profile dropdown
- Add logout functionality
- Style components to match platform

### Phase 5: Testing & Polish (Day 4-5)
- Test all authentication flows
- Error handling
- Security review
- Performance optimization
- Documentation

---

## Out of Scope (Phase 1)

- ❌ Email/password authentication
- ❌ Multi-factor authentication (MFA)
- ❌ Role-based access control (RBAC)
- ❌ User preferences/settings page
- ❌ Account deletion UI (can be added later)
- ❌ OAuth with other providers (Microsoft, GitHub)

---

## Future Enhancements (Phase 2+)

- ✨ Role-based access control (admin, user, viewer)
- ✨ User preferences and settings
- ✨ Activity logging and analytics
- ✨ Microsoft OAuth for enterprise users
- ✨ Multi-factor authentication
- ✨ Account management page

---

**Document Version**: 2.0  
**Created**: January 24, 2026  
**Last Updated**: January 24, 2026  
**Status**: ✅ Phase 1-4 Complete | 🔄 Phase 5 In Progress

---

## ✅ Implementation Status

### Completed (Phase 1-4):
- ✅ Google Cloud Console setup
- ✅ OAuth 2.0 credentials configured
- ✅ Users table created in database
- ✅ OAuth flow implemented (`utils/auth.py`)
- ✅ Login/logout functionality working
- ✅ Session management across pages
- ✅ UI components (sign-in button, profile dropdown)
- ✅ Error handling with detailed logging
- ✅ HTTP allowed for localhost development

### In Progress (Phase 5):
- 🔄 Security hardening
- 🔄 Data access control
- 🔄 Testing and polish

### Pending Issues:
1. **🚨 SECURITY: Users Table Visibility**
   - **Issue**: All authenticated users can see the `users` table in Data Explorer
   - **Risk**: User emails and profile data exposed to all users
   - **Priority**: HIGH
   - **Solutions**:
     - Option A: Hide `users` table from Data Explorer (Quick fix)
     - Option B: Implement Role-Based Access Control (RBAC)
     - Option C: Create separate admin interface

2. **Production Deployment**
   - Need to remove `OAUTHLIB_INSECURE_TRANSPORT` for production
   - Need to add HTTPS redirect URI to Google Console
   - Need to configure Streamlit Cloud secrets

3. **Session Security**
   - Add CSRF protection back (currently disabled for debugging)
   - Implement session timeout
   - Add rate limiting

---

## 🔒 New User Story: Data Access Control

### US-6: Secure User Data
**As a** platform administrator  
**I want to** control which users can see sensitive data  
**So that** user privacy is protected

**Acceptance Criteria:**
- AC-6.1: Users table is not visible in Data Explorer to regular users
- AC-6.2: Only admins can view user management data
- AC-6.3: Analytics data (admissions, marketing) remains accessible to all authenticated users
- AC-6.4: Clear separation between user data and analytics data
- AC-6.5: Audit log for sensitive data access (future)

**Implementation Options:**

#### Option A: Hide Users Table (Recommended for MVP)
**Pros:**
- Quick to implement (5 minutes)
- Solves immediate security concern
- No changes to existing functionality

**Cons:**
- No admin interface to manage users
- Can't see who's using the platform

**Implementation:**
```python
# In modules/database.py
EXCLUDED_TABLES = ['users', 'chat_history']  # Don't show in Data Explorer
```

#### Option B: Role-Based Access Control (Future)
**Pros:**
- Proper security model
- Flexible permissions
- Admin can manage users

**Cons:**
- Takes longer to implement (1-2 days)
- Requires role assignment UI
- More complex to maintain

**Implementation:**
- Add `role` field to users table (admin, user, viewer)
- Check role before showing sensitive data
- Create admin interface for user management

#### Option C: Separate Admin Page (Hybrid)
**Pros:**
- Clean separation of concerns
- Admin features don't clutter main app
- Can add more admin tools later

**Cons:**
- Requires new page
- Need to protect admin page

**Implementation:**
- Create `/admin` page (requires admin role)
- Show user management, logs, settings
- Hide from regular users

---

## 📋 Updated Technical Requirements

### TR-7: Data Access Control (NEW)
- TR-7.1: Exclude `users` table from Data Explorer
- TR-7.2: Exclude `chat_history` table from Data Explorer (future)
- TR-7.3: Add `role` field to users table (admin, user, viewer)
- TR-7.4: Implement role checking before displaying sensitive data
- TR-7.5: Default role for new users: "user"
- TR-7.6: First user gets "admin" role automatically

### TR-8: Production Security (NEW)
- TR-8.1: Remove `OAUTHLIB_INSECURE_TRANSPORT` for production
- TR-8.2: Use HTTPS redirect URI for production
- TR-8.3: Add CSRF protection back
- TR-8.4: Implement session timeout (7 days)
- TR-8.5: Add rate limiting (10 login attempts per hour)
- TR-8.6: Log all authentication events

---

## 🗄️ Updated Database Schema

### Users Table (Modified)
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    profile_picture_url TEXT,
    role TEXT DEFAULT 'user',  -- NEW: admin, user, viewer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    preferences TEXT  -- JSON string for future use
);

CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);  -- NEW
```

### Migration Needed:
```sql
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';
CREATE INDEX idx_users_role ON users(role);
```

---

## 🎯 Immediate Next Steps

### Priority 1: Security Fix (Today)
1. **Hide users table from Data Explorer**
   - Modify `modules/database.py`
   - Add `EXCLUDED_TABLES` list
   - Test that users table is hidden

2. **Add role field to users table**
   - Create migration script
   - Set your account as admin
   - Default new users to "user" role

### Priority 2: Admin Interface (This Week)
1. **Create admin check function**
   - `auth.is_admin()` helper
   - Check role before showing admin features

2. **Add admin indicator in UI**
   - Show "Admin" badge for admin users
   - Add admin menu option

3. **Create basic admin page**
   - View all users
   - Change user roles
   - View login history

### Priority 3: Production Prep (Next Week)
1. **Security hardening**
   - Remove insecure transport flag
   - Add CSRF protection
   - Implement rate limiting

2. **Streamlit Cloud deployment**
   - Add HTTPS redirect URI
   - Configure secrets
   - Test production login

---

## 🧪 Updated Testing Checklist

### Security Tests (NEW):
- [ ] Users table is NOT visible in Data Explorer
- [ ] Regular users cannot access admin features
- [ ] Admin users CAN access admin features
- [ ] Role changes take effect immediately
- [ ] First user automatically gets admin role
- [ ] CSRF protection works (production)
- [ ] Rate limiting prevents brute force

### Functional Tests:
- [x] User can sign in with Google account
- [x] User profile is saved to database
- [x] Session persists across page navigation
- [x] User can log out successfully
- [x] Unauthenticated users can still use platform
- [ ] Protected features show login prompt (chatbot pending)
- [x] Profile picture loads correctly
- [x] Error messages display appropriately

---

## 📝 Known Issues & Workarounds

### Issue 1: HTTP Required for Localhost
**Problem**: OAuth library requires HTTPS by default  
**Workaround**: `os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'`  
**Production Fix**: Use HTTPS redirect URI, remove workaround

### Issue 2: Users Table Exposed
**Problem**: All users can see user data in Data Explorer  
**Status**: 🔄 Fix in progress  
**Solution**: Hide users table from Data Explorer

### Issue 3: No Admin Interface
**Problem**: Can't manage users or roles  
**Status**: 📋 Planned for Phase 5  
**Solution**: Create admin page with user management

---
