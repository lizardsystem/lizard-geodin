# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals
import logging

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField


logger = logging.getLogger(__name__)


class Common(models.Model):
    name = models.CharField(
        _('name'),
        max_length=50,  # Geodin has 40 max.
        null=True,
        blank=True)
    slug = models.SlugField(_('slug'))
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


class ApiStartingPoint(Common):
    """Pointer at the Geodin API startpoint."""

    source_url = models.URLField(
        _('source url'),
        help_text=_("Geodin URL that lists the available projects."),
        null=True,
        blank=True)

    class Meta:
        verbose_name = _('API starting point')
        verbose_name_plural = _('API starting points')

    def update_from_geodin(self):
        """Load our data from the Geodin API."""
        if not self.source_url:
            raise ValueError("We need a source_url to update ourselves from.")
        logger.warn("Dummy update from geodin: %s", self.source_url)


class Project(Common):
    """Geodin project, it is the starting point for the API."""

    # TODO: field for location of project? For the ProjectsOverview page?
    source_url = models.URLField(
        _('source url'),
        help_text=_(
            "Geodin URL for automatically loading this project's data."),
        null=True,
        blank=True)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def get_absolute_url(self):
        return reverse('lizard_geodin_project_view',
                       kwargs={'slug': self.slug})

    def update_from_geodin(self):
        """Load our data from the Geodin API."""
        if not self.source_url:
            raise ValueError("We need a source_url to update ourselves from.")
        logger.warn("Dummy update from geodin: %s", self.source_url)


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

