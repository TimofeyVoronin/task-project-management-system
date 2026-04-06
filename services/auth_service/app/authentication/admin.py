from authentication.models import LoginHistory
from django.contrib import admin


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "created_at")
    search_fields = ("user__email", "ip_address", "user_agent")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
