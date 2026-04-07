"""
Critical-flow test suite for the Circles platform.
Covers: auth, validation, permissions, visibility, public/private events,
invite safety, last-admin protection, deactivation, dashboard, phone, address.
"""
import uuid
from datetime import timedelta
from django.test import TestCase, TransactionTestCase, Client
from django.utils import timezone
from accounts.models import User
from circles.models import Circle, CircleMembership, CircleInvite
from events.models import Event, EventSignup


def _user(email, password='Testpass1', **kw):
    return User.objects.create_user(email=email, password=password, first_name='T', **kw)

def _circle(slug=None, **kw):
    slug = slug or f'c-{uuid.uuid4().hex[:8]}'
    return Circle.objects.create(name=slug.title(), slug=slug, **kw)

def _login(client, email, password='Testpass1'):
    client.get('/api/private/auth/csrf/')
    csrf = client.cookies.get('csrftoken')
    return client.post('/api/private/auth/login/', data={'email': email, 'password': password},
                        content_type='application/json', HTTP_X_CSRFTOKEN=csrf.value if csrf else '')

def _post(client, url, data=None):
    csrf = client.cookies.get('csrftoken')
    return client.post(url, data=data or {}, content_type='application/json',
                        HTTP_X_CSRFTOKEN=csrf.value if csrf else '')


# ── Registration ────────────────────────────────────────────
class RegistrationTests(TestCase):
    def test_success(self):
        c = Client(); c.get('/api/private/auth/csrf/')
        r = _post(c, '/api/private/auth/register/', {'email': 'n@t.io', 'password': 'Testpass1', 'first_name': 'N'})
        self.assertEqual(r.status_code, 201)

    def test_weak_password(self):
        c = Client(); c.get('/api/private/auth/csrf/')
        r = _post(c, '/api/private/auth/register/', {'email': 'w@t.io', 'password': 'short', 'first_name': 'W'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'weak_password')

    def test_bad_email(self):
        c = Client(); c.get('/api/private/auth/csrf/')
        r = _post(c, '/api/private/auth/register/', {'email': 'nope', 'password': 'Testpass1', 'first_name': 'B'})
        self.assertEqual(r.status_code, 400)


# ── Profile phone field ────────────────────────────────────
class ProfilePhoneTests(TestCase):
    def setUp(self):
        self.u = _user('ph@t.io')

    def test_phone_update(self):
        c = Client(); _login(c, 'ph@t.io')
        csrf = c.cookies['csrftoken'].value
        r = c.patch('/api/private/profile/', data={'phone': '+1 555 0100'},
                     content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['phone'], '+1 555 0100')
        self.u.refresh_from_db()
        self.assertEqual(self.u.phone, '+1 555 0100')

    def test_phone_in_serialization(self):
        c = Client(); _login(c, 'ph@t.io')
        r = c.get('/api/private/auth/me/')
        self.assertIn('phone', r.json()['user'])


# ── Circle address ──────────────────────────────────────────
class CircleAddressTests(TestCase):
    def setUp(self):
        self.sm = _user('sm@t.io', is_site_manager=True)

    def test_create_with_address(self):
        c = Client(); _login(c, 'sm@t.io')
        r = _post(c, '/api/private/circles/', {
            'name': 'Addr Circle', 'slug': 'addr-c', 'address': '123 Main St', 'description': 'Test'
        })
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['address'], '123 Main St')

    def test_update_address(self):
        circle = _circle('addr-upd', address='Old')
        CircleMembership.objects.create(user=self.sm, circle=circle, role='CIRCLE_ADMIN')
        c = Client(); _login(c, 'sm@t.io')
        csrf = c.cookies['csrftoken'].value
        r = c.patch(f'/api/private/circles/{circle.id}/', data={'address': 'New Address'},
                     content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['address'], 'New Address')


