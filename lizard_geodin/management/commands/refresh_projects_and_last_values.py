import logging

from django.core.management.base import BaseCommand

from lizard_geodin import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = """Refresh the Projects which also refreshes the last values
of points.
"""

    def handle(self, *args, **options):
        for project in models.Project.objects.all():
            if not project.source_url:
                logger.warn("Skipping project without a json url: %s",
                            project)
                continue
            if not project.active:
                logger.info("Skipping inactive project: %s", project)
                continue
            logger.info("Refreshing %s.", project)
            project.load_from_geodin()
