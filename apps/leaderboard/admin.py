from django.contrib import admin

from .models import LeaderboardEntry


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    """Salt okunur; yalnızca uygunsuz kayıtları silmek için silme yetkisi var."""

    list_display = [
        "nickname",
        "score",
        "category",
        "correct_count",
        "total_elapsed_ms",
        "created_at",
    ]
    list_filter = ["category", "created_at"]
    search_fields = ["nickname"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
