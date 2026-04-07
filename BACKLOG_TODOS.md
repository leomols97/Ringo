# Backlog

## Important — Should be done before public launch

### Frontend pagination controls
- Backend returns `pagination` on all list endpoints
- Frontend currently does not render page controls
- Lists are capped at 50 items which is sufficient for V1 usage
- Proper prev/next pagination UI is needed before any circle exceeds ~50 members/events
- **Priority: HIGH for post-V1**

### Cookie security for production
- `SESSION_COOKIE_SAMESITE` and `CSRF_COOKIE_SAMESITE` are `None` for the current reverse-proxy setup
- Should be `Lax` when frontend and backend share an origin in production
- `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` are `True` — correct for HTTPS but blocks local HTTP testing without override
- **Priority: HIGH before production deployment**

### SECURE_PROXY_SSL_HEADER
- Currently commented out — Django cannot detect HTTPS through the proxy
- Should be re-enabled with tested reverse-proxy configuration
- **Priority: MEDIUM**

## Nice to have — Not blocking V1

### Email integration
- Invitation links: send via email instead of copy-paste only
- Signup approval/rejection notifications
- Email verification on registration
- Password reset flow

### Background cleanup
- Periodic cleanup of expired invite links (management command or cron)
- Periodic cleanup of stale Django sessions

### Accessibility
- Full ARIA audit for screen readers
- Skip-to-content link
- Focus management on dialog open/close

### Production infrastructure
- Switch LocMemCache to Redis for rate limiting (required for multi-worker)
- Health check endpoint
- Whitenoise for static file serving
- Structured logging (JSON format)

### Testing
- Add model-layer unit tests
- Add E2E tests with Playwright
- CI integration

### Documentation
- API endpoint reference
- Deployment guide
