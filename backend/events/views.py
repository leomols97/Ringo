from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Q, Prefetch
from .models import Event, EventSignup
from circles.models import Circle, CircleMembership
from project.utils import parse_json, login_required_json, paginate_qs


def serialize_event(event, user=None, signup_map=None):
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
        if signup_map is not None:
            signup = signup_map.get(event.id)
        else:
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


def _is_member(user, circle):
    return CircleMembership.objects.filter(
        user=user, circle=circle, active=True
    ).exists()


# ── Events of active circle (user view) ────────────────────
@require_GET
@login_required_json
def active_circle_events(request):
    circle = request.user.active_circle
    if not circle:
        return JsonResponse({'events': [], 'circle': None})
    if not _is_member(request.user, circle) and not request.user.is_site_manager:
        return JsonResponse({'events': [], 'circle': None})
    events = list(Event.objects.filter(
        circle=circle, published=True
    ).order_by('start_datetime'))
    # Batch-load signups for this user to avoid N+1
    signup_map = {}
    if events:
        signups = EventSignup.objects.filter(
            event__in=events, user=request.user
        )
        signup_map = {s.event_id: s for s in signups}
    return JsonResponse({
        'events': [serialize_event(e, request.user, signup_map) for e in events],
        'circle': {'id': str(circle.id), 'name': circle.name},
    })


# ── Circle events (admin) ──────────────────────────────────
@require_http_methods(['GET', 'POST'])
@login_required_json
def circle_events(request, circle_id):
    try:
        circle = Circle.objects.get(id=circle_id)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)

    if request.method == 'GET':
        qs = Event.objects.filter(circle=circle)
        pub_filter = request.GET.get('published')
        if pub_filter == 'true':
            qs = qs.filter(published=True)
        elif pub_filter == 'false':
            qs = qs.filter(published=False)
        sort = request.GET.get('sort', '-start_datetime')
        if sort in ('start_datetime', '-start_datetime', 'title', '-title', 'created_at', '-created_at'):
            qs = qs.order_by(sort)
        else:
            qs = qs.order_by('-start_datetime')
        items, pagination = paginate_qs(request, qs, default_per_page=50)
        return JsonResponse({
            'events': [serialize_event(e) for e in items],
            'pagination': pagination,
        })

    data = parse_json(request)
    if not data:
        return JsonResponse({'error': 'Invalid JSON', 'code': 'invalid_json'}, status=400)
    title = (data.get('title') or '').strip()
    if not title:
        return JsonResponse({'error': 'Title is required', 'code': 'missing_fields'}, status=400)
    start_dt = parse_datetime(data.get('start_datetime', ''))
    end_dt = parse_datetime(data.get('end_datetime', ''))
    if not start_dt or not end_dt:
        return JsonResponse({'error': 'Valid start and end datetimes are required', 'code': 'invalid_datetime'}, status=400)
    if end_dt <= start_dt:
        return JsonResponse({'error': 'End datetime must be after start datetime', 'code': 'invalid_datetime'}, status=400)
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
        return JsonResponse({'error': 'Event not found', 'code': 'not_found'}, status=404)

    if request.method == 'GET':
        can_admin = _can_manage(request.user, event.circle)
        is_mem = _is_member(request.user, event.circle)
        if not is_mem and not request.user.is_site_manager:
            return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
        # Normal members cannot see unpublished events
        if not event.published and not can_admin:
            return JsonResponse({'error': 'Event not found', 'code': 'not_found'}, status=404)
        return JsonResponse(serialize_event(event, request.user))

    if not _can_manage(request.user, event.circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)

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
        return JsonResponse({'error': 'Event not found', 'code': 'not_found'}, status=404)
    # Cannot sign up for unpublished events
    if not event.published:
        return JsonResponse({'error': 'Event not found', 'code': 'not_found'}, status=404)
    if not _is_member(request.user, event.circle):
        return JsonResponse({'error': 'You must be a member of this circle', 'code': 'not_member'}, status=403)
    if EventSignup.objects.filter(event=event, user=request.user).exists():
        return JsonResponse({'error': 'Already signed up for this event', 'code': 'already_signed_up'}, status=409)
    signup = EventSignup.objects.create(event=event, user=request.user, status='PENDING')
    signup.user = request.user
    return JsonResponse(serialize_signup(signup), status=201)


# ── Event signups list (admin) ──────────────────────────────
@require_GET
@login_required_json
def event_signups(request, eid):
    try:
        event = Event.objects.select_related('circle').get(id=eid)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, event.circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
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
        return JsonResponse({'error': 'Signup not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, signup.event.circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    signup.status = 'APPROVED'
    signup.decided_at = timezone.now()
    signup.decided_by = request.user
    signup.save(update_fields=['status', 'decided_at', 'decided_by'])
    return JsonResponse(serialize_signup(signup))


@require_POST
@login_required_json
def signup_reject(request, sid):
    try:
        signup = EventSignup.objects.select_related('event__circle', 'user').get(id=sid)
    except EventSignup.DoesNotExist:
        return JsonResponse({'error': 'Signup not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, signup.event.circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    signup.status = 'REJECTED'
    signup.decided_at = timezone.now()
    signup.decided_by = request.user
    signup.save(update_fields=['status', 'decided_at', 'decided_by'])
    return JsonResponse(serialize_signup(signup))
