"""
Critical-flow test suite for the Circles platform.
Tests the dangerous business logic that must never regress.
"""
import uuid
from datetime import timedelta
from django.test import TestCase, TransactionTestCase, Client
from django.utils import timezone
from accounts.models import User
from circles.models import Circle, CircleMembership, CircleInvite
from events.models import Event, EventSignup


def _make_user(email, password='Testpass1', **kw):
    return User.objects.create_user(email=email, password=password, first_name='T', **kw)


def _make_circle(slug=None):
    slug = slug or f'c-{uuid.uuid4().hex[:8]}'
    return Circle.objects.create(name=slug.title(), slug=slug)


def _login(client, email, password='Testpass1'):
    client.get('/api/private/auth/csrf/')
    csrf = client.cookies.get('csrftoken')
    r = client.post('/api/private/auth/login/',
                     data={'email': email, 'password': password},
                     content_type='application/json',
                     HTTP_X_CSRFTOKEN=csrf.value if csrf else '')
    return r


class RegistrationTests(TestCase):
    def test_register_success(self):
        c = Client()
        c.get('/api/private/auth/csrf/')
        csrf = c.cookies['csrftoken'].value
        r = c.post('/api/private/auth/register/',
                    data={'email': 'new@test.io', 'password': 'Testpass1', 'first_name': 'New'},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 201)
        self.assertTrue(User.objects.filter(email='new@test.io').exists())

    def test_register_weak_password_rejected(self):
        c = Client()
        c.get('/api/private/auth/csrf/')
        csrf = c.cookies['csrftoken'].value
        r = c.post('/api/private/auth/register/',
                    data={'email': 'weak@test.io', 'password': 'short', 'first_name': 'W'},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'weak_password')

    def test_register_no_digit_rejected(self):
        c = Client()
        c.get('/api/private/auth/csrf/')
        csrf = c.cookies['csrftoken'].value
        r = c.post('/api/private/auth/register/',
                    data={'email': 'nd@test.io', 'password': 'abcdefgh', 'first_name': 'N'},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 400)

    def test_register_bad_email_rejected(self):
        c = Client()
        c.get('/api/private/auth/csrf/')
        csrf = c.cookies['csrftoken'].value
        r = c.post('/api/private/auth/register/',
                    data={'email': 'notanemail', 'password': 'Testpass1', 'first_name': 'B'},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'invalid_email')


