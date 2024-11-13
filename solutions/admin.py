from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import AuditLog

# Default admin view of Auditlog
admin.site.register(AuditLog)


# Add auditlog as an inline of User
class AuditLogInline(admin.TabularInline):
    model = AuditLog
    fk_name = "user"
    readonly_fields = ["user", "message", "data", "timestamp"]
    extra = 0  # Don't show empty forms
    can_delete = False  # Prevent deletion through inline
    max_num = 0  # Prevent adding new through inline
    ordering = ["-timestamp"]  # Most recent first

    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding new logs through admin


# Unregister the default UserAdmin
admin.site.unregister(User)


# Create custom UserAdmin with inline
class CustomUserAdmin(UserAdmin):
    inlines = UserAdmin.inlines + (AuditLogInline,)


# Register the custom UserAdmin
admin.site.register(User, CustomUserAdmin)
