import logging

from django.core.management.base import BaseCommand

from lizard_geodin import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = """Load all geodin jsons and cache them permanently."""

    def handle(self, *args, **options):
        for model in [models.ApiStartingPoint, models.Project, models.Point]:
            for obj in model.objects.all():
                logger.info("Refreshing %s.", obj)
                key = obj.source_url
                if not key:
                    logger.warn("Obj without a json url: %s", obj)
                    continue
                obj.json_from_source_url(from_cache_is_ok=False)
