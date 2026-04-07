"""
Critical-flow tests for the Circles platform.
Covers: auth, profile deletion (anonymization), phone/address CRUD,
public/private events, permissions, invite safety, last-admin,
dashboard, public event discovery, site manager user management.
"""
import uuid
from datetime import timedelta
from django.test import TestCase, TransactionTestCase, Client
from django.utils import timezone
from accounts.models import User
from circles.models import Circle, CircleMembership, CircleInvite
from events.models import Event, EventSignup

def _user(email, password='Testpass1', **kw):
    kw.setdefault('first_name', 'T')
    return User.objects.create_user(email=email, password=password, **kw)

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

def _patch(client, url, data):
    csrf = client.cookies.get('csrftoken')
    return client.patch(url, data=data, content_type='application/json',
                         HTTP_X_CSRFTOKEN=csrf.value if csrf else '')


# ── Account deletion (anonymization) ───────────────────────
class AccountDeletionTests(TestCase):
    def test_delete_anonymizes_pii(self):
        u = _user('del@test.io', first_name='John', last_name='Doe', phone='+1555')
        c = Client(); _login(c, 'del@test.io')
        r = _post(c, '/api/private/profile/delete/')
        self.assertEqual(r.status_code, 200)
        u.refresh_from_db()
        self.assertFalse(u.is_active)
        self.assertNotEqual(u.email, 'del@test.io')
        self.assertIn('@removed.local', u.email)
        self.assertEqual(u.first_name, 'Deleted')
        self.assertEqual(u.last_name, 'User')
        self.assertEqual(u.phone, '')
        self.assertFalse(u.has_usable_password())

    def test_delete_blocked_when_last_admin(self):
        u = _user('del-adm@test.io')
        ci = _circle('del-c')
        CircleMembership.objects.create(user=u, circle=ci, role='CIRCLE_ADMIN')
        c = Client(); _login(c, 'del-adm@test.io')
        r = _post(c, '/api/private/profile/delete/')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'last_admin_deletion')
        u.refresh_from_db()
        self.assertTrue(u.is_active)

    def test_delete_clears_memberships(self):
        u = _user('del-mem@test.io')
        ci = _circle('del-m1')
        adm = _user('del-adm2@test.io')
        CircleMembership.objects.create(user=adm, circle=ci, role='CIRCLE_ADMIN')
        CircleMembership.objects.create(user=u, circle=ci, role='MEMBER')
        c = Client(); _login(c, 'del-mem@test.io')
        _post(c, '/api/private/profile/delete/')
        self.assertEqual(CircleMembership.objects.filter(user=u, active=True).count(), 0)


