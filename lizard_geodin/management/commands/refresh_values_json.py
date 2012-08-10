import logging
from optparse import make_option

from django.core.cache import cache
from django.core.management.base import BaseCommand

from lizard_geodin import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = """Refresh the cached Geodin json with values for the graphs.  By
default, only the already-cached jsons will be refreshed. Otherwise we'll
probably be DOSing the Geodin server.
"""

    option_list = BaseCommand.option_list + (
        make_option('--all', '-a', dest='all', action="store_true",
                    default=False,
                    help="Cache all possible jsons"),
        )

    def handle(self, *args, **options):
        refresh_all = options['all']
        if refresh_all:
            logger.info("Refreshing ALL jsons.")
        for point in models.Point.objects.all():
            key = point.source_url
            if not key:
                logger.warn("Point without a json url: %s", point)
                continue
            cached_value = cache.get(key)
            if cached_value is None and not refresh_all:
                logger.debug("Omitting %s: not already cached.", point)
                continue
            logger.debug("Refreshing %s.", point)
            point.json_from_source_url(from_cache_is_ok=False)
