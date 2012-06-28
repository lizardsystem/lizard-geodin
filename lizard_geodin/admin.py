from django.contrib import admin

from lizard_geodin import models


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'source_url')


class ApiStartingPointAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'source_url')


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.ApiStartingPoint, ApiStartingPointAdmin)
admin.site.register(models.LocationType)
admin.site.register(models.InvestigationType)
admin.site.register(models.DataType)
