# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import json

from django.test import TestCase

from lizard_geodin import models


class ProjectModelTest(TestCase):

    def test_project_smoke(self):
        project = models.Project()
        project.save()

    def test_project_metadata(self):
        project = models.Project(slug='slug')
        metadata = {'name': 'Atilla the Hun',
                    'occupation': 'destroyer of lawns'}
        project.metadata = metadata
        project.save()
        project = models.Project.objects.get(slug='slug')
        self.assertEquals(project.metadata['occupation'],
                          'destroyer of lawns')

    def test_absolute_url(self):
        project = models.Project(slug='slug')
        self.assertEquals(project.get_absolute_url(),
                          '/slug/')
