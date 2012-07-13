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
    url(r'^(?P<slug>[^/]+)/$',
        views.ProjectView.as_view(),
        name='lizard_geodin_project_view'),
    # url(r'^(?P<slug>[^/]+)/(?P<measurement_pk>[^/]+)$',
    #     views.ProjectView.as_view(),
    #     name='lizard_geodin_project_view'),
    )
urlpatterns += lizard_ui.urls.debugmode_urlpatterns()
