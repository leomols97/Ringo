import json
import re
from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings


def parse_json(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return None


def login_required_json(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required', 'code': 'auth_required'}, status=401)
        if not request.user.is_active:
            return JsonResponse({'error': 'Account deactivated', 'code': 'account_deactivated'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def csrf_failure_view(request, reason=""):
    return JsonResponse({'error': 'CSRF verification failed', 'code': 'csrf_failed', 'detail': reason}, status=403)


# ── Validation helpers ──────────────────────────────────────

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def validate_email_format(email):
    if not email or len(email) > 254:
        return False
    return bool(EMAIL_RE.match(email))


def validate_password_strength(password):
    """Min 8 chars, at least one letter and one digit."""
    if len(password) < 8:
        return 'Password must be at least 8 characters'
    if not re.search(r'[a-zA-Z]', password):
        return 'Password must contain at least one letter'
    if not re.search(r'[0-9]', password):
        return 'Password must contain at least one digit'
    return None


def validate_slug(slug):
    if not slug or len(slug) > 255:
        return False
    return bool(SLUG_RE.match(slug))


# ── Rate limiting ───────────────────────────────────────────

def _rate_limit_key(request, email):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    return f'login_rl:{ip}:{email}'


def check_login_rate_limit(request, email):
    key = _rate_limit_key(request, email)
    attempts = cache.get(key, 0)
    max_attempts = getattr(settings, 'LOGIN_RATE_LIMIT_MAX', 10)
    if attempts >= max_attempts:
        return False
    return True


def record_login_attempt(request, email, success):
    key = _rate_limit_key(request, email)
    window = getattr(settings, 'LOGIN_RATE_LIMIT_WINDOW', 300)
    if success:
        cache.delete(key)
    else:
        attempts = cache.get(key, 0)
        cache.set(key, attempts + 1, window)


# ── Pagination helper ───────────────────────────────────────

def paginate_qs(request, queryset, default_per_page=50):
    """Return (page_items, pagination_meta) from a queryset."""
    try:
        page = max(1, int(request.GET.get('page', 1)))
        per_page = min(100, max(1, int(request.GET.get('per_page', default_per_page))))
    except (ValueError, TypeError):
        page, per_page = 1, default_per_page
    total = queryset.count()
    offset = (page - 1) * per_page
    items = list(queryset[offset:offset + per_page])
    return items, {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': max(1, (total + per_page - 1) // per_page),
    }
