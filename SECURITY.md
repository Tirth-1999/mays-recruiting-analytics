# Security Policy

## Supported Versions

We actively support the following versions of the Mays Analytics Platform:

| Version | Supported          |
| ------- | ------------------ |
| 7.5.x   | :white_check_mark: |
| 7.1.x   | :white_check_mark: |
| 7.0.x   | :white_check_mark: |
| < 7.0   | :x:                |

## Reporting a Vulnerability

The security of the Mays Analytics Platform is important to us. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **Do NOT create a public GitHub issue** for security vulnerabilities
2. **Use the in-app feedback form** in the Documentation & Help section of the platform
3. **Mark your report as "Security Issue"** in the feedback type
4. **Include detailed information** about the vulnerability

### What to Include

Please include the following information in your security report:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** of the vulnerability
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours of receiving your report
- **Assessment**: Within 5 business days, we will assess the vulnerability
- **Resolution**: Critical vulnerabilities will be addressed within 7 days
- **Disclosure**: We will coordinate with you on responsible disclosure

### Security Measures

The Mays Analytics Platform implements several security measures:

#### Authentication & Authorization
- **Google OAuth 2.0** for secure user authentication
- **Role-based access control** (Admin and User roles)
- **Session management** with secure token handling
- **OAuth state validation** to prevent CSRF attacks

#### Data Protection
- **Input validation** on all user inputs
- **SQL injection prevention** through parameterized queries
- **XSS protection** through proper output encoding
- **Data privacy compliance** with automatic cleanup

#### Infrastructure Security
- **HTTPS enforcement** for all communications
- **Secure headers** implementation
- **Rate limiting** on API endpoints
- **Error message sanitization** to prevent information disclosure

#### Database Security
- **SQLite database** with proper access controls
- **Data encryption** for sensitive information
- **Regular backups** with secure storage
- **Connection pooling** with timeout management

### Security Best Practices for Users

#### For Administrators
- Use strong, unique passwords for your Google account
- Enable two-factor authentication on your Google account
- Regularly review user access and permissions
- Monitor application logs for suspicious activity
- Keep the platform updated to the latest version

#### For Regular Users
- Use secure authentication through Google OAuth
- Do not share your login credentials
- Report suspicious activity immediately
- Log out when finished using the platform
- Use the platform only from trusted networks

### Known Security Considerations

#### Current Limitations
- The platform is designed for internal use within Texas A&M University
- Database files should be protected with appropriate file system permissions
- Streamlit Cloud deployment requires proper environment variable management

#### Planned Improvements
- Enhanced audit logging
- Additional rate limiting measures
- Improved error handling and logging
- Regular security assessments

### Vulnerability Disclosure Policy

We follow responsible disclosure practices:

1. **Private Reporting**: Security issues should be reported privately first
2. **Coordinated Disclosure**: We will work with reporters on disclosure timing
3. **Credit**: We will acknowledge security researchers who report valid vulnerabilities
4. **No Legal Action**: We will not pursue legal action against researchers who follow this policy

### Security Updates

Security updates will be:
- **Prioritized** over feature development
- **Tested thoroughly** before deployment
- **Documented** in the changelog
- **Communicated** to all users through appropriate channels

### Contact Information

For security-related questions or concerns:
- **Primary**: Use the in-app feedback form (mark as "Security Issue")
- **Alternative**: Create a private GitHub issue if the platform is inaccessible

### Acknowledgments

We thank the security research community for helping keep the Mays Analytics Platform secure. We appreciate responsible disclosure and will acknowledge contributors who help improve our security posture.

---

**Last Updated**: February 3, 2026  
**Version**: 1.0  
**Next Review**: May 3, 2026