# ── Profile phone ──────────────────────────────────────────
class ProfilePhoneTests(TestCase):
    def test_phone_update(self):
        u = _user('ph@test.io')
        c = Client(); _login(c, 'ph@test.io')
        r = _patch(c, '/api/private/profile/', {'phone': '+1 555 0100'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['phone'], '+1 555 0100')


# ── Circle address CRUD ────────────────────────────────────
class CircleAddressTests(TestCase):
    def test_create_with_address(self):
        sm = _user('sm@test.io', is_site_manager=True)
        c = Client(); _login(c, 'sm@test.io')
        r = _post(c, '/api/private/circles/', {'name': 'Addr', 'slug': 'addr-c', 'address': '123 Main St'})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['address'], '123 Main St')

    def test_update_address(self):
        sm = _user('sm2@test.io', is_site_manager=True)
        ci = _circle('addr-upd', address='Old')
        CircleMembership.objects.create(user=sm, circle=ci, role='CIRCLE_ADMIN')
        c = Client(); _login(c, 'sm2@test.io')
        r = _patch(c, f'/api/private/circles/{ci.id}/', {'address': 'New'})
        self.assertEqual(r.json()['address'], 'New')

    def test_member_can_view_circle_profile(self):
        mem = _user('cview@test.io')
        ci = _circle('cview-c', description='A circle', address='456 Elm')
        CircleMembership.objects.create(user=mem, circle=ci, role='MEMBER')
        c = Client(); _login(c, 'cview@test.io')
        r = c.get(f'/api/private/circles/{ci.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['address'], '456 Elm')
        self.assertEqual(r.json()['description'], 'A circle')


# ── Event visibility: public / private ─────────────────────
class EventVisibilityTests(TestCase):
    def setUp(self):
        self.admin = _user('eva@test.io')
        self.member = _user('evm@test.io')
        self.outsider = _user('evo@test.io')
        self.circle = _circle('ev-vis')
        CircleMembership.objects.create(user=self.admin, circle=self.circle, role='CIRCLE_ADMIN')
        CircleMembership.objects.create(user=self.member, circle=self.circle, role='MEMBER')
        now = timezone.now()
        self.pub_event = Event.objects.create(circle=self.circle, title='Public', published=True, visibility='PUBLIC',
            created_by=self.admin, start_datetime=now+timedelta(days=1), end_datetime=now+timedelta(days=1,hours=2))
        self.priv_event = Event.objects.create(circle=self.circle, title='Private', published=True, visibility='PRIVATE',
            created_by=self.admin, start_datetime=now+timedelta(days=2), end_datetime=now+timedelta(days=2,hours=2))
        self.draft = Event.objects.create(circle=self.circle, title='Draft', published=False, visibility='PRIVATE',
            created_by=self.admin, start_datetime=now+timedelta(days=3), end_datetime=now+timedelta(days=3,hours=2))

    def test_outsider_can_view_public(self):
        c = Client(); _login(c, 'evo@test.io')
        self.assertEqual(c.get(f'/api/private/events/{self.pub_event.id}/').status_code, 200)

    def test_outsider_cannot_view_private(self):
        c = Client(); _login(c, 'evo@test.io')
        self.assertEqual(c.get(f'/api/private/events/{self.priv_event.id}/').status_code, 403)

    def test_outsider_can_signup_public(self):
        c = Client(); _login(c, 'evo@test.io')
        self.assertEqual(_post(c, f'/api/private/events/{self.pub_event.id}/signup/').status_code, 201)

    def test_outsider_cannot_signup_private(self):
        c = Client(); _login(c, 'evo@test.io')
        r = _post(c, f'/api/private/events/{self.priv_event.id}/signup/')
        self.assertEqual(r.status_code, 403)

    def test_member_can_signup_private(self):
        c = Client(); _login(c, 'evm@test.io')
        self.assertEqual(_post(c, f'/api/private/events/{self.priv_event.id}/signup/').status_code, 201)

    def test_draft_invisible_to_member(self):
        c = Client(); _login(c, 'evm@test.io')
        self.assertEqual(c.get(f'/api/private/events/{self.draft.id}/').status_code, 404)

    def test_draft_visible_to_admin(self):
        c = Client(); _login(c, 'eva@test.io')
        self.assertEqual(c.get(f'/api/private/events/{self.draft.id}/').status_code, 200)


# ── Public events discovery endpoint ───────────────────────
class PublicEventsDiscoveryTests(TestCase):
    def setUp(self):
        self.user = _user('disc@test.io')
        adm = _user('disc-adm@test.io')
        ci = _circle('disc-c')
        CircleMembership.objects.create(user=adm, circle=ci, role='CIRCLE_ADMIN')
        now = timezone.now()
        Event.objects.create(circle=ci, title='Public Browse', published=True, visibility='PUBLIC',
            created_by=adm, start_datetime=now+timedelta(days=1), end_datetime=now+timedelta(days=1,hours=2))
        Event.objects.create(circle=ci, title='Private Hidden', published=True, visibility='PRIVATE',
            created_by=adm, start_datetime=now+timedelta(days=2), end_datetime=now+timedelta(days=2,hours=2))
        Event.objects.create(circle=ci, title='Draft Hidden', published=False, visibility='PUBLIC',
            created_by=adm, start_datetime=now+timedelta(days=3), end_datetime=now+timedelta(days=3,hours=2))

    def test_only_published_public_events_returned(self):
        c = Client(); _login(c, 'disc@test.io')
        r = c.get('/api/private/events/public/')
        self.assertEqual(r.status_code, 200)
        titles = [e['title'] for e in r.json()['events']]
        self.assertIn('Public Browse', titles)
        self.assertNotIn('Private Hidden', titles)
        self.assertNotIn('Draft Hidden', titles)

    def test_pagination_present(self):
        c = Client(); _login(c, 'disc@test.io')
        r = c.get('/api/private/events/public/')
        self.assertIn('pagination', r.json())


# ── Last-admin protection ──────────────────────────────────
class LastAdminTests(TestCase):
    def test_demote_blocked(self):
        adm = _user('la@test.io'); ci = _circle('la-c')
        mem = CircleMembership.objects.create(user=adm, circle=ci, role='CIRCLE_ADMIN')
        c = Client(); _login(c, 'la@test.io')
        self.assertEqual(_post(c, f'/api/private/circles/{ci.id}/members/{mem.id}/demote/').status_code, 400)

    def test_remove_blocked(self):
        adm = _user('la2@test.io'); ci = _circle('la2-c')
        mem = CircleMembership.objects.create(user=adm, circle=ci, role='CIRCLE_ADMIN')
        c = Client(); _login(c, 'la2@test.io')
        self.assertEqual(_post(c, f'/api/private/circles/{ci.id}/members/{mem.id}/remove/').status_code, 400)


# ── Invite safety ───────────────────────────────────────────
class InviteTests(TransactionTestCase):
    def setUp(self):
        self.admin = _user('inv-a@test.io')
        self.u1 = _user('inv-1@test.io')
        self.circle = _circle('inv-c')
        CircleMembership.objects.create(user=self.admin, circle=self.circle, role='CIRCLE_ADMIN')
        self.inv = CircleInvite.objects.create(circle=self.circle, created_by=self.admin,
            token=str(uuid.uuid4()), expires_at=timezone.now()+timedelta(days=7))

    def test_accept(self):
        c = Client(); _login(c, 'inv-1@test.io')
        self.assertEqual(_post(c, f'/api/private/invites/accept/{self.inv.token}/').status_code, 200)

    def test_single_use(self):
        c1 = Client(); _login(c1, 'inv-1@test.io')
        _post(c1, f'/api/private/invites/accept/{self.inv.token}/')
        u2 = _user('inv-2@test.io')
        c2 = Client(); _login(c2, 'inv-2@test.io')
        self.assertEqual(_post(c2, f'/api/private/invites/accept/{self.inv.token}/').status_code, 400)


# ── Permissions ─────────────────────────────────────────────
class PermissionTests(TestCase):
    def test_admin_cannot_manage_other_circle(self):
        adm = _user('pa@test.io'); cb = _circle('pb-c')
        ca = _circle('pa-c'); CircleMembership.objects.create(user=adm, circle=ca, role='CIRCLE_ADMIN')
        c = Client(); _login(c, 'pa@test.io')
        self.assertEqual(c.get(f'/api/private/circles/{cb.id}/members/').status_code, 403)

    def test_site_manager_global_access(self):
        sm = _user('psm@test.io', is_site_manager=True); cb = _circle('pb2-c')
        c = Client(); _login(c, 'psm@test.io')
        self.assertEqual(c.get(f'/api/private/circles/{cb.id}/members/').status_code, 200)


# ── Site manager user management ───────────────────────────
class SiteManagerUserTests(TestCase):
    def setUp(self):
        self.sm = _user('sm-mgr@test.io', is_site_manager=True)
        self.target = _user('sm-target@test.io', first_name='Old')

    def test_view_user(self):
        c = Client(); _login(c, 'sm-mgr@test.io')
        r = c.get(f'/api/private/admin/users/{self.target.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['first_name'], 'Old')

    def test_update_user(self):
        c = Client(); _login(c, 'sm-mgr@test.io')
        r = _patch(c, f'/api/private/admin/users/{self.target.id}/', {'first_name': 'New'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['first_name'], 'New')

    def test_deactivate_user(self):
        c = Client(); _login(c, 'sm-mgr@test.io')
        r = _patch(c, f'/api/private/admin/users/{self.target.id}/', {'is_active': False})
        self.assertEqual(r.status_code, 200)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)

    def test_non_manager_forbidden(self):
        normal = _user('sm-normal@test.io')
        c = Client(); _login(c, 'sm-normal@test.io')
        self.assertEqual(c.get(f'/api/private/admin/users/{self.target.id}/').status_code, 403)


# ── Dashboard ───────────────────────────────────────────────
class DashboardTests(TestCase):
    def test_returns_signups_and_events(self):
        u = _user('dash@test.io')
        ci = _circle('dash-c')
        CircleMembership.objects.create(user=u, circle=ci, role='MEMBER')
        ev = Event.objects.create(circle=ci, title='Dash Event', published=True, visibility='PRIVATE',
            created_by=None, start_datetime=timezone.now()+timedelta(days=1), end_datetime=timezone.now()+timedelta(days=1,hours=2))
        EventSignup.objects.create(event=ev, user=u, status='PENDING')
        c = Client(); _login(c, 'dash@test.io')
        r = c.get('/api/private/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(len(r.json()['recent_signups']) >= 1)
        self.assertTrue(len(r.json()['circle_events']) >= 1)


# ── Rate limiting ───────────────────────────────────────────
class RateLimitTests(TestCase):
    def test_triggers(self):
        _user('rl@test.io')
        from django.core.cache import cache; cache.clear()
        c = Client(); c.get('/api/private/auth/csrf/')
        csrf = c.cookies['csrftoken'].value
        for _ in range(10):
            c.post('/api/private/auth/login/', data={'email': 'rl@test.io', 'password': 'wrong'},
                   content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        r = c.post('/api/private/auth/login/', data={'email': 'rl@test.io', 'password': 'wrong'},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 429)
