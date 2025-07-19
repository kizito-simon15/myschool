# accounts/models.py (updated)

from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

TZ_PHONE_RE = r'^\+255\d{9}$'
tz_phone_validator = RegexValidator(TZ_PHONE_RE, "Use +255XXXXXXXXX format (Tanzanian mobile).")

class CustomUserManager(BaseUserManager):
    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("The phone number must be set")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, password, **extra_fields)

class CustomUser(AbstractUser):
    phone = models.CharField(
        max_length=13,
        unique=True,
        validators=[tz_phone_validator],
        verbose_name="Mobile Number"
    )
    email = None  # Remove email field

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="custom_user_set",  # Custom related_name to avoid clash
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",  # Custom related_name to avoid clash
        related_query_name="user",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']  # Username can still be used if needed, but phone is primary

    def __str__(self):
        return self.phone