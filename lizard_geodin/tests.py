# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.http import Http404
from django.test import TestCase

from lizard_geodin import models
from lizard_geodin import views


class ModelsTest(TestCase):
    # Test utility functions in models.py.

    def test_create_multiple_from_json_empty(self):
        the_json = []
        the_model = models.Project
        self.assertEquals(
            models.create_multiple_from_json(the_json, the_model), [])

    def test_create_multiple_from_json(self):
        the_json = [{'prj_id': 'slug'},]
        the_model = models.Project
        self.assertEquals(
            models.create_multiple_from_json(the_json, the_model),
            ['slug'])
        self.assertEquals(len(models.Project.objects.all()), 1)


class CommonModelTest(TestCase):
    # The tests are done with Project because Common is abstract.

    def test_project_smoke(self):
        project = models.Project()
        project.save()

    def test_unicode(self):
        project = models.Project(name='Atilla the Hun')
        self.assertTrue(unicode(project))

    def test_project_metadata(self):
        project = models.Project(slug='slug')
        metadata = {'name': 'Atilla the Hun',
                    'occupation': 'destroyer of lawns'}
        project.metadata = metadata
        project.save()
        project = models.Project.objects.get(slug='slug')
        self.assertEquals(project.metadata['occupation'],
                          'destroyer of lawns')

    def test_update_from_json(self):
        project = models.Project(slug='slug')
        project.save()
        the_json = {'prj_id': 'slug',
                    'prj_name': 'name'}
        project.update_from_json(the_json)
        self.assertEquals(project.name, 'name')

    def test_update_from_json_with_left_over_data(self):
        project = models.Project(slug='slug')
        project.save()
        the_json = {'prj_id': 'slug',
                    'extra': 'extra'}
        project.update_from_json(the_json)
        # Nothing happens with this at the moment. But at least it doesn't
        # crash :-)

    def test_json_from_source_url_missing_source_url(self):
        project = models.Project()
        project.save()
        with self.assertRaises(ValueError):
            project.load_from_geodin()


class ProjectModelTest(TestCase):

    def test_absolute_url(self):
        project = models.Project(slug='slug')
        self.assertEquals(project.get_absolute_url(),
                          '/slug/')

    def test_load_from_geodin(self):
        project = models.Project(source_url='http://example.com')
        project.save()
        # project.load_from_geodin()  # Returns None for now. Dummy.


class ProjectsOverviewTest(TestCase):

    def test_projects(self):
        view = views.ProjectsOverview()
        self.assertEquals(len(view.projects()), 0)


class ProjectViewTest(TestCase):

    def test_projects_404(self):
        view = views.ProjectView()
        view.kwargs = {'slug': 'slug'}
        with self.assertRaises(Http404):
            view.project

    def test_projects(self):
        project = models.Project(slug='slug')
        project.save()
        view = views.ProjectView()
        view.kwargs = {'slug': 'slug'}
        self.assertEquals(view.project, project)
