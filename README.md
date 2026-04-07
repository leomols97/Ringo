# Circles - Multi-Circle Community Platform

## Purpose
A multi-circle community platform where users can belong to multiple circles, view circle-specific events, and interact with their communities. Circle administrators manage members, invitations, and events. Site managers oversee the entire platform.

## Stack
- **Frontend**: React (SPA) with Tailwind CSS and Shadcn/UI components
- **Backend**: Django 5.2 (served via ASGI/uvicorn)
- **Database**: PostgreSQL 15
- **Auth**: Django sessions + CSRF (cookie-based)

## Environment Variables

### Backend (`/app/backend/.env`)
| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django secret key for cryptographic signing |
| `FRONTEND_URL` | Frontend origin for CSRF trusted origins |

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
python manage.py makemigrations accounts circles events
python manage.py migrate

# Create first site manager
python manage.py shell -c "
from accounts.models import User
User.objects.create_superuser(email='admin@circles.io', password='admin123', first_name='Site', last_name='Manager')
"

# Frontend
cd /app/frontend
yarn install
yarn start
```

## Migrations
```bash
cd /app/backend
python manage.py makemigrations
python manage.py migrate
```

## Roles
| Role | Scope | Rights |
|------|-------|--------|
| Normal user | Personal | Manage own profile, join circles via invites, view events, request event signups |
| Circle admin | Per-circle | Manage members, invites, events, approve signups for circles where they are admin |
| Site manager | Global | Create/edit/delete circles, view all users, global overview |

## Permissions
- Anonymous: home page, register, login only
- Authenticated: own profile, own circles, active circle events, signup requests
- Circle admin: member management, invite management, event CRUD, signup approval (per-circle)
- Site manager: circle CRUD, user listing, platform overview

## Multi-Circle Behavior
- A user can belong to zero, one, or many circles
- Each membership has a role (MEMBER or CIRCLE_ADMIN)
- Different roles in different circles are supported
- Circle-specific data always reflects the currently active circle

## Active Circle Selection
- Persisted as a ForeignKey on the User model
- Switching is instant (no page reload)
- The circle selector in the navbar shows available circles
- In Admin view, only admin circles are shown in the selector

## Database
- PostgreSQL running locally (localhost:5432)
- Database: `circles_db`, User: `circleapp`
- Database remains movable: change `DATABASES` config in `project/settings.py`
