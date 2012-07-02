# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from lizard_map.views import MapView
from lizard_ui.views import UiView

from lizard_geodin import models


class ProjectsOverview(UiView):
    """Simple overview page with list of projects."""
    template_name = 'lizard_geodin/projects_overview.html'
    page_title = _('Overview of Geodin projects')

    def projects(self):
        """Return all projects."""
        return models.Project.objects.all()


class ProjectView(MapView):
    """View for a project's data selection hierarchy."""
    template_name = 'lizard_geodin/project.html'

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


