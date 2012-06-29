# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals
import logging

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
import requests

logger = logging.getLogger(__name__)


class Common(models.Model):
    id_field = 'id'
    field_mapping = ()
    name = models.CharField(
        _('name'),
        max_length=50,  # Geodin has 40 max.
        null=True,
        blank=True)
    slug = models.SlugField(
        _('slug'),
        help_text=_("Often set automatically from the internal Geodin ID"))
    # TODO: lizard-security dataset foreign key.
    metadata = JSONField(
        _('metadata'),
        help_text=_("Extra metadata provided by Geodin"),
        null=True,
        blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def update_from_json(self, the_json):
        self.slug = the_json.pop(self.id_field)
        for our_field, json_field in self.field_mapping:
            setattr(self, our_field, the_json.pop(json_field))
        if the_json:
            logger.debug("Left-over json data: %s", the_json)
        self.save()


class ApiStartingPoint(Common):
    """Pointer at the Geodin API startpoint.

    The API starting point has a reload action that grabs the json at
    ``source_url`` and generates/updates the projects that are listed in
    there. By default, new projects are inactive.

    If a project that used to be listed by the API isn't listed anymore, it is
    automatically marked as inactive.
    """

    source_url = models.URLField(
        _('source url'),
        help_text=_("Geodin URL that lists the available projects."),
        null=True,
        blank=True)

    class Meta:
        verbose_name = _('API starting point')
        verbose_name_plural = _('API starting points')

    def load_from_geodin(self):
        """Load our data from the Geodin API."""
        if not self.source_url:
            raise ValueError("We need a source_url to update ourselves from.")
        response = requests.get(self.source_url)
        if response.json is None:
            msg = "No json found. HTTP status code was %s, text was \n%s"
            raise ValueError(msg % (response.status_code, response.text))
        loaded_projects_ids = []
        for json_project in response.json:
            project, created = Project.objects.get_or_create(
                api_starting_point=self,
                slug=json_project['prj_id'])
            project.update_from_json(json_project)
            loaded_projects_ids.append(project.id)
        for unknown_project in Project.objects.exclude(
            pk__in=loaded_projects_ids):
            unknown_project.active=False
            unknown_project.save()


class Project(Common):
    """Geodin project, it is the starting point for the API."""
    id_field = 'prj_id'
    field_mapping = (('source_url', 'prj_url'),
                     ('name', 'prj_name'))

    # TODO: field for location of project? For the ProjectsOverview page?
    active = models.BooleanField(
        _('active'),
        help_text=_("Is the project used in this site?"),
        default=False)
    source_url = models.URLField(
        _('source url'),
        help_text=_(
            "Geodin URL for automatically loading this project's data."),
        null=True,
        blank=True)
    api_starting_point = models.ForeignKey(
        ApiStartingPoint,
        null=True,
        blank=True,
        related_name='location_types')

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ('-active', 'name')

    def get_absolute_url(self):
        return reverse('lizard_geodin_project_view',
                       kwargs={'slug': self.slug})

    def load_from_geodin(self):
        """Load our data from the Geodin API."""
        if not self.source_url:
            raise ValueError("We need a source_url to update ourselves from.")
        response = requests.get(self.source_url)
        if response.json is None:
            msg = "No json found. HTTP status code was %s, text was \n%s"
            raise ValueError(msg % (response.status_code, response.text))
        self.update_from_json(response.json)


class LocationType(Common):
    """Unknown; seems to be for setting attributes."""
    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        related_name='location_types')

    class Meta:
        verbose_name = _('location type')
        verbose_name_plural = _('location types')


class InvestigationType(Common):
    """Source of the measures.

    Source means where the measure physically came from. A ground sample, for
    instance.
    """
    location_type = models.ForeignKey(
        LocationType,
        null=True,
        blank=True,
        related_name='investigation_types')

    class Meta:
        verbose_name = _('investigation type')
        verbose_name_plural = _('investigation types')


class DataType(Common):
    """Type of measure that has been done.

    You need to do something with an investigation type. The data type tells
    you what you did with it, like analyzing it in a geotechnical lab. It
    results in a set of parameters like "dx=..., dy=..., dz=...".
    """
    investigation_type = models.ForeignKey(
        InvestigationType,
        null=True,
        blank=True,
        related_name='data_types')

    # Probably TODO: add parameters via extra json field? Including their
    # description?

    class Meta:
        verbose_name = _('data type')
        verbose_name_plural = _('data types')

