# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals
from collections import defaultdict
from pprint import pprint
import logging

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
import requests

logger = logging.getLogger(__name__)


# Notes: the source_url isn't our own source, but the url of our list of
# subitems.
# And the subitems aren't all unique, they might be pre-existing.
# So: update them, but maintain a list somewhere of items that have been
# recently changed, otherwise it takes a long time.
# But I fear there's a lot of m2m stuff around.
# Perhaps work around it with json?
#
# The hierarchy is a display hierarchy, really, not a database hierarchy. So
# perhaps I just need to store the hierarchy with name and slug per project?
# And retain the real DB objects for extra info about those items?


class Common(models.Model):
    """Abstract base class for the Geodin models.

    There's some automatic machinery in here to make it easy to sync between
    Geodin's json and our database models. ``.update_from_json()`` updates the
    objects's info from a snippet of json. ``.json_from_source_url()``
    reliably grabs the json from the server in case there's a source url
    field.

    There are three attributes you have to fill in to get it to work:

    - ``id_field`` is the field in the json that we use as slug in our
      database. This way our numeric database ID doesn't have to match
      Geodin's.

    - ``field_mapping`` is a dict that maps our model's fields to keys in the
      json dictionary. ``.update_from_json()`` automatically sets those
      fields.

    - ``subitems_mapping`` is the key in the json dictionary that lists the
      subitems. The mapping value is the model that should be created.

    - ``create_subitems`` to tell whether to automatically create subitems.

    """
    # Four attributes to help the automatic json conversion mechanism.
    id_field = 'Id'
    field_mapping = {}
    subitems_mapping = {}
    create_subitems = False
    auto_fill_metadata = False
    # The common fields.
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
        return self.name or self.slug

    def update_from_json(self, the_json):
        self.slug = the_json.pop(self.id_field)
        for our_field, json_field in self.field_mapping.items():
            if not json_field in the_json:
                # logger.warn("Field %s not available in %r", json_field, self)
                continue
            setattr(self, our_field, the_json.pop(json_field))
        if self.auto_fill_metadata:
            self.metadata = the_json
        else:
            for key in the_json:
                if key not in self.subitems_mapping:
                    logger.debug("Unknown key %s: %s", key, the_json[key])
        self.save()

    @classmethod
    def create_or_update_from_json(cls, the_json, extra_kwargs=None,
                                   already_handled=None):
        if extra_kwargs is None:
            extra_kwargs = {}
        slug = the_json[cls.id_field]
        if already_handled is not None:
            if slug in already_handled[cls]:
                logger.debug("Slug %s already handled, omitting", slug)
                return
        kwargs = {'slug': slug}
        kwargs.update(extra_kwargs)
        obj, is_created = cls.objects.get_or_create(**kwargs)
        obj.update_from_json(the_json)
        logger.debug("Created %r.", obj)
        if already_handled is not None:
            already_handled[cls].append(obj.slug)
        if cls.create_subitems:
            # Create subitems.
            for field, item_class in cls.subitems_mapping.items():
                for json_item in the_json[field]:
                    item_class.create_or_update_from_json(
                        json_item, already_handled=already_handled)
        return obj


    def json_from_source_url(self):
        """Return json from our source_url.

        Note: ``source_url`` is a convention, not every one of our subclasses
        has it. But having this method here is handy.
        """
        if not self.source_url:
            raise ValueError("We need a source_url to update ourselves from.")
        response = requests.get(self.source_url)
        if response.json is None:
            msg = "No json found. HTTP status code was %s, text was \n%s"
            raise ValueError(msg % (response.status_code, response.text))
        return response.json


class DataType(Common):
    """Type of measurement that has been done.

    You need to do something with an investigation type. The data type tells
    you what you did with it, like analyzing it in a geotechnical lab. It
    results in a set of parameters like "dx=..., dy=..., dz=...".
    """
    field_mapping = {'name': 'Name'}

    # Probably TODO: add parameters via extra json field? Including their
    # description?

    class Meta:
        verbose_name = _('data type')
        verbose_name_plural = _('data types')

    def update_from_json(self, the_json):
        # This one is custom!
        pprint(the_json)
        print "############"
        self.slug = the_json.pop(self.id_field)
        for our_field, json_field in self.field_mapping.items():
            if not json_field in the_json:
                # logger.warn("Field %s not available in %r", json_field, self)
                continue
            setattr(self, our_field, the_json.pop(json_field))
        # for key in the_json:
        #     if key not in self.subitems_mapping:
        #         logger.debug("Unknown key %s: %s", key, the_json[key])
        self.metadata = {'fields': the_json.pop('Fields')}
        # ^^^ I don't know if we actually need this.
        self.save()


class InvestigationType(Common):
    """Source of the measures.

    Source means where the measure physically came from. A ground sample, for
    instance.
    """
    field_mapping = {'name': 'Name'}
    subitems_mapping = {'DataTypes': DataType}
    # create_subitems = True

    class Meta:
        verbose_name = _('investigation type')
        verbose_name_plural = _('investigation types')


