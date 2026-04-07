# Assumptions

## Auth Model
- `manage.py createsuperuser` creates a **site manager**, not a Django superuser
- `is_superuser` and `is_staff` are always False — Django admin and permission framework are unused
- Authorization is entirely through `is_site_manager` (global) and `CircleMembership.role` (per-circle)
- `PermissionsMixin` is included solely for `login()` compatibility; its fields carry no meaning

## Active Circle Persistence
- Stored as ForeignKey on User model, SET_NULL on circle deletion
- Cleared on membership removal or account deactivation

## Account Deactivation
- **Blocked** if the user is the last active admin of any circle
- When allowed: sets `is_active=False`, deactivates all memberships, clears active_circle, logs out
- User data is retained for referential integrity
- Reactivation requires direct database intervention (not exposed in V1)

## Invitation Links
- Single-use: marked used AND deactivated on acceptance
- 7-day expiry
- Race-safe: acceptance uses `SELECT FOR UPDATE` inside a transaction
- After use, second acceptance gets "invitation has been deactivated" (since is_active is checked first)

## Event Visibility
- Published events: visible to all circle members
- Unpublished (draft) events: visible only to circle admins and site managers
- Both the detail endpoint and signup endpoint enforce this consistently

## Last Admin Protection
- Every circle must keep at least one active admin
- Enforced on: demote, remove, and account deactivation
- No exception for site managers — preventing accidental orphaning is the priority

## Rate Limiting
- Per IP+email, configurable via env vars
- Uses Django LocMemCache (in-memory, per-worker)
- Successful login clears the counter

## Pagination
- All list endpoints that can grow (members, events, invites, signups, users, circles) return a `pagination` object
- `?page=1&per_page=50`, max 100 per page
- Frontend does not yet have pagination controls — lists are capped at 50 items (documented in BACKLOG)

## Settings
- `ALLOWED_HOSTS` defaults to `*` only when `DEBUG=true`
- When `DEBUG=false` and `ALLOWED_HOSTS` is empty, Django refuses all requests (fail-fast)
- Cookie security flags (Secure, SameSite=None) are set for the current reverse-proxy environment
