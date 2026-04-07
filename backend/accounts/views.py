from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
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
    return JsonResponse({
        'authenticated': True,
        'user': serialize_user(request.user),
    })


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
    """Deactivate account: sets is_active=False, clears memberships, logs out."""
    user = request.user
    with transaction.atomic():
        from circles.models import CircleMembership
        CircleMembership.objects.filter(user=user, active=True).update(active=False)
        user.active_circle = None
        user.is_active = False
        user.save(update_fields=['active_circle', 'is_active'])
    logout(request)
    return JsonResponse({'ok': True, 'message': 'Account deactivated. All circle memberships have been removed.'})


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
        qs = qs.filter(
            models_Q(email__icontains=search) |
            models_Q(first_name__icontains=search) |
            models_Q(last_name__icontains=search)
        )
    items, pagination = paginate_qs(request, qs, default_per_page=50)
    return JsonResponse({
        'users': [{
            'id': str(u.id),
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'is_active': u.is_active,
            'is_site_manager': u.is_site_manager,
            'created_at': u.created_at.isoformat(),
        } for u in items],
        'pagination': pagination,
    })


# Import Q for search
from django.db.models import Q as models_Q
