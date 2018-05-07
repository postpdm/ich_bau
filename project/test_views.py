from django.contrib.auth.models import User

from django.test import TestCase, Client

from django.core.urlresolvers import reverse

class Project_View_Test_Client(TestCase):
    def test_Project_All_Public(self):
        c = Client()
        response = c.get( reverse('project:all_public') )
        self.assertEqual( response.status_code, 200 )

    def test_Project_Index(self):
        c = Client()
        response = c.get( reverse('project:index') )
        self.assertContains(response, 'Please, log in to see your projects.', status_code=200 )
