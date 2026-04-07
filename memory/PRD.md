# Circles - Multi-Circle Community Platform PRD

## Problem Statement
Multi-circle community platform with React frontend, Django backend, PostgreSQL.

## Architecture
- Frontend: React SPA (port 3000), Tailwind CSS, Shadcn/UI
- Backend: Django 5.2 ASGI via uvicorn (port 8001)
- Database: PostgreSQL 15

## What's Implemented (V1 Hardened - April 2026)
### Core Features
- Custom User model (UUID, email auth, PermissionsMixin)
- Session-based auth with CSRF, login rate limiting
- Multi-circle membership with per-circle roles
- Active circle selector with instant switching
- Role-view dropdown (User/Admin/Site Manager)
- Circle CRUD (site manager), circle update (admin)
- Invitation links (single-use, 7-day expiry, race-safe)
- Member management (promote/demote/remove with last-admin protection)
- Event CRUD with published/draft visibility control
- Event signup with PENDING/APPROVED/REJECTED flow
- Profile management with safe account deactivation

### V1 Hardening
- Environment-driven settings (no hardcoded secrets)
- Password strength validation (8+ chars, letter + digit)
- Email format validation, slug format validation
- Login rate limiting (10/5min per IP+email)
- Transaction-safe invite acceptance (SELECT FOR UPDATE)
- Atomic member operations with active_circle cleanup
- Last-admin protection on both demote and remove
- Unpublished events hidden from normal users
- Database indexes on all frequently queried columns
- N+1 query elimination
- Structured error codes in API responses
- Search/filter/sort on admin member lists
- Published/draft filter on admin event lists
- User search for site managers
- Pagination on all list endpoints

## Remaining Backlog
- P1: Frontend pagination controls, toast notifications
- P2: Email notifications, background cleanup tasks
- P3: Full ARIA audit, production hardening (Redis cache, health checks)
