"""
Account service functions — business logic for user management.
"""
from typing import Optional

from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session

from .models import User, UserSession


def register_user(username: str, email: str, password: str, role: str) -> User:
    """
    Create a new User with the given credentials and role.

    Requirements: 1.2
    """
    user = User.objects.create_user(username=username, email=email, password=password)
    user.role = role
    user.save()
    return user


def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Look up a user by email (case-insensitive) and authenticate with Django's
    authenticate(). Returns the User on success, None otherwise.

    Does NOT reveal which field (email vs password) caused a failure.

    Requirements: 1.5
    """
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None

    authenticated = authenticate(username=user.username, password=password)
    return authenticated if authenticated is not None else None


def update_profile(user: User, data: dict) -> User:
    """
    Update a user's email and/or role from the provided data dict.
    Saves and returns the updated user.

    Requirements: 1.7
    """
    if "email" in data:
        user.email = data["email"]
    if "role" in data:
        user.role = data["role"]
    user.save()
    return user


def suspend_user(user: User) -> None:
    """
    Suspend a user account and invalidate all active sessions.

    Requirements: 9.4, 9.5
    """
    user.is_suspended = True
    user.save()
    invalidate_sessions(user)


def invalidate_sessions(user: User) -> None:
    """
    Delete all UserSession records for the user and the corresponding
    Django session store entries.

    Requirements: 2.3, 9.5
    """
    session_keys = list(
        UserSession.objects.filter(user=user).values_list("session_key", flat=True)
    )
    # Remove Django session store entries first
    Session.objects.filter(session_key__in=session_keys).delete()
    # Remove tracked session records
    UserSession.objects.filter(user=user).delete()
