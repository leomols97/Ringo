# Backlog TODOs for Copilot

## HIGH Priority

### Input Validation Hardening
- TODO(COPILOT): Add comprehensive email format validation beyond Django's basic EmailField check
- TODO(COPILOT): Add password strength requirements (min length, complexity rules)
- TODO(COPILOT): Validate slug format on circle creation (alphanumeric + hyphens only)
- TODO(COPILOT): Add rate limiting on login attempts to prevent brute force

### Concurrency & Edge Cases
- TODO(COPILOT): Add optimistic locking for simultaneous admin actions (e.g., two admins removing each other)
- TODO(COPILOT): Handle race condition in invite acceptance (two users accepting same invite simultaneously)
- TODO(COPILOT): Ensure atomicity in member removal + active_circle cleanup

### Account Deletion Refinement
- TODO(COPILOT): Implement full account deletion (not just deactivation) with referential cleanup
- TODO(COPILOT): Handle orphaned memberships, events, and signups when user account is deleted
- TODO(COPILOT): Add confirmation email before account deletion in future

## MEDIUM Priority

### Background Cleanup
- TODO(COPILOT): Add background task to clean up expired invite links periodically
- TODO(COPILOT): Add background task to clean up stale sessions

### Error Handling
- TODO(COPILOT): Implement structured error responses with error codes
- TODO(COPILOT): Add more specific error messages for edge cases (e.g., circle at member capacity)
- TODO(COPILOT): Add request validation middleware for JSON body parsing

### Admin Enhancements
- TODO(COPILOT): Add filtering and sorting for member lists
- TODO(COPILOT): Add filtering and sorting for event lists
- TODO(COPILOT): Add search functionality for site manager user listing
- TODO(COPILOT): Add pagination for large lists (members, events, invites)

### Performance
- TODO(COPILOT): Add database indexes for frequently queried fields
- TODO(COPILOT): Optimize N+1 queries in serialization functions
- TODO(COPILOT): Add response caching for read-heavy endpoints

## LOW Priority

### Future Integrations
- TODO(COPILOT): Add email sending for invitation links
- TODO(COPILOT): Add email notifications for signup approval/rejection
- TODO(COPILOT): Add push notifications for new events
- TODO(COPILOT): Add email verification on registration

### Accessibility
- TODO(COPILOT): Audit all interactive elements for keyboard navigation
- TODO(COPILOT): Add ARIA labels to dynamic content
- TODO(COPILOT): Test with screen readers

### Production Hardening
- TODO(COPILOT): Re-enable SECURE_PROXY_SSL_HEADER with proper proxy config
- TODO(COPILOT): Set SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE to True
- TODO(COPILOT): Restrict ALLOWED_HOSTS to specific domains
- TODO(COPILOT): Add proper logging configuration
- TODO(COPILOT): Add health check endpoint
- TODO(COPILOT): Configure static file serving for production (whitenoise or CDN)

### Testing
- TODO(COPILOT): Add unit tests for models
- TODO(COPILOT): Add integration tests for API endpoints
- TODO(COPILOT): Add E2E tests with Playwright
- TODO(COPILOT): Add test fixtures and factories

### Documentation
- TODO(COPILOT): Add API endpoint documentation
- TODO(COPILOT): Add contributing guide
- TODO(COPILOT): Add deployment guide for production
