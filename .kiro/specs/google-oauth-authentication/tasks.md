# Google OAuth Authentication - Tasks

**Status**: Phase 1-4 Complete | Phase 5 In Progress  
**Last Updated**: January 24, 2026

---

## Phase 1: Setup & Configuration ✅ COMPLETE

- [x] 1.1 Create Google Cloud Console project
- [x] 1.2 Enable Google+ API and Google Identity
- [x] 1.3 Configure OAuth consent screen
- [x] 1.4 Create OAuth 2.0 credentials
- [x] 1.5 Add redirect URIs (localhost:8501)
- [x] 1.6 Store credentials in config_secrets.py
- [x] 1.7 Add credentials to .gitignore

---

## Phase 2: Database Setup ✅ COMPLETE

- [x] 2.1 Create users table schema
- [x] 2.2 Add indexes (google_id, email)
- [x] 2.3 Create migration script (add_users_table.py)
- [x] 2.4 Run migration
- [x] 2.5 Add role field to users table
- [x] 2.6 Create role migration script (add_user_roles.py)
- [x] 2.7 Set admin users

---

## Phase 3: Core Authentication ✅ COMPLETE

- [x] 3.1 Install Google auth libraries
- [x] 3.2 Create utils/auth.py module
- [x] 3.3 Implement OAuth flow creation
- [x] 3.4 Implement authorization URL generation
- [x] 3.5 Implement OAuth callback handling
- [x] 3.6 Implement user profile retrieval
- [x] 3.7 Implement create/update user function
- [x] 3.8 Implement login function
- [x] 3.9 Implement logout function
- [x] 3.10 Add session state initialization
- [x] 3.11 Add authentication check functions
- [x] 3.12 Add role-based functions (is_admin, get_user_role)
- [x] 3.13 Allow HTTP for localhost (OAUTHLIB_INSECURE_TRANSPORT)

---

## Phase 4: UI Integration ✅ COMPLETE

- [x] 4.1 Add OAuth callback handling to main_app.py
- [x] 4.2 Create "Sign in with Google" button
- [x] 4.3 Create user profile dropdown
- [x] 4.4 Add logout button to dropdown
- [x] 4.5 Style components with maroon/gold theme
- [x] 4.6 Add error handling and display
- [x] 4.7 Test authentication flow
- [x] 4.8 Hide users table from Data Explorer
- [x] 4.9 Add EXCLUDED_TABLES list

---

## Phase 5: Security & Polish 🔄 IN PROGRESS

### Security Hardening
- [ ] 5.1 Add session timeout (7 days)
  - [ ] 5.1.1 Store login timestamp in session
  - [ ] 5.1.2 Check timestamp on each page load
  - [ ] 5.1.3 Auto-logout if expired
  - [ ] 5.1.4 Show "Session expired" message

- [ ] 5.2 Re-enable CSRF protection
  - [ ] 5.2.1 Store OAuth state in session
  - [ ] 5.2.2 Validate state in callback
  - [ ] 5.2.3 Handle state mismatch errors

- [ ] 5.3 Add rate limiting
  - [ ] 5.3.1 Track login attempts per IP
  - [ ] 5.3.2 Limit to 10 attempts per hour
  - [ ] 5.3.3 Show "Too many attempts" message
  - [ ] 5.3.4 Add cooldown period

- [ ] 5.4 Support both HTTP and HTTPS
  - [ ] 5.4.1 Detect protocol from request
  - [ ] 5.4.2 Set OAUTHLIB flag conditionally
  - [ ] 5.4.3 Use appropriate redirect URI
  - [ ] 5.4.4 Test with both protocols

### User Management
- [ ] 5.5 Create user profile page
  - [ ] 5.5.1 Show user information
  - [ ] 5.5.2 Show account creation date
  - [ ] 5.5.3 Show last login date
  - [ ] 5.5.4 Show role badge

- [ ] 5.6 Add account deletion
  - [ ] 5.6.1 Create delete account button
  - [ ] 5.6.2 Add confirmation dialog
  - [ ] 5.6.3 Delete user from database
  - [ ] 5.6.4 Delete associated data (chat history)
  - [ ] 5.6.5 Logout after deletion
  - [ ] 5.6.6 Show success message

- [ ] 5.7 Add preferences management (optional)
  - [ ] 5.7.1 Create preferences UI
  - [ ] 5.7.2 Store preferences in JSON field
  - [ ] 5.7.3 Load preferences on login
  - [ ] 5.7.4 Apply preferences to UI

### Token Management
- [ ] 5.8 Implement token refresh
  - [ ] 5.8.1 Store refresh token
  - [ ] 5.8.2 Check token expiration
  - [ ] 5.8.3 Refresh before expiry
  - [ ] 5.8.4 Handle refresh errors

- [ ] 5.9 Handle token expiration
  - [ ] 5.9.1 Detect expired tokens
  - [ ] 5.9.2 Prompt re-authentication
  - [ ] 5.9.3 Preserve user state

### Logging & Monitoring
- [ ] 5.10 Add authentication event logging
  - [ ] 5.10.1 Log successful logins
  - [ ] 5.10.2 Log failed login attempts
  - [ ] 5.10.3 Log logouts
  - [ ] 5.10.4 Log role changes
  - [ ] 5.10.5 Store logs in database

