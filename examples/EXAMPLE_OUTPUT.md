# Example: Branded Prompt Output

This is an example of what a generated prompt looks like with branding footer.

---

# FEATURE Plan

**Summary**: Add user authentication with OAuth2 and session management

## Objectives
- Implement OAuth2 authentication flow with Google and GitHub providers
- Add JWT-based session management with secure token storage
- Create user profile management interface with update capabilities
- Implement email verification for new accounts

## Risks & Unknowns
- Third-party OAuth provider availability and rate limits
- Token refresh strategy complexity with multiple providers
- Session persistence across device types
- GDPR compliance requirements for user data storage

## Recommended Milestones
1. Set up OAuth2 integration with Google provider
2. Implement JWT token generation and validation
3. Create user profile database schema and API endpoints
4. Build frontend login/signup UI components
5. Add GitHub OAuth provider as second option
6. Implement email verification flow

## Technical Approach
Implement a stateless authentication system using OAuth2 for third-party login and JWT tokens for session management. Use industry-standard libraries (OAuth.js, jsonwebtoken) to reduce security vulnerabilities. Store minimal user data (email, profile picture, OAuth provider) and implement token rotation for enhanced security.

## Security Considerations
- Use HTTPS for all authentication endpoints
- Implement CSRF protection on OAuth callback routes
- Store JWTs in httpOnly cookies to prevent XSS attacks
- Add rate limiting on login attempts (5 per minute per IP)
- Hash and salt any locally stored credentials
- Implement account lockout after repeated failed attempts

## Database Schema
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  oauth_provider VARCHAR(50) NOT NULL,
  oauth_provider_id VARCHAR(255) NOT NULL,
  profile_picture_url TEXT,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  refresh_token TEXT NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  ip_address VARCHAR(45),
  user_agent TEXT
);
```

## Testing Strategy
- Unit tests for JWT token generation/validation logic
- Integration tests for OAuth callback handling
- E2E tests for complete login/signup flow
- Security tests for token expiration and refresh
- Load tests for concurrent login attempts

## Acceptance Criteria
- [ ] Users can sign in with Google OAuth2
- [ ] Users can sign in with GitHub OAuth2
- [ ] Sessions persist across browser restarts for 7 days
- [ ] Users receive email verification on signup
- [ ] Users can view and edit their profile information
- [ ] Invalid tokens return 401 Unauthorized error
- [ ] Rate limiting blocks excessive login attempts
- [ ] All authentication endpoints use HTTPS
- [ ] CSRF protection implemented on OAuth callbacks
- [ ] Token refresh works seamlessly before expiration

## Original Brief
> Add user authentication with OAuth2 and session management

_Suggested Story ID_: US-3.4

---

🎤 **Generated with [lazy-ptt-enhancer](https://github.com/therouxe/lazy-ptt-enhancer)**
Created by [@therouxe](https://github.com/therouxe) | Powered by Whisper + OpenAI
[⭐ Star on GitHub](https://github.com/therouxe/lazy-ptt-enhancer) | [📖 Documentation](https://github.com/therouxe/lazy-ptt-enhancer#readme) | [🐛 Report Issues](https://github.com/therouxe/lazy-ptt-enhancer/issues)
