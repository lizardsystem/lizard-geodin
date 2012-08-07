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
    url(r'^(?P<slug>[^/]+)/$',  # project slug
        views.ProjectView.as_view(),
        name='lizard_geodin_project_view'),
    url(r'^(?P<slug>[^/]+)/(?P<measurement_id>[^/]+)/$',
        views.MeasurementView.as_view(),
        name='lizard_geodin_measurement_view'),
    url(r'^measurement/(?P<measurement_id>[^/]+)/popup/$',
        views.MeasurementPopupView.as_view(),
        name='lizard_geodin_measurement_popup_view'),
    )
urlpatterns += lizard_ui.urls.debugmode_urlpatterns()
