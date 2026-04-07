import uuid
from django.db import models
from django.conf import settings


class Circle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'circles_circle'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name


class CircleMembership(models.Model):
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('CIRCLE_ADMIN', 'Circle Admin'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'circles_membership'
        unique_together = ('user', 'circle')
        indexes = [
            models.Index(fields=['circle', 'active']),
            models.Index(fields=['user', 'active']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.circle.name} ({self.role})'


class CircleInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, unique=True)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='invites')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'circles_invite'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['circle', 'is_active']),
        ]

    def __str__(self):
        return f'Invite to {self.circle.name} ({self.token[:8]}...)'
