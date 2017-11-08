from django.test import TestCase
from .templatetags.version_info import *

class Version_Info_Test(TestCase):
    def test_version_info(self):
        self.assertTrue( ' at ' in site_version_info() )