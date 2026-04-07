# Backlog TODOs

## Completed in V1 Hardening
- [DONE] Environment-driven database, DEBUG, ALLOWED_HOSTS configuration
- [DONE] PermissionsMixin added for Django auth compatibility
- [DONE] Unpublished events hidden from normal users (list, detail, signup)
- [DONE] Last-admin protection on both remove and demote
- [DONE] Race-safe invite acceptance (SELECT FOR UPDATE + transaction)
- [DONE] Atomic member removal with active_circle cleanup
- [DONE] Atomic member demotion
- [DONE] Email format validation
- [DONE] Password strength requirements (8+ chars, letter + digit)
- [DONE] Slug format validation (alphanumeric + hyphens)
- [DONE] Login rate limiting (cache-based)
- [DONE] Account deactivation clears memberships
- [DONE] Database indexes on frequently queried fields
- [DONE] N+1 query elimination (annotate for circle counts, batch signup loading)
- [DONE] Structured error codes in API responses
- [DONE] Member search and sort for admin
- [DONE] Event published/draft filter for admin
- [DONE] User search for site manager
- [DONE] Pagination on all list endpoints

## MEDIUM Priority — Remaining

### Background Cleanup
- TODO(COPILOT): Add periodic cleanup of expired invite links (cron or management command)
- TODO(COPILOT): Add periodic cleanup of stale Django sessions

### UX Improvements
- TODO(COPILOT): Add frontend pagination controls when lists exceed one page
- TODO(COPILOT): Add toast notifications for successful actions (using sonner)
- TODO(COPILOT): Add keyboard shortcuts for common admin actions

### Performance
- TODO(COPILOT): Add response caching for read-heavy endpoints if needed under load

## LOW Priority — Future

### Integrations
- TODO(COPILOT): Email sending for invitation links
- TODO(COPILOT): Email notifications for signup approval/rejection
- TODO(COPILOT): Email verification on registration

### Accessibility
- TODO(COPILOT): Full ARIA audit for screen readers
- TODO(COPILOT): Skip-to-content link

### Production Hardening
- TODO(COPILOT): Re-enable SECURE_PROXY_SSL_HEADER with proper reverse proxy config
- TODO(COPILOT): Switch to Redis/Memcached for rate limiting cache in production
- TODO(COPILOT): Add health check endpoint
- TODO(COPILOT): Configure whitenoise for static file serving

### Testing
- TODO(COPILOT): Add unit tests for model layer
- TODO(COPILOT): Add integration tests for critical API flows
- TODO(COPILOT): Add E2E tests with Playwright

### Documentation
- TODO(COPILOT): API endpoint reference documentation
- TODO(COPILOT): Deployment guide for production environments
