from django.contrib import admin

from .models import Organisation
from .models import OrganisationQuota


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


admin.site.register(OrganisationQuota)
