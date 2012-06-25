from django.contrib import admin

from lizard_geodin import models


admin.site.register(models.Project)
admin.site.register(models.LocationType)
admin.site.register(models.InvestigationType)
admin.site.register(models.DataType)
