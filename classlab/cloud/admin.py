from django.contrib import admin

from .models import ClusterConfig
from .models import ResourceQuota

admin.site.register(ClusterConfig)
admin.site.register(ResourceQuota)
