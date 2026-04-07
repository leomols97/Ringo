# Circles Platform PRD

## Data Model
- User: email, first_name, last_name, phone, is_site_manager, active_circle
- Circle: name, slug, description, address
- Event: circle, title, description, location, start/end datetime, published (bool), visibility (PUBLIC/PRIVATE)
- EventSignup: event, user, status (PENDING/APPROVED/REJECTED)
- CircleMembership: user, circle, role (MEMBER/CIRCLE_ADMIN), active
- CircleInvite: token, circle, expires_at, used_at, is_active

## Implemented
- Auth: register, login, logout, session persistence, rate limiting
- Profile: read/update (first_name, last_name, email, phone), circles list, deactivation with last-admin safety
- Circle: CRUD with address+description, member management, invites (single-use, race-safe)
- Events: CRUD with published/unpublished + PUBLIC/PRIVATE visibility, admin approval workflow
- Dashboard: recent signups + upcoming events from all circles
- Public events: any authenticated user can view and sign up
- Private events: circle members only
- 25 Django tests covering all critical flows
