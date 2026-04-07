import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import CustomUserManager


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_site_manager = models.BooleanField(default=False)
    active_circle = models.ForeignKey(
        'circles.Circle', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return self.email
