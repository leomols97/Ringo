# Circles — Multi-Circle Community Platform PRD

## Architecture
- Frontend: React SPA (port 3000), Tailwind CSS, Shadcn/UI
- Backend: Django 5.2 ASGI via uvicorn (port 8001)
- Database: PostgreSQL 15

## Implemented — V1 Final
- Custom User model (UUID, email auth, PermissionsMixin for Django compat)
- Site manager role with clean create_site_manager semantics
- Session auth with CSRF, login rate limiting (10/5min)
- Password (8+ chars, letter + digit), email format, slug format validation
- Multi-circle membership with per-circle MEMBER/CIRCLE_ADMIN roles
- Active circle selector (persisted FK, instant switching)
- Role-view dropdown (User/Admin/Site Manager)
- Circle CRUD (site manager), circle update (admin)
- Invitation links (single-use, 7-day expiry, race-safe SELECT FOR UPDATE)
- Member management (promote/demote/remove, all with last-admin protection)
- Event CRUD with published/draft visibility enforcement
- Event signup with PENDING/APPROVED/REJECTED flow
- Profile management with safe deactivation (blocks if last admin)
- Account deactivation clears all memberships atomically
- All list endpoints paginated with structured pagination response
- Search/filter/sort on admin lists
- Toast notifications (sonner) for all mutating actions
- DB indexes on all frequently queried columns
- N+1 query elimination
- 23 Django tests covering all critical business rules
- Structured error codes in all API responses
- .env.example with documented configuration

## Remaining Backlog (Honest)
- P1: Frontend pagination controls (backend ready, UI capped at 50)
- P1: Cookie SameSite settings need adjustment for production (currently None for proxy)
- P2: Email notifications, password reset
- P2: Background cleanup of expired invites
- P3: Full ARIA audit, Redis cache for rate limiting, health check endpoint
