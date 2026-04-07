# Circles - Multi-Circle Community Platform PRD

## Original Problem Statement
Build a V1 of a multi-circle community platform. React frontend, Django backend, PostgreSQL database. Single page application with multiple circles, role-based access control, event management, and invitation system.

## Architecture
- **Frontend**: React SPA on port 3000 (Tailwind CSS, Shadcn/UI)
- **Backend**: Django 5.2 served via uvicorn ASGI on port 8001
- **Database**: PostgreSQL 15 (circles_db)
- **Auth**: Django session-based + CSRF tokens

## User Personas
1. **Normal User**: Joins circles via invites, views events, requests signups
2. **Circle Admin**: Manages members, invites, events, approves signups within their circles
3. **Site Manager**: Global admin, creates/manages all circles, platform overview

## Core Requirements (Static)
- Multi-circle membership with per-circle roles
- Active circle selector with instant switching
- Role-view dropdown (User/Admin/Site Manager)
- Invitation links (single-use, 7-day expiry)
- Event CRUD with signup approval flow
- Profile management with account deactivation

## What's Been Implemented (April 2026)
- Custom User model (UUID, email-based auth)
- Session-based auth with CSRF (SameSite=None for cross-origin proxy)
- Circle CRUD (site manager), Circle update (admin)
- CircleMembership with MEMBER/CIRCLE_ADMIN roles
- Invitation generation, acceptance, deactivation
- Member promotion/demotion/removal
- Event CRUD with published/draft support
- Event signup with PENDING/APPROVED/REJECTED flow
- Role-view dropdown with dynamic view switching
- Circle selector in navbar
- 14+ frontend pages (Home, Auth, Dashboard, Profile, MyCircles, EventDetail, Admin suite, Site Manager suite)
- Swiss/high-contrast design (Outfit + IBM Plex Sans fonts)
- Polished empty states, loading states, error states

## Prioritized Backlog
### P0 (Critical for V1 completion)
- None remaining - all V1 scope implemented

### P1 (Recommended next)
- Pagination for large member/event lists
- Better error taxonomy and user feedback
- Password reset flow
- Email verification

### P2 (Future enhancements)
- Email notifications for invites and signups
- Search/filter for members and events
- Audit logging
- Advanced event types (recurring, multi-day)
- Public API

## Next Tasks
1. Add pagination for member/event lists
2. Implement password reset flow
3. Add email notification system
4. Production deployment hardening (HTTPS cookies, restricted ALLOWED_HOSTS)