- [ ] 5.11 Create auth_logs table
  - [ ] 5.11.1 Design schema
  - [ ] 5.11.2 Create migration
  - [ ] 5.11.3 Add logging functions

---

## Phase 6: Admin Features 📋 PLANNED

- [ ] 6.1 Create admin dashboard page
  - [ ] 6.1.1 Add "Admin" navigation option
  - [ ] 6.1.2 Restrict access to admins only
  - [ ] 6.1.3 Show user statistics

- [ ] 6.2 User management interface
  - [ ] 6.2.1 List all users
  - [ ] 6.2.2 Show user details
  - [ ] 6.2.3 Change user roles
  - [ ] 6.2.4 Deactivate users
  - [ ] 6.2.5 Delete users

- [ ] 6.3 Activity monitoring
  - [ ] 6.3.1 Show recent logins
  - [ ] 6.3.2 Show active sessions
  - [ ] 6.3.3 Show failed login attempts
  - [ ] 6.3.4 Export activity logs

- [ ] 6.4 System settings
  - [ ] 6.4.1 Configure session timeout
  - [ ] 6.4.2 Configure rate limits
  - [ ] 6.4.3 Manage admin emails list

---

## Phase 7: Production Deployment 🚀 PLANNED

- [ ] 7.1 Production environment setup
  - [ ] 7.1.1 Get production URL
  - [ ] 7.1.2 Add HTTPS redirect URI to Google Console
  - [ ] 7.1.3 Configure Streamlit Cloud secrets
  - [ ] 7.1.4 Remove OAUTHLIB_INSECURE_TRANSPORT for production

- [ ] 7.2 Security review
  - [ ] 7.2.1 Verify CSRF protection enabled
  - [ ] 7.2.2 Verify rate limiting works
  - [ ] 7.2.3 Verify session timeout works
  - [ ] 7.2.4 Test with HTTPS

- [ ] 7.3 Testing
  - [ ] 7.3.1 Test login flow on production
  - [ ] 7.3.2 Test logout on production
  - [ ] 7.3.3 Test session persistence
  - [ ] 7.3.4 Test error handling
  - [ ] 7.3.5 Test mobile responsiveness

- [ ] 7.4 Documentation
  - [ ] 7.4.1 Update README with auth info
  - [ ] 7.4.2 Create user guide
  - [ ] 7.4.3 Create admin guide
  - [ ] 7.4.4 Document troubleshooting

---

## Phase 8: Future Enhancements 💡 FUTURE

- [ ] 8.1 Multi-factor authentication (MFA)
- [ ] 8.2 Microsoft OAuth integration
- [ ] 8.3 GitHub OAuth integration
- [ ] 8.4 Email/password authentication
- [ ] 8.5 Password reset functionality
- [ ] 8.6 Email verification
- [ ] 8.7 Remember me functionality
- [ ] 8.8 Login history per user
- [ ] 8.9 Security notifications
- [ ] 8.10 GDPR compliance features

---

## Current Sprint: Phase 5 Security & Polish

### This Week (Priority Order)
1. **Session Timeout** (Task 5.1) - 2 hours
2. **HTTP/HTTPS Support** (Task 5.4) - 1 hour
3. **CSRF Protection** (Task 5.2) - 1 hour
4. **Rate Limiting** (Task 5.3) - 2 hours

### Next Week
5. **User Profile Page** (Task 5.5) - 3 hours
6. **Account Deletion** (Task 5.6) - 2 hours
7. **Auth Logging** (Task 5.10-5.11) - 3 hours

---

## Dependencies

### External
- Google Cloud Console (configured ✅)
- Google OAuth 2.0 API (active ✅)
- Streamlit Cloud (for production)

### Internal
- SQLite database (edulytix.db) ✅
- utils/auth.py module ✅
- config_secrets.py ✅

### Python Packages
- google-auth==2.27.0 ✅
- google-auth-oauthlib==1.2.0 ✅
- google-auth-httplib2==0.2.0 ✅
- streamlit ✅

---

## Testing Checklist

### Functional Tests
- [x] Sign in with Google
- [x] User profile saved to database
- [x] Session persists across pages
- [x] Logout works
- [x] Unauthenticated access works
- [x] Profile picture loads
- [x] Error messages display
- [x] Users table hidden
- [x] Admin role works
- [ ] Session timeout works
- [ ] CSRF protection works
- [ ] Rate limiting works
- [ ] HTTP and HTTPS both work
- [ ] Token refresh works
- [ ] Account deletion works

### Security Tests
- [x] Client secret not exposed
- [x] Session data secure
- [ ] CSRF attacks prevented
- [ ] Rate limiting prevents brute force
- [ ] Session timeout enforced
- [ ] Tokens refreshed properly

### Performance Tests
- [x] Login < 5 seconds
- [x] Profile picture < 1 second
- [x] No impact on unauthenticated users
- [ ] Database queries optimized

---

## Notes

### Known Issues
1. OAUTHLIB_INSECURE_TRANSPORT enabled (dev only)
2. CSRF protection disabled (temporary)
3. No session timeout
4. No rate limiting
5. No token refresh

### Technical Debt
1. Need to add comprehensive error logging
2. Need to add unit tests
3. Need to add integration tests
4. Need to document API functions

---

**Progress**: 45/80 tasks complete (56%)  
**Next Milestone**: Complete Phase 5 (Security & Polish)  
**Target Date**: End of week
