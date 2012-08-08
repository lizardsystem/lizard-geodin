# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals
from collections import defaultdict
import json

# from lizard_map.views import MapView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView

from lizard_ui.layout import Action
from lizard_ui.views import UiView
from lizard_ui.views import ViewContextMixin
from lizard_map.views import AppView

from lizard_geodin import models


def _breadcrumb_element(obj):
    """Return breadcrumb element for geodin object."""
    return Action(name=obj.name,
                  url=obj.get_absolute_url())


class ProjectsOverview(UiView):
    """Simple overview page with list of projects."""
    template_name = 'lizard_geodin/projects_overview.html'
    page_title = _('Overview of Geodin data')
    edit_link = '/admin/lizard_geodin/apistartingpoint/'

    def projects(self):
        """Return all active projects."""
        return models.Project.objects.filter(active=True)

    def suppliers(self):
        """Return all suppliers."""
        return models.Supplier.objects.filter()

    def measurements(self):
        """Return all measurements."""
        return models.Measurement.objects.filter()

    def show_activation_hint(self):
        """Return True if projects exist, but none are active."""
        if self.projects():
            return False
        if models.Project.objects.exists():
            return True
        return False


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
        """Return project (if it is active)."""
        return get_object_or_404(models.Project,
                                 slug=self.kwargs['slug'],
                                 active=True)

    @property
    def suppliers(self):
        suppliers = defaultdict(list)
        for measurement in self.project.measurements.all():
            suppliers[measurement.supplier].append(measurement)
        result = []
        for supplier in sorted(suppliers.keys()):
            result.append((supplier, suppliers[supplier]))
        return result

    @property
    def breadcrumbs(self):
        base = super(ProjectView, self).breadcrumbs
        return base + [_breadcrumb_element(self.project)]


class SupplierView(ProjectView):
    # TODO
    pass


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


class MeasurementPopupView(ViewContextMixin, TemplateView):
    template_name = 'lizard_geodin/measurement_popup.html'

    @property
    def measurement(self):
        """Return selected measurement"""
        return get_object_or_404(models.Measurement, pk=self.kwargs['measurement_id'])

    @property
    def num_points(self):
        return self.measurement.points.count()

    @property
    def first_point(self):
        return self.measurement.points.all()[0]
