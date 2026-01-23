# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 4.0.x   | :white_check_mark: |
| 3.0.x   | :white_check_mark: |
| 2.x.x   | :x:                |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

We take the security of the Mays Analytics Platform seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Primary Contact**: [Your Email]
- **Secondary Contact**: [Manager Email]

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of issue (e.g., SQL injection, cross-site scripting, data exposure)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Assessment**: We will assess the vulnerability and determine its impact and severity
- **Fix Development**: We will work on a fix and keep you informed of progress
- **Disclosure**: Once a fix is available, we will coordinate disclosure with you
- **Credit**: We will credit you in our security advisory (unless you prefer to remain anonymous)

## Security Best Practices

### For Administrators

1. **Database Security**
   - Never commit `edulytix.db` to version control
   - Use strong passwords for database access
   - Regularly backup the database
   - Restrict database file permissions: `chmod 600 edulytix.db`

2. **Data Protection**
   - Keep dataset files (`Dataset/*.xlsx`) secure and private
   - Do not share raw data files publicly
   - Ensure `.gitignore` properly excludes sensitive files

3. **Environment Variables**
   - Store sensitive configuration in `.env` files
   - Never commit `.env` files to version control
   - Use environment-specific configurations

4. **Access Control**
   - Limit access to the production server
   - Use SSH keys instead of passwords
   - Implement IP whitelisting if possible
   - Regularly review user access

5. **Updates**
   - Keep Python and all dependencies up to date
   - Monitor security advisories for Streamlit and other packages
   - Apply security patches promptly

### For Developers

1. **Code Security**
   - Validate all user inputs
   - Use parameterized queries (already implemented)
   - Avoid exposing sensitive information in error messages
   - Follow secure coding practices

2. **Dependencies**
   - Regularly update `requirements.txt`
   - Use `pip-audit` to check for vulnerable packages
   - Review dependency changes before updating

3. **Testing**
   - Test security features before deployment
   - Perform code reviews for security issues
   - Use static analysis tools

## Known Security Considerations

### Current Implementation

1. **Database Access**
   - SQLite database with read-only access for dashboard
   - No user authentication (designed for internal use)
   - File-based database (not exposed to network)

2. **Data Privacy**
   - Student data is aggregated (no PII)
   - Marketing spend data is internal only
   - No external API exposure

3. **Deployment**
   - Designed for internal network deployment
   - Not intended for public internet exposure
   - Streamlit default security settings apply

### Recommendations for Production

If deploying to production with external access:

1. **Add Authentication**
   ```python
   # Consider adding Streamlit authentication
   # Or deploy behind SSO/VPN
   ```

2. **Use HTTPS**
   - Deploy behind reverse proxy (nginx/Apache)
   - Use SSL/TLS certificates
   - Enable HSTS headers

3. **Network Security**
   - Deploy in private network/VPN
   - Use firewall rules
   - Implement rate limiting

4. **Monitoring**
   - Enable access logging
   - Monitor for suspicious activity
   - Set up alerts for anomalies

## Security Updates

Security updates will be released as patch versions (e.g., 4.0.1) and documented in [CHANGELOG.md](CHANGELOG.md).

Subscribe to repository releases to be notified of security updates:
- Watch → Custom → Releases

## Compliance

This platform handles educational data. Ensure compliance with:
- **FERPA** (Family Educational Rights and Privacy Act)
- **University Data Policies**
- **State and Federal Regulations**

## Contact

For security concerns or questions:
- **Email**: [Your Email]
- **GitHub**: [@Tirth-1999](https://github.com/Tirth-1999)

---

**Last Updated**: January 23, 2026  
**Version**: 4.0
