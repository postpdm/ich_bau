from django.test import TestCase, Client

from django.urls import reverse_lazy

class View_Test_Homepage(TestCase):
    def test_homepahe(self):
        c = Client()
        response = c.get( reverse_lazy('home') )
        self.assertEqual( response.status_code, 200 )
