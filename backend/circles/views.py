import uuid as uuid_lib
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from .models import Circle, CircleMembership, CircleInvite
from project.utils import parse_json, login_required_json, validate_slug, paginate_qs


def serialize_circle(circle, members_count=None):
    data = {
        'id': str(circle.id),
        'name': circle.name,
        'slug': circle.slug,
        'description': circle.description,
        'created_at': circle.created_at.isoformat(),
        'updated_at': circle.updated_at.isoformat(),
    }
    if members_count is not None:
        data['members_count'] = members_count
    return data


def serialize_membership(m):
    return {
        'id': str(m.id),
        'user_id': str(m.user_id),
        'user_email': m.user.email,
        'user_first_name': m.user.first_name,
        'user_last_name': m.user.last_name,
        'circle_id': str(m.circle_id),
        'role': m.role,
        'joined_at': m.joined_at.isoformat(),
        'active': m.active,
    }


def serialize_invite(inv):
    circle_name = ''
    try:
        circle_name = inv.circle.name
    except Exception:
        pass
    return {
        'id': str(inv.id),
        'token': inv.token,
        'circle_id': str(inv.circle_id),
        'circle_name': circle_name,
        'created_by_email': inv.created_by.email if inv.created_by_id else None,
        'expires_at': inv.expires_at.isoformat(),
        'used_at': inv.used_at.isoformat() if inv.used_at else None,
        'is_active': inv.is_active,
        'created_at': inv.created_at.isoformat(),
    }


def _is_circle_admin(user, circle):
    return CircleMembership.objects.filter(
        user=user, circle=circle, role='CIRCLE_ADMIN', active=True
    ).exists()


def _can_manage(user, circle):
    return user.is_site_manager or _is_circle_admin(user, circle)


def _check_last_admin(circle, exclude_membership_id):
    """Return True if removing/demoting this membership would leave zero admins."""
    other_admins = CircleMembership.objects.filter(
        circle=circle, role='CIRCLE_ADMIN', active=True
    ).exclude(id=exclude_membership_id).count()
    return other_admins == 0


# ── My circles ──────────────────────────────────────────────
@require_GET
@login_required_json
def my_circles(request):
    memberships = CircleMembership.objects.filter(
        user=request.user, active=True
    ).select_related('circle').order_by('-joined_at')
    return JsonResponse({
        'circles': [{
            **serialize_circle(m.circle),
            'role': m.role,
            'membership_id': str(m.id),
        } for m in memberships]
    })


# ── Active circle ───────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
@login_required_json
def active_circle(request):
    if request.method == 'GET':
        circle = request.user.active_circle
        if circle:
            membership = CircleMembership.objects.filter(
                user=request.user, circle=circle, active=True
            ).first()
            return JsonResponse({
                'circle': serialize_circle(circle),
                'role': membership.role if membership else None,
            })
        return JsonResponse({'circle': None, 'role': None})

    data = parse_json(request)
    if not data:
        return JsonResponse({'error': 'Invalid JSON', 'code': 'invalid_json'}, status=400)
    circle_id = data.get('circle_id')
    if circle_id is None:
        request.user.active_circle = None
        request.user.save(update_fields=['active_circle'])
        return JsonResponse({'circle': None, 'role': None})

    membership = CircleMembership.objects.filter(
        user=request.user, circle_id=circle_id, active=True
    ).select_related('circle').first()

    if not membership and not request.user.is_site_manager:
        return JsonResponse({'error': 'Not a member of this circle', 'code': 'not_member'}, status=403)

    try:
        circle = membership.circle if membership else Circle.objects.get(id=circle_id)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)

    request.user.active_circle = circle
    request.user.save(update_fields=['active_circle'])
    return JsonResponse({
        'circle': serialize_circle(circle),
        'role': membership.role if membership else 'SITE_MANAGER',
    })


