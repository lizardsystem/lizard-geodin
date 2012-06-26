# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.http import Http404
from django.test import TestCase

from lizard_geodin import models
from lizard_geodin import views


class CommonModelTest(TestCase):
    # The tests are done with Project because Common is abstract.

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


class ProjectModelTest(TestCase):

    def test_absolute_url(self):
        project = models.Project(slug='slug')
        self.assertEquals(project.get_absolute_url(),
                          '/slug/')


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

