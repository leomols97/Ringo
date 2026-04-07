import uuid
from django.db import models
from django.conf import settings


class Event(models.Model):
    VISIBILITY_CHOICES = [('PUBLIC', 'Public'), ('PRIVATE', 'Private')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey('circles.Circle', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    published = models.BooleanField(default=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PRIVATE')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events_event'
        indexes = [
            models.Index(fields=['circle', 'published']),
            models.Index(fields=['start_datetime']),
            models.Index(fields=['visibility']),
        ]

    def __str__(self):
        return self.title


class EventSignup(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='signups')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_signups')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='signup_decisions'
    )

    class Meta:
        db_table = 'events_signup'
        unique_together = ('event', 'user')
        indexes = [models.Index(fields=['event', 'status']), models.Index(fields=['user'])]

    def __str__(self):
        return f'{self.user.email} -> {self.event.title} ({self.status})'
