from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_site_manager(self, email, password=None, **extra_fields):
        """Create a site manager — the platform-level admin role."""
        extra_fields['is_site_manager'] = True
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Django compat hook (called by manage.py createsuperuser).
        Delegates to create_site_manager. Does NOT create a Django superuser
        because this project does not use Django admin.
        """
        return self.create_site_manager(email, password, **extra_fields)
