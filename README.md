# Circles — Multi-Circle Community Platform

## Stack
- **Frontend**: React SPA, Tailwind CSS, Shadcn/UI
- **Backend**: Django 5.2 (ASGI via uvicorn)
- **Database**: PostgreSQL 15

## Data Model

### User
`email`, `first_name`, `last_name`, `phone`, `is_active`, `is_site_manager`, `active_circle` (FK)

### Circle
`name`, `slug` (unique), `description`, `address`

### Event
`circle` (FK), `title`, `description`, `location`, `start_datetime`, `end_datetime`, `published` (bool), `visibility` (PUBLIC/PRIVATE), `created_by`

### EventSignup
`event` (FK), `user` (FK), `status` (PENDING/APPROVED/REJECTED), unique on (event, user)

## Event Visibility Rules
- **published=false (draft)**: only circle admins and site managers can see or manage
- **published=true, visibility=PRIVATE**: only circle members can view and sign up
- **published=true, visibility=PUBLIC**: any authenticated user can view and sign up
- Approval workflow applies to all signups regardless of visibility

## Setup
```bash
pg_ctlcluster 15 main start
sudo -u postgres createuser -P circleapp
sudo -u postgres createdb -O circleapp circles_db
cd backend && cp .env.example .env && pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # creates a site manager
cd ../frontend && yarn install && yarn start
```

## Tests
```bash
cd backend && python manage.py test tests.test_critical
```
25 tests: registration, phone update, circle address CRUD, public event signup, private event membership enforcement, draft invisibility, last-admin protection, deactivation safety, invite single-use, permissions isolation, dashboard data, rate limiting.

## Roles
| Role | Scope | Capabilities |
|------|-------|-------------|
| Normal user | Self | Own profile (incl. phone), view circles, view published events, sign up to public events, sign up to private events of own circles |
| Circle admin | Per-circle | Manage members/invites/events (incl. drafts, visibility), approve/reject signups |
| Site manager | Global | CRUD all circles (incl. address), view all users, platform overview |
