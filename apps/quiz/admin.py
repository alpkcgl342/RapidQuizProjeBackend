from django.contrib import admin

from .models import QuizSession, QuizSessionQuestion


class ReadOnlyAdminMixin:
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class QuizSessionQuestionInline(ReadOnlyAdminMixin, admin.TabularInline):
    model = QuizSessionQuestion
    fields = [
        "order",
        "question",
        "outcome",
        "selected_option",
        "elapsed_ms",
        "points",
        "served_at",
        "answered_at",
    ]
    readonly_fields = fields
    extra = 0
    can_delete = False


@admin.register(QuizSession)
class QuizSessionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "category",
        "status",
        "score",
        "correct_count",
        "wrong_count",
        "timeout_count",
        "client_platform",
        "started_at",
    ]
    list_filter = ["category", "status", "client_platform", "started_at"]
    exclude = ["token"]
    inlines = [QuizSessionQuestionInline]
    date_hierarchy = "started_at"