class LoginRateLimitTests(TestCase):
    def setUp(self):
        _make_user('rl@test.io')

    def test_rate_limit_triggers(self):
        from django.core.cache import cache
        cache.clear()
        c = Client()
        c.get('/api/private/auth/csrf/')
        csrf = c.cookies['csrftoken'].value
        for _ in range(10):
            c.post('/api/private/auth/login/',
                   data={'email': 'rl@test.io', 'password': 'wrongpassword'},
                   content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        r = c.post('/api/private/auth/login/',
                    data={'email': 'rl@test.io', 'password': 'wrongpassword'},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 429)
        self.assertEqual(r.json()['code'], 'rate_limited')


class ActiveCirclePermissionTests(TestCase):
    def setUp(self):
        self.user = _make_user('u@test.io')
        self.other = _make_user('other@test.io')
        self.circle = _make_circle('priv')
        CircleMembership.objects.create(user=self.other, circle=self.circle, role='MEMBER')

    def test_non_member_cannot_set_active_circle(self):
        c = Client()
        _login(c, 'u@test.io')
        csrf = c.cookies['csrftoken'].value
        r = c.post('/api/private/circles/active/',
                    data={'circle_id': str(self.circle.id)},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 403)

    def test_member_can_set_active_circle(self):
        c = Client()
        _login(c, 'other@test.io')
        csrf = c.cookies['csrftoken'].value
        r = c.post('/api/private/circles/active/',
                    data={'circle_id': str(self.circle.id)},
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 200)
        self.other.refresh_from_db()
        self.assertEqual(self.other.active_circle_id, self.circle.id)


class InviteAcceptanceTests(TransactionTestCase):
    def setUp(self):
        self.admin = _make_user('admin@test.io')
        self.user1 = _make_user('u1@test.io')
        self.user2 = _make_user('u2@test.io')
        self.circle = _make_circle('inv-test')
        CircleMembership.objects.create(user=self.admin, circle=self.circle, role='CIRCLE_ADMIN')
        self.invite = CircleInvite.objects.create(
            circle=self.circle, created_by=self.admin,
            token=str(uuid.uuid4()), expires_at=timezone.now() + timedelta(days=7))

    def test_accept_creates_membership(self):
        c = Client()
        _login(c, 'u1@test.io')
        csrf = c.cookies['csrftoken'].value
        r = c.post(f'/api/private/invites/accept/{self.invite.token}/',
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(CircleMembership.objects.filter(
            user=self.user1, circle=self.circle, active=True).exists())

    def test_single_use_enforcement(self):
        # First user accepts
        c1 = Client()
        _login(c1, 'u1@test.io')
        csrf1 = c1.cookies['csrftoken'].value
        c1.post(f'/api/private/invites/accept/{self.invite.token}/',
                content_type='application/json', HTTP_X_CSRFTOKEN=csrf1)
        # Second user tries same invite
        c2 = Client()
        _login(c2, 'u2@test.io')
        csrf2 = c2.cookies['csrftoken'].value
        r = c2.post(f'/api/private/invites/accept/{self.invite.token}/',
                     content_type='application/json', HTTP_X_CSRFTOKEN=csrf2)
        self.assertEqual(r.status_code, 400)
        self.assertIn(r.json()['code'], ('invite_used', 'invite_inactive'))

    def test_expired_invite_rejected(self):
        self.invite.expires_at = timezone.now() - timedelta(hours=1)
        self.invite.save()
        c = Client()
        _login(c, 'u1@test.io')
        csrf = c.cookies['csrftoken'].value
        r = c.post(f'/api/private/invites/accept/{self.invite.token}/',
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'invite_expired')


class UnpublishedEventTests(TestCase):
    def setUp(self):
        self.admin = _make_user('evadm@test.io')
        self.member = _make_user('evmem@test.io')
        self.circle = _make_circle('ev-test')
        CircleMembership.objects.create(user=self.admin, circle=self.circle, role='CIRCLE_ADMIN')
        CircleMembership.objects.create(user=self.member, circle=self.circle, role='MEMBER')
        self.draft = Event.objects.create(
            circle=self.circle, title='Draft', published=False, created_by=self.admin,
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=2))

    def test_member_cannot_see_unpublished_event(self):
        c = Client()
        _login(c, 'evmem@test.io')
        r = c.get(f'/api/private/events/{self.draft.id}/')
        self.assertEqual(r.status_code, 404)

    def test_member_cannot_signup_unpublished_event(self):
        c = Client()
        _login(c, 'evmem@test.io')
        csrf = c.cookies['csrftoken'].value
        r = c.post(f'/api/private/events/{self.draft.id}/signup/',
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 404)

    def test_admin_can_see_unpublished_event(self):
        c = Client()
        _login(c, 'evadm@test.io')
        r = c.get(f'/api/private/events/{self.draft.id}/')
        self.assertEqual(r.status_code, 200)

    def test_published_event_visible_to_member(self):
        self.draft.published = True
        self.draft.save()
        c = Client()
        _login(c, 'evmem@test.io')
        r = c.get(f'/api/private/events/{self.draft.id}/')
        self.assertEqual(r.status_code, 200)


class LastAdminProtectionTests(TestCase):
    def setUp(self):
        self.admin = _make_user('la-admin@test.io')
        self.circle = _make_circle('la-test')
        self.membership = CircleMembership.objects.create(
            user=self.admin, circle=self.circle, role='CIRCLE_ADMIN')

    def _login_admin(self):
        c = Client()
        _login(c, 'la-admin@test.io')
        return c

    def test_demote_last_admin_blocked(self):
        c = self._login_admin()
        csrf = c.cookies['csrftoken'].value
        r = c.post(f'/api/private/circles/{self.circle.id}/members/{self.membership.id}/demote/',
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'last_admin')

    def test_remove_last_admin_blocked(self):
        c = self._login_admin()
        csrf = c.cookies['csrftoken'].value
        r = c.post(f'/api/private/circles/{self.circle.id}/members/{self.membership.id}/remove/',
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'last_admin')

    def test_demote_with_second_admin_allowed(self):
        other = _make_user('la-other@test.io')
        CircleMembership.objects.create(user=other, circle=self.circle, role='CIRCLE_ADMIN')
        c = self._login_admin()
        csrf = c.cookies['csrftoken'].value
        r = c.post(f'/api/private/circles/{self.circle.id}/members/{self.membership.id}/demote/',
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 200)


class AccountDeactivationTests(TestCase):
    def test_deactivation_blocked_when_last_admin(self):
        admin = _make_user('deact-adm@test.io')
        circle = _make_circle('deact-c')
        CircleMembership.objects.create(user=admin, circle=circle, role='CIRCLE_ADMIN')
        c = Client()
        _login(c, 'deact-adm@test.io')
        csrf = c.cookies['csrftoken'].value
        r = c.post('/api/private/profile/deactivate/',
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['code'], 'last_admin_deactivation')
        admin.refresh_from_db()
        self.assertTrue(admin.is_active)

    def test_deactivation_allowed_with_other_admin(self):
        admin = _make_user('deact-ok@test.io')
        other = _make_user('deact-other@test.io')
        circle = _make_circle('deact-ok')
        CircleMembership.objects.create(user=admin, circle=circle, role='CIRCLE_ADMIN')
        CircleMembership.objects.create(user=other, circle=circle, role='CIRCLE_ADMIN')
        c = Client()
        _login(c, 'deact-ok@test.io')
        csrf = c.cookies['csrftoken'].value
        r = c.post('/api/private/profile/deactivate/',
                    content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(r.status_code, 200)
        admin.refresh_from_db()
        self.assertFalse(admin.is_active)
        self.assertFalse(CircleMembership.objects.filter(user=admin, active=True).exists())

    def test_deactivation_clears_memberships(self):
        user = _make_user('deact-mem@test.io')
        c1 = _make_circle('deact-m1')
        c2 = _make_circle('deact-m2')
        CircleMembership.objects.create(user=user, circle=c1, role='MEMBER')
        CircleMembership.objects.create(user=user, circle=c2, role='MEMBER')
        # Need an admin in each circle so user isn't last admin
        admin = _make_user('deact-adm2@test.io')
        CircleMembership.objects.create(user=admin, circle=c1, role='CIRCLE_ADMIN')
        CircleMembership.objects.create(user=admin, circle=c2, role='CIRCLE_ADMIN')
        c = Client()
        _login(c, 'deact-mem@test.io')
        csrf = c.cookies['csrftoken'].value
        c.post('/api/private/profile/deactivate/',
               content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(CircleMembership.objects.filter(user=user, active=True).count(), 0)


class PermissionTests(TestCase):
    def setUp(self):
        self.admin = _make_user('perm-adm@test.io')
        self.user = _make_user('perm-usr@test.io')
        self.circle_a = _make_circle('perm-a')
        self.circle_b = _make_circle('perm-b')
        CircleMembership.objects.create(user=self.admin, circle=self.circle_a, role='CIRCLE_ADMIN')
        CircleMembership.objects.create(user=self.user, circle=self.circle_a, role='MEMBER')

    def test_circle_admin_cannot_manage_unrelated_circle(self):
        c = Client()
        _login(c, 'perm-adm@test.io')
        r = c.get(f'/api/private/circles/{self.circle_b.id}/members/')
        self.assertEqual(r.status_code, 403)

    def test_site_manager_can_access_any_circle(self):
        sm = _make_user('perm-sm@test.io', is_site_manager=True)
        c = Client()
        _login(c, 'perm-sm@test.io')
        r = c.get(f'/api/private/circles/{self.circle_b.id}/members/')
        self.assertEqual(r.status_code, 200)

    def test_normal_user_cannot_list_all_circles(self):
        c = Client()
        _login(c, 'perm-usr@test.io')
        r = c.get('/api/private/circles/')
        self.assertEqual(r.status_code, 403)
