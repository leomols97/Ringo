from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import Q
from .models import User
from project.utils import (
    parse_json, login_required_json, validate_email_format,
    validate_password_strength, check_login_rate_limit,
    record_login_attempt, paginate_qs,
)


def serialize_user(user):
    from circles.models import CircleMembership
    admin_circle_ids = list(
        CircleMembership.objects.filter(
            user=user, role='CIRCLE_ADMIN', active=True
        ).values_list('circle_id', flat=True)
    )
    return {
        'id': str(user.id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'is_active': user.is_active,
        'is_site_manager': user.is_site_manager,
        'active_circle_id': str(user.active_circle_id) if user.active_circle_id else None,
        'admin_circle_ids': [str(cid) for cid in admin_circle_ids],
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


@require_GET
@ensure_csrf_cookie
def csrf_view(request):
    return JsonResponse({'ok': True})


@require_POST
def register_view(request):
    data = parse_json(request)
    if not data:
        return JsonResponse({'error': 'Invalid JSON', 'code': 'invalid_json'}, status=400)
    email = (data.get('email') or '').strip().lower()
    password = data.get('password', '')
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    if not email or not password or not first_name:
        return JsonResponse({'error': 'Email, password, and first name are required', 'code': 'missing_fields'}, status=400)
    if not validate_email_format(email):
        return JsonResponse({'error': 'Invalid email format', 'code': 'invalid_email'}, status=400)
    pw_err = validate_password_strength(password)
    if pw_err:
        return JsonResponse({'error': pw_err, 'code': 'weak_password'}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already registered', 'code': 'email_exists'}, status=409)
    user = User.objects.create_user(
        email=email, password=password,
        first_name=first_name, last_name=last_name,
    )
    login(request, user)
    return JsonResponse(serialize_user(user), status=201)


@require_POST
def login_view(request):
    data = parse_json(request)
    if not data:
        return JsonResponse({'error': 'Invalid JSON', 'code': 'invalid_json'}, status=400)
    email = (data.get('email') or '').strip().lower()
    password = data.get('password', '')
    if not check_login_rate_limit(request, email):
        return JsonResponse({'error': 'Too many login attempts. Try again later.', 'code': 'rate_limited'}, status=429)
    user = authenticate(request, email=email, password=password)
    if user is None:
        record_login_attempt(request, email, success=False)
        return JsonResponse({'error': 'Invalid email or password', 'code': 'invalid_credentials'}, status=401)
    if not user.is_active:
        return JsonResponse({'error': 'Account is deactivated', 'code': 'account_deactivated'}, status=403)
    record_login_attempt(request, email, success=True)
    login(request, user)
    return JsonResponse(serialize_user(user))


@require_POST
@login_required_json
def logout_view(request):
    logout(request)
    return JsonResponse({'ok': True})


@require_GET
def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False}, status=200)
    return JsonResponse({'authenticated': True, 'user': serialize_user(request.user)})


@require_http_methods(['GET', 'PATCH'])
@login_required_json
def profile_view(request):
    if request.method == 'GET':
        return JsonResponse(serialize_user(request.user))
    data = parse_json(request)
    if not data:
        return JsonResponse({'error': 'Invalid JSON', 'code': 'invalid_json'}, status=400)
    user = request.user
    if 'first_name' in data:
        val = data['first_name'].strip()
        if not val:
            return JsonResponse({'error': 'First name cannot be empty', 'code': 'validation'}, status=400)
        user.first_name = val
    if 'last_name' in data:
        user.last_name = data['last_name'].strip()
    if 'phone' in data:
        user.phone = (data['phone'] or '').strip()[:30]
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if not validate_email_format(new_email):
            return JsonResponse({'error': 'Invalid email format', 'code': 'invalid_email'}, status=400)
        if new_email != user.email and User.objects.filter(email=new_email).exists():
            return JsonResponse({'error': 'Email already in use', 'code': 'email_exists'}, status=409)
        user.email = new_email
    user.save()
    return JsonResponse(serialize_user(user))


@require_POST
@login_required_json
def deactivate_view(request):
    user = request.user
    from circles.models import CircleMembership
    admin_memberships = CircleMembership.objects.filter(
        user=user, role='CIRCLE_ADMIN', active=True
    ).select_related('circle')
    orphan_circles = []
    for m in admin_memberships:
        other_admins = CircleMembership.objects.filter(
            circle=m.circle, role='CIRCLE_ADMIN', active=True
        ).exclude(user=user).count()
        if other_admins == 0:
            orphan_circles.append(m.circle.name)
    if orphan_circles:
        names = ', '.join(orphan_circles)
        return JsonResponse({
            'error': f'You are the last admin of: {names}. Promote another admin before deactivating.',
            'code': 'last_admin_deactivation',
            'circles': orphan_circles,
        }, status=400)
    with transaction.atomic():
        CircleMembership.objects.filter(user=user, active=True).update(active=False)
        user.active_circle = None
        user.is_active = False
        user.save(update_fields=['active_circle', 'is_active'])
    logout(request)
    return JsonResponse({'ok': True, 'message': 'Account deactivated.'})


# ── Dashboard ───────────────────────────────────────────────
@require_GET
@login_required_json
def dashboard_view(request):
    """User dashboard: recent signups + events from all my circles."""
    from circles.models import CircleMembership
    from events.models import Event, EventSignup

    user = request.user
    my_circle_ids = list(
        CircleMembership.objects.filter(user=user, active=True).values_list('circle_id', flat=True)
    )

    # Recent signups by this user (last 10)
    recent_signups = EventSignup.objects.filter(
        user=user
    ).select_related('event', 'event__circle').order_by('-requested_at')[:10]
    signups_data = [{
        'id': str(s.id),
        'status': s.status,
        'requested_at': s.requested_at.isoformat(),
        'event': {
            'id': str(s.event.id),
            'title': s.event.title,
            'start_datetime': s.event.start_datetime.isoformat(),
            'circle_name': s.event.circle.name,
            'circle_id': str(s.event.circle_id),
            'visibility': s.event.visibility,
        },
    } for s in recent_signups]

    # Upcoming published events from all my circles
    from django.utils import timezone as tz
    circle_events = Event.objects.filter(
        circle_id__in=my_circle_ids, published=True,
        start_datetime__gte=tz.now(),
    ).select_related('circle').order_by('start_datetime')[:20]

    # Batch-load signups
    signup_map = {}
    if circle_events:
        for su in EventSignup.objects.filter(event__in=circle_events, user=user):
            signup_map[su.event_id] = su

    events_data = [{
        'id': str(e.id),
        'title': e.title,
        'start_datetime': e.start_datetime.isoformat(),
        'end_datetime': e.end_datetime.isoformat(),
        'location': e.location,
        'visibility': e.visibility,
        'circle_name': e.circle.name,
        'circle_id': str(e.circle_id),
        'my_signup_status': signup_map[e.id].status if e.id in signup_map else None,
    } for e in circle_events]

    return JsonResponse({
        'recent_signups': signups_data,
        'circle_events': events_data,
    })


@require_GET
@login_required_json
def admin_overview(request):
    if not request.user.is_site_manager:
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    from circles.models import Circle, CircleMembership
    from events.models import Event, EventSignup
    return JsonResponse({
        'users_count': User.objects.filter(is_active=True).count(),
        'circles_count': Circle.objects.count(),
        'memberships_count': CircleMembership.objects.filter(active=True).count(),
        'events_count': Event.objects.count(),
        'pending_signups_count': EventSignup.objects.filter(status='PENDING').count(),
    })


@require_GET
@login_required_json
def admin_users(request):
    if not request.user.is_site_manager:
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    qs = User.objects.all().order_by('-created_at')
    search = request.GET.get('search', '').strip().lower()
    if search:
        qs = qs.filter(Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
    items, pagination = paginate_qs(request, qs, default_per_page=50)
    return JsonResponse({
        'users': [{
            'id': str(u.id), 'email': u.email,
            'first_name': u.first_name, 'last_name': u.last_name,
            'phone': u.phone, 'is_active': u.is_active,
            'is_site_manager': u.is_site_manager,
            'created_at': u.created_at.isoformat(),
        } for u in items],
        'pagination': pagination,
    })
