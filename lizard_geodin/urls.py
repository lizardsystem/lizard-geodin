# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

import lizard_ui.urls
import lizard_map.urls

from lizard_geodin import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ui/', include(lizard_ui.urls)),
    url(r'^map/', include(lizard_map.urls)),
    url(r'^$',
        views.ProjectsOverview.as_view(),
        name='lizard_geodin_projects_overview'),
    url(r'^flot/(?P<point_id>[^/]+)/$',
        views.point_flot_data,
        name='lizard_geodin_flot_data'),

    url(r'^point/$',
        views.PointListView.as_view(),
        name='lizard_geodin_point_list'),
    url(r'^point/(?P<slug>[^/]+)/$',
        views.PointView.as_view(),
        name='lizard_geodin_point'),
    url(r'^sidebar/point/(?P<slug>[^/]+)/$',
        views.SidebarPointView.as_view(),
        name='lizard_geodin_sidebar_point'),
    url(r'^multiple-points/$',
        views.MultiplePointsView.as_view(),
        name='lizard_geodin_multiple_points'),

    url(r'^project/(?P<slug>[^/]+)/$',
        views.ProjectView.as_view(),
        name='lizard_geodin_project_view'),
    url(r'^supplier/(?P<slug>[^/]+)/$',
        views.SupplierView.as_view(),
        name='lizard_geodin_supplier_view'),
    url(r'^measurement/(?P<measurement_id>[^/]+)/$',
        views.MeasurementView.as_view(),
        name='lizard_geodin_measurement_view'),
    url(r'^measurement/(?P<measurement_id>[^/]+)/popup/$',
        views.MeasurementPopupView.as_view(),
        name='lizard_geodin_measurement_popup_view'),
    )
urlpatterns += lizard_ui.urls.debugmode_urlpatterns()
