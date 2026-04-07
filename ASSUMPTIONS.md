# Assumptions

## Authentication Model
- Uses Django's AbstractBaseUser + PermissionsMixin for compatibility
- `is_staff` is always False — the project does not use Django admin
- `create_superuser()` creates a site manager, not a Django superuser in the traditional sense
- `is_superuser` is always False — authorization is handled via `is_site_manager` and `CircleMembership.role`
- This is intentional: the project uses its own role system, not Django's permission framework

## Active Circle Persistence
- Stored as ForeignKey on User model
- SET_NULL on circle deletion
- Cleared when user is removed from circle or deactivates account

## Account Deactivation
- Sets `is_active = False`
- Deactivates all circle memberships
- Clears active_circle
- Logs user out
- User data is retained for referential integrity (events created by them, signup history)
- Reactivation would require direct database intervention (not exposed in V1 UI)

## Invitation Links
- Single-use (marked used + deactivated on acceptance)
- 7-day expiry
- Token is a random UUID
- Acceptance is race-safe (SELECT FOR UPDATE in transaction)

## Event Visibility
- Published events: visible to all circle members
- Unpublished (draft) events: visible only to circle admins and site managers
- Normal members cannot access draft events by direct URL or ID
- Normal members cannot sign up for unpublished events

## Last Admin Protection
- A circle must always have at least one active admin
- Both demote and remove operations check this constraint
- If the target is the last admin, the operation is rejected with a clear error
- Site managers are NOT exempt from this rule to prevent accidental orphaning

## Rate Limiting
- Login attempts are rate-limited per IP+email combination
- Default: 10 attempts per 5-minute window
- Uses Django's in-memory cache (LocMemCache)
- Successful login clears the counter

## Pagination
- All list endpoints support `?page=1&per_page=50` query parameters
- Default page size: 50, maximum: 100
- Response includes `pagination` object with total, page, per_page, total_pages
