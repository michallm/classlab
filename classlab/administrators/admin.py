from django.contrib import admin

from .models import Administrator


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ("user", "organisation")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "organisation__name",
    )
    list_filter = ("organisation",)
    raw_id_fields = ("user",)
    ordering = ("user__email",)
    autocomplete_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "organisation")
