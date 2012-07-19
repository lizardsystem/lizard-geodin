# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals
import json

# from lizard_map.views import MapView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from lizard_ui.layout import Action
from lizard_ui.views import UiView
from lizard_map.views import AppView
from lizard_map.lizard_widgets import WorkspaceAcceptable

from lizard_geodin import models


ADAPTER_NAME = 'lizard_geodin_points'


def _breadcrumb_element(obj):
    """Return breadcrumb element for geodin object."""
    return Action(name=obj.name,
                  url=obj.get_absolute_url())


class ProjectsOverview(UiView):
    """Simple overview page with list of projects."""
    template_name = 'lizard_geodin/projects_overview.html'
    page_title = _('Overview of Geodin projects')
    edit_link = '/admin/lizard_geodin/apistartingpoint/'

    def projects(self):
        """Return all projects."""
        return models.Project.objects.all()


class ProjectView(AppView):
    """View for a project's data selection hierarchy."""
    template_name = 'lizard_geodin/project.html'

    @property
    def page_title(self):
        return _('Project {name}').format(name=self.project.name)

    @property
    def edit_link(self):
        return '/admin/lizard_geodin/project/{pk}/'.format(
            pk=self.project.pk)

    @property
    def project(self):
        return get_object_or_404(models.Project, slug=self.kwargs['slug'])

    # @property
    # def location_types(self):
    #     return models.LocationType.objects.all()

    # @property
    # def investigation_types(self):
    #     return models.InvestigationType.objects.all()

    # @property
    # def data_types(self):
    #     return models.DataType.objects.all()

    @property
    def hierarchy(self):
        tree = self.project.metadata['hierarchy']
        for level1 in tree:
            for level2 in level1['subitems']:
                for level3 in level2['subitems']:
                    if 'measurement_id' in level3:
                        # Add it as a WorkspaceAcceptable.
                        id = level3['measurement_id']
                        measurement = models.Measurement.objects.get(id=id)
                        acceptable = WorkspaceAcceptable(
                            name=measurement.name,
                            adapter_name=ADAPTER_NAME,
                            adapter_layer_json={
                                'measurement_id': id})
                        level3['acceptable'] = acceptable
        return tree

    @property
    def measurements(self):
        return self.project.measurements.all()

    @property
    def breadcrumbs(self):
        base = super(ProjectView, self).breadcrumbs
        return base + [_breadcrumb_element(self.project)]


class MeasurementView(ProjectView):
    """View for a measurement inside a project."""
    template_name = 'lizard_geodin/measurement.html'

    @property
    def page_title(self):
        return _('Measurement {name}').format(name=self.measurement.name)

    @property
    def measurement(self):
        """Return selected measurement"""
        return get_object_or_404(models.Measurement, pk=self.kwargs['measurement_id'])

    @property
    def breadcrumbs(self):
        base = super(MeasurementView, self).breadcrumbs
        return base + [_breadcrumb_element(self.measurement)]

    @property
    def num_points(self):
        return self.measurement.points.count()

    @property
    def first_point(self):
        return self.measurement.points.all()[0]


def point_flot_data(request, point_id=None):
    point = get_object_or_404(models.Point, pk=int(point_id))
    the_json = json.dumps({'data': point.timeseries()}, indent=2)
    return HttpResponse(the_json, mimetype='application/json')