# ── Circle list / create ───────────────────────────────────
@require_http_methods(['GET', 'POST'])
@login_required_json
def circles_list_create(request):
    if request.method == 'GET':
        if not request.user.is_site_manager:
            return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
        qs = Circle.objects.annotate(
            members_count=Count('memberships', filter=Q(memberships__active=True))
        ).order_by('-created_at')
        search = request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(slug__icontains=search))
        items, pagination = paginate_qs(request, qs, default_per_page=50)
        return JsonResponse({
            'circles': [serialize_circle(c, members_count=c.members_count) for c in items],
            'pagination': pagination,
        })

    if not request.user.is_site_manager:
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    data = parse_json(request)
    if not data:
        return JsonResponse({'error': 'Invalid JSON', 'code': 'invalid_json'}, status=400)
    name = (data.get('name') or '').strip()
    slug = (data.get('slug') or '').strip().lower().replace(' ', '-')
    description = (data.get('description') or '').strip()
    if not name or not slug:
        return JsonResponse({'error': 'Name and slug are required', 'code': 'missing_fields'}, status=400)
    if not validate_slug(slug):
        return JsonResponse({'error': 'Slug must contain only lowercase letters, numbers, and hyphens', 'code': 'invalid_slug'}, status=400)
    if Circle.objects.filter(slug=slug).exists():
        return JsonResponse({'error': 'Slug already exists', 'code': 'slug_exists'}, status=409)
    with transaction.atomic():
        circle = Circle.objects.create(name=name, slug=slug, description=description)
        CircleMembership.objects.create(user=request.user, circle=circle, role='CIRCLE_ADMIN')
    return JsonResponse(serialize_circle(circle), status=201)


# ── Circle detail ───────────────────────────────────────────
@require_http_methods(['GET', 'PATCH', 'DELETE'])
@login_required_json
def circle_detail(request, pk):
    try:
        circle = Circle.objects.get(id=pk)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)

    if request.method == 'GET':
        is_member = CircleMembership.objects.filter(
            user=request.user, circle=circle, active=True
        ).exists()
        if not is_member and not request.user.is_site_manager:
            return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
        mc = CircleMembership.objects.filter(circle=circle, active=True).count()
        return JsonResponse(serialize_circle(circle, members_count=mc))

    if request.method == 'PATCH':
        if not _can_manage(request.user, circle):
            return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
        data = parse_json(request)
        if data:
            if 'name' in data:
                circle.name = data['name'].strip()
            if 'description' in data:
                circle.description = data['description'].strip()
            circle.save()
        return JsonResponse(serialize_circle(circle))

    if not request.user.is_site_manager:
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    circle.delete()
    return JsonResponse({'ok': True})


# ── Members ─────────────────────────────────────────────────
@require_GET
@login_required_json
def circle_members(request, pk):
    try:
        circle = Circle.objects.get(id=pk)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    qs = CircleMembership.objects.filter(
        circle=circle, active=True
    ).select_related('user')
    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    sort = request.GET.get('sort', 'joined_at')
    if sort == 'name':
        qs = qs.order_by('user__first_name', 'user__last_name')
    elif sort == 'role':
        qs = qs.order_by('-role', 'joined_at')
    else:
        qs = qs.order_by('joined_at')
    items, pagination = paginate_qs(request, qs, default_per_page=50)
    return JsonResponse({
        'members': [serialize_membership(m) for m in items],
        'pagination': pagination,
    })


@require_POST
@login_required_json
def circle_member_remove(request, pk, mid):
    try:
        circle = Circle.objects.get(id=pk)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    with transaction.atomic():
        try:
            membership = CircleMembership.objects.select_for_update().get(
                id=mid, circle=circle, active=True
            )
        except CircleMembership.DoesNotExist:
            return JsonResponse({'error': 'Member not found', 'code': 'not_found'}, status=404)
        # Last-admin protection
        if membership.role == 'CIRCLE_ADMIN' and _check_last_admin(circle, mid):
            return JsonResponse({
                'error': 'Cannot remove the last admin of a circle',
                'code': 'last_admin',
            }, status=400)
        membership.active = False
        membership.save(update_fields=['active'])
        # Clear active_circle if it was this circle
        from accounts.models import User
        User.objects.filter(id=membership.user_id, active_circle=circle).update(active_circle=None)
    return JsonResponse({'ok': True})


@require_POST
@login_required_json
def member_promote(request, pk, mid):
    try:
        circle = Circle.objects.get(id=pk)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    try:
        membership = CircleMembership.objects.select_related('user').get(
            id=mid, circle=circle, active=True
        )
    except CircleMembership.DoesNotExist:
        return JsonResponse({'error': 'Member not found', 'code': 'not_found'}, status=404)
    membership.role = 'CIRCLE_ADMIN'
    membership.save(update_fields=['role'])
    return JsonResponse(serialize_membership(membership))


