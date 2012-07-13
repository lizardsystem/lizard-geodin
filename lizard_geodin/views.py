# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals
import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.translation import ugettext as _
# from lizard_map.views import MapView
from lizard_ui.views import UiView

from lizard_geodin import models


class ProjectsOverview(UiView):
    """Simple overview page with list of projects."""
    template_name = 'lizard_geodin/projects_overview.html'
    page_title = _('Overview of Geodin projects')
    edit_link = '/admin/lizard_geodin/apistartingpoint/'

    def projects(self):
        """Return all projects."""
        return models.Project.objects.all()


class ProjectView(UiView):
    """View for a project's data selection hierarchy."""
    template_name = 'lizard_geodin/project.html'

    @property
    def edit_link(self):
        return '/admin/lizard_geodin/project/{pk}/'.format(
            pk=self.project.pk)

    @property
    def project(self):
        return get_object_or_404(models.Project, slug=self.kwargs['slug'])

    @property
    def location_types(self):
        return models.LocationType.objects.all()

    @property
    def investigation_types(self):
        return models.InvestigationType.objects.all()

    @property
    def data_types(self):
        return models.DataType.objects.all()

    @property
    def measurements(self):
        return self.project.measurements.all()


def point_flot_data(request, point_id=None):
    point = models.Point.objects.get(id=point_id)
    the_json = json.dumps({'data': point.timeseries()})
    return HttpResponse(the_json)
