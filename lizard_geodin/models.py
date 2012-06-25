# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField


class Common(models.Model):
    name = models.CharField(
        _('name'),
        max_length=50,  # Geodin has 40 max.
        null=True,
        blank=True)

    slug = models.SlugField(_('slug'))

    metadata = JSONField(
        _('metadata'),
        help_text=_("Extra metadata provided by Geodin"),
        null=True,
        blank=True)

    class Meta:
        abstract = True


class Project(Common):
    """Geodin project, it is the starting point for the API."""

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')


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

