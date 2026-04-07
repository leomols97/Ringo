# Assumptions

## Account Removal
- "Delete account" performs permanent anonymization: email randomized, name set to "Deleted User", phone cleared, password made unusable
- The database row is kept with is_active=False for referential integrity (events/signups the user created still reference a valid row)
- All memberships are deactivated
- Blocked if user is last admin of any circle — must transfer admin rights first
- This is genuine removal: the user cannot log in, their identity is erased, the email is freed up

## Event Visibility
- Two independent dimensions: published (draft vs live) and visibility (PUBLIC vs PRIVATE)
- Draft events are invisible to non-admins regardless of visibility
- PUBLIC published events: any authenticated user can view and sign up (no membership needed)
- PRIVATE published events: only circle members can view and sign up
- Admin approval workflow applies to all signups regardless of visibility

## User Management Scope
- Normal users: CRUD own profile only
- Circle admins: manage members within their own circles only — no global user powers
- Site managers: view/update any user (name, phone, active status), full circle CRUD, platform overview

## Circle Profiles
- Circles have name, slug, description, and address
- Members can view the full circle profile
- Circle admins can edit name, description, address
- Site managers have full CRUD

## Dashboard
- Recent signups: last 10 signup requests by the current user, across all circles
- Circle events: next 20 upcoming published events from all circles the user belongs to
- Both sections show circle name for context
