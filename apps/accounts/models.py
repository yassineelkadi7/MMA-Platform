"""
Accounts app models — User and UserSession.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("amateur", "Amateur"),
        ("coach", "Coach"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="amateur")
    preferences = models.JSONField(default=dict, blank=True)
    is_suspended = models.BooleanField(default=False)
    # username, email, password inherited from AbstractUser


class UserSession(models.Model):
    """Tracks active Django sessions per user for forced invalidation."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tracked_sessions"
    )
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
