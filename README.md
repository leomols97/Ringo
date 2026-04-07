# Circles — Multi-Circle Community Platform

## Stack
- **Frontend**: React SPA, Tailwind CSS, Shadcn/UI
- **Backend**: Django 5.2 (ASGI via uvicorn)
- **Database**: PostgreSQL 15

## Data Model
- **User**: email, first_name, last_name, phone, is_active, is_site_manager, active_circle
- **Circle**: name, slug, description, address
- **Event**: circle, title, description, location, start/end datetime, published (draft/live), visibility (PUBLIC/PRIVATE)
- **EventSignup**: event, user, status (PENDING/APPROVED/REJECTED)

## Core Features
- **Auth**: register, login, logout, session persistence, rate limiting
- **Profile**: read/update (first name, last name, email, phone), view joined circles, **delete account** (anonymizes PII, erases personal data permanently)
- **Circle profiles**: name, address, description — members can view, admins can edit, site managers CRUD
- **Invitations**: unique temporary links, single-use, race-safe acceptance
- **Member management**: list, promote, demote, remove — with last-admin protection
- **Events**: CRUD with published/draft + PUBLIC/PRIVATE visibility
- **Public events page**: browse and sign up for public events without circle membership
- **Private events**: require circle membership to sign up
- **Dashboard**: recent signups + upcoming events from all joined circles
- **Site manager**: platform overview, user search/view/edit/deactivate, circle CRUD
- **Pagination**: all list endpoints paginated, frontend prev/next controls

## Account Deletion
- Endpoint: `POST /api/private/profile/delete/`
- Anonymizes email to `deleted-xxx@removed.local`, sets name to "Deleted User", clears phone
- Sets password unusable, deactivates all memberships, sets is_active=False
- Blocked if user is last admin of any circle
- Row kept for referential integrity; all PII erased

## Event Visibility
- **published=false** (draft): invisible to non-admins
- **published=true + PRIVATE**: members/admins only
- **published=true + PUBLIC**: any authenticated user can view and sign up
- Public events browseable via `/public-events` page and `GET /api/private/events/public/`

## Setup
```bash
pg_ctlcluster 15 main start
sudo -u postgres createuser -P circleapp
sudo -u postgres createdb -O circleapp circles_db
cd backend && cp .env.example .env && pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
cd ../frontend && yarn install && yarn start
```

## Tests
```bash
cd backend && python manage.py test tests.test_critical
```
28 tests covering: account deletion (anonymization + last-admin block), phone update, circle address CRUD, circle profile viewing, public/private/draft event visibility, public events discovery, last-admin protection, invite single-use, permissions isolation, site manager user management (view/update/deactivate), dashboard data, rate limiting.