# ── Event visibility: public vs private ─────────────────────
class EventVisibilityTests(TestCase):
    def setUp(self):
        self.admin = _user('eva@t.io')
        self.member = _user('evm@t.io')
        self.outsider = _user('evo@t.io')
        self.circle = _circle('ev-vis')
        CircleMembership.objects.create(user=self.admin, circle=self.circle, role='CIRCLE_ADMIN')
        CircleMembership.objects.create(user=self.member, circle=self.circle, role='MEMBER')
        now = timezone.now()
        self.pub_event = Event.objects.create(
            circle=self.circle, title='Public Meetup', published=True, visibility='PUBLIC',
            created_by=self.admin, start_datetime=now + timedelta(days=1), end_datetime=now + timedelta(days=1, hours=2))
        self.priv_event = Event.objects.create(
            circle=self.circle, title='Private Session', published=True, visibility='PRIVATE',
            created_by=self.admin, start_datetime=now + timedelta(days=2), end_datetime=now + timedelta(days=2, hours=2))
        self.draft = Event.objects.create(
            circle=self.circle, title='Draft', published=False, visibility='PRIVATE',
            created_by=self.admin, start_datetime=now + timedelta(days=3), end_datetime=now + timedelta(days=3, hours=2))

    def test_outsider_can_view_public_event(self):
        c = Client(); _login(c, 'evo@t.io')
        r = c.get(f'/api/private/events/{self.pub_event.id}/')
        self.assertEqual(r.status_code, 200)

    def test_outsider_cannot_view_private_event(self):
        c = Client(); _login(c, 'evo@t.io')
        r = c.get(f'/api/private/events/{self.priv_event.id}/')
        self.assertEqual(r.status_code, 403)

    def test_outsider_can_signup_public_event(self):
        c = Client(); _login(c, 'evo@t.io')
        r = _post(c, f'/api/private/events/{self.pub_event.id}/signup/')
        self.assertEqual(r.status_code, 201)

    def test_outsider_cannot_signup_private_event(self):
        c = Client(); _login(c, 'evo@t.io')
        r = _post(c, f'/api/private/events/{self.priv_event.id}/signup/')
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.json()['code'], 'not_member')

    def test_member_can_signup_private_event(self):
        c = Client(); _login(c, 'evm@t.io')
        r = _post(c, f'/api/private/events/{self.priv_event.id}/signup/')
        self.assertEqual(r.status_code, 201)

    def test_member_cannot_see_draft(self):
        c = Client(); _login(c, 'evm@t.io')
        r = c.get(f'/api/private/events/{self.draft.id}/')
        self.assertEqual(r.status_code, 404)

    def test_admin_can_see_draft(self):
        c = Client(); _login(c, 'eva@t.io')
        r = c.get(f'/api/private/events/{self.draft.id}/')
        self.assertEqual(r.status_code, 200)

    def test_outsider_cannot_signup_draft(self):
        c = Client(); _login(c, 'evo@t.io')
        r = _post(c, f'/api/private/events/{self.draft.id}/signup/')
        self.assertEqual(r.status_code, 404)


# ── Last-admin protection ──────────────────────────────────
class LastAdminTests(TestCase):
    def setUp(self):
        self.admin = _user('la@t.io')
        self.circle = _circle('la-c')
        self.mem = CircleMembership.objects.create(user=self.admin, circle=self.circle, role='CIRCLE_ADMIN')

    def test_demote_blocked(self):
        c = Client(); _login(c, 'la@t.io')
        r = _post(c, f'/api/private/circles/{self.circle.id}/members/{self.mem.id}/demote/')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'last_admin')

    def test_remove_blocked(self):
        c = Client(); _login(c, 'la@t.io')
        r = _post(c, f'/api/private/circles/{self.circle.id}/members/{self.mem.id}/remove/')
        self.assertEqual(r.status_code, 400)


# ── Account deactivation ───────────────────────────────────
class DeactivationTests(TestCase):
    def test_blocked_when_last_admin(self):
        u = _user('da@t.io')
        ci = _circle('da-c')
        CircleMembership.objects.create(user=u, circle=ci, role='CIRCLE_ADMIN')
        c = Client(); _login(c, 'da@t.io')
        r = _post(c, '/api/private/profile/deactivate/')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'last_admin_deactivation')

    def test_allowed_with_other_admin(self):
        u = _user('da2@t.io'); o = _user('da3@t.io')
        ci = _circle('da2-c')
        CircleMembership.objects.create(user=u, circle=ci, role='CIRCLE_ADMIN')
        CircleMembership.objects.create(user=o, circle=ci, role='CIRCLE_ADMIN')
        c = Client(); _login(c, 'da2@t.io')
        r = _post(c, '/api/private/profile/deactivate/')
        self.assertEqual(r.status_code, 200)
        u.refresh_from_db()
        self.assertFalse(u.is_active)