@require_POST
@login_required_json
def member_demote(request, pk, mid):
    try:
        circle = Circle.objects.get(id=pk)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    with transaction.atomic():
        try:
            membership = CircleMembership.objects.select_for_update().select_related('user').get(
                id=mid, circle=circle, active=True
            )
        except CircleMembership.DoesNotExist:
            return JsonResponse({'error': 'Member not found', 'code': 'not_found'}, status=404)
        if membership.role == 'CIRCLE_ADMIN' and _check_last_admin(circle, mid):
            return JsonResponse({
                'error': 'Cannot demote the last admin of a circle',
                'code': 'last_admin',
            }, status=400)
        membership.role = 'MEMBER'
        membership.save(update_fields=['role'])
    return JsonResponse(serialize_membership(membership))


# ── Invites ─────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
@login_required_json
def circle_invites(request, pk):
    try:
        circle = Circle.objects.get(id=pk)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)

    if request.method == 'GET':
        invites = CircleInvite.objects.filter(
            circle=circle
        ).select_related('created_by', 'circle').order_by('-created_at')
        items, pagination = paginate_qs(request, invites, default_per_page=50)
        return JsonResponse({'invites': [serialize_invite(i) for i in items], 'pagination': pagination})

    invite = CircleInvite.objects.create(
        circle=circle,
        created_by=request.user,
        token=str(uuid_lib.uuid4()),
        expires_at=timezone.now() + timedelta(days=7),
    )
    invite.circle = circle
    return JsonResponse(serialize_invite(invite), status=201)


@require_POST
@login_required_json
def invite_deactivate(request, pk, iid):
    try:
        circle = Circle.objects.get(id=pk)
    except Circle.DoesNotExist:
        return JsonResponse({'error': 'Circle not found', 'code': 'not_found'}, status=404)
    if not _can_manage(request.user, circle):
        return JsonResponse({'error': 'Forbidden', 'code': 'forbidden'}, status=403)
    try:
        invite = CircleInvite.objects.select_related('circle', 'created_by').get(id=iid, circle=circle)
    except CircleInvite.DoesNotExist:
        return JsonResponse({'error': 'Invite not found', 'code': 'not_found'}, status=404)
    invite.is_active = False
    invite.save(update_fields=['is_active'])
    return JsonResponse(serialize_invite(invite))


# ── Accept invite (race-safe) ──────────────────────────────
@require_POST
@login_required_json
def invite_accept(request, token):
    with transaction.atomic():
        try:
            invite = CircleInvite.objects.select_for_update().select_related('circle').get(token=token)
        except CircleInvite.DoesNotExist:
            return JsonResponse({'error': 'Invalid invitation link', 'code': 'not_found'}, status=404)
        if not invite.is_active:
            return JsonResponse({'error': 'This invitation has been deactivated', 'code': 'invite_inactive'}, status=400)
        if invite.used_at is not None:
            return JsonResponse({'error': 'This invitation has already been used', 'code': 'invite_used'}, status=400)
        if invite.expires_at < timezone.now():
            return JsonResponse({'error': 'This invitation has expired', 'code': 'invite_expired'}, status=400)
        if CircleMembership.objects.filter(
            user=request.user, circle=invite.circle, active=True
        ).exists():
            return JsonResponse({'error': 'You are already a member of this circle', 'code': 'already_member'}, status=409)
        CircleMembership.objects.create(
            user=request.user, circle=invite.circle, role='MEMBER',
        )
        invite.used_at = timezone.now()
        invite.is_active = False
        invite.save(update_fields=['used_at', 'is_active'])
    return JsonResponse({
        'ok': True,
        'circle': serialize_circle(invite.circle),
        'message': f'You have joined {invite.circle.name}',
    })


# ── Invite info (public) ───────────────────────────────────
@require_GET
def invite_info(request, token):
    try:
        invite = CircleInvite.objects.select_related('circle').get(token=token)
    except CircleInvite.DoesNotExist:
        return JsonResponse({'error': 'Invalid invitation link', 'code': 'not_found'}, status=404)
    valid = invite.is_active and invite.used_at is None and invite.expires_at >= timezone.now()
    return JsonResponse({
        'valid': valid,
        'circle_name': invite.circle.name if valid else None,
        'circle_id': str(invite.circle_id) if valid else None,
        'expires_at': invite.expires_at.isoformat() if valid else None,
    })
