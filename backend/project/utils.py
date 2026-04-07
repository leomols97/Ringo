import json
from functools import wraps
from django.http import JsonResponse


def parse_json(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return None


def login_required_json(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not request.user.is_active:
            return JsonResponse({'error': 'Account deactivated'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def csrf_failure_view(request, reason=""):
    return JsonResponse({'error': 'CSRF verification failed', 'detail': reason}, status=403)