# ── Invite safety ───────────────────────────────────────────
class InviteTests(TransactionTestCase):
    def setUp(self):
        self.admin = _user('inv-a@t.io')
        self.u1 = _user('inv-1@t.io')
        self.circle = _circle('inv-c')
        CircleMembership.objects.create(user=self.admin, circle=self.circle, role='CIRCLE_ADMIN')
        self.inv = CircleInvite.objects.create(
            circle=self.circle, created_by=self.admin,
            token=str(uuid.uuid4()), expires_at=timezone.now() + timedelta(days=7))

    def test_accept_creates_membership(self):
        c = Client(); _login(c, 'inv-1@t.io')
        r = _post(c, f'/api/private/invites/accept/{self.inv.token}/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(CircleMembership.objects.filter(user=self.u1, circle=self.circle, active=True).exists())

    def test_single_use(self):
        c1 = Client(); _login(c1, 'inv-1@t.io')
        _post(c1, f'/api/private/invites/accept/{self.inv.token}/')
        u2 = _user('inv-2@t.io')
        c2 = Client(); _login(c2, 'inv-2@t.io')
        r = c2.post(f'/api/private/invites/accept/{self.inv.token}/',
                     content_type='application/json', HTTP_X_CSRFTOKEN=c2.cookies['csrftoken'].value)
        self.assertEqual(r.status_code, 400)


# ── Permissions ─────────────────────────────────────────────
class PermissionTests(TestCase):
    def setUp(self):
        self.admin = _user('pa@t.io')
        self.user = _user('pu@t.io')
        self.ca = _circle('pa-c')
        self.cb = _circle('pb-c')
        CircleMembership.objects.create(user=self.admin, circle=self.ca, role='CIRCLE_ADMIN')

    def test_admin_cannot_manage_other_circle(self):
        c = Client(); _login(c, 'pa@t.io')
        r = c.get(f'/api/private/circles/{self.cb.id}/members/')
        self.assertEqual(r.status_code, 403)

    def test_site_manager_global_access(self):
        sm = _user('psm@t.io', is_site_manager=True)
        c = Client(); _login(c, 'psm@t.io')
        r = c.get(f'/api/private/circles/{self.cb.id}/members/')
        self.assertEqual(r.status_code, 200)


# ── Dashboard ───────────────────────────────────────────────
class DashboardTests(TestCase):
    def setUp(self):
        self.u = _user('dash@t.io')
        self.circle = _circle('dash-c')
        CircleMembership.objects.create(user=self.u, circle=self.circle, role='MEMBER')
        now = timezone.now()
        self.ev = Event.objects.create(
            circle=self.circle, title='Dash Event', published=True, visibility='PRIVATE',
            created_by=None, start_datetime=now + timedelta(days=1), end_datetime=now + timedelta(days=1, hours=2))
        EventSignup.objects.create(event=self.ev, user=self.u, status='PENDING')

    def test_dashboard_returns_signups_and_events(self):
        c = Client(); _login(c, 'dash@t.io')
        r = c.get('/api/private/dashboard/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(len(data['recent_signups']) >= 1)
        self.assertTrue(len(data['circle_events']) >= 1)
        self.assertEqual(data['recent_signups'][0]['event']['title'], 'Dash Event')


# ── Rate limiting ───────────────────────────────────────────
class RateLimitTests(TestCase):
    def setUp(self):
        _user('rl@t.io')
        from django.core.cache import cache
        cache.clear()

    def test_triggers(self):
        c = Client(); c.get('/api/private/auth/csrf/')
        csrf = c.cookies['csrftoken'].value
        for _ in range(10):
            c.post('/api/private/auth/login/', data={'email': 'rl@t.io', 'password': 'wrong'},
                   content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        r = c.post('/api/private/auth/login/', data={'email': 'rl@t.io', 'password': 'wrong'},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 429)
