"""
Accounts app views — registration, login, logout, profile.

Requirements: 1.2, 1.5, 1.6, 1.7, 2.2, 2.3, 2.5
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from datetime import timedelta

from apps.accounts.forms import ProfileUpdateForm, RegistrationForm
from apps.accounts.models import UserSession
from apps.accounts.services import (
    authenticate_user,
    invalidate_sessions,
    register_user,
    update_profile,
)


class RegisterView(View):
    """
    Handles new user registration.

    GET  — render a blank RegistrationForm.
    POST — validate the form; on success create the user, log them in, and
           redirect to the profile page; on failure re-render with errors.

    Requirements: 1.2
    """

    template_name = "accounts/register.html"

    def get(self, request):
        form = RegistrationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = register_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                role=form.cleaned_data["role"],
            )
            login(request, user)
            return redirect("/accounts/profile/")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    """
    Handles user authentication.

    GET  — render a blank login form.
    POST — authenticate via email + password; on success create a UserSession
           record, call Django's login(), and redirect to home; on failure
           render with a generic error that does NOT reveal which field failed
           (Requirement 1.6).  Suspended accounts receive a generic
           "account unavailable" message.

    Requirements: 1.5, 1.6
    """

    template_name = "accounts/login.html"
    _generic_error = "Invalid credentials. Please check your details and try again."
    _suspended_error = "This account is currently unavailable. Please contact support."

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = authenticate_user(email, password)

        if user is None:
            # Do not reveal whether email or password was wrong (Req 1.6).
            return render(
                request,
                self.template_name,
                {"error": self._generic_error},
            )

        if user.is_suspended:
            # Generic message — do not confirm suspension status (design doc).
            return render(
                request,
                self.template_name,
                {"error": self._suspended_error},
            )

        # Record the session for forced-invalidation support (Req 2.3).
        login(request, user)
        # Ensure session is saved so session_key is available
        if not request.session.session_key:
            request.session.create()
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key,
            expires_at=timezone.now() + timedelta(
                seconds=request.session.get_expiry_age()
            ),
        )

        return redirect("/")


class LogoutView(View):
    """
    Handles user logout.

    Accepts both POST and GET so that a simple link can trigger logout during
    development; production templates should use a POST form with CSRF token.

    Invalidates all tracked sessions for the user, then calls Django's
    logout() and redirects to home.

    Requirements: 1.7, 2.3
    """

    def get(self, request):
        return self._logout(request)

    def post(self, request):
        return self._logout(request)

    def _logout(self, request):
        if request.user.is_authenticated:
            invalidate_sessions(request.user)
        logout(request)
        return redirect("/")


class ProfileView(LoginRequiredMixin, View):
    """
    Displays and updates the authenticated user's profile.

    GET  — render the profile page with user data and a pre-filled
           ProfileUpdateForm.
    POST — validate the form; on success call update_profile() and show a
           confirmation message via Django's messages framework; on failure
           re-render with errors.

    Requirements: 2.2, 2.3, 2.5
    """

    template_name = "accounts/profile.html"

    def get(self, request):
        form = ProfileUpdateForm(
            initial={
                "email": request.user.email,
                "role": request.user.role,
            }
        )
        return render(request, self.template_name, {"form": form, "user": request.user})

    def post(self, request):
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            update_profile(request.user, form.cleaned_data)
            messages.success(request, "Your profile has been updated successfully.")
            # Re-initialise the form with the freshly saved values.
            form = ProfileUpdateForm(
                initial={
                    "email": request.user.email,
                    "role": request.user.role,
                }
            )
        return render(request, self.template_name, {"form": form, "user": request.user})
