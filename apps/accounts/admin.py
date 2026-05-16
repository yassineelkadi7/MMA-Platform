"""
Accounts app admin configuration.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import User, UserSession
from apps.accounts.services import suspend_user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "date_joined", "is_suspended", "is_active")
    list_filter = ("role", "is_suspended", "is_active")
    search_fields = ("username", "email")
    actions = ["suspend_selected_users"]

    # Add role and is_suspended to the fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ("MMA Platform", {"fields": ("role", "preferences", "is_suspended")}),
    )

    @admin.action(description="Suspend selected users (invalidates sessions)")
    def suspend_selected_users(self, request, queryset):
        count = 0
        for user in queryset:
            if not user.is_suspended:
                suspend_user(user)
                count += 1
        self.message_user(request, f"{count} user(s) suspended and sessions invalidated.")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "session_key", "created_at", "expires_at")
    raw_id_fields = ("user",)
