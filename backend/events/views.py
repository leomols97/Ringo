from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import Event, EventSignup
from circles.models import Circle, CircleMembership
from project.utils import parse_json, login_required_json


def serialize_event(event, user=None):
    data = {
        'id': str(event.id),
        'circle_id': str(event.circle_id),
        'title': event.title,
        'description': event.description,
        'location': event.location,
        'start_datetime': event.start_datetime.isoformat(),
        'end_datetime': event.end_datetime.isoformat(),
        'published': event.published,
        'created_by_id': str(event.created_by_id) if event.created_by_id else None,
        'created_at': event.created_at.isoformat(),
        'updated_at': event.updated_at.isoformat(),
    }
    if user:
        signup = EventSignup.objects.filter(event=event, user=user).first()
        data['my_signup_status'] = signup.status if signup else None
        data['my_signup_id'] = str(signup.id) if signup else None
    return data


def serialize_signup(s):
    return {
        'id': str(s.id),
        'event_id': str(s.event_id),
        'user_id': str(s.user_id),
        'user_email': s.user.email,
        'user_first_name': s.user.first_name,
        'user_last_name': s.user.last_name,
        'status': s.status,
        'requested_at': s.requested_at.isoformat(),
        'decided_at': s.decided_at.isoformat() if s.decided_at else None,
        'decided_by_id': str(s.decided_by_id) if s.decided_by_id else None,
    }


def _can_manage(user, circle):
    return user.is_site_manager or CircleMembership.objects.filter(
        user=user, circle=circle, role='CIRCLE_ADMIN', active=True
    ).exists()


# ── Events of active circle (user view) ────────────────────
@require_GET
@login_required_json
def active_circle_events(request):
    circle = request.user.active_circle
    if not circle:
        return JsonResponse({'events': [], 'circle': None})
    is_member = CircleMembership.objects.filter(
        user=request.user, circle=circle, active=True
    ).exists()
    if not is_member and not request.user.is_site_manager:
        return JsonResponse({'events': [], 'circle': None})
    events = Event.objects.filter(
        circle=circle, published=True
    ).order_by('start_datetime')
    return JsonResponse({
        'events': [serialize_event(e, request.user) for e in events],
        'circle': {'id': str(circle.id), 'name': circle.name},
    })


# ── Circle events (admin) ──────────────────────────────────
@require_http_methods(['GET', 'POST'])
@login_required_json
def circle_events(request, circle_id):
    try:
        circle = Circle.objects.get(id=circle_id)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found'}, status=404)
    if not _can_manage(request.user, circle):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method == 'GET':
        events = Event.objects.filter(circle=circle).order_by('-start_datetime')
        return JsonResponse({'events': [serialize_event(e) for e in events]})

    data = parse_json(request)
    if not data:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    title = (data.get('title') or '').strip()
    if not title:
        return JsonResponse({'error': 'Title is required'}, status=400)
    start_dt = parse_datetime(data.get('start_datetime', ''))
    end_dt = parse_datetime(data.get('end_datetime', ''))
    if not start_dt or not end_dt:
        return JsonResponse({'error': 'Valid start and end datetimes are required'}, status=400)
    event = Event.objects.create(
        circle=circle, title=title,
        description=(data.get('description') or '').strip(),
        location=(data.get('location') or '').strip(),
        start_datetime=start_dt, end_datetime=end_dt,
        published=data.get('published', True),
        created_by=request.user,
    )
    return JsonResponse(serialize_event(event), status=201)


# ── Event detail ────────────────────────────────────────────
@require_http_methods(['GET', 'PATCH', 'DELETE'])
@login_required_json
def event_detail(request, eid):
    try:
        event = Event.objects.select_related('circle').get(id=eid)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

    if request.method == 'GET':
        is_member = CircleMembership.objects.filter(
            user=request.user, circle=event.circle, active=True
        ).exists()
        if not is_member and not request.user.is_site_manager:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        return JsonResponse(serialize_event(event, request.user))

    if not _can_manage(request.user, event.circle):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method == 'DELETE':
        event.delete()
        return JsonResponse({'ok': True})

    data = parse_json(request)
    if data:
        if 'title' in data:
            event.title = data['title'].strip()
        if 'description' in data:
            event.description = data['description'].strip()
        if 'location' in data:
            event.location = data['location'].strip()
        if 'start_datetime' in data:
            dt = parse_datetime(data['start_datetime'])
            if dt:
                event.start_datetime = dt
        if 'end_datetime' in data:
            dt = parse_datetime(data['end_datetime'])
            if dt:
                event.end_datetime = dt
        if 'published' in data:
            event.published = bool(data['published'])
        event.save()
    return JsonResponse(serialize_event(event))


# ── Event signup ────────────────────────────────────────────
@require_POST
@login_required_json
def event_signup(request, eid):
    try:
        event = Event.objects.select_related('circle').get(id=eid)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    is_member = CircleMembership.objects.filter(
        user=request.user, circle=event.circle, active=True
    ).exists()
    if not is_member:
        return JsonResponse({'error': 'You must be a member of this circle'}, status=403)
    if EventSignup.objects.filter(event=event, user=request.user).exists():
        return JsonResponse({'error': 'Already signed up for this event'}, status=409)
    signup = EventSignup.objects.create(event=event, user=request.user, status='PENDING')
    signup.user = request.user  # ensure cached
    return JsonResponse(serialize_signup(signup), status=201)


# ── Event signups list (admin) ──────────────────────────────
@require_GET
@login_required_json
def event_signups(request, eid):
    try:
        event = Event.objects.select_related('circle').get(id=eid)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    if not _can_manage(request.user, event.circle):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    signups = EventSignup.objects.filter(event=event).select_related('user').order_by('-requested_at')
    return JsonResponse({
        'signups': [serialize_signup(s) for s in signups],
        'event': serialize_event(event),
    })


# ── Approve / reject signup ────────────────────────────────
@require_POST
@login_required_json
def signup_approve(request, sid):
    try:
        signup = EventSignup.objects.select_related('event__circle', 'user').get(id=sid)
    except EventSignup.DoesNotExist:
        return JsonResponse({'error': 'Signup not found'}, status=404)
    if not _can_manage(request.user, signup.event.circle):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    signup.status = 'APPROVED'
    signup.decided_at = timezone.now()
    signup.decided_by = request.user
    signup.save()
    return JsonResponse(serialize_signup(signup))


@require_POST
@login_required_json
def signup_reject(request, sid):
    try:
        signup = EventSignup.objects.select_related('event__circle', 'user').get(id=sid)
    except EventSignup.DoesNotExist:
        return JsonResponse({'error': 'Signup not found'}, status=404)
    if not _can_manage(request.user, signup.event.circle):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    signup.status = 'REJECTED'
    signup.decided_at = timezone.now()
    signup.decided_by = request.user
    signup.save()
    return JsonResponse(serialize_signup(signup))