class LocationType(Common):
    """Unknown; seems to be for setting attributes."""
    field_mapping = {'name': 'Name'}
    subitems_mapping = {'InvestigationTypes': InvestigationType}
    # create_subitems = True

    class Meta:
        verbose_name = _('location type')
        verbose_name_plural = _('location types')


class Project(Common):
    """Geodin project, it is the starting point for the API.
    """
    field_mapping = {'source_url': 'Url',
                     'name': 'Name'}

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
        'ApiStartingPoint',
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
        """Load our data from the Geodin API.

        What we receive is a list of location types. In the end, we get
        location types and data types and measures, which are a set of points.

        """
        the_json = self.json_from_source_url()
        already_handled = defaultdict(list)
        # Clean up old measurement data.
        logger.debug("Deleting %s old measurements.",
                     Measurement.objects.filter(project=self).count())
        Measurement.objects.filter(project=self).delete()
        for location_dict in the_json:
            location_type = LocationType.create_or_update_from_json(
                location_dict,
                already_handled=already_handled)
            for investigation_dict in location_dict['InvestigationTypes']:
                investigation_type = InvestigationType.create_or_update_from_json(
                    investigation_dict,
                    already_handled=already_handled)
                for data_dict in investigation_dict['DataTypes']:
                    points = data_dict.pop('Points')
                    data_type = DataType.create_or_update_from_json(
                        data_dict,
                        already_handled=already_handled)
                    if not points:
                        logger.debug("No measurements found.")
                        continue
                    name = ', '.join([location_type.name,
                                      investigation_type.name,
                                      data_type.name])
                    measurement = Measurement(
                        name=name,
                        project=self,
                        location_type=location_type,
                        investigation_type=investigation_type,
                        data_type=data_type)
                    measurement.save()
                    logger.debug("Created a measurement: %s", name)
                    for point_dict in points:
                        point = Point.create_or_update_from_json(point_dict)
                        point.measurement = measurement
                        point.save()


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
        """Load our data from the Geodin API.

        What we receive is a list of projects.
        """
        the_json = self.json_from_source_url()
        already_handled = {Project: []}
        for json_item in the_json:
            Project.create_or_update_from_json(
                json_item,
                extra_kwargs={'api_starting_point': self},
                already_handled=already_handled)

        loaded_projects_slugs = already_handled[Project]
        for unknown_project in Project.objects.exclude(
            slug__in=loaded_projects_slugs, api_starting_point=self):
            unknown_project.active = False
            unknown_project.save()


class Measurement(models.Model):
    """The hierarchy of geodin boils down to this really-unnamed class.


    """
    name = models.CharField(
        _('name'),
        max_length=255,
        null=True,
        blank=True)
    # slug = models.SlugField(
    #     _('slug'))
    metadata = JSONField(
        _('metadata'),
        help_text=_("Extra metadata provided by Geodin"),
        null=True,
        blank=True)
    project = models.ForeignKey(
        'Project',
        null=True,
        blank=True,
        related_name='measurements')
    location_type = models.ForeignKey(
        'LocationType',
        null=True,
        blank=True,
        related_name='measurements')
    investigation_type = models.ForeignKey(
        'InvestigationType',
        null=True,
        blank=True,
        related_name='measurements')
    data_type = models.ForeignKey(
        'DataType',
        null=True,
        blank=True,
        related_name='measurements')

    class Meta:
        verbose_name = _('measurement')
        verbose_name_plural = _('measurements')

    def __unicode__(self):
        return self.name

    def fields(self):
        return ', '.join(self.data_type.metadata['fields'])

    def num_points(self):
        return self.points.count()

    def first_point(self):
        return self.points.all()[0]


class Point(Common):
    """Data point."""
    auto_fill_metadata = True
    field_mapping = {'timeseries_url': 'Url',
                     'name': 'Name',
                     'x': 'Xcoord',
                     'y': 'Ycoord',
                     'z': 'Zcoord',
                     }
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    measurement = models.ForeignKey(
        'Measurement',
        null=True,
        blank=True,
        related_name='points')
    timeseries_url = models.URLField(
        _('timeseries url'),
        help_text=_(
            "Geodin URL that gives the last couple of days' data."),
        null=True,
        blank=True)

    what_it_looks_like = {
        'Name': 'S1',
        'Ycoord': '1337.779',
        'Zcoord': '1.6685',
        'Url':
            'http://borealis.fugro-nederland.nl/borportal/geodinwebservice.exe/getportalpage?layout=Prism_Deformation_1_All&portal=10&objectid1=NIJ0010007SEN000',
        '__type': 'GdpMeasurementPoint:#ServiceLibrary',
        'Xcoord': '959.1575',
        'Dx': '0',
        'Dy': '0',
        'Geodpoint': 'M',
        'Dz': '0'}

    class Meta:
        verbose_name = _('point with data')
        verbose_name_plural = _('points with data')

    def content_for_display(self):
        result = {}
        for field_name in self.field_mapping:
            result[field_name] = getattr(self, field_name)
        if self.metadata is not None:
            result.update(self.metadata)
        return sorted(result.items())
