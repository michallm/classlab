from django import forms
from django.contrib import admin
from django_ace import AceWidget
from reversion.admin import VersionAdmin

from .models import App
from .models import AppCategory
from .models import AppTemplate
from .models import AppTemplateKeyValue


class AppTemplateAdminForm(forms.ModelForm):
    manifest = forms.CharField(
        widget=AceWidget(mode="yaml", theme="github", width="100%", height="500px"),
    )

    class Meta:
        model = AppTemplate
        fields = "__all__"  # noqa: DJ007


@admin.register(AppTemplate)
class AppTemplateAdmin(VersionAdmin):
    form = AppTemplateAdminForm
    list_display = ("name", "template_id", "category", "created_at", "updated_at")
    list_filter = ("category", "created_at", "updated_at")
    search_fields = ("name", "template_id", "category__name", "description")
    autocomplete_fields = ("organisations",)
    readonly_fields = ("template_id", "created_at", "updated_at")


@admin.register(AppCategory)
class AppCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ("name", "template", "created_at", "updated_at")
    list_filter = ("template", "created_at", "updated_at")
    search_fields = ("name", "template__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AppTemplateKeyValue)
class AppTemplateKeyValueAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "type",
        "required",
        "editable",
        "end_user_editable",
        "created_at",
        "updated_at",
    )
    list_filter = ("type", "required", "editable", "end_user_editable")
    search_fields = ("key",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("app_template", "name", "description")}),
        (
            "Details",
            {
                "fields": (
                    "key",
                    "type",
                    "required",
                    "editable",
                    "secret",
                    "end_user_editable",
                ),
            },
        ),
        (
            "Generated",
            {
                "fields": (
                    "generated",
                    "generator",
                ),
            },
        ),
        (
            "Managed",
            {"fields": ("student_only", "teacher_only")},
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
