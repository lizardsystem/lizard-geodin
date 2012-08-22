# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals
import datetime
import logging

import pytz
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point as GeosPoint
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from lizard_map.lizard_widgets import WorkspaceAcceptable
import dateutil.parser
import requests

ADAPTER_NAME = 'lizard_geodin_points'
POINT_JSON_CACHE_TIMEOUT = 120  # In seconds
FALLBACK_POINT_JSON_CACHE_TIMEOUT = 60 * 60  # One hour.

logger = logging.getLogger(__name__)


def timestamp_in_ms(date):
    # See http://people.iola.dk/olau/flot/examples/time.html
    date += datetime.timedelta(hours=4)  # Make it look good for flot.
    timestamp_in_seconds = int(date.strftime("%s"))
    return 1000 * timestamp_in_seconds


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
    cache_json_from_api = False
    json_request_timeout = 10
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
        private_fields = [key for key in the_json if key.startswith('_')]
        for key in private_fields:
            the_json.pop(key)
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
                return cls.objects.get(slug=slug)
        kwargs = {'slug': slug}
        kwargs.update(extra_kwargs)
        obj, is_created = cls.objects.get_or_create(**kwargs)
        if is_created:
            logger.info("Created %r.", obj)
        obj.update_from_json(the_json)
        if already_handled is not None:
            already_handled[cls].append(obj.slug)
        if cls.create_subitems:
            # Create subitems.
            for field, item_class in cls.subitems_mapping.items():
                for json_item in the_json[field]:
                    item_class.create_or_update_from_json(
                        json_item, already_handled=already_handled)
        return obj

    def json_from_source_url(self, from_cache_is_ok=True):
        """Return json from our source_url.

        Note: ``source_url`` is a convention, not every one of our subclasses
        has it. But having this method here is handy.

        Set ``from_cache_is_ok`` to False if you want to refresh the cache.

        """
        if not self.source_url:
            raise ValueError("We need a source_url to update ourselves from.")
        cache_key = self.source_url
        fallback_cache_key = 'FALLBACK' + self.source_url
        if self.cache_json_from_api and from_cache_is_ok:
            cache_result = cache.get(cache_key)
            if cache_result is not None:
                logger.debug("Returning cached json result.")
                return cache_result
        try:
            response = requests.get(self.source_url,
                                    timeout=self.json_request_timeout)
        except requests.exceptions.Timeout:
            if self.cache_json_from_api:
                # Try and grab the fallback cache value, which can be up to an
                # hour old.
                cache_result = cache.get(fallback_cache_key)
                if cache_result is not None:
                    logger.warn(
                        "Timeout on %s; returning fallback cache value",
                        self.source_url)
                    return cache_result
            raise
        if response.json is None:
            msg = "No json found. HTTP status code was %s, text was \n%s"
            msg = msg % (response.status_code, response.text)
            if self.cache_json_from_api:
                cache_result = cache.get(fallback_cache_key)
                if cache_result is not None:
                    logger.warn(msg + " Returning fallback cache value")
                    return cache_result
            raise ValueError(msg)
        result = response.json
        if self.cache_json_from_api:
            cache.set(cache_key, result, POINT_JSON_CACHE_TIMEOUT)
            cache.set(fallback_cache_key, result,
                      FALLBACK_POINT_JSON_CACHE_TIMEOUT)
            logger.debug("Caching json result from API.")
        return result


class Project(Common):
    """Geodin project, it is the starting point for the API.
    """
    json_request_timeout = 30  # One of 'em takes 25 seconds...
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

    def load_from_geodin(self, from_cache_is_ok=True):
        """Load our data from the Geodin API.

        What we receive is a list of location types. In the end, we get
        location types and data types and measures, which are a set of points.

        Note: the hierarchy is depended upon by ``ProjectView`` in our
        ``views.py``.

        """
        the_json = self.json_from_source_url(
            from_cache_is_ok=from_cache_is_ok)
        # already_handled = defaultdict(list)
        for location_dict in the_json:
            location_type_name = location_dict['Name']
            for investigation_dict in location_dict['InvestigationTypes']:
                investigation_type_name = investigation_dict['Name']
                for data_dict in investigation_dict['DataTypes']:
                    points = data_dict.pop('Points')
                    data_type_name = data_dict['Name']
                    if not points:
                        logger.debug(
                            "No points found, not creating a measurement.")
                        continue
                    for point_dict in points:
                        # Get supplier.
                        supplier_name = point_dict.pop('Leverancier')
                        supplier_slug = slugify(supplier_name)[:50]
                        supplier, is_created = Supplier.objects.get_or_create(
                            slug=supplier_slug)
                        if is_created:
                            supplier.name = supplier_name
                            supplier.save()
                        # Get parameter.
                        parameter_name = point_dict.pop('Description')
                        parameter_slug = slugify(parameter_name)[:50]
                        parameter, is_created = Parameter.objects.get_or_create(
                            slug=parameter_slug)
                        if is_created:
                            parameter.name = parameter_name
                            parameter.save()
                        # Get measurement.
                        measurement_name = '{project}: {parameter} ({supplier})'.format(
                            project=self.name,
                            parameter=parameter_name,
                            supplier=supplier_name)
                        measurement, created = Measurement.objects.get_or_create(
                            project=self,
                            parameter=parameter,
                            supplier=supplier)
                        if created:
                            logger.debug("Created a new measurement: %s",
                                         measurement_name)
                            measurement.location_type_name = location_type_name
                            measurement.investigation_type_name = investigation_type_name
                            measurement.data_type_name = data_type_name
                            measurement.name = measurement_name
                            measurement.save()
                        else:
                            logger.debug("Reusing existing measurement: %s",
                                         measurement_name)

                        try:
                            point = Point.create_or_update_from_json(point_dict)
                            point.measurement = measurement
                            point.set_location_from_xy()
                            point.save()
                        except ValueError:
                            logger.warn("Point has no x/y: %s", point_dict)


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

    A measurement is unique per project/location/investigation/datatype
    combination.
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
    location_type_name = models.CharField(
        _('location type'),
        max_length=50,
        null=True,
        blank=True)
    investigation_type_name = models.CharField(
        _('location type'),
        max_length=50,
        null=True,
        blank=True)
    data_type_name = models.CharField(
        _('location type'),
        max_length=50,
        null=True,
        blank=True)
    supplier = models.ForeignKey(
        'Supplier',
        null=True,
        blank=True,
        related_name='measurements')
    parameter = models.ForeignKey(
        'Parameter',
        null=True,
        blank=True,
        related_name='measurements')

    class Meta:
        verbose_name = _('measurement')
        verbose_name_plural = _('measurements')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('lizard_geodin_measurement_view',
                       kwargs={'measurement_id': self.id})

    def get_popup_url(self):
        return reverse('lizard_geodin_measurement_popup_view',
                       kwargs={'measurement_id': self.id})

    def workspace_acceptable(self):
        return WorkspaceAcceptable(
            name=self.name,
            adapter_name=ADAPTER_NAME,
            adapter_layer_json={'measurement_id': self.id})


