"""
Accounts app forms — RegistrationForm and ProfileUpdateForm.
"""
from django import forms

from apps.accounts.models import User

# Only amateur and coach are valid registration/profile roles (admin is internal)
REGISTRATION_ROLE_CHOICES = [
    ("amateur", "Amateur"),
    ("coach", "Coach"),
]


class RegistrationForm(forms.Form):
    """
    Form for new user registration.

    Validates:
    - username: required, must not already exist
    - email: required, must be unique across existing User accounts
    - password: required, minimum 8 characters
    - password_confirm: must match password
    - role: must be 'amateur' or 'coach'
    """

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
        error_messages={"required": "Please enter a username."},
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        error_messages={"required": "Please enter your email address."},
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={"required": "Please enter a password."},
    )
    password_confirm = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={"required": "Please confirm your password."},
    )
    role = forms.ChoiceField(
        choices=REGISTRATION_ROLE_CHOICES,
        error_messages={"required": "Please select a role.", "invalid_choice": "Please select a valid role."},
    )

    def clean_email(self):
        """Ensure the email address is not already registered."""
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )
        return email

    def clean_password(self):
        """Enforce minimum password length of 8 characters."""
        password = self.cleaned_data.get("password", "")
        if len(password) < 8:
            raise forms.ValidationError(
                "Your password must be at least 8 characters long."
            )
        return password

    def clean(self):
        """Cross-field validation: password and password_confirm must match."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "The two passwords you entered do not match.")

        return cleaned_data


class ProfileUpdateForm(forms.Form):
    """
    Form for updating an existing user's profile.

    Validates:
    - email: required, must be a valid email format
    - role: must be 'amateur' or 'coach'
    """

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        error_messages={
            "required": "Please enter your email address.",
            "invalid": "Please enter a valid email address.",
        },
    )
    role = forms.ChoiceField(
        choices=REGISTRATION_ROLE_CHOICES,
        error_messages={
            "required": "Please select a role.",
            "invalid_choice": "Please select a valid role.",
        },
    )
