# Lots of copy/paste from lizard-riool, btw.  [reinout]
# from __future__ import unicode_literals  # Mapnik dislikes this.
import json
import logging
import os

from django.conf import settings
from django.contrib.gis import geos
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from lizard_map import coordinates
from lizard_map.mapnik_helper import add_datasource_point
from lizard_map.models import ICON_ORIGINALS
from lizard_map.models import WorkspaceItemError
from lizard_map.symbol_manager import SymbolManager
from lizard_map.workspace import WorkspaceItemAdapter
import mapnik

from lizard_geodin import models



EPSILON = 0.0001

DATABASE = settings.DATABASES['default']
PARAMS = {
    'host': DATABASE['HOST'],
    'port': DATABASE['PORT'],
    'user': DATABASE['USER'],
    'password': DATABASE['PASSWORD'],
    'dbname': DATABASE['NAME'],
    # 'srid': models.SRID,
}
ICON_STYLE = {'icon': 'meetpuntPeil.png',
              'mask': ('meetpuntPeil_mask.png', ),
              'color': (0, 0, 1, 0)}

logger = logging.getLogger(__name__)


def html_to_mapnik(color):
    r, g, b = color[0:2], color[2:4], color[4:6]
    rr, gg, bb = int(r, 16), int(g, 16), int(b, 16)
    return rr / 255.0, gg / 255.0, bb / 255.0, 1.0


def default_database_params():
    """Get default database params. Use a copy of the dictionary
    because it is mutated by the functions that use it."""
    return PARAMS.copy()


class GeodinPoints(WorkspaceItemAdapter):
    # javascript_hover_handler = 'popup_hover_handler'

    def __init__(self, *args, **kwargs):
        super(GeodinPoints, self).__init__(*args, **kwargs)
        self.measurement_id = self.layer_arguments['measurement_id']
        try:
            self.measurement = models.Measurement.objects.get(
                pk=self.measurement_id)
        except models.Measurement.DoesNotExist:
            raise WorkspaceItemError(
                "Measurement %s doesn't exist." % self.measurement_id)

    def style(self):
        """Return mapnik point style.
        """
        symbol_manager = SymbolManager(
            ICON_ORIGINALS,
            os.path.join(settings.MEDIA_ROOT, 'generated_icons'))
        output_filename = symbol_manager.get_symbol_transformed(
            ICON_STYLE['icon'], **ICON_STYLE)
        output_filename_abs = os.path.join(
            settings.MEDIA_ROOT, 'generated_icons', output_filename)
        # use filename in mapnik pointsymbolizer
        point_looks = mapnik.PointSymbolizer(
            output_filename_abs, 'png', 16, 16)
        point_looks.allow_overlap = True
        layout_rule = mapnik.Rule()
        layout_rule.symbols.append(point_looks)
        points_style = mapnik.Style()
        points_style.rules.append(layout_rule)
        return points_style

    def layer(self, layer_ids=None, request=None):
        "Return Mapnik layers and styles."
        layers, styles = [], {}
        styles["pointsStyle"] = self.style()
        layer = mapnik.Layer("Geodin points layer", coordinates.WGS84)
        layer.datasource = mapnik.PointDatasource()
        layer.styles.append("pointsStyle")

        for point in self.measurement.points.all():
            add_datasource_point(
                layer.datasource,
                point.location.x,
                point.location.y,
                'style',
                'pointsStyle')

        layers.append(layer)
        return layers, styles

    def legend(self, updates=None):
        legend = []
        # for classname, classdesc, _, _, color in CLASSES:
        #     r, g, b, a = html_to_mapnik(color)

        #     icon = SYMBOL_MANAGER.get_symbol_transformed(
        #         RIOOL_ICON_LARGE, color=(r, g, b, a))

        #     legend.append({
        #             'img_url': os.path.join(
        #                 settings.MEDIA_URL, 'generated_icons', icon),
        #             'description': "klasse %s (%s)" % (classname, classdesc),
        #             })
        return legend

    def extent(self, identifiers=None):
        "Return the extent in Google projection"
        north = None
        south = None
        east = None
        west = None
        wgs0coord_x, wgs0coord_y = coordinates.rd_to_wgs84(0.0, 0.0)
        for point in self.measurement.points.all():
            x = point.location.x
            y = point.location.y
            if (abs(x - wgs0coord_x) > EPSILON or
                abs(y - wgs0coord_y) > EPSILON):

                if x > east or east is None:
                    east = x
                if x < west or west is None:
                    west = x
                if y < south or south is None:
                    south = y
                if y > north or north is None:
                    north = y
        if north is None:
            logger.warn("Data points are all at (0, 0) RD, cannot calculate "
                        "extent!")
            return

        west_transformed, north_transformed = coordinates.wgs84_to_google(
            west, north)
        east_transformed, south_transformed = coordinates.wgs84_to_google(
            east, south)
        return  {
            'north': north_transformed,
            'west': west_transformed,
            'south': south_transformed,
            'east': east_transformed}

    def search(self, x, y, radius=None):
        """We only use this for the mouse hover function; return the
        minimal amount of information necessary to show it."""

        pnt = geos.Point(x, y, srid=900913)
        points = self.measurement.points.filter(
            location__distance_lte=(pnt, radius)).distance(pnt).order_by('distance')
        if not points:
            return []

        point = points[0]

        return [{'name': point.name,
                 'distance': point.distance.m,
                 'workspace_item': self.workspace_item,
                 'identifier': {'point_id': point.id},
                 }]

    # def location(self, point_id, layout=None):
    #     """
    #     returns location dict.

    #     requires identifier_json
    #     """
    #     point = get_object_or_404(models.Point, pk=point_id)
    #     identifier = {'point_id': point.id}
    #     return {
    #         'name': '%s' % point.name,
    #         'workspace_item': self.workspace_item,
    #         'identifier': identifier,
    #         'google_coords': coordinates.wgs84_to_google(
    #             point.location.x, point.location.y),
    #         'object': point,
    #         }

    def html(self, identifiers=None, layout_options=None):
        points = [get_object_or_404(models.Point, pk=identifier['point_id'])
                  for identifier in identifiers]
        return render_to_string(
            'lizard_geodin/point_popup.html',
            {'points': points})
