# Circles - Multi-Circle Community Platform

## Purpose
A multi-circle community platform where users belong to multiple circles, view circle-specific events, and interact with their communities. Circle administrators manage members, invitations, and events. Site managers oversee the entire platform.

## Stack
- **Frontend**: React SPA with Tailwind CSS and Shadcn/UI
- **Backend**: Django 5.2 (ASGI via uvicorn)
- **Database**: PostgreSQL 15

## Environment Variables

### Backend (`/app/backend/.env`)
| Variable | Description | Required |
|----------|-------------|----------|
| `DJANGO_SECRET_KEY` | Cryptographic signing key | Yes |
| `DJANGO_DEBUG` | Enable debug mode (`true`/`false`) | No (default: `false`) |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames | No (default: `*`) |
| `PG_NAME` | PostgreSQL database name | Yes |
| `PG_USER` | PostgreSQL user | Yes |
| `PG_PASSWORD` | PostgreSQL password | Yes |
| `PG_HOST` | PostgreSQL host | No (default: `localhost`) |
| `PG_PORT` | PostgreSQL port | No (default: `5432`) |
| `FRONTEND_URL` | Frontend origin for CSRF | No |
| `LOGIN_RATE_LIMIT_MAX` | Max login attempts per window | No (default: `10`) |
| `LOGIN_RATE_LIMIT_WINDOW` | Rate limit window in seconds | No (default: `300`) |

### Frontend (`/app/frontend/.env`)
| Variable | Description |
|----------|-------------|
| `REACT_APP_BACKEND_URL` | Backend API base URL |

## Local Setup
```bash
# PostgreSQL
pg_ctlcluster 15 main start
sudo -u postgres psql -c "CREATE USER circleapp WITH PASSWORD 'circleapp123' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE circles_db OWNER circleapp;"

# Backend
cd /app/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py shell -c "
from accounts.models import User
User.objects.create_superuser(email='admin@circles.io', password='admin123', first_name='Site', last_name='Manager')
"

# Frontend
cd /app/frontend
yarn install && yarn start
```

## Roles
| Role | Scope | Rights |
|------|-------|--------|
| Normal user | Personal | Own profile, join circles via invites, view published events, request signups |
| Circle admin | Per-circle | Manage members, invites, events (incl. unpublished), approve signups |
| Site manager | Global | Create/edit/delete any circle, view all users, platform overview |

## Permissions
- Anonymous: home page, register, login only
- Normal user: published events only, cannot access unpublished events by URL
- Circle admin: full event lifecycle including drafts, member/invite management
- Site manager: all circle CRUD, user listing with search, global overview

## Multi-Circle Behavior
- Users can belong to zero or many circles with independent roles per circle
- Active circle persisted as FK on User model
- Circle selector shows in navbar; switching is instant (no page reload)

## Security
- Session-based auth with CSRF tokens (SameSite=None for cross-origin proxy)
- Login rate limiting (10 attempts per 5-minute window per IP+email)
- Password requirements: min 8 chars, at least one letter and one digit
- Email validation: format check on registration and profile update
- Slug validation: lowercase alphanumeric with hyphens only
- Transaction safety: invite acceptance uses SELECT FOR UPDATE to prevent races
- Atomic operations: member removal + active_circle cleanup is transactional
- Last-admin protection: cannot remove or demote the last admin of a circle
- Account deactivation clears all memberships and active circle

## Database
- PostgreSQL running locally (configurable via PG_* env vars)
- Indexes on all frequently queried columns
- N+1 queries eliminated via annotate/prefetch
