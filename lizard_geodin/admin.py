from __future__ import unicode_literals
import logging

from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext as _

from lizard_geodin import models

logger = logging.getLogger(__name__)


class ApiStartingPointAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'source_url')
    actions = ['reload']

    def reload(self, request, queryset):
        num_updated = 0
        for api_starting_point in queryset:
            try:
                api_starting_point.load_from_geodin()
                num_updated += 1
            except Exception, e:
                msg = ("Something went wrong when updating %s. " +
                       "Look at %s directly. %s")
                msg = msg % (api_starting_point.name,
                             api_starting_point.source_url,
                             e)
                logger.exception(msg)
                messages.error(request, msg)
        self.message_user(
            request,
            "Reloaded %s api starting points." % (num_updated))

    reload.short_description = _(
        "Update list of available projects from API.")


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('slug', 'active', 'name', 'source_url')
    list_editable = ('active', )


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.ApiStartingPoint, ApiStartingPointAdmin)
admin.site.register(models.LocationType)
admin.site.register(models.InvestigationType)
admin.site.register(models.DataType)
