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
        return models.Supplier.objects.all()

    def measurements(self):
        """Return all measurements."""
        return models.Measurement.objects.all()

    def api_starting_points(self):
        return models.ApiStartingPoint.objects.all()

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


class SupplierView(AppView):
    """View for a supplier's data overview."""
    template_name = 'lizard_geodin/supplier.html'

    @property
    def page_title(self):
        return _('Supplier {name}').format(name=self.supplier.name)

    @property
    def edit_link(self):
        return '/admin/lizard_geodin/supplier/{pk}/'.format(
            pk=self.supplier.pk)

    @property
    def supplier(self):
        """Return supplier."""
        return get_object_or_404(models.Supplier,
                                 slug=self.kwargs['slug'])

    @property
    def projects(self):
        projects = defaultdict(list)
        for measurement in self.supplier.measurements.all():
            projects[measurement.project].append(measurement)
        result = []
        for project in sorted(projects.keys()):
            result.append((project, projects[project]))
        return result

    @property
    def breadcrumbs(self):
        base = super(SupplierView, self).breadcrumbs
        return base + [_breadcrumb_element(self.supplier)]


class MeasurementView(UiView):
    """Debug view for a measurement."""
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


class PointListView(ViewContextMixin, TemplateView):
    """Display a list of all points. Optionally provide point slugs as get parameters
    """
    template_name = 'lizard_geodin/point_list.html'

    def filter_request_points(self, points):
        """Filter out items that are not selected in the filter pane.
        """
        filters = {}
        try:
            filters = self.request.session['filter-measurements']
        except:
            pass
        result = []
        for point in points:
            filter_key = 'Supplier::%d' % point.measurement.supplier.id
            filter_key_param = 'Parameter::%d' % point.measurement.parameter.id
            if ((filter_key not in filters or filters[filter_key] == 'true') and
                (filter_key_param not in filters or filters[filter_key_param] == 'true')):
                # This object is wanted.
                result.append(point)
        return result

    def points(self):
        points = models.Point.objects.all()
        slugs = self.request.GET.getlist('slug')
        if slugs:
            points = points.filter(slug__in=slugs)
        points = self.filter_request_points(points)
        return points


class PointView(ViewContextMixin, TemplateView):
    template_name = 'lizard_geodin/point.html'

    @property
    def point(self):
        return get_object_or_404(models.Point,
                                 slug=self.kwargs['slug'])

    @property
    def extra(self):
        return self.request.GET.get('extra', 'False') == 'True'

    @property
    def width(self):
        return self.request.GET.get('width', 900)

    @property
    def height(self):
        return self.request.GET.get('height', 240)


class MultiplePointsView(ViewContextMixin, TemplateView):
    template_name = 'lizard_geodin/point.html'

    @property
    def width(self):
        return self.request.GET.get('width', 500)

    @property
    def height(self):
        return self.request.GET.get('height', 100)

    @property
    def points(self):
        points = models.Point.objects.all()
        slugs = self.request.GET.getlist('slug')
        if slugs:
            points = points.filter(slug__in=slugs)
        return points[:10]  # max 10!
