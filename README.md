# Circles — Multi-Circle Community Platform

## Purpose
A multi-circle community hub where users belong to multiple circles, view circle-specific events, and interact with their communities. Circle administrators manage members, invitations, and events. Site managers oversee the entire platform.

## Stack
- **Frontend**: React SPA, Tailwind CSS, Shadcn/UI
- **Backend**: Django 5.2 (ASGI via uvicorn)
- **Database**: PostgreSQL 15

## Environment Variables
See `.env.example` for all supported variables with descriptions.

Key variables:
| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Yes | Cryptographic signing key |
| `PG_NAME`, `PG_USER`, `PG_PASSWORD` | Yes | PostgreSQL credentials |
| `DJANGO_DEBUG` | No | `true` for dev (default `false`) |
| `DJANGO_ALLOWED_HOSTS` | Prod only | Comma-separated; empty = `*` in debug, fails in prod |

## Setup

```bash
# PostgreSQL
pg_ctlcluster 15 main start
sudo -u postgres psql -c "CREATE USER circleapp WITH PASSWORD 'circleapp123' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE circles_db OWNER circleapp;"

# Backend
cd backend
cp .env.example .env   # then edit .env with real values
pip install -r requirements.txt
python manage.py migrate

# Create a site manager
python manage.py createsuperuser
# (this creates a site manager, not a Django superuser — see Auth Model below)

# Frontend
cd frontend
yarn install && yarn start
```

## Auth Model

This project uses a custom User model with email as the unique identifier.

- **`is_site_manager`**: The platform-level admin flag. Controls global access.
- **`is_staff`**: Always `False`. Django admin is not used.
- **`is_superuser`**: Always `False`. Django's permission framework is not used.
- **`manage.py createsuperuser`**: Creates a site manager (sets `is_site_manager=True`). The Django naming is kept for CLI compatibility, but internally this calls `create_site_manager()`.

Authorization is handled by the project's own role system:
- Per-circle: `CircleMembership.role` (MEMBER or CIRCLE_ADMIN)
- Global: `User.is_site_manager`

## Roles & Permissions

| Role | Scope | Can do |
|------|-------|--------|
| Normal user | Personal | Own profile, join via invites, view published events, request signups |
| Circle admin | Per-circle | Manage members/invites/events (incl. drafts), approve/reject signups |
| Site manager | Global | All circle CRUD, user listing, platform overview, manage any circle |

**Key restrictions:**
- Normal members cannot see unpublished (draft) events, not even by direct URL
- Normal members cannot sign up for unpublished events
- A circle can never be left with zero active admins (demote, remove, and account deactivation all enforce this)
- Account deactivation is blocked if the user is the last admin of any circle

## Multi-Circle Behavior
- Users can belong to zero or many circles with independent roles per circle
- Active circle persisted as FK on User model; switching is instant
- Role-view dropdown: User / Admin / Site Manager (visibility depends on user's actual roles)

## Security
- Session-based auth with CSRF tokens
- Login rate limiting (configurable, default 10 attempts / 5 min per IP+email)
- Password: min 8 chars, letter + digit required
- Invite acceptance: race-safe (SELECT FOR UPDATE in transaction)
- Member removal: atomic with active_circle cleanup
- Settings: DEBUG, ALLOWED_HOSTS, DB creds all environment-driven

## Tests
```bash
cd backend
python manage.py test tests.test_critical
```
23 tests covering: registration validation, rate limiting, active circle permissions, invite acceptance (success + single-use + expiry), unpublished event invisibility, last-admin protection (demote + remove), account deactivation safety, circle admin isolation, site manager global access.

## Database
PostgreSQL. Configurable via `PG_*` env vars. Indexes on all frequently queried columns. Movable to any PostgreSQL instance by changing env vars.