class Supplier(models.Model):
    """Supplier/company that provides the measurement data apparatus."""
    name = models.CharField(
        _('name'),
        max_length=100,
        null=True,
        blank=True)
    slug = models.SlugField(
        _('slug'),
        help_text=_("Often set automatically from the internal Geodin ID"))
    html_color = models.CharField(max_length=20, default="#444444")

    def __unicode__(self):
        return self.name or self.slug

    def get_absolute_url(self):
        return reverse('lizard_geodin_supplier_view',
                       kwargs={'slug': self.slug})

    class Meta:
        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')


class Parameter(models.Model):
    """Parameter of a measurement, including unit."""
    name = models.CharField(
        _('name'),
        max_length=100,
        null=True,
        blank=True)
    slug = models.SlugField(
        _('slug'),
        help_text=_("Often set automatically from the internal Geodin ID"))
    unit = models.CharField(
        _('unit'),
        max_length=100,
        null=True,
        blank=True)

    def __unicode__(self):
        return self.name or self.slug

    class Meta:
        verbose_name = _('parameter of a measurement')
        verbose_name_plural = _('parameters of measurements')


class Point(Common):
    """Data point."""
    auto_fill_metadata = True
    cache_json_from_api = True
    field_mapping = {'source_url': 'Url',
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
    source_url = models.URLField(
        _('timeseries url'),
        help_text=_(
            "Geodin URL that gives the last couple of days' data."),
        null=True,
        blank=True)
    location = models.PointField(
        help_text=_(
            "Generated automatically from the x/y/z values."),
        null=True,
        blank=True)
    objects = models.GeoManager()

    class Meta:
        ordering = ('name', 'slug', )
        verbose_name = _('point with data')
        verbose_name_plural = _('points with data')

    def content_for_display(self):
        """Helper method. Return field/value tuples for showing the content.
        """
        result = {}
        for field_name in self.field_mapping:
            result[field_name] = getattr(self, field_name)
        if self.metadata is not None:
            result.update(self.metadata)
        return sorted(result.items())

    def timeseries(self, one_day_only=False):
        """Return last couple of days' timeseries data for flot.

        Note that it is by geodin's/anysense's design *one* single timeseries.

        What it returns is a one-item list of dictionaries with 'label' and
        'data' for flot. You can add 'color' and so yourself afterwards.

        """
        the_json = self.json_from_source_url()
        logger.debug("Got the json data from Geodin.")
        if not the_json:
            # Empty.
            return []

        line = []
        now = datetime.datetime.now(tz=pytz.timezone('Europe/Amsterdam'))
        if one_day_only:
            cutoff_date = now - datetime.timedelta(days=1)
        else:
            # Just one week.
            cutoff_date = now - datetime.timedelta(days=7)
        for timestep in the_json:
            date = timestep.pop('Date')
            if not 'Z' in date:
                date = date  + "Z"  # Assumption: we're in UTC.
            date = dateutil.parser.parse(date)
            # ^^^ Add TZ offset to correct the timezone differences.
            if date < cutoff_date:
                continue
            line.append((timestamp_in_ms(date), timestep['Value']))
        result = [{'label': self.measurement.parameter.name,
                   'data': line,
                   'min': timestamp_in_ms(cutoff_date),
                   'max': timestamp_in_ms(now)}]
        # TODO: needs the unit from the parameter, really, too. This still
        # needs to be imported, btw.
        return result

    def last_value(self):
        """Return last known value."""
        if (self.metadata is not None) and (len(self.metadata) == 2):
            # Date and a second key.
            keys = [key for key in self.metadata.keys()
                   if key != 'Date']
            if len(keys) == 1:
                # Yep, we've got only one.
                last_value_key = keys[0]
                return self.metadata[last_value_key]
        # Fallback: grab the json.
        the_json = self.json_from_source_url()
        last_timestep = the_json[-1]
        return last_timestep['Value']

    def set_location_from_xy(self):
        """x/y is assumed to be in WGS."""
        self.location = GeosPoint(float(self.x), float(self.y))

    def get_popup_url(self):
        return reverse('lizard_geodin_point', kwargs={'slug': self.slug})

    def __unicode__(self):
        try:
            return '%s (%s)' % (
                self.name, self.slug)
        except:
            return self.name or self.slug

