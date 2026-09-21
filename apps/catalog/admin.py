from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

from .models import OPTIONS_PER_QUESTION, AnswerOption, Category, Question, validate_option_set


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "color_preview",
        "active_question_count",
        "display_order",
        "is_active",
    ]
    list_editable = ["display_order", "is_active"]
    prepopulated_fields = {"slug": ["name"]}

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_active_questions=Count("questions", filter=Q(questions__is_active=True)))
        )

    @admin.display(description="Aktif soru", ordering="_active_questions")
    def active_question_count(self, obj):
        return obj._active_questions

    @admin.display(description="Renk")
    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:14px;height:14px;border-radius:4px;'
            'background:{};vertical-align:middle"></span> {}',
            obj.color_hex,
            obj.color_hex,
        )


class AnswerOptionFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        options = [
            (form.cleaned_data.get("text", ""), form.cleaned_data.get("is_correct", False))
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
        ]
        try:
            validate_option_set(options)
        except ValidationError as exc:
            raise ValidationError(exc.messages) from exc


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    formset = AnswerOptionFormSet
    extra = OPTIONS_PER_QUESTION
    max_num = OPTIONS_PER_QUESTION
    fields = ["display_order", "text", "is_correct"]

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else OPTIONS_PER_QUESTION


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["short_text", "category", "difficulty", "is_active", "times_served", "accuracy"]
    list_filter = ["category", "difficulty", "is_active"]
    search_fields = ["text", "external_ref"]
    readonly_fields = ["times_served", "times_correct", "created_at", "updated_at"]
    inlines = [AnswerOptionInline]
    actions = ["activate", "deactivate"]

    @admin.display(description="Soru")
    def short_text(self, obj):
        return obj.text[:90]

    @admin.display(description="Doğruluk")
    def accuracy(self, obj):
        if not obj.times_served:
            return "—"
        return f"%{100 * obj.times_correct / obj.times_served:.0f}"

    @admin.action(description="Seçili soruları aktif et")
    def activate(self, request, queryset):
        self.message_user(request, f"{queryset.update(is_active=True)} soru aktif edildi.")

    @admin.action(description="Seçili soruları pasif et")
    def deactivate(self, request, queryset):
        self.message_user(request, f"{queryset.update(is_active=False)} soru pasif edildi.")
