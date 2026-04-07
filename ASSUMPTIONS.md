# Assumptions

## Event Visibility Model
Two independent dimensions:
- **published** (bool): controls whether non-admins can see the event at all. Draft events (published=false) are invisible to normal users.
- **visibility** (PUBLIC/PRIVATE): controls who can sign up. PUBLIC = any authenticated user. PRIVATE = circle members only. This only applies to published events.

Both are enforced on the backend, not just the UI.

## Account Deactivation
- Blocked if user is the last admin of any circle
- When allowed: deactivates all memberships, clears active_circle, sets is_active=False, logs out
- User data retained for referential integrity

## Invitation Links
- Single-use, 7-day expiry, race-safe (SELECT FOR UPDATE)
- After acceptance, invite is both used and deactivated

## Auth Model
- `manage.py createsuperuser` creates a site manager (is_site_manager=True, is_superuser=False)
- Django admin is not used; is_staff is always False
- Authorization via is_site_manager (global) and CircleMembership.role (per-circle)

## Dashboard
- Shows user's recent signups (last 10) across all circles
- Shows upcoming published events from all circles the user belongs to (next 20)
- Both sections show circle name for context

## Phone Field
- Optional, max 30 chars, stored as-is (no format validation beyond length)
- Editable via profile PATCH

## Circle Address
- Optional, max 500 chars
- Editable by circle admins and site managers via circle PATCH
- Included in circle create payload
